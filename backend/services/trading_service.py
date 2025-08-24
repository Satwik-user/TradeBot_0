import requests
import random
import time
import logging
import json
from typing import Dict, Any, Optional, List

# Set up logger
logger = logging.getLogger("tradebot.trading")

def get_market_data(symbol: str, indicator: Optional[str] = None) -> Dict[str, Any]:
    """
    Get market data for a given symbol
    
    Args:
        symbol (str): Trading pair symbol (e.g., BTCUSDT)
        indicator (Optional[str]): Technical indicator to include
        
    Returns:
        Dict[str, Any]: Market data including price and indicator values
    """
    logger.info(f"Getting market data for symbol: {symbol}, indicator: {indicator}")
    
    try:
        # In a real application, you would connect to TradingView API or another data provider
        # For this hackathon, we'll simulate the response
        
        # Generate a realistic price based on the symbol
        base_prices = {
            "BTCUSDT": 58000,
            "ETHUSDT": 3200,
            "DOGEUSDT": 0.12
        }
        
        base_price = base_prices.get(symbol, 100)
        current_price = base_price * (1 + random.uniform(-0.02, 0.02))
        
        # Create response
        response = {
            "symbol": symbol,
            "price": round(current_price, 2),
            "change_24h": round(random.uniform(-5, 5), 2),
            "volume": round(random.uniform(1000000, 10000000), 2),
            "timestamp": int(time.time())
        }
        
        # Add indicator data if requested
        if indicator:
            indicator_lower = indicator.lower()
            
            if "rsi" in indicator_lower:
                rsi_value = round(random.uniform(30, 70), 2)
                response["indicator"] = {
                    "name": "RSI",
                    "value": rsi_value,
                    "interpretation": get_rsi_interpretation(rsi_value)
                }
            
            elif "macd" in indicator_lower:
                macd_value = round(random.uniform(-20, 20), 2)
                signal_value = round(random.uniform(-20, 20), 2)
                
                response["indicator"] = {
                    "name": "MACD",
                    "value": macd_value,
                    "signal": signal_value,
                    "histogram": round(macd_value - signal_value, 2),
                    "interpretation": get_macd_interpretation(macd_value, signal_value)
                }
            
            elif "bollinger" in indicator_lower:
                middle_band = current_price
                band_width = current_price * 0.05
                
                response["indicator"] = {
                    "name": "Bollinger Bands",
                    "upper": round(middle_band + band_width, 2),
                    "middle": round(middle_band, 2),
                    "lower": round(middle_band - band_width, 2),
                    "interpretation": get_bollinger_interpretation(current_price, middle_band, band_width)
                }
                
            elif "moving average" in indicator_lower or "ma" in indicator_lower:
                ma_value = current_price * (1 + random.uniform(-0.01, 0.01))
                
                response["indicator"] = {
                    "name": "Moving Average (MA 20)",
                    "value": round(ma_value, 2),
                    "interpretation": get_ma_interpretation(current_price, ma_value)
                }
        
        logger.info(f"Generated market data: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting market data: {e}", exc_info=True)
        raise

def simulate_trade(order_type: str, symbol: str, quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
    """
    Simulate a trade order
    
    Args:
        order_type (str): "buy" or "sell"
        symbol (str): Trading pair symbol
        quantity (float): Quantity to trade
        price (Optional[float]): Limit price (if None, treated as market order)
        
    Returns:
        Dict[str, Any]: Trade simulation result
    """
    logger.info(f"Simulating trade: {order_type} {quantity} {symbol} at price {price}")
    
    try:
        # Get current market price for the symbol
        market_data = get_market_data(symbol)
        current_price = market_data["price"]
        
        # Generate order ID
        order_id = f"ord-{int(time.time())}-{random.randint(1000, 9999)}"
        
        # Determine if this is a market or limit order
        order_subtype = "market" if price is None else "limit"
        
        # Calculate total value
        executed_price = current_price if price is None else price
        total_value = quantity * executed_price
        
        # Simulate a small fee
        fee = round(total_value * 0.001, 2)  # 0.1% fee
        
        # Create response
        response = {
            "order_id": order_id,
            "symbol": symbol,
            "order_type": order_type,
            "order_subtype": order_subtype,
            "quantity": quantity,
            "price": round(executed_price, 2),
            "total_value": round(total_value, 2),
            "fee": fee,
            "status": "simulated",  # In a real app, this would be "pending", "filled", etc.
            "timestamp": int(time.time())
        }
        
        # For limit orders that are not immediately executable
        if price is not None:
            if (order_type == "buy" and price < current_price) or (order_type == "sell" and price > current_price):
                response["status"] = "pending"
                response["message"] = f"Limit order placed. Current market price is ${current_price}."
        
        logger.info(f"Trade simulation result: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        logger.error(f"Error simulating trade: {e}", exc_info=True)
        raise

# Helper functions for interpreting technical indicators

def get_rsi_interpretation(rsi_value: float) -> str:
    """Get interpretation of RSI value"""
    if rsi_value < 30:
        return "Oversold - potentially bullish signal"
    elif rsi_value > 70:
        return "Overbought - potentially bearish signal"
    else:
        return "Neutral - no strong buy or sell signal"

def get_macd_interpretation(macd: float, signal: float) -> str:
    """Get interpretation of MACD values"""
    if macd > signal:
        return "Bullish signal - MACD above signal line"
    else:
        return "Bearish signal - MACD below signal line"

def get_bollinger_interpretation(price: float, middle: float, band_width: float) -> str:
    """Get interpretation of price relative to Bollinger Bands"""
    upper = middle + band_width
    lower = middle - band_width
    
    if price > upper:
        return "Price above upper band - potentially overbought"
    elif price < lower:
        return "Price below lower band - potentially oversold"
    else:
        return "Price within bands - no strong signal"

def get_ma_interpretation(price: float, ma: float) -> str:
    """Get interpretation of price relative to moving average"""
    if price > ma:
        return "Price above MA - generally bullish"
    else:
        return "Price below MA - generally bearish"