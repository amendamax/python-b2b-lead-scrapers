import os
import shutil

source_dir = r"D:\FDM"
dest_dir = r"G:\1_Cursuri_si_Educatie\CARTI"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

files_to_move = [
    r"D:\FDM\Indicators and Ebooks\FOREX_TRADING_The_Basics_Explained_in_Simple_Terms_by_Jim_Brown.pdf",
    r"D:\FDM\Indicators and Ebooks\Three Lines Forecasting Forex Price Action by Rana, R.pdf",
    r"D:\FDM\Indicators and Ebooks\Trading_Price_Action_Trading_Ranges_Technical_Analysis_of_Price.pdf",
    r"D:\FDM\dokumen.pub_web-scraping-with-python-data-extraction-from-the-modern-web-3rd-edition-3nbsped-9781098145354.epub",
    r"D:\FDM\head-first-design-patterns-eric-freeman.pdf",
    r"D:\FDM\OceanofPDF.compractical_python_for_effective_algorithmic_trading_-_Kuldeep_Singh_Rathore.epub",
    r"D:\FDM\OceanofPDF.comPython_for_Algorithmic_Trading_-_Yves_Hilpisch.epub",
    r"D:\FDM\OceanofPDF.comPython_for_Algorithmic_Trading_Cookbook_-_Jason_Strimpel.epub",
    r"D:\FDM\python-for-dummies-aahz-maruch.pdf"
]

moved = 0
for f in files_to_move:
    if os.path.exists(f):
        filename = os.path.basename(f)
        dest = os.path.join(dest_dir, filename)
        try:
            shutil.move(f, dest)
            print(f"Mutat: {filename}")
            moved += 1
        except Exception as e:
            print(f"Eroare mutare {filename}: {e}")

print(f"\nAu fost salvate {moved} carti/e-book-uri in biblioteca principala.")
