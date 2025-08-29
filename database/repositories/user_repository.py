# database/repositories/user_repository.py
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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
    
    try:
        result = execute_query(query, (user_id,), fetch_all=False)
        if result:
            logger.debug(f"Found user by ID: {user_id}")
        return result
    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {e}")
        return None

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
    
    try:
        result = execute_query(query, (username,), fetch_all=False)
        if result:
            logger.debug(f"Found user by username: {username}")
        return result
    except Exception as e:
        logger.error(f"Error getting user by username {username}: {e}")
        return None

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
    
    try:
        result = execute_query(query, (email,), fetch_all=False)
        if result:
            logger.debug(f"Found user by email: {email}")
        return result
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        return None

def create_user(username: str, password_hash: str, email: str, initial_balance: float = 10000.0) -> Optional[Dict[str, Any]]:
    """
    Create a new user
    
    Args:
        username (str): Username
        password_hash (str): Hashed password
        email (str): Email address
        initial_balance (float): Initial balance in USDT
        
    Returns:
        Optional[Dict[str, Any]]: Created user data or None if failed
    """
    query = """
    INSERT INTO users (username, password_hash, email, balance)
    VALUES (%s, %s, %s, %s)
    RETURNING id, username, email, balance, created_at, updated_at
    """
    
    try:
        result = execute_query(query, (username, password_hash, email, initial_balance), fetch_all=False)
        
        if result:
            logger.info(f"✅ Created new user: {username} with ID: {result['id']}")
            
            # Create initial USDT balance
            try:
                balance_query = """
                INSERT INTO user_balances (user_id, asset, balance)
                VALUES (%s, 'USDT', %s)
                """
                execute_query(balance_query, (result['id'], initial_balance))
                logger.debug(f"Created initial USDT balance for user {result['id']}")
            except Exception as e:
                logger.warning(f"Could not create initial balance for user {result['id']}: {e}")
            
        return result
    except Exception as e:
        logger.error(f"Error creating user {username}: {e}")
        return None

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
    WHERE user_id = %s AND balance > 0
    ORDER BY asset
    """
    
    try:
        result = execute_query(query, (user_id,))
        logger.debug(f"Found {len(result)} balances for user {user_id}")
        return result if result else []
    except Exception as e:
        logger.error(f"Error getting balances for user {user_id}: {e}")
        return []

def get_user_balance(user_id: int, asset: str) -> float:
    """
    Get balance for a specific asset for a user
    
    Args:
        user_id (int): User ID
        asset (str): Asset code (e.g., 'BTC', 'USDT')
        
    Returns:
        float: Balance amount (0.0 if not found)
    """
    query = """
    SELECT balance
    FROM user_balances
    WHERE user_id = %s AND asset = %s
    """
    
    try:
        result = execute_query(query, (user_id, asset), fetch_all=False)
        return float(result['balance']) if result else 0.0
    except Exception as e:
        logger.error(f"Error getting balance for user {user_id}, asset {asset}: {e}")
        return 0.0

def update_user_balance(user_id: int, asset: str, amount: float) -> Optional[Dict[str, Any]]:
    """
    Update a user's balance for a specific asset
    
    Args:
        user_id (int): User ID
        asset (str): Asset code (e.g., 'BTC', 'USDT')
        amount (float): New balance amount
        
    Returns:
        Optional[Dict[str, Any]]: Updated balance data or None if failed
    """
    query = """
    INSERT INTO user_balances (user_id, asset, balance)
    VALUES (%s, %s, %s)
    ON CONFLICT (user_id, asset)
    DO UPDATE SET balance = %s, updated_at = CURRENT_TIMESTAMP
    RETURNING id, user_id, asset, balance, updated_at
    """
    
    try:
        result = execute_query(query, (user_id, asset, amount, amount), fetch_all=False)
        if result:
            logger.debug(f"Updated balance for user {user_id}, asset {asset}: {amount}")
        return result
    except Exception as e:
        logger.error(f"Error updating balance for user {user_id}, asset {asset}: {e}")
        return None

# Test function for the repository
def test_repository():
    """Test the user repository functions"""
    try:
        # Test getting demo user
        demo_user = get_user_by_username("demo")
        if demo_user:
            print(f"✅ Found demo user: {demo_user['username']}")
            
            # Test getting balances
            balances = get_user_balances(demo_user['id'])
            print(f"✅ Demo user has {len(balances)} asset balances")
            
            for balance in balances:
                print(f"  - {balance['asset']}: {balance['balance']}")
                
            return True
        else:
            print("⚠️ Demo user not found")
            return False
            
    except Exception as e:
        print(f"❌ Repository test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing User Repository...")
    test_repository()