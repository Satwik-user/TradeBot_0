# backend/services/technical_analysis_service.py
import pandas as pd
import numpy as np
import aiohttp
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json

from database.db_connector import get_db_connection

logger = logging.getLogger("tradebot.tech_analysis")

class TechnicalAnalysisService:
    def __init__(self):
        self.symbols = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
        self.timeframes = ["5m", "15m", "1h", "4h", "1d"]
    
    async def fetch_kline_data(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """Fetch OHLCV data from Binance API"""
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': timeframe,
            'limit': limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        raise Exception(f"Binance API error: {response.status}")
                    data = await response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert to proper types
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            raise
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # Avoid division by zero
            loss = loss.replace(0, np.finfo(float).eps)
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
        except Exception as e:
            logger.error(f"RSI calculation error: {e}")
            return None
    
    def calculate_macd(self, prices: pd.Series) -> Dict:
        """Calculate MACD indicator"""
        try:
            if len(prices) < 26:
                return {'macd': None, 'signal': None, 'histogram': None}
                
            ema12 = prices.ewm(span=12).mean()
            ema26 = prices.ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            histogram = macd - signal
            
            return {
                'macd': float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
                'signal': float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else None,
                'histogram': float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None
            }
        except Exception as e:
            logger.error(f"MACD calculation error: {e}")
            return {'macd': None, 'signal': None, 'histogram': None}
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Dict:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < period:
                return {'upper': None, 'middle': None, 'lower': None}
                
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper = sma + (std * 2)
            lower = sma - (std * 2)
            
            return {
                'upper': float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else None,
                'middle': float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None,
                'lower': float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else None
            }
        except Exception as e:
            logger.error(f"Bollinger Bands calculation error: {e}")
            return {'upper': None, 'middle': None, 'lower': None}
    
    def calculate_moving_averages(self, prices: pd.Series) -> Dict:
        """Calculate various moving averages"""
        try:
            result = {}
            
            # EMA 20
            if len(prices) >= 20:
                ema20 = prices.ewm(span=20).mean().iloc[-1]
                result['ema_20'] = float(ema20) if not pd.isna(ema20) else None
            else:
                result['ema_20'] = None
                
            # EMA 50
            if len(prices) >= 50:
                ema50 = prices.ewm(span=50).mean().iloc[-1]
                result['ema_50'] = float(ema50) if not pd.isna(ema50) else None
            else:
                result['ema_50'] = None
                
            # SMA 20
            if len(prices) >= 20:
                sma20 = prices.rolling(window=20).mean().iloc[-1]
                result['sma_20'] = float(sma20) if not pd.isna(sma20) else None
            else:
                result['sma_20'] = None
                
            # SMA 50
            if len(prices) >= 50:
                sma50 = prices.rolling(window=50).mean().iloc[-1]
                result['sma_50'] = float(sma50) if not pd.isna(sma50) else None
            else:
                result['sma_50'] = None
            
            return result
        except Exception as e:
            logger.error(f"Moving averages calculation error: {e}")
            return {'ema_20': None, 'ema_50': None, 'sma_20': None, 'sma_50': None}
    
    def detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Basic pattern detection"""
        patterns = []
        
        try:
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            
            if len(df) >= 20:
                # Simple pattern detection logic
                recent_high = np.max(high[-10:])
                recent_low = np.min(low[-10:])
                current_price = close[-1]
                
                # Support/Resistance pattern
                if abs(current_price - recent_low) / recent_low < 0.02:
                    patterns.append({
                        'pattern_type': 'support_test',
                        'confidence': 0.7,
                        'description': 'Price testing support level',
                        'pattern_data': {'support_level': float(recent_low)}
                    })
                
                if abs(current_price - recent_high) / recent_high < 0.02:
                    patterns.append({
                        'pattern_type': 'resistance_test',
                        'confidence': 0.7,
                        'description': 'Price testing resistance level',
                        'pattern_data': {'resistance_level': float(recent_high)}
                    })
        except Exception as e:
            logger.error(f"Pattern detection error: {e}")
        
        return patterns
    
    def generate_analysis(self, symbol: str, indicators: Dict, patterns: List[Dict], df: pd.DataFrame) -> Dict:
        """Generate technical analysis with signals"""
        signals = []
        current_price = df['close'].iloc[-1]
        
        try:
            # RSI signals
            rsi = indicators.get('rsi')
            if rsi is not None:
                if rsi < 30:
                    signals.append({
                        'type': 'buy',
                        'strength': 'strong',
                        'reason': f"RSI oversold at {rsi:.1f}"
                    })
                elif rsi > 70:
                    signals.append({
                        'type': 'sell',
                        'strength': 'strong',
                        'reason': f"RSI overbought at {rsi:.1f}"
                    })
            
            # ✅ FIXED: MACD signals - accessing nested dict properly
            macd_data = indicators.get('macd_data', {})
            macd = macd_data.get('macd') if isinstance(macd_data, dict) else indicators.get('macd')
            signal = macd_data.get('signal') if isinstance(macd_data, dict) else indicators.get('signal')
            
            if macd is not None and signal is not None:
                if macd > signal:
                    signals.append({
                        'type': 'buy',
                        'strength': 'medium',
                        'reason': 'MACD above signal line'
                    })
                else:
                    signals.append({
                        'type': 'sell',
                        'strength': 'medium', 
                        'reason': 'MACD below signal line'
                    })
            
            # ✅ FIXED: Trend analysis - accessing nested dict properly
            ma_data = indicators.get('moving_averages', {})
            ema_20 = ma_data.get('ema_20') if isinstance(ma_data, dict) else indicators.get('ema_20')
            ema_50 = ma_data.get('ema_50') if isinstance(ma_data, dict) else indicators.get('ema_50')
            
            trend = 'sideways'
            if ema_20 is not None and ema_50 is not None:
                if ema_20 > ema_50 * 1.01:
                    trend = 'bullish'
                elif ema_20 < ema_50 * 0.99:
                    trend = 'bearish'
            
            # Generate analysis text
            analysis_text = f"Technical Analysis for {symbol}\n"
            analysis_text += f"Current Price: ${current_price:,.2f}\n"
            analysis_text += f"Trend: {trend.title()}\n"
            
            if rsi is not None:
                rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
                analysis_text += f"RSI: {rsi:.1f} ({rsi_status})\n"
            
            analysis_text += f"Active Signals: {len(signals)}\n"
            
            return {
                'analysis_text': analysis_text,
                'signals': signals,
                'key_levels': self._calculate_key_levels(df),
                'trend_direction': trend,
                'risk_level': 'medium'  # Simplified
            }
            
        except Exception as e:
            logger.error(f"Analysis generation error: {e}")
            return {
                'analysis_text': f"Analysis error for {symbol}",
                'signals': [],
                'key_levels': {},
                'trend_direction': 'unknown',
                'risk_level': 'high'
            }
    
    def _calculate_key_levels(self, df: pd.DataFrame) -> Dict:
        """Calculate support/resistance levels"""
        try:
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values[-1]
            
            recent_high = float(np.max(high[-20:]))
            recent_low = float(np.min(low[-20:]))
            
            return {
                'support_levels': [recent_low, close * 0.95],
                'resistance_levels': [recent_high, close * 1.05],
                'pivot_point': float((recent_high + recent_low + close) / 3)
            }
        except Exception as e:
            logger.error(f"Key levels calculation error: {e}")
            return {'support_levels': [], 'resistance_levels': [], 'pivot_point': None}
    
    async def analyze_symbol(self, symbol: str, timeframe: str) -> Dict:
        """Main analysis function"""
        try:
            logger.info(f"Analyzing {symbol} {timeframe}")
            
            # Fetch data
            df = await self.fetch_kline_data(symbol, timeframe)
            
            if len(df) < 10:
                raise Exception(f"Insufficient data for {symbol} {timeframe}")
            
            # ✅ FIXED: Calculate indicators properly
            rsi = self.calculate_rsi(df['close'])
            macd_data = self.calculate_macd(df['close'])
            bb_data = self.calculate_bollinger_bands(df['close'])
            ma_data = self.calculate_moving_averages(df['close'])
            volume_sma = float(df['volume'].rolling(window=min(20, len(df))).mean().iloc[-1])
            
            indicators = {
                'rsi': rsi,
                'macd': macd_data.get('macd'),
                'signal': macd_data.get('signal'),
                'histogram': macd_data.get('histogram'),
                'macd_data': macd_data,  # Keep structured data
                'bollinger_bands': bb_data,
                'moving_averages': ma_data,
                'volume_sma': volume_sma
            }
            
            # Detect patterns
            patterns = self.detect_patterns(df)
            
            # Generate analysis
            analysis = self.generate_analysis(symbol, indicators, patterns, df)
            
            # Save to database
            await self.save_to_database(symbol, timeframe, indicators, patterns, analysis)
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'indicators': indicators,
                'patterns': patterns,
                'analysis': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol} {timeframe}: {e}")
            raise
    
    async def save_to_database(self, symbol: str, timeframe: str, indicators: Dict, 
                              patterns: List[Dict], analysis: Dict):
        """Save analysis to database"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # ✅ FIXED: Save technical indicators with proper data access
                cursor.execute("""
                    INSERT INTO technical_indicators 
                    (symbol, timeframe, rsi, macd, macd_signal, macd_histogram,
                     bb_upper, bb_middle, bb_lower, ema_20, ema_50, sma_20, sma_50, volume_sma)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    symbol, timeframe, 
                    indicators.get('rsi'),
                    indicators.get('macd'), 
                    indicators.get('signal'), 
                    indicators.get('histogram'),
                    indicators.get('bollinger_bands', {}).get('upper'),
                    indicators.get('bollinger_bands', {}).get('middle'),
                    indicators.get('bollinger_bands', {}).get('lower'),
                    indicators.get('moving_averages', {}).get('ema_20'),
                    indicators.get('moving_averages', {}).get('ema_50'),
                    indicators.get('moving_averages', {}).get('sma_20'),
                    indicators.get('moving_averages', {}).get('sma_50'),
                    indicators.get('volume_sma')
                ))
                
                # Save patterns
                for pattern in patterns:
                    cursor.execute("""
                        INSERT INTO pattern_detections 
                        (symbol, timeframe, pattern_type, pattern_data, confidence, description)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        symbol, timeframe, pattern['pattern_type'],
                        json.dumps(pattern['pattern_data']), pattern['confidence'], pattern['description']
                    ))
                
                # Save analysis
                cursor.execute("""
                    INSERT INTO technical_analysis 
                    (symbol, timeframe, analysis_text, signals, key_levels, trend_direction, risk_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    symbol, timeframe, analysis['analysis_text'],
                    json.dumps(analysis['signals']), json.dumps(analysis['key_levels']),
                    analysis['trend_direction'], analysis['risk_level']
                ))
                
                conn.commit()
                logger.info(f"✅ Saved analysis for {symbol} {timeframe}")
                
        except Exception as e:
            logger.error(f"Database save error: {e}")
            raise