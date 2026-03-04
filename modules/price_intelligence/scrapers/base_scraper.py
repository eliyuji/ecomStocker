import time
import random
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseScraper(ABC):
    """
    ABC for all price scrapers
    """

    def __init__(self):
        """
        Set up a shared requests Session with browser-like headers.
         WHAT TO DO:
            1. Create self.session = requests.Session()
            2. Set self.session.headers to a dict containing:
               - 'User-Agent': a real browser user agent string
                 (Google "latest Chrome user agent string")
               - 'Accept-Language': 'en-US,en;q=0.9'
               - 'Accept': 'text/html,application/xhtml+xml,...'

        WHY FAKE HEADERS?
            Sites detect bots by checking headers. A default requests
            call has User-Agent='python-requests/2.x' which is instantly
            blocked. Mimicking a browser header gets past basic detection.

        :param self: Description
        """
        pass

    @abstractmethod
    def get_sold_listings(self, product_name: str, condition: Optional[str] = None):
        """
        Scrape recently sold listings for a product

        Parameters:
        product_name: The search term
        condition: Optional filter; Different platforms have different filters so child classes map base scraper labels to platforms'

        Returns a list of dicts:
        {
                'title':      str,    # Listing title
                'price':      float,  # Sale price in USD
                'sold_date':  str,    # ISO date string 'YYYY-MM-DD' or None
                'condition':  str,    # Condition label from platform
                'url':        str,    # Link to the original listing
                'source':     str,    # Platform name, e.g. 'ebay'
            }

        
            Returns empty [] on any error
        """
    def get_active_listings(self, product_name: str, condition: Optional[str]):
        """
        Scape currently active (unsold) listings for a product.
        
        Must return same dict shape as get_sold_listings() but with:
        'sold_date': None
        """
        pass

    def _rate_limit(self, min_seconds: float = 1.0, max_seconds: float = 5.0):
        """
        Sleep for a random amount of time in between requests

        Todo:
            Use time.sleep(random.uniform(min_seconds, max_seconds))

        USAGE IN CHILD CLASS:
            def get_sold_listings(self, product_name, condition):
                self._rate_limit()          # Wait before each request
                response = self.session.get(url)
        """
        pass
    def _safe_get(self, url: str, params: Dict = None, retries: int = 3) -> Optional[requests.Response]:
         """
         PARAMETERS:
            url      Full URL to request
            params   Query string parameters as dict (requests handles encoding)
            retries  How many times to try before giving up (default 3)

        WHAT TO DO:
            1. Loop up to `retries` times
            2. Call self._rate_limit() before each attempt
            3. Try self.session.get(url, params=params, timeout=10)
            4. If status_code == 200, return the response
            5. If status_code == 429 (rate limited), wait longer (5-10s) then retry
            6. If any exception occurs, wait and retry
            7. After all retries exhausted, return None (don't raise)

        USAGE IN CHILD CLASS:
            response = self._safe_get(url, params={'_nkw': 'charizard'})
            if response is None:
                return []   # Scrape failed, return empty    
         """
         pass
    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Convert a raw price string from a webpage into a float

        1. Return None if price_text is empty or None
        2. Use a regex or string methods to strip non-numeric chars
               Hint: re.sub(r'[^\d.]', '', price_text)
        3. Try float(cleaned), return None on ValueError
        """
        pass
    
    def _normalize_condition(self, raw_conditions:str) -> str:
        """
        Map a platform's condition label to our standard labels
        
        Todo:
            Build a mapping dict and do a case-insensitive lookup.
            Return 'unknown' if no match found.

        EXAMPLE MAPPING (add more as you discover platform labels):
            {
                'new':          'mint',
                'like new':     'near_mint',
                'very good':    'excellent',
                'good':         'good',
                'acceptable':   'fair',
                'for parts':    'poor',
            }
        """
        pass