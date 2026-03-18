 # Analyze pricing data
# modules/price_intelligence/analyzer.py

import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

class PriceAnalyzer:
    
    @staticmethod
    def analyze(sold_items: List[Dict], condition: Optional[str] = None) -> Optional[Dict]:
        items = sold_items
        if condition:
            filtered = [i for i in sold_items if i.get('condition')== condition]

            if filtered:
                items = filtered
        prices = [item['price'] for item in items]

        if prices is None:
            return None
        average = statistics.mean(prices)
        median = statistics.median(prices)
        min_price = min(prices)
        max_price = max(prices)
        std_dev = statistics.stdev(prices) if len(prices) > 1 else 0

        if len(prices) >= 30:
            confidence = 'high'
        elif 10 <= len(prices) < 30:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        suggested_price = median * 1.05 #5% above median for profit

        trend = TrendAnalyzer.calculate_trend(items)
        reccomendation = PriceAnalyzer._generate_recommendation(suggested_price, len(prices), trend, std_dev, average)
        return{ 'suggested_price': suggested_price,
                'confidence': confidence,
                'market_average':average,
                'median_price': median,
                'min_price': min_price,
                'max_price': max_price,
                'std_dev': std_dev,
                'sample_size': len(prices),
                'trend': trend,
                'recommendation': reccomendation}

    @staticmethod
    def _generate_recommendation(suggested_price: float,sample_size: int,trend: str,std_dev: float, market_avg:float ) -> str:
        """
        Generate a plain-English pricing recommendation.
        """
        parts = []

        if sample_size < 10:
            parts.append(f"Based on only {sample_size} recent sales, this is a rough pricing estimate.")
        elif sample_size < 30:
            parts.append(f"Based on {sample_size} recenet sales, this pricing estimate is reasonably supported")
        else:
            parts.append(f'Base on {sample_size} recent sales, this pricing estimate is strongly supported by market data')
        
        volatility_ratio = std_dev/ market_avg if market_avg > 0 else 0
        if volatility_ratio > 0.50:
            parts.append("Sale prices vary widely, suggesting condition, completeness, or provenance may significantly affect value.")
        elif volatility_ratio > 0.20:
            parts.append("Sale prices show some variation, so item-specific details may still affect the final selling price.")
        else:
            parts.append("Recent sale prices are fairly consistent, which makes the estimate more reliable.")

        #trend
        if trend == "increasing":
            parts.append("The market appears to be trending upward.")
        elif trend == "decreasing":
            parts.append("The market appears to be trending downward.")
        else:
            parts.append("The market appears stable.")

        #action advice

        if trend == "increasing":
            if sample_size < 10:
                parts.append(f"You could start around ${suggested_price:.2f}, but be prepared to adjust quickly as more market data comes in.")
            else:
                parts.append(f"You could consider listing near ${suggested_price:.2f} or slightly higher if you are willing to wait for the right buyer.")
        elif trend == "decreasing":
            parts.append(f"Pricing competitively around ${suggested_price:.2f} may improve your chances of a quicker sale.")
        else:
            parts.append(f"Listing around ${suggested_price:.2f} is a reasonable starting point based on recent comparable sales.")

        return " ".join(parts)
    
    @staticmethod
    def remove_outliers(prices: List[float]) -> List[float]:
        """
        Remove statistical outliers using the IQR method.

        IQR = Interquartile Range = 75th percentile - 25th percentile
            Lower bound = Q1 - 1.5 * IQR
            Upper bound = Q3 + 1.5 * IQR
            Anything outside these bounds is an outlier.
        """
        n = len(prices)
        if n < 4:
            return prices
        prices.sort()
        q1= prices[n//4]
        q3= prices[3*n//4]
        iqr = q3-q1
        filtered = [i for i in prices if q1 - 1.5 * iqr <= i <= q3 + 1.5 * iqr ]
        return filtered
class TrendAnalyzer:

    @staticmethod
    def calculate_trend(sold_items: List[Dict], days_recent: int = 30) -> str:
        """
        Compare recent average price vs older average price.
        """    
        recent_items = []
        older_items = []
        for item in sold_items:
            sold_date_str = item.get("sold_date")
            if not sold_date_str:
                continue
            sold_date = datetime.strptime(sold_date_str,"%Y-%m-%d").date()
            today = datetime.today
            cutoff = today - timedelta(days=days_recent)
            if sold_date >= cutoff:
                recent_items.append(item)
            else:
                older_items.append(item)
        
        if len(recent_items) <=3 or len(older_items) < 3:
            return 'stable'
        
        recent_prices = [item['price'] for item in recent_items]
        older_prices = [item['price'] for item in older_items]
        recent_avg = statistics.mean(recent_prices)
        older_avg = statistics.mean(older_prices)
        change_pct = (recent_avg-older_avg)/ older_avg * 100

        if change_pct >= 10:
            return 'increasing'
        else:
            return 'decreasing'
        
    def get_price_by_month(sold_items: List[Dict]) -> List[Dict]:
        """ 
        Group sold prices by month for graph data
        """
        grouped = defaultdict(list)
        for item in sold_items:
            sold_date = item.get('sold_date')
            if not sold_date:
                continue
            month_key = sold_date[:7] #YYYY-MM
            grouped[month_key].append(item)
        
        monthly_avg = {
        month: statistics.mean(i["price"] for i in items)
        for month, items in grouped.items()
        }


 