import logging
import hashlib
import time
from typing import Dict, Any, List, Optional

# Set up logger
logger = logging.getLogger("tradebot.trading_utils")

def calculate_order_hash(
    symbol: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
    timestamp: int
) -> str:
    """
    Calculate a unique hash for an order
    
    Args:
        symbol (str): Trading pair symbol
        order_type (str): Order type (buy/sell)
        quantity (float): Order quantity
        price (Optional[float]): Order price
        timestamp (int): Order timestamp
        
    Returns:
        str: Order hash
    """
    # Create a string with all order data
    price_str = str(price) if price is not None else "market"
    order_data = f"{symbol}-{order_type}-{quantity}-{price_str}-{timestamp}"
    
    # Generate a SHA-256 hash
    return hashlib.sha256(order_data.encode()).hexdigest()[:16]

def format_price(value: float, decimals: int = 2) -> str:
    """
    Format a price with the appropriate number of decimals
    
    Args:
        value (float): Price value
        decimals (int): Number of decimal places
        
    Returns:
        str: Formatted price string
    """
    return f"{value:,.{decimals}f}"

def get_symbol_precision(symbol: str) -> int:
    """
    Get the appropriate decimal precision for a symbol
    
    Args:
        symbol (str): Trading pair symbol
        
    Returns:
        int: Decimal precision
    """
    # Different symbols might require different precisions
    precision_map = {
        "BTCUSDT": 6,   # 0.000001 BTC
        "ETHUSDT": 5,   # 0.00001 ETH
        "DOGEUSDT": 1,  # 0.1 DOGE
    }
    
    return precision_map.get(symbol, 2)

def calculate_position_size(
    available_balance: float, 
    risk_percentage: float,
    entry_price: float,
    stop_loss_price: float
) -> float:
    """
    Calculate position size based on risk management
    
    Args:
        available_balance (float): Available balance
        risk_percentage (float): Percentage of balance to risk
        entry_price (float): Entry price
        stop_loss_price (float): Stop loss price
        
    Returns:
        float: Position size
    """
    if entry_price <= stop_loss_price:
        # For long positions, stop loss should be below entry
        logger.warning("Stop loss price should be below entry price for long positions")
        return 0
        
    # Calculate risk amount
    risk_amount = available_balance * (risk_percentage / 100)
    
    # Calculate position size
    price_difference = entry_price - stop_loss_price
    position_size = risk_amount / price_difference
    
    return position_size

def calculate_take_profit_price(
    entry_price: float,
    stop_loss_price: float,
    risk_reward_ratio: float = 2.0
) -> float:
    """
    Calculate take profit price based on risk-reward ratio
    
    Args:
        entry_price (float): Entry price
        stop_loss_price (float): Stop loss price
        risk_reward_ratio (float): Risk-reward ratio
        
    Returns:
        float: Take profit price
    """
    # Calculate risk (difference between entry and stop loss)
    risk = abs(entry_price - stop_loss_price)
    
    # Calculate reward (risk * risk_reward_ratio)
    reward = risk * risk_reward_ratio
    
    # Calculate take profit price
    if entry_price > stop_loss_price:
        # Long position
        take_profit = entry_price + reward
    else:
        # Short position
        take_profit = entry_price - reward
        
    return take_profit