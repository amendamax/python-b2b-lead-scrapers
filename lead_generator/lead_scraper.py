from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import time
import random

class B2BLeadScraper:
    """
    A professional, modular B2B Lead Scraper designed for Yellowpages.com.
    Uses curl_cffi to bypass browser TLS filters and parses clean business leads.
    """
    
    BASE_URL = "https://www.yellowpages.com"

    def __init__(self):
        self.session = requests.Session(impersonate="chrome")

    def parse_listing(self, item_element):
        """Parses a single Yellowpages search result into a structured lead dictionary."""
        # 1. Extract Business Name
        name_el = item_element.select_one('a.business-name')
        if not name_el:
            return None
        name = name_el.text.strip()
        
        # 2. Yellowpages Profile Link
        profile_url = urllib.parse.urljoin(self.BASE_URL, name_el['href']) if 'href' in name_el.attrs else ""
        
        # 3. Phone Number
        phone_el = item_element.select_one('.phone')
        phone = phone_el.text.strip() if phone_el else "N/A"
        
        # 4. Street Address & Locality
        street_el = item_element.select_one('.street-address')
        locality_el = item_element.select_one('.locality')
        street = street_el.text.strip() if street_el else ""
        locality = locality_el.text.strip() if locality_el else ""
        
        address = f"{street}, {locality}".strip(", ")
        if not address:
            address = "N/A"
            
        # 5. Rating & Reviews Count
        rating_el = item_element.select_one('.ratings .rating')
        rating = 0.0
        if rating_el:
            rating_classes = rating_el.get('class', [])
            for cls in rating_classes:
                if cls != 'rating':
                    # Parse classes like 'five', 'four-half', 'three'
                    cls_clean = cls.replace('-', '.')
                    # Map common rating word representations
                    mapping = {"one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0, 
                               "one.half": 1.5, "two.half": 2.5, "three.half": 3.5, "four.half": 4.5}
                    rating = mapping.get(cls_clean, 0.0)
                    break
        
        reviews_el = item_element.select_one('.ratings span')
        # Clean reviews text, e.g. "(12)" -> 12
        reviews = 0
        if reviews_el:
            reviews_text = re.sub(r'[^\d]', '', reviews_el.text)
            try:
                reviews = int(reviews_text) if reviews_text else 0
            except ValueError:
                pass
                
        # 6. Website URL
        website_el = item_element.select_one('.track-visit-website')
        website = website_el['href'] if website_el and 'href' in website_el.attrs else "N/A"
        
        return {
            "Business Name": name,
            "Phone": phone,
            "Address": address,
            "Rating (1-5)": rating,
            "Reviews Count": reviews,
            "Website": website,
            "Profile URL": profile_url
        }

    def scrape_leads(self, search_term, location, max_pages=1, progress_callback=None):
        """
        Scrapes multiple pages of local leads for a search term and location.
        Includes random delays and reports progress.
        """
        results = []
        encoded_term = urllib.parse.quote_plus(search_term)
        encoded_location = urllib.parse.quote_plus(location)
        
        for page in range(1, max_pages + 1):
            if progress_callback:
                progress_callback(page, max_pages, f"Fetching page {page} for '{search_term}' in '{location}'...")
            
            # Yellowpages URL pagination is ?page=X
            url = f"{self.BASE_URL}/search?search_terms={encoded_term}&geo_location_terms={encoded_location}&page={page}"
            
            try:
                response = self.session.get(url, timeout=15)
                if response.status_code != 200:
                    if progress_callback:
                        progress_callback(page, max_pages, f"Finished (or rate-limited). Status: {response.status_code}")
                    break
                    
                soup = BeautifulSoup(response.text, 'lxml')
                listings = soup.select('.search-results .result, .srp-list .result, .result')
                
                if not listings:
                    if progress_callback:
                        progress_callback(page, max_pages, "No listings found on this page.")
                    break
                    
                page_leads_count = 0
                for item in listings:
                    parsed = self.parse_listing(item)
                    if parsed:
                        results.append(parsed)
                        page_leads_count += 1
                
                if progress_callback:
                    progress_callback(page, max_pages, f"Page {page} completed. Extracted {page_leads_count} leads.")
                
                # Polite short delay
                if page < max_pages:
                    time.sleep(random.uniform(1.5, 3.0))
                    
            except Exception as e:
                if progress_callback:
                    progress_callback(page, max_pages, f"Error on page {page}: {str(e)}")
                break
                
        return results

# Self-test block
if __name__ == "__main__":
    print("Testing B2B Lead Scraper...")
    scraper = B2BLeadScraper()
    print("Scraping 1 page for 'dentist' in 'Boston, MA'...")
    
    def log_progress(page, max_pages, msg):
        print(f"[{page}/{max_pages}] {msg}")
        
    data = scraper.scrape_leads("dentist", "Boston, MA", max_pages=1, progress_callback=log_progress)
    print(f"\nExtracted {len(data)} leads successfully!")
    if data:
        print("First lead parsed sample:")
        for k, v in data[0].items():
            print(f"  {k}: {v}")
