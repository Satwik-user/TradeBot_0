# backend/app.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

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

# Create FastAPI app
app = FastAPI(
    title="TradeBot API",
    description="Voice Trading Assistant API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    # Process the request
    response = await call_next(request)
    
    # Log response
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"← {request.method} {request.url.path} "
        f"| Status: {response.status_code} "
        f"| Time: {process_time:.2f}ms"
    )
    
    return response

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Starting TradeBot API server...")
    
    # Test database connection
    try:
        if test_connection():
            logger.info("✅ Database connection verified")
        else:
            logger.error("❌ Database connection failed")
            raise Exception("Cannot start server: Database connection failed")
    except Exception as e:
        logger.error(f"❌ Database startup error: {e}")
        # Don't fail startup in development, just warn
        logger.warning("⚠️ Continuing startup despite database issues...")

    logger.info("✅ TradeBot API server startup complete")

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
        "message": "TradeBot Voice Trading Assistant API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/healthcheck")
async def healthcheck():
    """Health check endpoint"""
    try:
        # Test database connection
        db_status = "connected" if test_connection() else "disconnected"
        
        return {
            "status": "healthy" if db_status == "connected" else "unhealthy",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": {
                "DB_HOST": os.getenv("DB_HOST", "localhost"),
                "DB_NAME": os.getenv("DB_NAME", "tradebot"),
                "DB_USER": os.getenv("DB_USER", "tradebot_user"),
                "API_PORT": os.getenv("API_PORT", "8000")
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice Commands"])
app.include_router(trade_router, prefix="/api/trades", tags=["Trading"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")