from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
import time
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import controllers
from controllers.voice_controller import router as voice_router
from controllers.trade_controller import router as trade_router
from controllers.auth_controller import router as auth_router

# Import database connector
from database.db_connector import get_db_connection, test_connection

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tradebot")

app = FastAPI(
    title="TradeBot API",
    description="Voice Trading Assistant API",
    version="0.1.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting TradeBot API server...")
    
    # Test database connection
    if test_connection():
        logger.info("✅ Database connection verified")
    else:
        logger.error("❌ Database connection failed")
        raise Exception("Cannot start server: Database connection failed")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TradeBot Voice Trading Assistant API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/healthcheck")
async def healthcheck():
    """Health check endpoint"""
    try:
        db_status = test_connection()
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Log the request details
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"| Status: {response.status_code} "
        f"| Time: {process_time:.2f}ms"
    )
    
    return response

# Error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"}
    )

# Include routers
app.include_router(voice_router, prefix="/api/voice", tags=["Voice Commands"])
app.include_router(trade_router, prefix="/api/trades", tags=["Trading"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to TradeBot API",
        "docs_url": "/docs",
        "version": "0.1.0"
    }

@app.get("/healthcheck")
async def healthcheck():
    """Health check endpoint"""
    # Test database connection
    try:
        conn = get_db_connection()
        conn.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        db_status = f"error: {str(e)}"
    
    return {
        "status": "online",
        "database": db_status,
        "version": "0.1.0",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)