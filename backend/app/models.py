# backend/app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TradePair(Base):
    __tablename__ = "trade_pairs"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True)
    base_asset = Column(String(10))
    quote_asset = Column(String(10))
    is_active = Column(Boolean, default=True)

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True)
    user_id = Column(Integer, index=True)
    symbol = Column(String(20))
    order_type = Column(String(10))  # buy/sell
    order_subtype = Column(String(10))  # market/limit
    quantity = Column(Float)
    price = Column(Float)
    total_value = Column(Float)
    fee = Column(Float, default=0.0)
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)
    price = Column(Float)
    volume_24h = Column(Float)
    change_24h = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ✅ NEW: Technical Analysis Models
class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)
    timeframe = Column(String(10))  # 1m, 5m, 15m, 1h, 4h, 1d
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    volume_sma = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class PatternDetection(Base):
    __tablename__ = "pattern_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)
    pattern_type = Column(String(50))  # head_and_shoulders, double_top, etc.
    pattern_data = Column(JSON)  # Store pattern coordinates/details
    confidence = Column(Float)  # Confidence score 0-1
    description = Column(Text)
    timeframe = Column(String(10))
    detected_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class TechnicalAnalysis(Base):
    __tablename__ = "technical_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)
    timeframe = Column(String(10))
    analysis_text = Column(Text)  # AI-generated analysis
    signals = Column(JSON)  # Buy/sell/hold signals with reasons
    key_levels = Column(JSON)  # Support/resistance levels
    trend_direction = Column(String(20))  # bullish/bearish/sideways
    risk_level = Column(String(20))  # low/medium/high
    created_at = Column(DateTime, default=datetime.utcnow)