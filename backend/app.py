# backend/app.py - FIXED VERSION
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
import os
import time
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from backend.controllers.llm_controller import router as llm_router

# Add the project root to the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Set up logging BEFORE imports
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tradebot")

# Test database imports
try:
    from database.db_connector import get_db_connection, test_connection, init_db
    logger.info("✅ Database connector imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import database connector: {e}")
    raise

# Import controllers
try:
    from backend.controllers.voice_controller import router as voice_router
    from backend.controllers.trade_controller import router as trade_router  
    from backend.controllers.auth_controller import router as auth_router
    logger.info("✅ Controllers imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import controllers: {e}")
    raise

# ✅ FIXED: Import technical analysis components (corrected filename)
try:
    from backend.controllers.technical_analysis_controller import router as technical_analysis_router
    from backend.services.technical_analysis_services import TechnicalAnalysisService  # ✅ FIXED: _service not _services
    logger.info("✅ Technical Analysis components imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import technical analysis components: {e}")
    # Don't fail startup, just log the error
    technical_analysis_router = None
    TechnicalAnalysisService = None  # ✅ ADDED: Set to None if import fails
    logger.warning("⚠️ Technical Analysis features will not be available")

# ✅ NEW: Global technical analysis service instance
tech_analysis_service = None
analysis_task = None

# ✅ IMPROVED: Background task for periodic technical analysis with better error handling
async def periodic_technical_analysis():
    """Run technical analysis periodically in the background"""
    global tech_analysis_service
    
    if not TechnicalAnalysisService:
        logger.error("❌ TechnicalAnalysisService class not available")
        return
    
    if not tech_analysis_service:
        try:
            tech_analysis_service = TechnicalAnalysisService()
            logger.info("✅ Technical Analysis service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Technical Analysis service: {e}")
            return
    
    symbols = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
    timeframes = ["5m", "1h", "4h"]
    
    while True:
        try:
            logger.info("🔍 Starting periodic technical analysis...")
            
            for symbol in symbols:
                for timeframe in timeframes:
                    try:
                        await tech_analysis_service.analyze_symbol(symbol, timeframe)
                        logger.info(f"✅ Analyzed {symbol} {timeframe}")
                        await asyncio.sleep(2)  # Rate limiting
                    except Exception as e:
                        logger.error(f"❌ Error analyzing {symbol} {timeframe}: {e}")
                        continue
            
            logger.info("✅ Periodic technical analysis completed")
            await asyncio.sleep(300)  # Run every 5 minutes
            
        except Exception as e:
            logger.error(f"❌ Periodic analysis error: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global analysis_task
    
    # Startup
    logger.info("🚀 Starting TradeBot API server...")
    
    # Test database connection
    try:
        if test_connection():
            logger.info("✅ Database connection verified")
            
            # ✅ IMPROVED: Initialize database tables for technical analysis with better error handling
            try:
                from backend.models.technical_analysis_models import create_technical_analysis_tables
                create_technical_analysis_tables()
                logger.info("✅ Technical analysis database tables verified/created")
            except ImportError as e:
                logger.error(f"❌ Could not import technical analysis models: {e}")
            except Exception as e:
                logger.error(f"❌ Technical analysis database setup error: {e}")
                
        else:
            logger.error("❌ Database connection failed")
            logger.warning("⚠️ Continuing startup despite database issues...")
    except Exception as e:
        logger.error(f"❌ Database startup error: {e}")
        logger.warning("⚠️ Continuing startup despite database issues...")

    # ✅ IMPROVED: Start background technical analysis task with better conditions
    if TechnicalAnalysisService and technical_analysis_router:
        try:
            # Wait a bit before starting analysis to ensure everything is ready
            await asyncio.sleep(3)
            analysis_task = asyncio.create_task(periodic_technical_analysis())
            logger.info("✅ Periodic technical analysis task started")
        except Exception as e:
            logger.error(f"❌ Failed to start technical analysis task: {e}")
    else:
        logger.warning("⚠️ Technical analysis not available - skipping background task")

    logger.info("✅ TradeBot API server startup complete")
    
    yield  # Server is running
    
    # Shutdown
    logger.info("🛑 Shutting down TradeBot API server...")
    
    # Cancel background tasks
    if analysis_task and not analysis_task.done():
        analysis_task.cancel()
        try:
            await analysis_task
        except asyncio.CancelledError:
            logger.info("✅ Technical analysis task cancelled")
        except Exception as e:
            logger.error(f"❌ Error cancelling analysis task: {e}")
    
    logger.info("✅ TradeBot API server shutdown complete")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="TradeBot API with Technical Analysis",
    description="Voice Trading Assistant API with Advanced Technical Analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001"  # Alternative frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request (only for non-static files)
    if not request.url.path.startswith('/static'):
        logger.info(f"→ {request.method} {request.url.path}")
    
    # Process the request
    response = await call_next(request)
    
    # Log response (only for non-static files)
    if not request.url.path.startswith('/static'):
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"← {request.method} {request.url.path} "
            f"| Status: {response.status_code} "
            f"| Time: {process_time:.2f}ms"
        )
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "TradeBot Voice Trading Assistant API with Technical Analysis",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "voice_commands",
            "automated_trading", 
            "technical_analysis" if TechnicalAnalysisService else "technical_analysis_unavailable",
            "pattern_detection" if TechnicalAnalysisService else "pattern_detection_unavailable",
            "ai_insights" if TechnicalAnalysisService else "ai_insights_unavailable"
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

