 # Analyze pricing data
# modules/price_intelligence/analyzer.py

class PriceAnalyzer:
    
    @staticmethod
    def analyze_market_price(scraped_data):
        """
        Analyze scraped data to suggest price
        
        Returns:
        {
            'suggested_price': 25.99,
            'confidence': 'high',
            'market_average': 24.50,
            'price_range': {'min': 18.00, 'max': 35.00},
            'sample_size': 47,
            'trend': 'increasing'  # or 'stable', 'decreasing'
        }
        """
        prices = [item['price'] for item in scraped_data]
        
        # Calculate statistics
        avg_price = sum(prices) / len(prices)
        median_price = sorted(prices)[len(prices)//2]
        
        # Check trend (recent vs older sales)
        recent_avg = calculate_recent_average(scraped_data, days=30)
        older_avg = calculate_older_average(scraped_data, days=90)
        
        trend = 'increasing' if recent_avg > older_avg * 1.1 else 'stable'
        
        return {
            'suggested_price': median_price * 1.05,  # Slight markup
            'confidence': 'high' if len(prices) > 20 else 'medium',
            'market_average': avg_price,
            'trend': trend
        }