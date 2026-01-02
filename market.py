from typing import Dict, List, Optional

class MarketAnalyzer:
    """
    Analyzes market depth data to estimate buy/sell pressure and sentiment.
    Strictly follows domain rules: No exact volume claims, use specific terminology.
    """

    @staticmethod
    def calculate_strength(depth_data: Dict) -> Dict:
        """
        Calculates market strength based on Top 5 Buy/Sell orders (Market Depth).
        
        Args:
            depth_data: Dictionary containing 'buy' and 'sell' lists of orders.
                        Expected format: {'buy': [{'quantity': 10, ...}, ...], 'sell': [...]}
        
        Returns:
            Dictionary with calculated metrics:
            - totalVolume
            - buyVolume (Estimated)
            - sellVolume (Estimated)
            - buyPercent
            - sellPercent
            - strengthPercent
            - sentiment
        """
        
        # 1. Calculate Buy Volume (Sum of top 5 buy orders)
        buy_orders = depth_data.get('buy', [])
        buy_volume = sum(order.get('quantity', 0) for order in buy_orders)

        # 2. Calculate Sell Volume (Sum of top 5 sell orders)
        # Note: In real SmartAPI response, keys might vary slightly, assuming standard format here.
        sell_orders = depth_data.get('sell', [])
        sell_volume = sum(order.get('quantity', 0) for order in sell_orders)

        # 3. Total Order Volume
        total_order_volume = buy_volume + sell_volume

        # Default values if no data to avoid division by zero
        if total_order_volume == 0:
            return {
                "totalVolume": 0,
                "buyVolume": 0,
                "sellVolume": 0,
                "buyPercent": 0.0,
                "sellPercent": 0.0,
                "strengthPercent": 0.0,
                "sentiment": "Neutral"
            }

        # 4. Percentage Logic
        buy_percent = (buy_volume / total_order_volume) * 100
        sell_percent = (sell_volume / total_order_volume) * 100

        # 5. Strength Calculation
        # strengthPercent = ((buyVolume - sellVolume) / totalOrderVolume) * 100
        strength_percent = ((buy_volume - sell_volume) / total_order_volume) * 100

        # 6. Sentiment Logic
        sentiment = "Neutral"
        if strength_percent > 5:
            sentiment = "Bullish"
        elif strength_percent < -5:
            sentiment = "Bearish"

        return {
            "totalVolume": total_order_volume,
            "buyVolume": buy_volume, # IMPORTANT: This is estimated pressure from top 5 orders
            "sellVolume": sell_volume, # IMPORTANT: This is estimated pressure from top 5 orders
            "tradedVolume": depth_data.get('tradedVolume', 0), # New Field: Executed Volume
            "buyPercent": round(buy_percent, 2),
            "sellPercent": round(sell_percent, 2),
            "strengthPercent": round(strength_percent, 2),
            "sentiment": sentiment
        }
