from fastapi import APIRouter, HTTPException, Body, Depends, status
from pydantic import BaseModel
import json
import logging
from typing import Dict, Any, Optional

from services.nlp_service import analyze_command
from services.trading_service import get_market_data, simulate_trade
from services.voice_service import generate_response
from utils.auth_utils import get_current_user_optional
from database.repositories.market_repository import log_voice_command

# Set up logger
logger = logging.getLogger("tradebot.voice")

router = APIRouter()

class VoiceCommand(BaseModel):
    command: str

class CommandResponse(BaseModel):
    response: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

@router.post("/process", response_model=CommandResponse)
async def process_voice_command(
    command: VoiceCommand,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """Process a voice command and return an appropriate response"""
    try:
        # Log the command
        user_id = current_user["id"] if current_user else None
        logger.info(f"Processing command: '{command.command}' | User ID: {user_id}")
        
        # Analyze the voice command to determine intent
        command_text = command.command.lower()
        intent, entities = analyze_command(command_text)
        
        logger.info(f"Detected intent: {intent} | Entities: {entities}")
        
        response = "I'm sorry, I didn't understand that command."
        action = None
        data = {}
        
        # Handle different intents
        if intent == "market_query":
            # Get market data for the requested symbol
            symbol = entities.get("symbol", "BTCUSDT")
            market_data = get_market_data(symbol)
            
            # Generate a response based on the market data
            response = generate_response("market_query", market_data)
            action = "display_market_data"
            data = market_data
            
        elif intent == "trade_order":
            # Handle trade order (buy/sell)
            order_type = entities.get("order_type")
            symbol = entities.get("symbol", "BTCUSDT")
            quantity = entities.get("quantity", 1)
            price = entities.get("price")
            
            # Simulate the trade
            trade_result = simulate_trade(order_type, symbol, quantity, price)
            
            # Generate a response based on the trade result
            response = generate_response("trade_order", trade_result)
            action = "execute_trade"
            data = trade_result
            
        elif intent == "indicator_query":
            # Handle indicator query
            indicator = entities.get("indicator")
            symbol = entities.get("symbol", "BTCUSDT")
            
            # Get indicator data
            indicator_data = get_market_data(symbol, indicator=indicator)
            
            # Generate a response based on the indicator data
            response = generate_response("indicator_query", indicator_data)
            action = "display_indicator"
            data = indicator_data
            
        elif intent == "stop_loss":
            # Handle stop loss setting
            percentage = entities.get("percentage", 2)
            symbol = entities.get("symbol", "BTCUSDT")
            
            # Get current price
            market_data = get_market_data(symbol)
            current_price = market_data["price"]
            
            # Calculate stop loss price
            stop_loss_price = current_price * (1 - percentage / 100)
            
            response = f"Setting a stop loss at {percentage}% below current price. If {symbol} falls below ${stop_loss_price:.2f}, your position will be closed."
            action = "set_stop_loss"
            data = {
                "symbol": symbol,
                "current_price": current_price,
                "stop_loss_percentage": percentage,
                "stop_loss_price": stop_loss_price
            }
        
        # Log the voice command to database if user is authenticated
        if user_id:
            try:
                log_voice_command(user_id, command_text, intent, response)
            except Exception as e:
                logger.error(f"Error logging voice command: {e}")
        
        return CommandResponse(
            response=response,
            action=action,
            data=data
        )
        
    except Exception as e:
        logger.error(f"Error processing voice command: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing command: {str(e)}"
        )