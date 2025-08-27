import sys
import os
sys.path.append('..')

from database.db_connector import execute_query

def test_database_integration():
    """Test database integration"""
    try:
        # Test 1: Query users
        print("Testing users query...")
        users = execute_query("SELECT * FROM users LIMIT 1")
        print(f"✅ Users query successful: Found {len(users)} users")
        
        # Test 2: Query trading pairs
        print("Testing trading pairs query...")
        pairs = execute_query("SELECT * FROM trading_pairs")
        print(f"✅ Trading pairs query successful: Found {len(pairs)} pairs")
        
        # Test 3: Query market data
        print("Testing market data query...")
        market_data = execute_query("SELECT * FROM market_data LIMIT 3")
        print(f"✅ Market data query successful: Found {len(market_data)} records")
        
        # Test 4: Insert and query test record
        print("Testing insert operation...")
        test_query = """
        INSERT INTO voice_commands (user_id, command_text, detected_intent, response_text)
        VALUES (1, 'test command', 'test_intent', 'test response')
        RETURNING id, command_text
        """
        result = execute_query(test_query, fetch_all=False)
        print(f"✅ Insert test successful: {result}")
        
        print("\n🎉 All database integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_integration()