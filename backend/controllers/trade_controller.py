from fastapi import APIRouter, HTTPException, Body, Depends, Query, Path, status
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any, List, Optional

from services.trading_service import get_market_data, simulate_trade
from utils.auth_utils import get_current_user, get_current_user_optional
from database.repositories.trade_repository import (
    create_trade as db_create_trade,
    get_user_trades,
    get_trade_by_id,
    update_trade_status,
    get_trading_pair_by_symbol
)

# Set up logger
logger = logging.getLogger("tradebot.trades")

router = APIRouter()

# Trade models
class TradeRequest(BaseModel):
    symbol: str
    orderType: str
    orderSubtype: str
    quantity: float
    price: Optional[float] = None

class TradeResponse(BaseModel):
    order_id: str
    symbol: str
    order_type: str
    order_subtype: str
    quantity: float
    price: float
    total_value: float
    fee: float
    status: str
    timestamp: int

@router.post("/execute", response_model=TradeResponse)
async def execute_trade(
    trade_request: TradeRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """Execute a trade order"""
    try:
        # Get user ID if authenticated
        user_id = current_user["id"] if current_user else None
        
        # Simulate trade execution
        trade_result = simulate_trade(
            trade_request.orderType,
            trade_request.symbol,
            trade_request.quantity,
            trade_request.price
        )
        
        # If user is authenticated, save trade to database
        if user_id:
            try:
                # Get trading pair ID
                pair_info = get_trading_pair_by_symbol(trade_request.symbol)
                if not pair_info:
                    raise ValueError(f"Trading pair {trade_request.symbol} not found")
                
                # Save trade to database
                db_trade = db_create_trade(
                    user_id=user_id,
                    pair_id=pair_info["id"],
                    order_type=trade_request.orderType,
                    order_subtype=trade_request.orderSubtype,
                    quantity=trade_request.quantity,
                    price=trade_result["price"],
                    total_value=trade_result["total_value"],
                    fee=trade_result["fee"],
                    status=trade_result["status"]
                )
                
                # Update order ID in response
                trade_result["order_id"] = f"ord-{db_trade['id']}"
            except Exception as e:
                logger.error(f"Error saving trade to database: {e}")
                # Continue with simulated trade
        
        return trade_result
    except Exception as e:
        logger.error(f"Error executing trade: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing trade: {str(e)}"
        )

@router.get("/market-data/{symbol}")
async def get_symbol_market_data(
    symbol: str = Path(..., description="Trading pair symbol (e.g., BTCUSDT)"),
    indicator: Optional[str] = Query(None, description="Technical indicator to include")
):
    """Get market data for a specific trading pair"""
    try:
        market_data = get_market_data(symbol, indicator=indicator)
        return market_data
    except Exception as e:
        logger.error(f"Error getting market data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting market data: {str(e)}"
        )

@router.get("/history")
async def get_trade_history(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get trade history for the authenticated user"""
    try:
        trades = get_user_trades(current_user["id"], limit, offset)
        return trades
    except Exception as e:
        logger.error(f"Error getting trade history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting trade history: {str(e)}"
        )

@router.get("/history/{trade_id}")
async def get_trade_details(
    trade_id: int = Path(..., description="Trade ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get details for a specific trade"""
    try:
        trade = get_trade_by_id(trade_id)
        
        if not trade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade not found"
            )
        
        # Check if trade belongs to the authenticated user
        if trade["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this trade"
            )
        
        return trade
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trade details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting trade details: {str(e)}"
        )