# database/repositories/trade_repository.py
from database.db_connector import execute_query, execute_transaction
from typing import Dict, Any, List, Optional
import logging

# Set up logger
logger = logging.getLogger("tradebot.database.trade")


def create_trade(
    user_id: int,
    pair_id: int,
    order_type: str,
    order_subtype: str,
    quantity: float,
    price: float,
    total_value: float,
    fee: float,
    status: str
) -> Dict[str, Any]:
    """
    Create a new trade record
    """
    query = """
    INSERT INTO trades (
        user_id, pair_id, order_type, order_subtype, 
        quantity, price, total_value, fee, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id, user_id, pair_id, order_type, order_subtype,
              quantity, price, total_value, fee, status, created_at, updated_at
    """

    params = (
        user_id, pair_id, order_type, order_subtype,
        quantity, price, total_value, fee, status
    )

    result = execute_query(query, params, fetch_all=False)
    logger.info(f"✅ Created trade: user {user_id}, {order_type} {quantity} of pair {pair_id} at {price}")
    return result


def get_user_trades(user_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get trades for a specific user
    """
    query = """
    SELECT t.id, t.order_type, t.order_subtype, t.quantity, t.price, t.total_value,
           t.fee, t.status, t.created_at, t.updated_at,
           tp.symbol, tp.base_asset, tp.quote_asset
    FROM trades t
    JOIN trading_pairs tp ON t.pair_id = tp.id
    WHERE t.user_id = %s
    ORDER BY t.created_at DESC
    LIMIT %s OFFSET %s
    """
    return execute_query(query, (user_id, limit, offset))


def get_trade_by_id(trade_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a trade by ID
    """
    query = """
    SELECT t.id, t.user_id, t.order_type, t.order_subtype, t.quantity, t.price, 
           t.total_value, t.fee, t.status, t.created_at, t.updated_at,
           tp.symbol, tp.base_asset, tp.quote_asset
    FROM trades t
    JOIN trading_pairs tp ON t.pair_id = tp.id
    WHERE t.id = %s
    """
    return execute_query(query, (trade_id,), fetch_all=False)


def get_trades_by_user(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all trades for a user
    """
    query = "SELECT * FROM trades WHERE user_id = %s ORDER BY created_at DESC"
    return execute_query(query, (user_id,), fetch_all=True)


def update_trade_status(trade_id: int, status: str) -> Dict[str, Any]:
    """
    Update a trade's status
    """
    query = """
    UPDATE trades
    SET status = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    RETURNING id, user_id, pair_id, order_type, order_subtype,
              quantity, price, total_value, fee, status, created_at, updated_at
    """
    result = execute_query(query, (status, trade_id), fetch_all=False)
    logger.info(f"🔄 Updated trade {trade_id} status → {status}")
    return result


def get_user_trade_stats(user_id: int) -> Dict[str, Any]:
    """
    Get trade statistics for a user
    """
    query = """
    SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN order_type = 'buy' THEN 1 ELSE 0 END) as buy_count,
        SUM(CASE WHEN order_type = 'sell' THEN 1 ELSE 0 END) as sell_count,
        SUM(total_value) as total_value,
        SUM(fee) as total_fees,
        AVG(price) as avg_price,
        MIN(created_at) as first_trade,
        MAX(created_at) as last_trade
    FROM trades
    WHERE user_id = %s
    """
    return execute_query(query, (user_id,), fetch_all=False)


def get_trade_history_by_symbol(user_id: int, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get trade history for a specific symbol
    """
    query = """
    SELECT t.id, t.order_type, t.order_subtype, t.quantity, t.price, t.total_value,
           t.fee, t.status, t.created_at, t.updated_at,
           tp.symbol, tp.base_asset, tp.quote_asset
    FROM trades t
    JOIN trading_pairs tp ON t.pair_id = tp.id
    WHERE t.user_id = %s AND tp.symbol = %s
    ORDER BY t.created_at DESC
    LIMIT %s
    """
    return execute_query(query, (user_id, symbol, limit))


def get_trading_pair_by_symbol(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get a trading pair by symbol
    """
    query = """
    SELECT id, symbol, base_asset, quote_asset, description, created_at
    FROM trading_pairs
    WHERE symbol = %s
    """
    return execute_query(query, (symbol,), fetch_all=False)


def get_all_trading_pairs() -> List[Dict[str, Any]]:
    """
    Get all trading pairs
    """
    query = """
    SELECT id, symbol, base_asset, quote_asset, description, created_at
    FROM trading_pairs
    ORDER BY symbol
    """
    return execute_query(query)


def execute_trade_transaction(
    user_id: int,
    pair_id: int,
    order_type: str,
    order_subtype: str,
    quantity: float,
    price: float,
    total_value: float,
    fee: float,
    base_asset: str,
    quote_asset: str
) -> Dict[str, Any]:
    """
    Execute a trade and update user balances in a single transaction
    """
    queries = []

    # Insert trade record
    trade_query = """
    INSERT INTO trades (
        user_id, pair_id, order_type, order_subtype, 
        quantity, price, total_value, fee, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'filled')
    RETURNING id
    """
    trade_params = (user_id, pair_id, order_type, order_subtype, quantity, price, total_value, fee)

    queries.append({"query": trade_query, "params": trade_params})

    if order_type == "buy":
        # Reduce quote asset (e.g., USDT)
        queries.append({
            "query": """
                UPDATE user_balances
                SET balance = balance - %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND asset = %s
            """,
            "params": (total_value + fee, user_id, quote_asset)
        })

        # Increase base asset (e.g., BTC)
        queries.append({
            "query": """
                INSERT INTO user_balances (user_id, asset, balance)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, asset)
                DO UPDATE SET balance = user_balances.balance + %s, updated_at = CURRENT_TIMESTAMP
            """,
            "params": (user_id, base_asset, quantity, quantity)
        })
    else:  # sell
        # Reduce base asset
        queries.append({
            "query": """
                UPDATE user_balances
                SET balance = balance - %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND asset = %s
            """,
            "params": (quantity, user_id, base_asset)
        })

        # Increase quote asset
        net_value = total_value - fee
        queries.append({
            "query": """
                INSERT INTO user_balances (user_id, asset, balance)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, asset)
                DO UPDATE SET balance = user_balances.balance + %s, updated_at = CURRENT_TIMESTAMP
            """,
            "params": (user_id, quote_asset, net_value, net_value)
        })

    result = execute_transaction(queries)
    logger.info(f"💹 Executed {order_type} trade: user {user_id}, {quantity} {base_asset} @ {price} {quote_asset}")
    return result
