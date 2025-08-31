# backend/app/routers/technical_analysis.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import TechnicalIndicator, PatternDetection, TechnicalAnalysis
from ..services.technical_analysis import technical_analysis_service
from ..schemas import TechnicalAnalysisResponse, IndicatorResponse, PatternResponse

router = APIRouter(prefix="/api/technical-analysis", tags=["Technical Analysis"])

@router.get("/indicators/{symbol}")
async def get_indicators(
    symbol: str,
    timeframe: str = "1h",
    db: Session = Depends(get_db)
):
    """Get latest technical indicators for a symbol"""
    indicator = db.query(TechnicalIndicator).filter(
        TechnicalIndicator.symbol == symbol,
        TechnicalIndicator.timeframe == timeframe
    ).order_by(TechnicalIndicator.timestamp.desc()).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="No indicators found")
    
    return {
        "symbol": indicator.symbol,
        "timeframe": indicator.timeframe,
        "rsi": indicator.rsi,
        "macd": {
            "macd": indicator.macd,
            "signal": indicator.macd_signal,
            "histogram": indicator.macd_histogram
        },
        "bollinger_bands": {
            "upper": indicator.bb_upper,
            "middle": indicator.bb_middle,
            "lower": indicator.bb_lower
        },
        "moving_averages": {
            "ema_20": indicator.ema_20,
            "ema_50": indicator.ema_50,
            "sma_20": indicator.sma_20,
            "sma_50": indicator.sma_50
        },
        "volume_sma": indicator.volume_sma,
        "timestamp": indicator.timestamp
    }

@router.get("/patterns/{symbol}")
async def get_patterns(
    symbol: str,
    timeframe: str = "1h",
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get detected patterns for a symbol"""
    query = db.query(PatternDetection).filter(
        PatternDetection.symbol == symbol,
        PatternDetection.timeframe == timeframe
    )
    
    if active_only:
        query = query.filter(PatternDetection.is_active == True)
    
    patterns = query.order_by(PatternDetection.detected_at.desc()).limit(10).all()
    
    return [{
        "pattern_type": pattern.pattern_type,
        "confidence": pattern.confidence,
        "description": pattern.description,
        "pattern_data": pattern.pattern_data,
        "detected_at": pattern.detected_at
    } for pattern in patterns]

@router.get("/analysis/{symbol}")
async def get_analysis(
    symbol: str,
    timeframe: str = "1h",
    db: Session = Depends(get_db)
):
    """Get latest technical analysis for a symbol"""
    analysis = db.query(TechnicalAnalysis).filter(
        TechnicalAnalysis.symbol == symbol,
        TechnicalAnalysis.timeframe == timeframe
    ).order_by(TechnicalAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found")
    
    return {
        "symbol": analysis.symbol,
        "timeframe": analysis.timeframe,
        "analysis_text": analysis.analysis_text,
        "signals": analysis.signals,
        "key_levels": analysis.key_levels,
        "trend_direction": analysis.trend_direction,
        "risk_level": analysis.risk_level,
        "created_at": analysis.created_at
    }

@router.post("/analyze/{symbol}")
async def analyze_symbol(
    symbol: str,
    timeframe: str = "1h",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Trigger technical analysis for a symbol"""
    try:
        result = await technical_analysis_service.process_symbol(symbol, timeframe, db)
        return {
            "message": f"Analysis completed for {symbol} {timeframe}",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/all")
async def analyze_all_symbols(
    timeframe: str = "1h",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Trigger analysis for all symbols"""
    symbols = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
    results = []
    
    for symbol in symbols:
        try:
            result = await technical_analysis_service.process_symbol(symbol, timeframe, db)
            results.append(result)
        except Exception as e:
            results.append({"symbol": symbol, "error": str(e)})
    
    return {
        "message": f"Analysis completed for {len(symbols)} symbols",
        "results": results
    }

@router.get("/summary/{symbol}")
async def get_analysis_summary(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive analysis summary combining all timeframes"""
    timeframes = ["5m", "15m", "1h", "4h", "1d"]
    summary = {}
    
    for tf in timeframes:
        # Get latest analysis
        analysis = db.query(TechnicalAnalysis).filter(
            TechnicalAnalysis.symbol == symbol,
            TechnicalAnalysis.timeframe == tf
        ).order_by(TechnicalAnalysis.created_at.desc()).first()
        
        if analysis:
            summary[tf] = {
                "trend_direction": analysis.trend_direction,
                "risk_level": analysis.risk_level,
                "signals_count": len(analysis.signals) if analysis.signals else 0,
                "updated_at": analysis.created_at
            }
    
    return {
        "symbol": symbol,
        "timeframe_summary": summary,
        "overall_sentiment": _calculate_overall_sentiment(summary)
    }

def _calculate_overall_sentiment(summary: dict) -> str:
    """Calculate overall market sentiment across timeframes"""
    bullish_count = sum(1 for tf_data in summary.values() if tf_data.get('trend_direction') == 'bullish')
    bearish_count = sum(1 for tf_data in summary.values() if tf_data.get('trend_direction') == 'bearish')
    
    if bullish_count > bearish_count:
        return "bullish"
    elif bearish_count > bullish_count:
        return "bearish"
    else:
        return "neutral"