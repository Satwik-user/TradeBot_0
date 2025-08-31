# backend/app/services/technical_analysis.py
import pandas as pd
import numpy as np
import talib
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
from sqlalchemy.orm import Session
from ..models import TechnicalIndicator, PatternDetection, TechnicalAnalysis
from ..database import get_db
import json

class TechnicalAnalysisService:
    def __init__(self):
        self.timeframes = ['5m', '15m', '1h', '4h', '1d']
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT']
    
    async def fetch_kline_data(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """Fetch OHLCV data from Binance API"""
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': timeframe,
            'limit': limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
        
        # Convert to pandas DataFrame
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
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate various technical indicators"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        indicators = {}
        
        try:
            # RSI (Relative Strength Index)
            indicators['rsi'] = talib.RSI(close, timeperiod=14)[-1]
            
            # MACD (Moving Average Convergence Divergence)
            macd, macd_signal, macd_histogram = talib.MACD(close)
            indicators['macd'] = macd[-1]
            indicators['macd_signal'] = macd_signal[-1]
            indicators['macd_histogram'] = macd_histogram[-1]
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close)
            indicators['bb_upper'] = bb_upper[-1]
            indicators['bb_middle'] = bb_middle[-1]
            indicators['bb_lower'] = bb_lower[-1]
            
            # Moving Averages
            indicators['ema_20'] = talib.EMA(close, timeperiod=20)[-1]
            indicators['ema_50'] = talib.EMA(close, timeperiod=50)[-1]
            indicators['sma_20'] = talib.SMA(close, timeperiod=20)[-1]
            indicators['sma_50'] = talib.SMA(close, timeperiod=50)[-1]
            
            # Volume SMA
            indicators['volume_sma'] = talib.SMA(volume, timeperiod=20)[-1]
            
            # Additional indicators
            indicators['stoch_k'], indicators['stoch_d'] = talib.STOCH(high, low, close)
            indicators['stoch_k'] = indicators['stoch_k'][-1] if indicators['stoch_k'] is not None else None
            indicators['stoch_d'] = indicators['stoch_d'][-1] if indicators['stoch_d'] is not None else None
            
            # Williams %R
            indicators['williams_r'] = talib.WILLR(high, low, close)[-1]
            
            # Average True Range
            indicators['atr'] = talib.ATR(high, low, close)[-1]
            
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return {}
        
        # Clean NaN values
        for key, value in indicators.items():
            if pd.isna(value):
                indicators[key] = None
        
        return indicators
    
    def detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect chart patterns"""
        patterns = []
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        
        # Head and Shoulders detection (simplified)
        if len(df) >= 20:
            patterns.extend(self._detect_head_and_shoulders(df))
            patterns.extend(self._detect_double_top_bottom(df))
            patterns.extend(self._detect_triangles(df))
        
        return patterns
    
    def _detect_head_and_shoulders(self, df: pd.DataFrame) -> List[Dict]:
        """Detect Head and Shoulders pattern"""
        patterns = []
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        if len(df) < 30:
            return patterns
        
        # Simplified head and shoulders detection
        # Look for three peaks where middle peak is highest
        window = 10
        peaks = []
        
        for i in range(window, len(high) - window):
            if (high[i] > max(high[i-window:i]) and 
                high[i] > max(high[i+1:i+window+1])):
                peaks.append((i, high[i]))
        
        if len(peaks) >= 3:
            # Check if middle peak is highest
            peaks.sort(key=lambda x: x[1], reverse=True)
            if peaks[0][0] > peaks[1][0] and peaks[0][0] > peaks[2][0]:
                patterns.append({
                    'pattern_type': 'head_and_shoulders',
                    'confidence': 0.75,
                    'description': 'Head and Shoulders pattern detected - bearish reversal signal',
                    'pattern_data': {
                        'head': {'index': peaks[0][0], 'price': peaks[0][1]},
                        'left_shoulder': {'index': peaks[1][0], 'price': peaks[1][1]},
                        'right_shoulder': {'index': peaks[2][0], 'price': peaks[2][1]}
                    }
                })
        
        return patterns
    
    def _detect_double_top_bottom(self, df: pd.DataFrame) -> List[Dict]:
        """Detect Double Top/Bottom patterns"""
        patterns = []
        high = df['high'].values
        low = df['low'].values
        
        # Double Top detection
        window = 10
        peaks = []
        
        for i in range(window, len(high) - window):
            if (high[i] > max(high[i-window:i]) and 
                high[i] > max(high[i+1:i+window+1])):
                peaks.append((i, high[i]))
        
        # Look for two similar peaks
        for i in range(len(peaks) - 1):
            for j in range(i + 1, len(peaks)):
                price_diff = abs(peaks[i][1] - peaks[j][1]) / peaks[i][1]
                if price_diff < 0.02:  # Within 2%
                    patterns.append({
                        'pattern_type': 'double_top',
                        'confidence': 0.7,
                        'description': 'Double Top pattern detected - bearish reversal signal',
                        'pattern_data': {
                            'first_peak': {'index': peaks[i][0], 'price': peaks[i][1]},
                            'second_peak': {'index': peaks[j][0], 'price': peaks[j][1]}
                        }
                    })
                    break
        
        return patterns
    
    def _detect_triangles(self, df: pd.DataFrame) -> List[Dict]:
        """Detect Triangle patterns (ascending, descending, symmetric)"""
        patterns = []
        # Simplified triangle detection logic
        # This would need more sophisticated implementation
        return patterns
    
    def generate_analysis(self, symbol: str, indicators: Dict, patterns: List[Dict], df: pd.DataFrame) -> Dict:
        """Generate AI-powered technical analysis"""
        current_price = df['close'].iloc[-1]
        
        # Signal generation
        signals = []
        
        # RSI signals
        if indicators.get('rsi'):
            if indicators['rsi'] < 30:
                signals.append({
                    'type': 'buy',
                    'strength': 'strong',
                    'reason': f"RSI oversold at {indicators['rsi']:.1f}"
                })
            elif indicators['rsi'] > 70:
                signals.append({
                    'type': 'sell',
                    'strength': 'strong',
                    'reason': f"RSI overbought at {indicators['rsi']:.1f}"
                })
        
        # MACD signals
        if indicators.get('macd') and indicators.get('macd_signal'):
            if indicators['macd'] > indicators['macd_signal']:
                signals.append({
                    'type': 'buy',
                    'strength': 'medium',
                    'reason': 'MACD above signal line - bullish momentum'
                })
            else:
                signals.append({
                    'type': 'sell',
                    'strength': 'medium',
                    'reason': 'MACD below signal line - bearish momentum'
                })
        
        # Moving average signals
        if indicators.get('ema_20') and indicators.get('ema_50'):
            if indicators['ema_20'] > indicators['ema_50']:
                signals.append({
                    'type': 'buy',
                    'strength': 'medium',
                    'reason': 'EMA 20 above EMA 50 - upward trend'
                })
            else:
                signals.append({
                    'type': 'sell',
                    'strength': 'medium',
                    'reason': 'EMA 20 below EMA 50 - downward trend'
                })
        
        # Support/Resistance levels
        key_levels = self._calculate_key_levels(df)
        
        # Trend direction
        trend = self._determine_trend(indicators, df)
        
        # Generate descriptive analysis
        analysis_text = self._generate_analysis_text(symbol, indicators, signals, patterns, trend, current_price)
        
        return {
            'analysis_text': analysis_text,
            'signals': signals,
            'key_levels': key_levels,
            'trend_direction': trend,
            'risk_level': self._assess_risk(indicators, patterns)
        }
    
    def _calculate_key_levels(self, df: pd.DataFrame) -> Dict:
        """Calculate support and resistance levels"""
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        # Calculate pivot points
        recent_high = np.max(high[-20:])
        recent_low = np.min(low[-20:])
        pivot = (recent_high + recent_low + close[-1]) / 3
        
        return {
            'support_levels': [recent_low, pivot - (recent_high - recent_low) * 0.382],
            'resistance_levels': [recent_high, pivot + (recent_high - recent_low) * 0.382],
            'pivot_point': pivot
        }
    
    def _determine_trend(self, indicators: Dict, df: pd.DataFrame) -> str:
        """Determine overall trend direction"""
        if indicators.get('ema_20') and indicators.get('ema_50'):
            if indicators['ema_20'] > indicators['ema_50'] * 1.02:
                return 'bullish'
            elif indicators['ema_20'] < indicators['ema_50'] * 0.98:
                return 'bearish'
        
        return 'sideways'
    
    def _assess_risk(self, indicators: Dict, patterns: List[Dict]) -> str:
        """Assess risk level based on indicators and patterns"""
        risk_factors = 0
        
        # High volatility indicators
        if indicators.get('atr'):
            # This would need proper ATR threshold calculation
            pass
        
        # Pattern-based risk
        for pattern in patterns:
            if pattern['pattern_type'] in ['head_and_shoulders', 'double_top']:
                risk_factors += 1
        
        if risk_factors >= 2:
            return 'high'
        elif risk_factors == 1:
            return 'medium'
        else:
            return 'low'
    
    def _generate_analysis_text(self, symbol: str, indicators: Dict, signals: List[Dict], 
                               patterns: List[Dict], trend: str, current_price: float) -> str:
        """Generate human-readable technical analysis"""
        analysis = f"Technical Analysis for {symbol} (Current Price: ${current_price:,.2f})\n\n"
        
        # Trend analysis
        analysis += f"📈 **Trend Direction**: {trend.title()}\n"
        
        # Indicator summary
        if indicators.get('rsi'):
            rsi_status = "Oversold" if indicators['rsi'] < 30 else "Overbought" if indicators['rsi'] > 70 else "Neutral"
            analysis += f"📊 **RSI (14)**: {indicators['rsi']:.1f} - {rsi_status}\n"
        
        if indicators.get('macd') and indicators.get('macd_signal'):
            macd_trend = "Bullish" if indicators['macd'] > indicators['macd_signal'] else "Bearish"
            analysis += f"📊 **MACD**: {macd_trend} momentum\n"
        
        # Pattern analysis
        if patterns:
            analysis += f"\n🔍 **Detected Patterns**:\n"
            for pattern in patterns:
                analysis += f"  • {pattern['pattern_type'].replace('_', ' ').title()}: {pattern['description']}\n"
        
        # Signal summary
        buy_signals = [s for s in signals if s['type'] == 'buy']
        sell_signals = [s for s in signals if s['type'] == 'sell']
        
        analysis += f"\n🎯 **Trading Signals**:\n"
        if len(buy_signals) > len(sell_signals):
            analysis += "  • Overall: **BULLISH** bias\n"
        elif len(sell_signals) > len(buy_signals):
            analysis += "  • Overall: **BEARISH** bias\n"
        else:
            analysis += "  • Overall: **NEUTRAL** - wait for confirmation\n"
        
        return analysis
    
    async def process_symbol(self, symbol: str, timeframe: str, db: Session):
        """Process technical analysis for a symbol and timeframe"""
        try:
            # Fetch OHLCV data
            df = await self.fetch_kline_data(symbol, timeframe)
            
            # Calculate indicators
            indicators = self.calculate_technical_indicators(df)
            
            # Detect patterns
            patterns = self.detect_patterns(df)
            
            # Generate analysis
            analysis = self.generate_analysis(symbol, indicators, patterns, df)
            
            # Save to database
            await self.save_to_database(symbol, timeframe, indicators, patterns, analysis, db)
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'indicators': indicators,
                'patterns': patterns,
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"Error processing {symbol} {timeframe}: {e}")
            return None
    
    async def save_to_database(self, symbol: str, timeframe: str, indicators: Dict, 
                              patterns: List[Dict], analysis: Dict, db: Session):
        """Save analysis results to database"""
        try:
            # Save technical indicators
            tech_indicator = TechnicalIndicator(
                symbol=symbol,
                timeframe=timeframe,
                **{k: v for k, v in indicators.items() if k in [
                    'rsi', 'macd', 'macd_signal', 'macd_histogram',
                    'bb_upper', 'bb_middle', 'bb_lower',
                    'ema_20', 'ema_50', 'sma_20', 'sma_50', 'volume_sma'
                ]}
            )
            db.add(tech_indicator)
            
            # Save patterns
            for pattern in patterns:
                pattern_detection = PatternDetection(
                    symbol=symbol,
                    timeframe=timeframe,
                    pattern_type=pattern['pattern_type'],
                    pattern_data=pattern['pattern_data'],
                    confidence=pattern['confidence'],
                    description=pattern['description']
                )
                db.add(pattern_detection)
            
            # Save analysis
            tech_analysis = TechnicalAnalysis(
                symbol=symbol,
                timeframe=timeframe,
                analysis_text=analysis['analysis_text'],
                signals=analysis['signals'],
                key_levels=analysis['key_levels'],
                trend_direction=analysis['trend_direction'],
                risk_level=analysis['risk_level']
            )
            db.add(tech_analysis)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"Database error: {e}")

# Create service instance
technical_analysis_service = TechnicalAnalysisService()