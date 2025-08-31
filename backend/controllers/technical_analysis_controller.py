# backend/controllers/technical_analysis_controller.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from backend.services.technical_analysis_services import TechnicalAnalysisService
from database.db_connector import get_db_connection

logger = logging.getLogger("tradebot.technical_analysis")
router = APIRouter()

# Initialize service
tech_service = TechnicalAnalysisService()

@router.get("/indicators/{symbol}")
async def get_indicators(
    symbol: str,
    timeframe: str = Query(default="1h", regex="^(5m|15m|1h|4h|1d)$")
):
    """Get latest technical indicators for a symbol"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT symbol, timeframe, rsi, macd, macd_signal, macd_histogram,
                       bb_upper, bb_middle, bb_lower, ema_20, ema_50, 
                       sma_20, sma_50, volume_sma, created_at
                FROM technical_indicators 
                WHERE symbol = %s AND timeframe = %s
                ORDER BY created_at DESC LIMIT 1
            """, (symbol, timeframe))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="No indicators found")
            
            return {
                "symbol": result[0],
                "timeframe": result[1],
                "rsi": result[2],
                "macd": {
                    "macd": result[3],
                    "signal": result[4],
                    "histogram": result[5]
                },
                "bollinger_bands": {
                    "upper": result[6],
                    "middle": result[7],
                    "lower": result[8]
                },
                "moving_averages": {
                    "ema_20": result[9],
                    "ema_50": result[10],
                    "sma_20": result[11],
                    "sma_50": result[12]
                },
                "volume_sma": result[13],
                "timestamp": result[14]
            }
            
    except Exception as e:
        logger.error(f"Error getting indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patterns/{symbol}")
async def get_patterns(
    symbol: str,
    timeframe: str = Query(default="1h", regex="^(5m|15m|1h|4h|1d)$"),
    active_only: bool = True
):
    """Get detected patterns for a symbol"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT pattern_type, confidence, description, pattern_data, detected_at
                FROM pattern_detections 
                WHERE symbol = %s AND timeframe = %s
            """
            params = [symbol, timeframe]
            
            if active_only:
                query += " AND is_active = true"
            
            query += " ORDER BY detected_at DESC LIMIT 10"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [{
                "pattern_type": row[0],
                "confidence": row[1],
                "description": row[2],
                "pattern_data": row[3],
                "detected_at": row[4]
            } for row in results]
            
    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{symbol}")
async def get_analysis(
    symbol: str,
    timeframe: str = Query(default="1h", regex="^(5m|15m|1h|4h|1d)$")
):
    """Get latest technical analysis for a symbol"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT symbol, timeframe, analysis_text, signals, key_levels,
                       trend_direction, risk_level, created_at
                FROM technical_analysis 
                WHERE symbol = %s AND timeframe = %s
                ORDER BY created_at DESC LIMIT 1
            """, (symbol, timeframe))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="No analysis found")
            
            return {
                "symbol": result[0],
                "timeframe": result[1],
                "analysis_text": result[2],
                "signals": result[3],
                "key_levels": result[4],
                "trend_direction": result[5],
                "risk_level": result[6],
                "created_at": result[7]
            }
            
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/{symbol}")
async def analyze_symbol(
    symbol: str,
    timeframe: str = Query(default="1h", regex="^(5m|15m|1h|4h|1d)$"),
    background_tasks: BackgroundTasks = None
):
    """Trigger technical analysis for a symbol"""
    try:
        result = await tech_service.analyze_symbol(symbol, timeframe)
        return {
            "message": f"Analysis completed for {symbol} {timeframe}",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error analyzing symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{symbol}")
async def get_analysis_summary(symbol: str):
    """Get comprehensive analysis summary across timeframes"""
    try:
        timeframes = ["5m", "15m", "1h", "4h", "1d"]
        summary = {}
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for tf in timeframes:
                cursor.execute("""
                    SELECT trend_direction, risk_level, signals, created_at
                    FROM technical_analysis 
                    WHERE symbol = %s AND timeframe = %s
                    ORDER BY created_at DESC LIMIT 1
                """, (symbol, tf))
                
                result = cursor.fetchone()
                if result:
                    signals_count = len(result[2]) if result[2] else 0
                    summary[tf] = {
                        "trend_direction": result[0],
                        "risk_level": result[1],
                        "signals_count": signals_count,
                        "updated_at": result[3]
                    }
        
        # Calculate overall sentiment
        bullish_count = sum(1 for tf_data in summary.values() 
                           if tf_data.get('trend_direction') == 'bullish')
        bearish_count = sum(1 for tf_data in summary.values() 
                           if tf_data.get('trend_direction') == 'bearish')
        
        if bullish_count > bearish_count:
            overall_sentiment = "bullish"
        elif bearish_count > bullish_count:
            overall_sentiment = "bearish"
        else:
            overall_sentiment = "neutral"
        
        return {
            "symbol": symbol,
            "timeframe_summary": summary,
            "overall_sentiment": overall_sentiment,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
from backend.services.llm_service import LLMService

llm_service = LLMService()

@router.get("/llm-insight/{symbol}")
async def get_llm_insight(
    symbol: str,
    timeframe: str = Query(default="1h", regex="^(5m|15m|1h|4h|1d)$")
):
    """Get simplified LLM-based insight for a symbol"""
    try:
        # Fetch latest indicators
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rsi, macd, macd_signal, macd_histogram,
                       ema_20, ema_50, sma_20, sma_50, volume_sma
                FROM technical_indicators 
                WHERE symbol = %s AND timeframe = %s
                ORDER BY created_at DESC LIMIT 1
            """, (symbol, timeframe))
            indicators = cursor.fetchone()

            cursor.execute("""
                SELECT analysis_text, signals, key_levels, trend_direction, risk_level
                FROM technical_analysis 
                WHERE symbol = %s AND timeframe = %s
                ORDER BY created_at DESC LIMIT 1
            """, (symbol, timeframe))
            analysis = cursor.fetchone()

            cursor.execute("""
                SELECT pattern_type, confidence, description
                FROM pattern_detections 
                WHERE symbol = %s AND timeframe = %s
                ORDER BY detected_at DESC LIMIT 3
            """, (symbol, timeframe))
            patterns = cursor.fetchall()

        # Format data
        indicators_dict = dict(zip(
            ["rsi","macd","macd_signal","macd_histogram","ema_20","ema_50","sma_20","sma_50","volume_sma"],
            indicators or []
        ))
        analysis_dict = dict(zip(
            ["analysis_text","signals","key_levels","trend_direction","risk_level"],
            analysis or []
        ))
        patterns_list = [{"pattern_type": p[0], "confidence": p[1], "description": p[2]} for p in patterns] if patterns else []

        # Get LLM insight
        simplified = llm_service.summarize_analysis(symbol, indicators_dict, patterns_list, analysis_dict)

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "simplified_insight": simplified,
            "raw": {
                "indicators": indicators_dict,
                "patterns": patterns_list,
                "analysis": analysis_dict
            }
        }
    except Exception as e:
        logger.error(f"Error generating LLM insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))
