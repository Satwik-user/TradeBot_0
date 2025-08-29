# scripts/init_database.py
"""
Database initialization script for TradeBot
"""

import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from database.db_connector import test_connection, init_db
from database.repositories.user_repository import test_repository
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tradebot.init")

def main():
    """Initialize the database"""
    print("🚀 TradeBot Database Initialization")
    print("=" * 50)
    
    # Test connection
    print("1. Testing database connection...")
    if not test_connection():
        print("❌ Database connection failed!")
        print("\nPlease check:")
        print("- PostgreSQL is running")
        print("- Database 'tradebot' exists")
        print("- User 'tradebot_user' has permissions")
        print("- .env file has correct credentials")
        return False
    
    print("✅ Database connection successful!")
    
    # Initialize schema
    print("\n2. Initializing database schema...")
    try:
        init_db()
        print("✅ Database schema initialized!")
    except Exception as e:
        print(f"❌ Schema initialization failed: {e}")
        return False
    
    # Test repositories
    print("\n3. Testing database repositories...")
    if test_repository():
        print("✅ Repository tests passed!")
    else:
        print("⚠️ Repository tests had issues")
    
    print("\n🎉 Database initialization complete!")
    print("\nYou can now start the backend server:")
    print("cd backend && uvicorn app:app --reload")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)