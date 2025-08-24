from database.db_connector import execute_query, execute_transaction
from typing import Dict, Any, List, Optional
import logging

# Set up logger
logger = logging.getLogger("tradebot.database.user")

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user by ID
    
    Args:
        user_id (int): User ID
        
    Returns:
        Optional[Dict[str, Any]]: User data or None if not found
    """
    query = """
    SELECT id, username, password_hash, email, balance, created_at, updated_at
    FROM users
    WHERE id = %s
    """
    
    return execute_query(query, (user_id,), fetch_all=False)

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user by username
    
    Args:
        username (str): Username
        
    Returns:
        Optional[Dict[str, Any]]: User data or None if not found
    """
    query = """
    SELECT id, username, password_hash, email, balance, created_at, updated_at
    FROM users
    WHERE username = %s
    """
    
    return execute_query(query, (username,), fetch_all=False)

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get user by email
    
    Args:
        email (str): Email address
        
    Returns:
        Optional[Dict[str, Any]]: User data or None if not found
    """
    query = """
    SELECT id, username, password_hash, email, balance, created_at, updated_at
    FROM users
    WHERE email = %s
    """
    
    return execute_query(query, (email,), fetch_all=False)

def get_user_balances(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all balances for a user
    
    Args:
        user_id (int): User ID
        
    Returns:
        List[Dict[str, Any]]: List of user balances
    """
    query = """
    SELECT asset, balance, updated_at
    FROM user_balances
    WHERE user_id = %s
    ORDER BY asset
    """
    
    return execute_query(query, (user_id,))

def get_user_balance(user_id: int, asset: str) -> Optional[Dict[str, Any]]:
    """
    Get balance for a specific asset for a user
    
    Args:
        user_id (int): User ID
        asset (str): Asset code (e.g., 'BTC', 'USDT')
        
    Returns:
        Optional[Dict[str, Any]]: Balance data or None if not found
    """
    query = """
    SELECT asset, balance, updated_at
    FROM user_balances
    WHERE user_id = %s AND asset = %s
    """
    
    return execute_query(query, (user_id, asset), fetch_all=False)

def update_user_balance(user_id: int, asset: str, amount: float) -> Dict[str, Any]:
    """
    Update a user's balance for a specific asset
    
    Args:
        user_id (int): User ID
        asset (str): Asset code (e.g., 'BTC', 'USDT')
        amount (float): New balance amount
        
    Returns:
        Dict[str, Any]: Result of the update operation
    """
    query = """
    INSERT INTO user_balances (user_id, asset, balance)
    VALUES (%s, %s, %s)
    ON CONFLICT (user_id, asset)
    DO UPDATE SET balance = %s, updated_at = CURRENT_TIMESTAMP
    RETURNING id, user_id, asset, balance, updated_at
    """
    
    result = execute_query(query, (user_id, asset, amount, amount), fetch_all=False)
    logger.info(f"Updated balance for user {user_id}, asset {asset}: {amount}")
    return result

def create_user(username: str, password_hash: str, email: str) -> Dict[str, Any]:
    """
    Create a new user
    
    Args:
        username (str): Username
        password_hash (str): Hashed password
        email (str): Email address
        
    Returns:
        Dict[str, Any]: Created user data
    """
    query = """
    INSERT INTO users (username, password_hash, email)
    VALUES (%s, %s, %s)
    RETURNING id, username, email, balance, created_at, updated_at
    """
    
    result = execute_query(query, (username, password_hash, email), fetch_all=False)
    logger.info(f"Created new user: {username}")
    return result

def update_user(user_id: int, **kwargs) -> Dict[str, Any]:
    """
    Update user data
    
    Args:
        user_id (int): User ID
        **kwargs: Fields to update (username, email, password_hash, balance)
        
    Returns:
        Dict[str, Any]: Result of the update operation
    """
    allowed_fields = ['username', 'email', 'password_hash', 'balance']
    update_fields = []
    params = []
    
    # Build SET clause for SQL UPDATE
    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            update_fields.append(f"{field} = %s")
            params.append(value)
    
    if not update_fields:
        return {"affected_rows": 0}
        
    # Add updated_at timestamp and user_id
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    
    # Build the query
    query = f"""
    UPDATE users
    SET {', '.join(update_fields)}
    WHERE id = %s
    RETURNING id, username, email, balance, created_at, updated_at
    """
    
    # Add user_id as the last parameter
    params.append(user_id)
    
    result = execute_query(query, tuple(params), fetch_all=False)
    logger.info(f"Updated user {user_id}: fields {list(kwargs.keys())}")
    return result

def update_user_balance_transaction(user_id: int, asset_changes: Dict[str, float]) -> Dict[str, int]:
    """
    Update multiple asset balances for a user in a single transaction
    
    Args:
        user_id (int): User ID
        asset_changes (Dict[str, float]): Dict mapping assets to changes in balance
        
    Returns:
        Dict[str, int]: Result of the transaction
    """
    queries = []
    
    for asset, amount in asset_changes.items():
        query = """
        INSERT INTO user_balances (user_id, asset, balance)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, asset)
        DO UPDATE SET balance = user_balances.balance + %s, updated_at = CURRENT_TIMESTAMP
        """
        queries.append({
            "query": query,
            "params": (user_id, asset, amount, amount)
        })
    
    result = execute_transaction(queries)
    logger.info(f"Updated balances for user {user_id}: {asset_changes}")
    return result