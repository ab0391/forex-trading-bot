#!/usr/bin/env python3
"""
Enhanced H4 Bias Confirmation for ZoneSync FX Bot
Implements missing H4 bias logic to improve signal quality
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class H4BiasAnalyzer:
    """
    Comprehensive H4 timeframe bias analysis to confirm D1 direction
    and filter low-quality H1 zone signals
    """

    def __init__(self):
        self.ema_fast = 20
        self.ema_slow = 50
        self.ema_trend = 200
        self.rsi_period = 14
        self.rsi_oversold = 30
        self.rsi_overbought = 70

    def calculate_h4_bias(self, h4_df: pd.DataFrame) -> Dict[str, any]:
        """
        Calculate comprehensive H4 bias with multiple confluence factors

        Returns:
            Dict containing bias, strength, and supporting factors
        """
        if len(h4_df) < self.ema_trend:
            logger.warning("Insufficient H4 data for bias calculation")
            return {"bias": "insufficient_data", "strength": 0, "factors": []}

        try:
            # Calculate EMAs
            close = h4_df['close']
            ema20 = self._ema(close, self.ema_fast)
            ema50 = self._ema(close, self.ema_slow)
            ema200 = self._ema(close, self.ema_trend)

            # Calculate RSI
            rsi = self._rsi(close, self.rsi_period)

            # Calculate bias components
            bias_result = self._determine_bias(h4_df, ema20, ema50, ema200, rsi)

            # Add momentum analysis
            bias_result['momentum'] = self._analyze_momentum(h4_df, ema20, ema50)

            # Add structure analysis
            bias_result['structure'] = self._analyze_structure(h4_df)

            # Calculate overall confidence
            bias_result['confidence'] = self._calculate_confidence(bias_result)

            return bias_result

        except Exception as e:
            logger.error(f"Error calculating H4 bias: {e}")
            return {"bias": "error", "strength": 0, "factors": [], "error": str(e)}

    def _determine_bias(self, df: pd.DataFrame, ema20: pd.Series,
                       ema50: pd.Series, ema200: pd.Series, rsi: pd.Series) -> Dict[str, any]:
        """Determine primary H4 bias using multiple factors"""

        current_price = df['close'].iloc[-1]
        current_ema20 = ema20.iloc[-1]
        current_ema50 = ema50.iloc[-1]
        current_ema200 = ema200.iloc[-1]
        current_rsi = rsi.iloc[-1]

        bullish_factors = []
        bearish_factors = []
        strength = 0

        # Factor 1: EMA Stack Analysis
        if current_ema20 > current_ema50 > current_ema200:
            bullish_factors.append("EMA_stack_bullish")
            strength += 25
        elif current_ema20 < current_ema50 < current_ema200:
            bearish_factors.append("EMA_stack_bearish")
            strength += 25

        # Factor 2: Price vs EMA200
        if current_price > current_ema200:
            bullish_factors.append("price_above_ema200")
            strength += 15
        elif current_price < current_ema200:
            bearish_factors.append("price_below_ema200")
            strength += 15

        # Factor 3: EMA20 vs EMA50 Cross
        if self._check_ema_cross(ema20, ema50, lookback=3):
            cross_direction = "bullish" if ema20.iloc[-1] > ema50.iloc[-1] else "bearish"
            if cross_direction == "bullish":
                bullish_factors.append("ema20_50_cross_bullish")
                strength += 20
            else:
                bearish_factors.append("ema20_50_cross_bearish")
                strength += 20

        # Factor 4: RSI Conditions
        if 40 < current_rsi < 80:  # Healthy bullish range
            bullish_factors.append("rsi_bullish_range")
            strength += 10
        elif 20 < current_rsi < 60:  # Healthy bearish range
            bearish_factors.append("rsi_bearish_range")
            strength += 10

        # Factor 5: Price Action (last 3 candles)
        recent_candles = df.tail(3)
        if self._bullish_price_action(recent_candles):
            bullish_factors.append("bullish_price_action")
            strength += 15
        elif self._bearish_price_action(recent_candles):
            bearish_factors.append("bearish_price_action")
            strength += 15

        # Determine final bias
        if len(bullish_factors) > len(bearish_factors) and len(bullish_factors) >= 2:
            bias = "bullish"
            factors = bullish_factors
        elif len(bearish_factors) > len(bullish_factors) and len(bearish_factors) >= 2:
            bias = "bearish"
            factors = bearish_factors
        else:
            bias = "neutral"
            factors = bullish_factors + bearish_factors
            strength = max(strength - 20, 0)  # Reduce strength for neutral

        return {
            "bias": bias,
            "strength": min(strength, 100),
            "factors": factors,
            "bullish_factors": bullish_factors,
            "bearish_factors": bearish_factors,
            "current_rsi": current_rsi,
            "ema_stack": f"EMA20:{current_ema20:.5f} EMA50:{current_ema50:.5f} EMA200:{current_ema200:.5f}"
        }

    def _analyze_momentum(self, df: pd.DataFrame, ema20: pd.Series, ema50: pd.Series) -> Dict[str, any]:
        """Analyze momentum characteristics"""

        # EMA slope analysis
        ema20_slope = self._calculate_slope(ema20, periods=3)
        ema50_slope = self._calculate_slope(ema50, periods=5)

        # Recent volatility
        atr = self._atr(df, 14)
        current_atr = atr.iloc[-1]
        avg_atr = atr.tail(20).mean()
        volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1.0

        return {
            "ema20_slope": ema20_slope,
            "ema50_slope": ema50_slope,
            "volatility_ratio": volatility_ratio,
            "atr_current": current_atr,
            "momentum_strength": abs(ema20_slope) + abs(ema50_slope)
        }

    def _analyze_structure(self, df: pd.DataFrame) -> Dict[str, any]:
        """Analyze market structure (higher highs/lows)"""

        recent_df = df.tail(10)  # Last 10 H4 candles

        highs = recent_df['high'].values
        lows = recent_df['low'].values

        # Simple structure analysis
        higher_highs = sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])
        lower_highs = sum(1 for i in range(1, len(highs)) if highs[i] < highs[i-1])

        higher_lows = sum(1 for i in range(1, len(lows)) if lows[i] > lows[i-1])
        lower_lows = sum(1 for i in range(1, len(lows)) if lows[i] < lows[i-1])

        structure_score = (higher_highs + higher_lows) - (lower_highs + lower_lows)

        if structure_score > 2:
            structure_bias = "bullish"
        elif structure_score < -2:
            structure_bias = "bearish"
        else:
            structure_bias = "neutral"

        return {
            "structure_bias": structure_bias,
            "structure_score": structure_score,
            "higher_highs": higher_highs,
            "higher_lows": higher_lows,
            "lower_highs": lower_highs,
            "lower_lows": lower_lows
        }

    def _calculate_confidence(self, bias_result: Dict[str, any]) -> int:
        """Calculate overall confidence in the bias"""

        base_confidence = bias_result['strength']

        # Boost confidence for momentum alignment
        momentum = bias_result.get('momentum', {})
        if momentum.get('momentum_strength', 0) > 0.0001:  # Strong momentum
            base_confidence += 10

        # Boost confidence for structure alignment
        structure = bias_result.get('structure', {})
        if structure.get('structure_bias') == bias_result['bias']:
            base_confidence += 15

        # Reduce confidence for conflicting signals
        bullish_count = len(bias_result.get('bullish_factors', []))
        bearish_count = len(bias_result.get('bearish_factors', []))

        if abs(bullish_count - bearish_count) < 2:  # Close competition
            base_confidence -= 15

        return max(0, min(100, base_confidence))

    def should_take_h1_signal(self, h4_bias: Dict[str, any], h1_zone_type: str,
                             d1_bias: str) -> Tuple[bool, str]:
        """
        Determine if H1 zone signal should be taken based on H4 analysis

        Returns:
            (should_take, reason)
        """

        if h4_bias['bias'] == 'error' or h4_bias['bias'] == 'insufficient_data':
            return False, f"H4 bias calculation failed: {h4_bias.get('error', 'insufficient_data')}"

        # Minimum confidence threshold
        if h4_bias['confidence'] < 60:
            return False, f"H4 bias confidence too low: {h4_bias['confidence']}%"

        # Check timeframe alignment
        if d1_bias == "bullish" and h1_zone_type == "demand":
            if h4_bias['bias'] == "bullish":
                return True, f"Full confluence: D1 bullish → H4 bullish → H1 demand (confidence: {h4_bias['confidence']}%)"
            elif h4_bias['bias'] == "neutral" and h4_bias['confidence'] >= 70:
                return True, f"Acceptable: D1 bullish → H4 neutral → H1 demand (confidence: {h4_bias['confidence']}%)"
            else:
                return False, f"H4 bias conflict: D1 bullish but H4 {h4_bias['bias']} (confidence: {h4_bias['confidence']}%)"

        elif d1_bias == "bearish" and h1_zone_type == "supply":
            if h4_bias['bias'] == "bearish":
                return True, f"Full confluence: D1 bearish → H4 bearish → H1 supply (confidence: {h4_bias['confidence']}%)"
            elif h4_bias['bias'] == "neutral" and h4_bias['confidence'] >= 70:
                return True, f"Acceptable: D1 bearish → H4 neutral → H1 supply (confidence: {h4_bias['confidence']}%)"
            else:
                return False, f"H4 bias conflict: D1 bearish but H4 {h4_bias['bias']} (confidence: {h4_bias['confidence']}%)"

        else:
            return False, f"D1/H1 mismatch: D1 {d1_bias} with H1 {h1_zone_type}"

    # Technical indicator helper methods
    def _ema(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return series.ewm(span=period).mean()

    def _rsi(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate RSI"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()

    def _calculate_slope(self, series: pd.Series, periods: int) -> float:
        """Calculate slope of recent price movement"""
        recent_values = series.tail(periods).values
        if len(recent_values) < 2:
            return 0.0
        x = np.arange(len(recent_values))
        slope = np.polyfit(x, recent_values, 1)[0]
        return slope

    def _check_ema_cross(self, fast_ema: pd.Series, slow_ema: pd.Series, lookback: int) -> bool:
        """Check for recent EMA crossover"""
        recent_fast = fast_ema.tail(lookback)
        recent_slow = slow_ema.tail(lookback)

        for i in range(1, len(recent_fast)):
            if (recent_fast.iloc[i-1] <= recent_slow.iloc[i-1] and
                recent_fast.iloc[i] > recent_slow.iloc[i]):
                return True
            if (recent_fast.iloc[i-1] >= recent_slow.iloc[i-1] and
                recent_fast.iloc[i] < recent_slow.iloc[i]):
                return True
        return False

    def _bullish_price_action(self, candles: pd.DataFrame) -> bool:
        """Check for bullish price action patterns"""
        if len(candles) < 2:
            return False

        # Check for higher closes
        closes = candles['close'].values
        higher_closes = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i-1])

        # Check for bullish candles
        bullish_candles = sum(1 for _, row in candles.iterrows() if row['close'] > row['open'])

        return higher_closes >= len(candles) // 2 and bullish_candles >= len(candles) // 2

    def _bearish_price_action(self, candles: pd.DataFrame) -> bool:
        """Check for bearish price action patterns"""
        if len(candles) < 2:
            return False

        # Check for lower closes
        closes = candles['close'].values
        lower_closes = sum(1 for i in range(1, len(closes)) if closes[i] < closes[i-1])

        # Check for bearish candles
        bearish_candles = sum(1 for _, row in candles.iterrows() if row['close'] < row['open'])

        return lower_closes >= len(candles) // 2 and bearish_candles >= len(candles) // 2


# Global analyzer instance
h4_analyzer = H4BiasAnalyzer()

def calculate_h4_bias(h4_df: pd.DataFrame) -> Dict[str, any]:
    """Convenience function for H4 bias calculation"""
    return h4_analyzer.calculate_h4_bias(h4_df)

def should_take_signal(h4_bias: Dict[str, any], h1_zone_type: str, d1_bias: str) -> Tuple[bool, str]:
    """Convenience function for signal filtering"""
    return h4_analyzer.should_take_h1_signal(h4_bias, h1_zone_type, d1_bias)


if __name__ == "__main__":
    # Test the H4 bias analyzer
    import logging
    logging.basicConfig(level=logging.INFO)

    print("H4 Bias Analyzer loaded successfully")
    print("Use calculate_h4_bias(h4_df) to analyze H4 timeframe")
    print("Use should_take_signal(h4_bias, zone_type, d1_bias) to filter signals")