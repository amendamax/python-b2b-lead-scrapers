import undetected_chromedriver as uc
import time

def test_bypass():
    options = uc.ChromeOptions()
    options.add_argument('--headless')  # Incercam headless mai intai, dar uc functioneaza si mai bine headful
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    print("[*] Initializez Undetected Chromedriver...")
    try:
        driver = uc.Chrome(options=options)
        print("[*] Navighez la Upwork...")
        driver.get('https://www.upwork.com/nx/search/jobs/?q=data+scraping&sort=recency')
        
        time.sleep(10)  # Asteptam sa treaca de eventualele provocari
        
        print("Page Title:", driver.title)
        print("Page Source Length:", len(driver.page_source))
        
        if "Challenge" in driver.title or "Just a moment" in driver.title:
            print("[-] Blocat de Cloudflare.")
        else:
            print("[+] Am trecut cu succes! Pagina este incarcata.")
            
        driver.quit()
    except Exception as e:
        print("[-] Eroare:", e)

if __name__ == "__main__":
    test_bypass()
