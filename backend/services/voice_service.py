import random
import logging
from typing import Dict, Any, List

# Set up logger
logger = logging.getLogger("tradebot.voice")

def generate_response(intent: str, data: Dict[str, Any]) -> str:
    """
    Generate a natural language response based on the intent and data
    
    Args:
        intent (str): The detected intent
        data (Dict[str, Any]): Data to include in the response
        
    Returns:
        str: Natural language response
    """
    logger.info(f"Generating response for intent: {intent}")
    
    if intent == "market_query":
        return generate_market_query_response(data)
    elif intent == "trade_order":
        return generate_trade_order_response(data)
    elif intent == "indicator_query":
        return generate_indicator_query_response(data)
    else:
        return "I'm sorry, I couldn't process that request."

def generate_market_query_response(data: Dict[str, Any]) -> str:
    """Generate response for market query intent"""
    symbol = data.get("symbol", "").replace("USDT", "")
    price = data.get("price")
    change_24h = data.get("change_24h")
    
    # Generate different response variants for natural conversation
    responses = [
        f"The current price of {symbol} is ${price:,.2f}. It has changed {change_24h:.2f}% in the last 24 hours.",
        f"{symbol} is currently trading at ${price:,.2f}, with a 24-hour change of {change_24h:.2f}%.",
        f"Right now, {symbol} is worth ${price:,.2f}. That's a {change_24h:.2f}% change since yesterday."
    ]
    
    # Add sentiment based on price change
    if change_24h > 3:
        responses.append(f"{symbol} is performing strongly today, up {change_24h:.2f}% at ${price:,.2f}.")
    elif change_24h < -3:
        responses.append(f"{symbol} is down significantly today, falling {abs(change_24h):.2f}% to ${price:,.2f}.")
    elif change_24h > 0:
        responses.append(f"{symbol} is slightly up today, gaining {change_24h:.2f}% to ${price:,.2f}.")
    else:
        responses.append(f"{symbol} is slightly down today, falling {abs(change_24h):.2f}% to ${price:,.2f}.")
    
    return random.choice(responses)

def generate_trade_order_response(data: Dict[str, Any]) -> str:
    """Generate response for trade order intent"""
    order_type = data.get("order_type", "").upper()
    symbol = data.get("symbol", "").replace("USDT", "")
    quantity = data.get("quantity")
    price = data.get("price")
    total_value = data.get("total_value")
    status = data.get("status", "").lower()
    
    # For pending limit orders
    if status == "pending":
        return f"I've placed a limit order to {order_type} {quantity} {symbol} at ${price:,.2f}. The current market price is ${data.get('message', '').split('$')[-1]}."
    
    # For market orders or executed limit orders
    responses = [
        f"Your {order_type} order for {quantity} {symbol} has been simulated at ${price:,.2f}, with a total value of ${total_value:,.2f}.",
        f"I've simulated a {order_type} order for {quantity} {symbol} at ${price:,.2f}. Total value: ${total_value:,.2f}.",
        f"Order simulated: {order_type} {quantity} {symbol} at ${price:,.2f}. Total value: ${total_value:,.2f}."
    ]
    
    return random.choice(responses)

def generate_indicator_query_response(data: Dict[str, Any]) -> str:
    """Generate response for indicator query intent"""
    symbol = data.get("symbol", "").replace("USDT", "")
    indicator = data.get("indicator", {})
    
    if not indicator:
        return f"I couldn't find indicator data for {symbol} at the moment."
    
    indicator_name = indicator.get("name", "")
    
    if indicator_name == "RSI":
        value = indicator.get("value")
        interpretation = indicator.get("interpretation", "")
        
        responses = [
            f"The RSI for {symbol} is currently at {value}. {interpretation}",
            f"{symbol}'s RSI is showing a value of {value}. {interpretation}",
            f"The Relative Strength Index for {symbol} is {value}. {interpretation}"
        ]
        
    elif indicator_name == "MACD":
        value = indicator.get("value")
        signal = indicator.get("signal")
        histogram = indicator.get("histogram")
        interpretation = indicator.get("interpretation", "")
        
        responses = [
            f"The MACD line for {symbol} is at {value} with a signal line at {signal}. Histogram: {histogram}. {interpretation}",
            f"{symbol}'s MACD indicator shows {interpretation} The MACD is at {value} and signal line at {signal}.",
            f"MACD analysis for {symbol}: Line at {value}, signal at {signal}, and histogram at {histogram}. {interpretation}"
        ]
        
    elif "Bollinger" in indicator_name:
        upper = indicator.get("upper")
        middle = indicator.get("middle")
        lower = indicator.get("lower")
        interpretation = indicator.get("interpretation", "")
        
        responses = [
            f"Bollinger Bands for {symbol}: Upper band at ${upper:,.2f}, middle band at ${middle:,.2f}, and lower band at ${lower:,.2f}. {interpretation}",
            f"{symbol}'s price in relation to Bollinger Bands: ${data.get('price'):,.2f}. {interpretation} Bands are set at ${upper:,.2f}, ${middle:,.2f}, and ${lower:,.2f}.",
            f"Bollinger Band analysis for {symbol}: Current price is ${data.get('price'):,.2f}, with bands at ${upper:,.2f} (upper), ${middle:,.2f} (middle), and ${lower:,.2f} (lower). {interpretation}"
        ]
        
    elif "Moving Average" in indicator_name:
        ma_value = indicator.get("value")
        interpretation = indicator.get("interpretation", "")
        
        responses = [
            f"The 20-day Moving Average for {symbol} is ${ma_value:,.2f}. Current price: ${data.get('price'):,.2f}. {interpretation}",
            f"{symbol}'s price (${data.get('price'):,.2f}) relative to its 20-day MA (${ma_value:,.2f}): {interpretation}",
            f"Moving Average analysis for {symbol}: 20-day MA is at ${ma_value:,.2f} while the price is ${data.get('price'):,.2f}. {interpretation}"
        ]
        
    else:
        return f"I have indicator data for {symbol}, but I'm not sure how to interpret it."
    
    return random.choice(responses)