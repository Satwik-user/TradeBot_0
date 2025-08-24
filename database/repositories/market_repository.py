from database.db_connector import execute_query
from typing import Dict, Any, List, Optional
import time
from datetime import datetime, timedelta
import logging

# Set up logger
logger = logging.getLogger("tradebot.database.market")

def save_market_data(symbol: str, price: float, change_24h: float, volume: float) -> Dict[str, Any]:
    """
    Save market data for a trading pair
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        price (float): Current price
        change_24h (float): 24-hour price change percentage
        volume (float): 24-hour trading volume
        
    Returns:
        Dict[str, Any]: Result of the insert operation
    """
    query = """
    INSERT INTO market_data (symbol, price, change_24h, volume)
    VALUES (%s, %s, %s, %s)
    RETURNING id, symbol, price, change_24h, volume, timestamp
    """
    
    result = execute_query(query, (symbol, price, change_24h, volume), fetch_all=False)
    logger.info(f"Saved market data for {symbol}: price {price}, change {change_24h}%, volume {volume}")
    return result

def get_latest_market_data(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get the latest market data for a trading pair
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        
    Returns:
        Optional[Dict[str, Any]]: Market data or None if not found
    """
    query = """
    SELECT id, symbol, price, change_24h, volume, timestamp
    FROM market_data
    WHERE symbol = %s
    ORDER BY timestamp DESC
    LIMIT 1
    """
    
    return execute_query(query, (symbol,), fetch_all=False)

def get_historical_market_data(symbol: str, hours: int = 24) -> List[Dict[str, Any]]:
    """
    Get historical market data for a trading pair
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        hours (int): Number of hours of historical data to retrieve
        
    Returns:
        List[Dict[str, Any]]: List of market data records
    """
    query = """
    SELECT id, symbol, price, change_24h, volume, timestamp
    FROM market_data
    WHERE symbol = %s
    AND timestamp >= %s
    ORDER BY timestamp ASC
    """
    
    # Calculate timestamp for hours ago
    hours_ago = datetime.now() - timedelta(hours=hours)
    
    return execute_query(query, (symbol, hours_ago))

def get_market_data_by_time_range(symbol: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """
    Get market data for a trading pair within a specific time range
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        start_time (datetime): Start of time range
        end_time (datetime): End of time range
        
    Returns:
        List[Dict[str, Any]]: List of market data records
    """
    query = """
    SELECT id, symbol, price, change_24h, volume, timestamp
    FROM market_data
    WHERE symbol = %s
    AND timestamp BETWEEN %s AND %s
    ORDER BY timestamp ASC
    """
    
    return execute_query(query, (symbol, start_time, end_time))

def get_aggregated_market_data(symbol: str, interval: str = '1h', limit: int = 24) -> List[Dict[str, Any]]:
    """
    Get aggregated market data for a trading pair
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        interval (str): Aggregation interval ('1h', '1d', etc.)
        limit (int): Maximum number of records to return
        
    Returns:
        List[Dict[str, Any]]: List of aggregated market data records
    """
    # Determine the time bucket based on interval
    interval_map = {
        '1h': '1 hour',
        '4h': '4 hours',
        '12h': '12 hours',
        '1d': '1 day',
        '1w': '1 week'
    }
    
    time_bucket = interval_map.get(interval, '1 hour')
    
    query = """
    SELECT
        time_bucket(%s, timestamp) AS bucket,
        symbol,
        FIRST(price, timestamp) AS open_price,
        MAX(price) AS high_price,
        MIN(price) AS low_price,
        LAST(price, timestamp) AS close_price,
        SUM(volume) AS volume
    FROM market_data
    WHERE symbol = %s
    GROUP BY bucket, symbol
    ORDER BY bucket DESC
    LIMIT %s
    """
    
    # For the hackathon, we don't have TimescaleDB installed for time bucketing,
    # so we'll simulate the result with basic hourly grouping
    if interval == '1h':
        query = """
        SELECT
            date_trunc('hour', timestamp) AS bucket,
            symbol,
            FIRST_VALUE(price) OVER (PARTITION BY date_trunc('hour', timestamp) ORDER BY timestamp) AS open_price,
            MAX(price) OVER (PARTITION BY date_trunc('hour', timestamp)) AS high_price,
            MIN(price) OVER (PARTITION BY date_trunc('hour', timestamp)) AS low_price,
            LAST_VALUE(price) OVER (PARTITION BY date_trunc('hour', timestamp) ORDER BY timestamp) AS close_price,
            SUM(volume) OVER (PARTITION BY date_trunc('hour', timestamp)) AS volume
        FROM market_data
        WHERE symbol = %s
        ORDER BY bucket DESC
        LIMIT %s
        """
        return execute_query(query, (symbol, limit))
    elif interval == '1d':
        query = """
        SELECT
            date_trunc('day', timestamp) AS bucket,
            symbol,
            AVG(price) AS avg_price,
            MAX(price) AS high_price,
            MIN(price) AS low_price,
            SUM(volume) AS volume
        FROM market_data
        WHERE symbol = %s
        GROUP BY bucket, symbol
        ORDER BY bucket DESC
        LIMIT %s
        """
        return execute_query(query, (symbol, limit))
    else:
        # For other intervals, just return the most recent data points
        query = """
        SELECT id, symbol, price, change_24h, volume, timestamp
        FROM market_data
        WHERE symbol = %s
        ORDER BY timestamp DESC
        LIMIT %s
        """
        return execute_query(query, (symbol, limit))

def log_voice_command(user_id: int, command_text: str, detected_intent: str, response_text: str) -> Dict[str, Any]:
    """
    Log a user's voice command
    
    Args:
        user_id (int): User ID
        command_text (str): Voice command text
        detected_intent (str): Detected intent
        response_text (str): Response text
        
    Returns:
        Dict[str, Any]: Result of the insert operation
    """
    query = """
    INSERT INTO voice_commands (user_id, command_text, detected_intent, response_text)
    VALUES (%s, %s, %s, %s)
    RETURNING id, user_id, command_text, detected_intent, response_text, created_at
    """
    
    result = execute_query(query, (user_id, command_text, detected_intent, response_text), fetch_all=False)
    logger.info(f"Logged voice command for user {user_id}: '{command_text}' with intent '{detected_intent}'")
    return result

def get_user_voice_commands(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get voice command history for a user
    
    Args:
        user_id (int): User ID
        limit (int): Maximum number of records to return
        
    Returns:
        List[Dict[str, Any]]: List of voice command records
    """
    query = """
    SELECT id, command_text, detected_intent, response_text, created_at
    FROM voice_commands
    WHERE user_id = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    
    return execute_query(query, (user_id, limit))