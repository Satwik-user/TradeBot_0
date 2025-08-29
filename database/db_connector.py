# database/db_connector.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional, Union, List

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Set up logger
logger = logging.getLogger("tradebot.database")

# Database connection parameters
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "tradebot"),
    "user": os.getenv("DB_USER", "tradebot_user"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432"))
}

def get_db_connection():
    """
    Create and return a database connection
    
    Returns:
        connection: PostgreSQL database connection
    """
    try:
        logger.debug(f"Connecting to database: {DB_PARAMS['user']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['dbname']}")
        conn = psycopg2.connect(**DB_PARAMS)
        logger.debug("Database connection established")
        return conn
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL connection error: {e}")
        raise
    except Exception as e:
        logger.error(f"Database connection error: {e}", exc_info=True)
        raise

def execute_query(
    query: str,
    params: Optional[tuple] = None,
    fetch_all: bool = True
) -> Union[List[Dict[str, Any]], Dict[str, Any], Dict[str, int], None]:
    """
    Execute a SQL query and return the results
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch_all (bool): Whether to fetch all results or just one
        
    Returns:
        list or dict: Query results
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            logger.debug(f"Executing query: {query[:100]}...")
            cur.execute(query, params)
            
            if query.strip().upper().startswith(('SELECT', 'WITH', 'RETURNING')):
                if fetch_all:
                    result = cur.fetchall()
                    logger.debug(f"Query returned {len(result) if result else 0} rows")
                    return [dict(row) for row in result] if result else []
                else:
                    result = cur.fetchone()
                    logger.debug(f"Query returned {'1 row' if result else 'no rows'}")
                    return dict(result) if result else None
            else:
                conn.commit()
                affected_rows = cur.rowcount
                logger.debug(f"Query affected {affected_rows} rows")
                return {"affected_rows": affected_rows}
                
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"PostgreSQL query execution error: {e}")
        logger.error(f"Query: {query}")
        if params:
            logger.error(f"Parameters: {params}")
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Query execution error: {e}", exc_info=True)
        raise
    finally:
        if conn:
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
    conn = None
    affected_rows = 0
    
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            for query_item in queries:
                query = query_item.get("query")
                params = query_item.get("params")
                
                logger.debug(f"Transaction query: {query[:100]}...")
                cur.execute(query, params)
                affected_rows += cur.rowcount
                
            conn.commit()
            logger.debug(f"Transaction completed, {affected_rows} total rows affected")
            return {"affected_rows": affected_rows}
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Transaction execution error: {e}", exc_info=True)
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize the database with schema"""
    try:
        # Get the schema file path
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
        # Read schema from file
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        logger.info("Initializing database schema...")
        
        # Execute schema
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
            logger.info("✅ Database initialized successfully")
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error executing schema: {e}", exc_info=True)
            raise
        finally:
            if conn:
                conn.close()
                
    except FileNotFoundError as e:
        logger.error(f"Schema file error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise

def test_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 'Connection successful!' AS message, version() AS db_version")
            result = cur.fetchone()
            
        conn.close()
        
        if result:
            logger.info(f"✅ Database test: {result[0]}")
            logger.debug(f"Database version: {result[1]}")
            return True
        else:
            logger.error("❌ Database test failed: No result")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

# Database management functions
def drop_all_tables():
    """Drop all tables (for development/testing)"""
    try:
        drop_queries = [
            "DROP TABLE IF EXISTS voice_commands CASCADE;",
            "DROP TABLE IF EXISTS market_data CASCADE;",
            "DROP TABLE IF EXISTS user_balances CASCADE;",
            "DROP TABLE IF EXISTS trades CASCADE;",
            "DROP TABLE IF EXISTS trading_pairs CASCADE;",
            "DROP TABLE IF EXISTS users CASCADE;"
        ]
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                for query in drop_queries:
                    cur.execute(query)
            conn.commit()
            logger.info("✅ All tables dropped successfully")
            return True
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        return False

if __name__ == "__main__":
    # Test the connection when run directly
    print("Testing TradeBot Database Connection...")
    print(f"Database: {DB_PARAMS['dbname']}")
    print(f"Host: {DB_PARAMS['host']}:{DB_PARAMS['port']}")
    print(f"User: {DB_PARAMS['user']}")
    print("-" * 50)
    
    if test_connection():
        print("✅ Database connection successful!")
        
        # Test a simple query
        try:
            result = execute_query("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public'", fetch_all=False)
            print(f"✅ Database has {result['table_count']} tables")
        except Exception as e:
            print(f"⚠️ Could not query tables: {e}")
            
    else:
        print("❌ Database connection failed!")
        print("\nTroubleshooting steps:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify database credentials in .env file")
        print("3. Ensure database 'tradebot' exists")
        print("4. Check if user has proper permissions")