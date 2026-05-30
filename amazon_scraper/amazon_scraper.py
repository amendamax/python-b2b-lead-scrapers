from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import time
import random

class AmazonPhoneScraper:
    """
    A professional, high-performance Amazon scraper built to extract ONLY actual phones or laptops
    (accessories, cases, parts, and chargers are semantically filtered out).
    Uses curl_cffi to bypass Akamai browser detection blocks.
    """
    
    BASE_URL = "https://www.amazon.com"
    
    # Semantic verification keywords for phones and laptops
    PRODUCT_KEYWORDS = [
        "iphone", "samsung", "galaxy", "pixel", "oneplus", "motorola", "xiaomi",
        "laptop", "notebook", "ultrabook", "computer", "chromebook"
    ]
    SPEC_KEYWORDS = [
        "gb", "tb", "gigabyte", "terabyte", "ram", "rtx", "intel", "amd", 
        "ryzen", "core", "unlocked", "renewed", "refurbished", "inch", "hz"
    ]
    
    # Keywords to strictly filter out (covers phone cases, laptop bags, chargers, parts)
    ACCESSORY_KEYWORDS = [
        "case", "cover", "protector", "glass", "cable", "charger", "adapter", 
        "power bank", "holder", "mount", "strap", "wallet", "stand", "film", 
        "shield", "casing", "sleeve", "replacement", "camera module", "repair", 
        "parts", "battery replacement", "screen replacement", "spigen", "otterbox", 
        "supcase", "ring", "loop", "bag", "backpack", "power cord", "keyboard cover",
        "hub", "dock", "dongle", "mousepad", "cooling pad"
    ]

    def __init__(self):
        self.session = requests.Session(impersonate="chrome")

    def clean_price(self, price_str):
        """Cleans price strings (e.g., '$1,099.99') into a float."""
        if not price_str:
            return 0.0
        cleaned = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    def parse_listing(self, item_element):
        """Parses a single Amazon search result card into a structured dictionary."""
        # 1. Extract Title
        title_el = item_element.select_one('h2 span') or item_element.select_one('h2')
        if not title_el:
            return None
        title = title_el.text.strip()
        
        # 2. Strict Semantic Filters
        title_lower = title.lower()
        
        # Must match phone/laptop brand/term AND specify a tech spec (e.g. 16GB RAM, 512GB, RTX)
        is_valid_product = any(k in title_lower for k in self.PRODUCT_KEYWORDS)
        has_tech_specs = any(spec in title_lower for spec in self.SPEC_KEYWORDS)
        
        if not (is_valid_product and has_tech_specs):
            return None # Skip non-related search noise
            
        # Strict accessory/bag/parts filter
        is_accessory = any(word in title_lower for word in self.ACCESSORY_KEYWORDS)
        if is_accessory:
            return None # Skip cases, screen protectors, bags, chargers, etc.
            
        # 3. Extract Price
        price = 0.0
        price_el = item_element.select_one('.a-price .a-offscreen') or item_element.select_one('.a-price') or item_element.select_one('.a-color-price')
        if price_el:
            price = self.clean_price(price_el.text.strip())
            
        # 4. Extract Product Link
        link = ""
        for a in item_element.select('a'):
            href = a.get('href', '')
            if '/dp/' in href or '/gp/product/' in href:
                clean_path = href.split('?')[0]
                link = urllib.parse.urljoin(self.BASE_URL, clean_path)
                break
        
        if not link:
            first_a = item_element.select_one('a')
            if first_a and 'href' in first_a.attrs:
                link = urllib.parse.urljoin(self.BASE_URL, first_a['href'].split('?')[0])
                
        # 5. Extract Image URL
        img_el = item_element.select_one('.s-image, img')
        img_url = ""
        if img_el:
            img_url = img_el.get('src', '')
            
        return {
            "Title": title,
            "Price": price,
            "Product URL": link,
            "Image URL": img_url
        }

    def scrape_search(self, query, max_pages=1, progress_callback=None):
        """
        Scrapes multiple pages of Amazon search results.
        Includes random sleep intervals to mimic human scrolling.
        """
        results = []
        encoded_query = urllib.parse.quote_plus(query)
        
        for page in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/s?k={encoded_query}&page={page}"
            
            if progress_callback:
                progress_callback(page, max_pages, f"Fetching page {page}...")
                
            try:
                response = self.session.get(url, timeout=20)
                if response.status_code != 200:
                    if progress_callback:
                        progress_callback(page, max_pages, f"Finished (reached end of pages or blocked). Status: {response.status_code}")
                    break
                    
                soup = BeautifulSoup(response.text, 'lxml')
                listings = soup.select('[data-component-type="s-search-result"]')
                
                if not listings:
                    if progress_callback:
                        progress_callback(page, max_pages, "No listings found on page.")
                    break
                    
                page_results_count = 0
                for item in listings:
                    parsed = self.parse_listing(item)
                    if parsed:
                        results.append(parsed)
                        page_results_count += 1
                
                if progress_callback:
                    progress_callback(page, max_pages, f"Page {page} completed. Extracted {page_results_count} items.")
                
                # Polite delay to mimic human behavior
                if page < max_pages:
                    time.sleep(random.uniform(1.5, 3.0))
                    
            except Exception as e:
                if progress_callback:
                    progress_callback(page, max_pages, f"Error on page {page}: {str(e)}")
                break
                
        return results

# Self-test block
if __name__ == "__main__":
    print("Testing Amazon Product Scraper...")
    scraper = AmazonPhoneScraper()
    test_query = "gaming laptop"
    print(f"Scraping 1 page for '{test_query}'...")
    
    def log_progress(page, max_pages, msg):
        print(f"[{page}/{max_pages}] {msg}")
        
    data = scraper.scrape_search(test_query, max_pages=1, progress_callback=log_progress)
    print(f"\nExtracted {len(data)} ACTUAL PRODUCTS successfully!")
    if data:
        print("First product parsed sample:")
        for k, v in data[0].items():
            print(f"  {k}: {v}")
