import csv
import requests
from bs4 import BeautifulSoup
import time

def scrape_books():
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    output_file = "scraped_books.csv"
    
    # CSV Header
    fields = ["Title", "Price", "Availability", "Rating", "Product URL"]
    
    print("🚀 Starting Open-Source Web Scraper Demo...")
    print(f"📁 Results will be saved to: {output_file}\n")
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        
        page = 1
        while True:
            url = base_url.format(page)
            print(f"🔍 Crawling page {page}: {url}")
            
            response = requests.get(url)
            if response.status_code != 200:
                print("🏁 No more pages found or rate-limit encountered. Stopping.")
                break
                
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all("article", class="product_pod")
            
            if not articles:
                break
                
            for article in articles:
                title = article.h3.a["title"]
                price = article.find("p", class="price_color").text
                availability = article.find("p", class="instock availability").text.strip()
                
                # Extract rating from class name (e.g. "star-rating Three")
                rating_classes = article.find("p", class="star-rating")["class"]
                rating = [c for c in rating_classes if c != "star-rating"][0]
                
                product_path = article.h3.a["href"]
                product_url = f"http://books.toscrape.com/catalogue/{product_path}"
                
                writer.writerow({
                    "Title": title,
                    "Price": price,
                    "Availability": availability,
                    "Rating": rating,
                    "Product URL": product_url
                })
                
            print(f"✅ Extracted {len(articles)} items from page {page}")
            page += 1
            time.sleep(1) # Polite crawler delay
            
    print(f"\n🎉 Scraping completed successfully! Output saved in '{output_file}'")

if __name__ == "__main__":
    scrape_books()
