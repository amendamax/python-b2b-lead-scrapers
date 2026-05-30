import requests
from bs4 import BeautifulSoup
import time
import re
import urllib.parse

class ECommerceScraper:
    """
    A robust, modular scraper designed for extracting product listings from Books to Scrape.
    Demonstrates clean exception handling, advanced data cleaning (text-to-numeric ratings),
    and reliable URL resolution.
    """
    
    BASE_URL = "http://books.toscrape.com/"
    
    # Mapping for star ratings text to numbers
    RATING_MAP = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

    def clean_price(self, price_str):
        """Cleans price strings (e.g. '£51.77') and extracts the float value."""
        if not price_str:
            return 0.0
        cleaned = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    def parse_rating(self, rating_classes):
        """Extracts numerical rating from class list (e.g., ['star-rating', 'Three'] -> 3)."""
        for cls in rating_classes:
            cls_lower = cls.lower()
            if cls_lower in self.RATING_MAP:
                return self.RATING_MAP[cls_lower]
        return 0

    def parse_listing(self, item_element):
        """Parses a single HTML book element into a structured dictionary."""
        # Find Title Link
        link_el = item_element.select_one('h3 a')
        if not link_el:
            return None
        
        # Expert tip: The 'title' attribute contains the full, untruncated title!
        title = link_el.get('title') or link_el.text.strip()
        
        # Link resolution
        href = link_el.get('href', '')
        # Handle relative URL resolution depending on whether it's catalog/ or root
        if href.startswith('catalogue/'):
            product_url = urllib.parse.urljoin(self.BASE_URL, href)
        else:
            product_url = urllib.parse.urljoin(self.BASE_URL, f"catalogue/{href}")
            
        # Find Price
        price_el = item_element.select_one('.price_color')
        price_raw = price_el.text.strip() if price_el else ""
        price = self.clean_price(price_raw)
        
        # Find Rating
        rating_el = item_element.select_one('.star-rating')
        rating_classes = rating_el.get('class', []) if rating_el else []
        rating = self.parse_rating(rating_classes)
        
        # Find Availability
        availability_el = item_element.select_one('.instock.availability')
        availability_text = availability_el.text.strip() if availability_el else "Out of stock"
        in_stock = "in stock" in availability_text.lower()
        
        # Find Image URL
        img_el = item_element.select_one('.image_container img')
        img_url = ""
        if img_el:
            src = img_el.get('src', '')
            # Clean leading dots in relative paths
            src_cleaned = re.sub(r'^\.+/', '', src)
            img_url = urllib.parse.urljoin(self.BASE_URL, src_cleaned)
            
        return {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "In Stock": "Yes" if in_stock else "No",
            "Product URL": product_url,
            "Image URL": img_url
        }

    def scrape_query(self, category=None, max_pages=1, progress_callback=None):
        """
        Scrapes multiple pages of books.
        Optionally filters by category (mocked or via URL path if provided).
        """
        results = []
        
        # Standard books.toscrape pagination URL
        for page in range(1, max_pages + 1):
            if progress_callback:
                progress_callback(page, max_pages, f"Fetching page {page}...")
                
            # If no category, scrape main list
            url = f"{self.BASE_URL}catalogue/page-{page}.html"
            
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code != 200:
                    if progress_callback:
                        progress_callback(page, max_pages, f"Finished (reached end of pages or page {page} not found).")
                    break
                    
                soup = BeautifulSoup(response.text, 'lxml')
                listings = soup.select('article.product_pod')
                
                if not listings:
                    break
                    
                page_results_count = 0
                for item in listings:
                    parsed = self.parse_listing(item)
                    if parsed:
                        results.append(parsed)
                        page_results_count += 1
                
                if progress_callback:
                    progress_callback(page, max_pages, f"Page {page} completed. Extracted {page_results_count} books.")
                
                # Polite short delay
                time.sleep(0.5)
                    
            except Exception as e:
                if progress_callback:
                    progress_callback(page, max_pages, f"Network error on page {page}: {str(e)}")
                break
                
        return results

# Self-test block
if __name__ == "__main__":
    print("Testing Books to Scrape Scraper...")
    scraper = ECommerceScraper()
    print("Scraping page 1...")
    
    def log_progress(page, max_pages, msg):
        print(f"[{page}/{max_pages}] {msg}")
        
    data = scraper.scrape_query(max_pages=1, progress_callback=log_progress)
    print(f"\nExtracted {len(data)} books successfully!")
    if data:
        print("First book parsed sample:")
        for k, v in data[0].items():
            print(f"  {k}: {v}")
