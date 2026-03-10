"""
ebay Scraper
URL Patterns:
https://www.ebay.com/sch/i.html
        ?_nkw=charizard+pokemon+card   ← search term
        &LH_Sold=1                     ← only sold listings
        &LH_Complete=1                 ← only completed listings
        &LH_ItemCondition=3000         ← condition filter (optional)
        &_sop=13                       ← sort by recently sold
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .base_scraper import BaseScraper
from datetime import datetime

class EbayScraper(BaseScraper):
    BASE_URL = "https://www.ebay.com/sch/i.html"    
    def __init__(self):
        super().__init__()
    
    def convert_sold_date(item):
            sold_el = item.find('span', attrs={'aria-label': 'Sold Item'})

            sold_date = None
            if sold_el:
                sold_text = sold_el.get_text(strip=True)
                cleaned = sold_text.replace('Sold','').strip()

                try:
                    sold_date = datetime.strptime(cleaned,"%b %d, %Y").strftime("%Y-%m-%d")
                except ValueError:
                    sold_date = None
    def _normalize_condition(self, raw_conditions):
        """
        Map a platform's condition label to our standard labels
        """

        if not raw_conditions:
            return "unknown"

        # normalize text
        condition = raw_conditions.strip().lower()

        mapping = {
            'new': 'mint',
            'like new': 'near_mint',
            'very good': 'excellent',
            'good': 'good',
            'acceptable': 'fair',
            'for parts': 'poor',
            'pre-owned': 'good',
            'used': 'good',
            'open box': 'near_mint'
        }

        return mapping.get(condition, "unknown")
    

    def get_sold_listings(self, product_name, condition = None):
        EBAY_CONDITION_CODES = {
        'mint':       '1000',   # New
        'near_mint':  '2750',   # Like New
        'excellent':  '3000',   # Very Good
        'good':       '4000',   # Good
        'fair':       '5000',   # Acceptable
        'poor':       '6000',   # For parts/not working
        }

        params = {
            '_nkw': product_name,
            'LH_Sold': '1',
            'LH_Complete': '1',
            '_sop': '13',
            '_ipg': '60',
        }
        if condition and condition in EBAY_CONDITION_CODES:
            params['LH_ItemCondition'] = EBAY_CONDITION_CODES[condition]

        res = []

        response = self._safe_get(self.BASE_URL, params=params)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('li', class_='s-card')


        for item in items:
            title_el = item.find('div', class_='s-card__title')
            price_el = item.find('span', class_='s-card__price')
            condition_el = item.select_one('.s-card__subtitle span')
            url_el = item.select_one('.su-card-container__content a.s-card__link')

            title = title_el.get_text(" ", strip=True) if title_el else None
            price = self._parse_price(price_el.get_text(strip=True)) if price_el else None
            sold_date = self.convert_sold_date(item)

            raw_condition = condition_el.get_text(strip=True) if condition_el else None
            normalized_condition = (
                self._normalize_condition(raw_condition) if raw_condition else None
            )

            url = url_el.get('href') if url_el else None

            if price is None:
                continue
            
            result = {
                'title': title,
                'price': price,
                'sold_date': sold_date,
                'condition': normalized_condition,
                'url': url,
                'source': 'ebay'
            }
            res.append(result)
        return res

        
