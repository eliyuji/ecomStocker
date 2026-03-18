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
        
    