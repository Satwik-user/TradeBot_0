# backend/controllers/llm_controller.py
from fastapi import APIRouter, Query
from backend.services.llm_service import LLMService

router = APIRouter(prefix="/api/llm", tags=["LLM Insights"])

# instantiate once
llm_service = LLMService()

@router.get("/analysis/{symbol}")
async def llm_analysis(
    symbol: str,
    timeframe: str = Query("1h"),
):
    """
    Generate simplified technical analysis insights via LLM.
    (For now, this uses mocked analysis & indicators; replace with real TA data.)
    """
    # TODO: Replace these with real TA outputs
    indicators = {
        "rsi": 55,
        "macd_data": {"macd": 0.002, "signal": 0.001},
        "bollinger_bands": {"upper": 45000, "lower": 43000},
        "moving_averages": {"50MA": 44000, "200MA": 42000},
        "volume_sma": 1200
    }
    patterns = ["Bullish Engulfing"]
    analysis = {"analysis_text": f"{symbol} shows moderate strength on {timeframe}"}

    insight = await llm_service.generate_insight(
        symbol, timeframe, indicators, patterns, analysis
    )
    return {"symbol": symbol, "timeframe": timeframe, "insight": insight}
