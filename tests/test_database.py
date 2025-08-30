# tests/test_database.py

from database.repositories.user_repository import create_user, get_user_by_username, delete_user
from database.repositories.trade_repository import create_trade, get_trades_by_user
from database.repositories.market_repository import save_market_data, get_latest_market_data


def run_tests():
    print("🚀 Starting database tests...")

    # --- User Repository Test ---
    print("\n[USER TEST]")
    delete_user("test_user")  # cleanup before test
    create_user("test_user", "hashed_pw", "test@example.com")
    user = get_user_by_username("test_user")
    assert user, "❌ User creation failed"
    print("✅ User creation and retrieval passed")

    # --- Trade Repository Test ---
    print("\n[TRADE TEST]")
    trade = create_trade(user["id"], "AAPL", 1.5, "BUY")
    trades = get_trades_by_user(user["id"])
    assert trades, "❌ Trade creation failed"
    print("✅ Trade creation and retrieval passed")

    # --- Market Repository Test ---
    print("\n[MARKET DATA TEST]")
    save_market_data("AAPL", 175.25)
    market_data = get_latest_market_data("AAPL")
    assert market_data, "❌ Market data save/retrieve failed"
    print("✅ Market data save and retrieval passed")

    # Cleanup
    delete_user("test_user")
    print("\n🧹 Cleanup done")

    print("\n🎉 All tests passed successfully!")


if __name__ == "__main__":
    run_tests()
