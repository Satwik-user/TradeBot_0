# backend/models/technical_analysis_models.py
from database.db_connector import get_db_connection
import logging

logger = logging.getLogger("tradebot.models")

def create_technical_analysis_tables():
    """Create technical analysis database tables"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # ✅ FIXED: Technical indicators table with correct PostgreSQL syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technical_indicators (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    timeframe VARCHAR(10) NOT NULL,
                    rsi DECIMAL(5,2),
                    macd DECIMAL(10,6),
                    macd_signal DECIMAL(10,6),
                    macd_histogram DECIMAL(10,6),
                    bb_upper DECIMAL(10,2),
                    bb_middle DECIMAL(10,2),
                    bb_lower DECIMAL(10,2),
                    ema_20 DECIMAL(10,2),
                    ema_50 DECIMAL(10,2),
                    sma_20 DECIMAL(10,2),
                    sma_50 DECIMAL(10,2),
                    volume_sma DECIMAL(15,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes separately
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_technical_symbol_timeframe 
                ON technical_indicators (symbol, timeframe)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_technical_created_at 
                ON technical_indicators (created_at)
            """)
            
            # ✅ FIXED: Pattern detections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pattern_detections (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    timeframe VARCHAR(10) NOT NULL,
                    pattern_type VARCHAR(50) NOT NULL,
                    pattern_data JSONB,
                    confidence DECIMAL(3,2),
                    description TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Create indexes for pattern_detections
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_symbol_timeframe_type 
                ON pattern_detections (symbol, timeframe, pattern_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_detected_at 
                ON pattern_detections (detected_at)
            """)
            
            # ✅ FIXED: Technical analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technical_analysis (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    timeframe VARCHAR(10) NOT NULL,
                    analysis_text TEXT,
                    signals JSONB,
                    key_levels JSONB,
                    trend_direction VARCHAR(20),
                    risk_level VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for technical_analysis
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_symbol_timeframe 
                ON technical_analysis (symbol, timeframe)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_created_at 
                ON technical_analysis (created_at)
            """)
            
            conn.commit()
            logger.info("✅ Technical analysis tables created/verified")
            
    except Exception as e:
        logger.error(f"Error creating technical analysis tables: {e}")
        raise