# ✅ ENHANCED: Health check endpoint with technical analysis status
@app.get("/healthcheck")
async def healthcheck():
    """Enhanced health check endpoint"""
    try:
        # Test database connection
        db_status = "connected" if test_connection() else "disconnected"
        
        # ✅ IMPROVED: Check technical analysis service status
        tech_analysis_status = "available" if (TechnicalAnalysisService and tech_analysis_service) else "unavailable"
        background_task_status = "running" if (analysis_task and not analysis_task.done()) else "stopped"
        
        overall_status = "healthy" if db_status == "connected" else "degraded"
        
        return {
            "status": overall_status,
            "database": db_status,
            "technical_analysis": tech_analysis_status,
            "background_tasks": background_task_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "environment": {
                "DB_HOST": os.getenv("DB_HOST", "localhost"),
                "DB_NAME": os.getenv("DB_NAME", "tradebot"),
                "DB_USER": os.getenv("DB_USER", "tradebot_user"),
                "API_PORT": os.getenv("API_PORT", "8000")
            },
            "features": {
                "voice_commands": True,
                "trading": True,
                "technical_analysis": tech_analysis_status == "available",
                "background_analysis": background_task_status == "running"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "error",
                "technical_analysis": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# ✅ IMPROVED: Technical Analysis status endpoint
@app.get("/api/status/technical-analysis")
async def technical_analysis_status():
    """Get technical analysis service status"""
    try:
        if not TechnicalAnalysisService or not tech_analysis_service:
            return {
                "status": "unavailable",
                "message": "Technical analysis service not initialized",
                "class_available": TechnicalAnalysisService is not None,
                "service_instance": tech_analysis_service is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get recent analysis count from database
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM technical_indicators 
                    WHERE created_at >= NOW() - INTERVAL '1 hour'
                """)
                recent_analyses = cursor.fetchone()[0]
        except Exception as e:
            recent_analyses = 0
            logger.error(f"Error getting analysis count: {e}")
        
        return {
            "status": "available",
            "background_task": "running" if (analysis_task and not analysis_task.done()) else "stopped",
            "recent_analyses_1h": recent_analyses,
            "supported_symbols": ["BTCUSDT", "ETHUSDT", "DOGEUSDT"],
            "supported_timeframes": ["5m", "15m", "1h", "4h", "1d"],
            "features": [
                "RSI", "MACD", "Bollinger Bands", 
                "Moving Averages", "Pattern Detection", 
                "AI Analysis"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Technical analysis status error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# ✅ IMPROVED: Manual trigger for technical analysis
@app.post("/api/triggers/analyze-all")
async def trigger_analysis_all(background_tasks: BackgroundTasks):
    """Manually trigger technical analysis for all symbols"""
    if not TechnicalAnalysisService or not tech_analysis_service:
        raise HTTPException(
            status_code=503, 
            detail="Technical analysis service unavailable"
        )
    
    async def run_analysis():
        symbols = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
        timeframes = ["5m", "1h", "4h"]
        
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    await tech_analysis_service.analyze_symbol(symbol, timeframe)
                    logger.info(f"✅ Manual analysis completed: {symbol} {timeframe}")
                    await asyncio.sleep(1)  # Brief pause between analyses
                except Exception as e:
                    logger.error(f"❌ Manual analysis failed: {symbol} {timeframe}: {e}")
    
    background_tasks.add_task(run_analysis)
    
    return {
        "message": "Technical analysis triggered for all symbols",
        "symbols": ["BTCUSDT", "ETHUSDT", "DOGEUSDT"],
        "timeframes": ["5m", "1h", "4h"],
        "status": "processing",
        "timestamp": datetime.utcnow().isoformat()
    }

# ✅ IMPROVED: Debug endpoint to check imports
@app.get("/api/debug/imports")
async def debug_imports():
    """Debug endpoint to check import status"""
    return {
        "technical_analysis_router": technical_analysis_router is not None,
        "technical_analysis_service_class": TechnicalAnalysisService is not None,
        "technical_analysis_service_instance": tech_analysis_service is not None,
        "analysis_task_running": analysis_task is not None and not analysis_task.done() if analysis_task else False,
        "timestamp": datetime.utcnow().isoformat()
    }

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice Commands"])
app.include_router(trade_router, prefix="/api/trades", tags=["Trading"])

# ✅ IMPROVED: Include technical analysis router if available
if technical_analysis_router:
    app.include_router(
        technical_analysis_router, 
        prefix="/api/technical-analysis", 
        tags=["Technical Analysis"]
    )
    logger.info("✅ Technical Analysis API endpoints registered")
else:
    logger.warning("⚠️ Technical Analysis API endpoints not available")

# ✅ Add LLM endpoints
app.include_router(llm_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")