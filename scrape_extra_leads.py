from global_lead_generator import GlobalB2BLeadGenerator
import os
import shutil

def main():
    generator = GlobalB2BLeadGenerator()
    targets = [
        {"niche": "webagency", "country": "romania", "city": "Timisoara", "count": 5},
        {"niche": "webagency", "country": "romania", "city": "Iasi", "count": 5},
        {"niche": "webagency", "country": "uk", "city": "Manchester", "count": 5},
        {"niche": "webagency", "country": "usa", "city": "Miami", "count": 5}
    ]

    for t in targets:
        print(f"\n=======================================================")
        print(f"🚀 SCRAPING: {t['niche'].upper()} in {t['city'].upper()}, {t['country'].upper()}")
        print(f"=======================================================")
        try:
            leads = generator.run_lead_gen(t["niche"], t["country"], t["city"], t["count"])
            if not leads:
                print(f"No leads found for {t['city']}.")
                continue
                
            filename = f"leads_{t['niche']}_{t['city'].lower()}.xlsx"
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            theme = "emerald" if t["niche"] in ["imobiliare", "real estate"] else "gold"
            generator.format_excel_report(leads, output_path, theme)
            
            # Copy to Desktop/Outreach_B2B
            desktop_filename = f"PROSPECTE_{t['niche'].upper()}_{t['city'].upper()}.xlsx"
            outreach_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Outreach_B2B")
            os.makedirs(outreach_dir, exist_ok=True)
            desktop_path = os.path.join(outreach_dir, desktop_filename)
            shutil.copy(output_path, desktop_path)
            print(f"Successfully saved and copied to Desktop/Outreach_B2B/{desktop_filename}")
        except Exception as e:
            print(f"Error scraping {t['city']}: {e}")

if __name__ == "__main__":
    main()
