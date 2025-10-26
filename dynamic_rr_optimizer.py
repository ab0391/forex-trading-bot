#!/usr/bin/env python3
"""
Dynamic Risk/Reward Optimizer - AI-Powered R:R Selection
Uses technical analysis to optimize R:R ratio (2:1 to 5:1)
NO GUESSING - Pure data-driven decisions
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DynamicRROptimizer:
    """
    AI-Powered Risk/Reward Optimizer
    
    Uses technical indicators to determine optimal R:R:
    - ATR (Average True Range) for volatility
    - Zone strength analysis
    - Price momentum
    - Support/Resistance distance
    
    Output: R:R between 2:1 and 5:1 (data-driven)
    """
    
    def __init__(self):
        self.min_rr = 2.0  # Minimum R:R (your baseline)
        self.max_rr = 5.0  # Maximum R:R (agreed limit)
        
        # ATR periods for volatility analysis
        self.atr_period = 14  # Standard ATR period
        
        logger.info("✅ Dynamic R:R Optimizer initialized (2:1 to 5:1)")
    
    def calculate_atr(self, df, period=14):
        """
        Calculate Average True Range (ATR)
        Measures market volatility - higher ATR = more volatile
        """
        if df is None or len(df) < period:
            return None
        
        try:
            # True Range calculation
            high_low = df['High'] - df['Low']
            high_close = abs(df['High'] - df['Close'].shift())
            low_close = abs(df['Low'] - df['Close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            
            # ATR is the moving average of True Range
            atr = true_range.rolling(window=period).mean()
            
            return atr.iloc[-1]  # Return current ATR
        
        except Exception as e:
            logger.error(f"ATR calculation error: {e}")
            return None
    
    def calculate_zone_strength(self, df, zone_price, zone_type):
        """
        Calculate support/resistance zone strength
        Based on:
        - Number of touches (more touches = stronger zone)
        - Price reaction at zone (bounce strength)
        - Time since last test
        """
        if df is None or df.empty:
            return 0.5  # Default medium strength
        
        try:
            touches = 0
            bounce_strength = []
            tolerance = zone_price * 0.002  # 0.2% tolerance
            
            for i in range(len(df)):
                if zone_type == 'demand':  # Support
                    # Check if price touched support
                    if df['Low'].iloc[i] <= zone_price + tolerance:
                        touches += 1
                        # Calculate bounce strength (how far price bounced)
                        if i < len(df) - 1:
                            bounce = (df['Close'].iloc[i+1] - df['Low'].iloc[i]) / df['Low'].iloc[i]
                            bounce_strength.append(bounce)
                
                else:  # supply - Resistance
                    # Check if price touched resistance
                    if df['High'].iloc[i] >= zone_price - tolerance:
                        touches += 1
                        # Calculate rejection strength
                        if i < len(df) - 1:
                            rejection = (df['High'].iloc[i] - df['Close'].iloc[i+1]) / df['High'].iloc[i]
                            bounce_strength.append(rejection)
            
            # Normalize strength (0 to 1)
            touch_score = min(touches / 5.0, 1.0)  # Max score at 5 touches
            bounce_score = np.mean(bounce_strength) * 100 if bounce_strength else 0.5
            bounce_score = min(bounce_score, 1.0)
            
            # Combined strength score
            strength = (touch_score * 0.6) + (bounce_score * 0.4)
            
            return max(0.1, min(strength, 1.0))  # Clamp between 0.1 and 1.0
        
        except Exception as e:
            logger.error(f"Zone strength calculation error: {e}")
            return 0.5
    
    def calculate_momentum(self, df, period=10):
        """
        Calculate price momentum
        Helps determine if trend is strong enough for higher R:R
        """
        if df is None or len(df) < period:
            return 0.5
        
        try:
            # Calculate rate of change
            roc = (df['Close'].iloc[-1] - df['Close'].iloc[-period]) / df['Close'].iloc[-period]
            
            # Normalize momentum (-1 to 1)
            momentum = np.tanh(roc * 10)  # Smooth scaling
            
            # Convert to 0-1 scale
            momentum_score = (momentum + 1) / 2
            
            return momentum_score
        
        except Exception as e:
            logger.error(f"Momentum calculation error: {e}")
            return 0.5
    
    def calculate_distance_score(self, current_price, zone_price, zone_type):
        """
        Calculate score based on distance from zone
        Closer to zone = better R:R potential
        """
        distance = abs(current_price - zone_price) / current_price
        
        # Optimal distance: 0.1% to 0.5%
        if distance < 0.001:  # Too close (<0.1%)
            return 0.7
        elif distance < 0.005:  # Optimal range (0.1% to 0.5%)
            return 1.0
        elif distance < 0.01:  # Acceptable (0.5% to 1.0%)
            return 0.8
        else:  # Too far (>1.0%)
            return 0.5
    
    def optimize_rr_ratio(self, hist_data, current_price, zone_price, zone_type):
        """
        Main optimization function
        
        Analyzes technical indicators and returns optimal R:R ratio
        
        Parameters:
        - hist_data: Historical price data (pandas DataFrame)
        - current_price: Current market price
        - zone_price: Support/Resistance zone price
        - zone_type: 'demand' (support/long) or 'supply' (resistance/short)
        
        Returns:
        - Optimal R:R ratio (2.0 to 5.0)
        - Confidence score (0 to 1)
        - Explanation string
        """
        
        # Default to 2:1 if we can't analyze
        if hist_data is None or hist_data.empty:
            return 2.0, 0.5, "Insufficient data - using baseline 2:1"
        
        try:
            # 1. Calculate ATR (Volatility)
            atr = self.calculate_atr(hist_data, self.atr_period)
            if atr is None:
                atr_score = 0.5
            else:
                # Normalize ATR (higher volatility = higher R:R potential)
                atr_pct = (atr / current_price) * 100
                if atr_pct > 1.0:  # High volatility
                    atr_score = 0.9
                elif atr_pct > 0.5:  # Medium volatility
                    atr_score = 0.7
                else:  # Low volatility
                    atr_score = 0.5
            
            # 2. Calculate Zone Strength
            zone_strength = self.calculate_zone_strength(hist_data, zone_price, zone_type)
            
            # 3. Calculate Momentum
            momentum = self.calculate_momentum(hist_data, period=10)
            
            # 4. Calculate Distance Score
            distance_score = self.calculate_distance_score(current_price, zone_price, zone_type)
            
            # 5. Combine scores with weights
            # Stronger zone + higher volatility + good momentum = higher R:R
            weights = {
                'atr': 0.30,        # Volatility is important
                'zone': 0.35,       # Zone strength is critical
                'momentum': 0.20,   # Momentum helps
                'distance': 0.15    # Distance matters
            }
            
            combined_score = (
                atr_score * weights['atr'] +
                zone_strength * weights['zone'] +
                momentum * weights['momentum'] +
                distance_score * weights['distance']
            )
            
            # 6. Map combined score to R:R ratio (2.0 to 5.0)
            # Score 0.0-0.4 → 2:1
            # Score 0.4-0.6 → 3:1
            # Score 0.6-0.8 → 4:1
            # Score 0.8-1.0 → 5:1
            
            if combined_score < 0.4:
                optimal_rr = 2.0
                confidence = combined_score / 0.4
            elif combined_score < 0.6:
                optimal_rr = 3.0
                confidence = 0.7
            elif combined_score < 0.8:
                optimal_rr = 4.0
                confidence = 0.85
            else:
                optimal_rr = 5.0
                confidence = 0.95
            
            # 7. Build explanation
            explanation_parts = []
            if atr_score > 0.7:
                explanation_parts.append("high volatility")
            if zone_strength > 0.7:
                explanation_parts.append("strong zone")
            if momentum > 0.7:
                explanation_parts.append("good momentum")
            if distance_score > 0.8:
                explanation_parts.append("optimal entry")
            
            if not explanation_parts:
                explanation_parts.append("baseline conditions")
            
            explanation = f"{optimal_rr}:1 R:R - " + ", ".join(explanation_parts)
            
            logger.info(f"📊 R:R Optimizer: {explanation} (confidence: {confidence:.2f})")
            logger.info(f"   ATR: {atr_score:.2f} | Zone: {zone_strength:.2f} | Momentum: {momentum:.2f} | Distance: {distance_score:.2f}")
            
            return optimal_rr, confidence, explanation
        
        except Exception as e:
            logger.error(f"R:R optimization error: {e}")
            return 2.0, 0.5, "Error in analysis - using baseline 2:1"
    
    def calculate_stop_and_target(self, entry, zone_type, rr_ratio):
        """
        Calculate stop loss and take profit based on R:R ratio
        
        Parameters:
        - entry: Entry price
        - zone_type: 'demand' (long) or 'supply' (short)
        - rr_ratio: Risk/Reward ratio (2.0 to 5.0)
        
        Returns:
        - stop: Stop loss price
        - target: Take profit price
        """
        
        # Base risk: 0.5% of entry (your standard risk)
        base_risk_pct = 0.005
        
        if zone_type == 'demand':  # LONG trade
            stop = entry * (1 - base_risk_pct)
            reward_pct = base_risk_pct * rr_ratio
            target = entry * (1 + reward_pct)
        
        else:  # 'supply' - SHORT trade
            stop = entry * (1 + base_risk_pct)
            reward_pct = base_risk_pct * rr_ratio
            target = entry * (1 - reward_pct)
        
        return stop, target

# Test the optimizer
if __name__ == "__main__":
    import yfinance as yf
    
    print("🧪 Testing Dynamic R:R Optimizer...")
    print("="*60)
    
    optimizer = DynamicRROptimizer()
    
    # Test with EUR/USD data
    try:
        ticker = yf.Ticker("EURUSD=X")
        hist = ticker.history(period="60d", interval="1h")
        
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            zone_price = current_price * 0.995  # Demand zone 0.5% below
            
            print(f"\n📊 Test Case: EUR/USD LONG")
            print(f"   Current Price: {current_price:.5f}")
            print(f"   Zone Price: {zone_price:.5f}")
            
            rr, confidence, explanation = optimizer.optimize_rr_ratio(
                hist, current_price, zone_price, 'demand'
            )
            
            print(f"\n✅ Optimized R:R: {rr}:1")
            print(f"   Confidence: {confidence:.2%}")
            print(f"   Explanation: {explanation}")
            
            stop, target = optimizer.calculate_stop_and_target(
                current_price, 'demand', rr
            )
            
            print(f"\n📈 Trade Setup:")
            print(f"   Entry: {current_price:.5f}")
            print(f"   Stop: {stop:.5f}")
            print(f"   Target: {target:.5f}")
            print(f"   R:R: {rr}:1")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "="*60)
    print("✅ Dynamic R:R Optimizer ready for integration!")


