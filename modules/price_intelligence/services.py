"""
Price Intelligence Service
The coordinator between scrapers, analyzer, and the database.

ROLE IN THE SYSTEM:
    Routes call the service.
    The service calls the scraper to get raw data.
    The service calls the analyzer to process that data.
    The service saves results to the database.
    The service returns results back to the route.
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from modules.price_intelligence.models import PriceCheck, MarketSale, PriceAlert, AlertNotification
from modules.price_intelligence.scrapers.ebay_scraper import EbayScraper
from modules.price_intelligence.analyzer import PriceAnalyzer, TrendAnalyzer
from modules.products.models import Product

class PriceIntelligenceService:
    #Check market price for a product

    @staticmethod
    def check_market_price(db: Session, product_name: str, category: Optional[str] = None, condition: Optional[str] = None) -> Optional[Dict]:
        """
        Full pipeline: scrape → analyze → return insights.
        This is the main method called by the route handler.
        """
        try:
            scraper = EbayScraper()
            sold_items = scraper.get_sold_listings(product_name, condition)
            if not sold_items:
                return {'error': 'No market data found', 'product_name': product_name}
        
            PriceIntelligenceService._save_market_sales(db, sold_items, product_name, category, condition)
            analysis = PriceAnalyzer.analyze(sold_items, condition)
            if not analysis:
                return {
                    'error': 'Analysis Failed',
                    'product_name': product_name
                }
            return analysis
        except Exception as e:
            return {
                'error': f'Market check failed: {str(e)}',
                'product_name': product_name
            }
    
    @staticmethod
    def _save_market_sales(db: Session, sold_items, product_name: str, category: Optional[str], condition: Optional[str])-> None:
        """
        Persist raw scraped listings to the market_sales table.
        """
        try:
            for item in sold_items:
                url = item.get('url')

                if url:
                    existing = db.query(MarketSale).filter(MarketSale.source_url == url).first()
                    if existing:
                        continue
                sale = MarketSale(
                    product_name = product_name,
                    category = category,
                    condition = item.get('condition') or condition,
                    sold_price= item['price'],
                    sold_date=item.get('sold_date'),
                    source= item.get('source'),
                    source_url=url
                )
                db.add(sale)
            db.commit()
        except Exception:
            db.rollback()

    @staticmethod
    def check_and_save_product_price(db: Session, product_id: int) -> Optional[Dict]:
        """
        Check market price for a specific product in our database,
        then update the product's price intelligence fields.
        """
        product = db.query(Product).filter_by(product_id=product_id).first()
        if not product:
            return None
        analysis= PriceIntelligenceService.check_market_price(db, product.name,product.category, product.condition)
        if 'error' not in analysis:
            product.suggested_price = analysis['suggested_price']
            product.market_average = analysis['market_average']
            product.price_confidence = analysis['confidence']
            product.last_market_check = datetime.utcnow()
        
        #save a price check row
        price_check = PriceCheck(
            product_id = product_id,
            source = 'ebay',
            average_price = analysis['market_average'],
            median_price  = analysis['median_price'],
            min_price     = analysis['min_price'],
            max_price     = analysis['max_price'],
            sample_size   = analysis['sample_size'],
            confidence    = analysis['confidence'],
        )
        db.add(price_check)
        db.commit()

        # Future:
        # AlertService.check_alerts_for_product(db, product_id)
        return analysis
    
    @staticmethod
    def get_price_history(db: Session, product_id: int) -> List[Dict]:
        """
        Return all saved PriceCheck rows for a product, newest first.
        """
        results = (db.query(PriceCheck)
        .filter_by(product_id=product_id)
        .order_by(PriceCheck.checked_at.desc())
        .all()
        )

        return [check.to_dict() for check in results]
    
    @staticmethod
    def get_latest_price_check(db: Session, product_id: int) -> Optional[Dict]:
        result = (db.query(PriceCheck)
                  .filter_by(product_id=product_id)
                  .order_by(PriceCheck.checked_at.desc())
                  .first()
                  )
        if result:
            return result.to_dict()
        else:
            return None

    @staticmethod
    def get_market_sales(db:Session, product_name: str, days:int = 90, limit:int = 100) -> List[Dict]:
        cutoff= datetime.utcnow() - timedelta(days=days)
        results = (db.query(MarketSale)
                .filter_by(MarketSale.product_name.ilike(f"%{product_name}%"),MarketSale.created_at >= cutoff)
                .order_by(MarketSale.sold_date.desc())
                .limit(limit)
                .all()
                )
        return [sale.to_dict() for sale in results]
    
    @staticmethod
    def get_product_intelligence(db: Session, product_id: int) -> Dict:
        """
        Return a full price intelligence summary for one product.
        This is what the route returns when someone calls
        GET /api/price/product/<product_id>

        WHAT TO DO:
            1. Fetch product from DB, return error dict if not found
            2. Get latest price check: get_latest_price_check(db, product_id)
            3. Build and return a dict:
               {
                   'product_id':        product.product_id,
                   'product_name':      product.name,
                   'your_price':        float(product.price),
                   'suggested_price':   float(product.suggested_price) or None,
                   'market_average':    float(product.market_average)  or None,
                   'price_confidence':  product.price_confidence,
                   'last_checked':      product.last_market_check.isoformat() or None,
                   'latest_check':      latest_check dict or None,
                   'is_overpriced':     True if your_price > market_average * 1.2 else False,
                   'is_underpriced':    True if your_price < market_average * 0.8 else False,
                   'price_difference':  your_price - market_average (positive = above market),
               }

        NOTE: is_overpriced/is_underpriced logic lives HERE (service layer),
              NOT in the model. This was discussed in our Week 1 review.
        """
        try:
            product = (db.query(Product).filter_by(product_id=product_id).first())
        except Exception as e:
            return {'error': f'Query failed due to {e}'}

        if not product:
            return {'error': 'Product not found', 'product_id': product_id }
        latest_check = PriceIntelligenceService.get_latest_price_check(db, product_id)

        return {
            'product_id': product.product_id,
            'product_name': product.name,
            'your_price': float(product.price),
            'suggested_price': float(product.suggested_price) if product.suggested_price is not None else None,
            'market_average': float(product.market_average) if product.market_average is not None else None,
            'price_confidence': product.price_confidence,
            'last_checked': product.last_market_check.isoformat() if product.last_market_check else None,
            'latest_checked': latest_check,
            'is_overpriced': True if product.price > product.market_average *1.2 else False,
            'is_underpriced': True if product.price < product.market_average * 0.8 else False,
            'price_difference': float(product.price - product.market_average)
        }

    @staticmethod
    def _is_stale(product: Product, max_age_hours: int=24) -> bool:
        """
        Check if a product's price intelligence is outdated.
        USAGE IN check_and_save_product_price():
            if PriceIntelligenceService._is_stale(product):
                # Re-scrape
            else:
                # Return cached data from product fields
        """
        if product.last_market_check is None:
            return True
        age = datetime.utcnow() - product.last_market_check
        if age > timedelta(hours=max_age_hours):
            return True
        return False
    