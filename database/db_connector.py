import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional, Union, List

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger("tradebot.database")

# Database connection parameters
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "tradebot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

def get_db_connection():
    """
    Create and return a database connection
    
    Returns:
        connection: PostgreSQL database connection
    """
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}", exc_info=True)
        raise

def execute_query(
    query: str,
    params: Optional[tuple] = None,
    fetch_all: bool = True
) -> Union[List[Dict[str, Any]], Dict[str, Any], Dict[str, int]]:
    """
    Execute a SQL query and return the results
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch_all (bool): Whether to fetch all results or just one
        
    Returns:
        list or dict: Query results
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            
            if query.strip().upper().startswith(('SELECT', 'WITH')):
                if fetch_all:
                    result = cur.fetchall()
                else:
                    result = cur.fetchone()
                return result
            else:
                conn.commit()
                return {"affected_rows": cur.rowcount}
    except Exception as e:
        conn.rollback()
        logger.error(f"Query execution error: {e}", exc_info=True)
        logger.error(f"Query: {query}")
        if params:
            logger.error(f"Parameters: {params}")
        raise
    finally:
        conn.close()

def execute_transaction(queries: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Execute multiple queries in a transaction
    
    Args:
        queries (List[Dict[str, Any]]): List of queries with their parameters
                                       [{"query": "SQL string", "params": tuple}]
        
    Returns:
        Dict[str, int]: Number of affected rows
    """
    conn = get_db_connection()
    affected_rows = 0
    
    try:
        with conn.cursor() as cur:
            for query_item in queries:
                query = query_item.get("query")
                params = query_item.get("params")
                
                cur.execute(query, params)
                affected_rows += cur.rowcount
                
            conn.commit()
            return {"affected_rows": affected_rows}
    except Exception as e:
        conn.rollback()
        logger.error(f"Transaction execution error: {e}", exc_info=True)
        raise
    finally:
        conn.close()

def init_db():
    """Initialize the database with schema"""
    try:
        # Read schema from file
        with open('database/schema.sql', 'r') as f:
            schema_sql = f.read()
            
        # Execute schema
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error initializing database: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error reading schema file: {e}", exc_info=True)
        raise