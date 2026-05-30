import win32com.client
import os
import sys

def convert_excel_to_pdf(xlsx_path, pdf_path):
    """
    Converts a styled Excel sheet into a perfect landscape PDF using
    Microsoft Excel's native COM engine. Ensures all columns are scaled to fit
    neatly on a single page, keeping the chart and data perfectly composed.
    """
    abs_xlsx = os.path.abspath(xlsx_path)
    abs_pdf = os.path.abspath(pdf_path)
    
    if not os.path.exists(abs_xlsx):
        print(f"[!] Error: Source file not found: {abs_xlsx}")
        sys.exit(1)
        
    print(f"[>] Connecting to Excel Engine and opening: {os.path.basename(abs_xlsx)}")
    
    excel = None
    wb = None
    try:
        # Initialize the Excel COM Application
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        
        # Open workbook (ReadOnly=True prevents sharing violations if the user has it open!)
        wb = excel.Workbooks.Open(abs_xlsx, ReadOnly=True)
        ws = wb.ActiveSheet
        
        print("[>] Configuring page setup (Landscape, Narrow Margins, Fit to 1 Page Width)...")
        # Page Setup Configurations
        ws.PageSetup.Orientation = 2 # 2 = Landscape (1 = Portrait)
        
        # Fit to Page scaling rules
        ws.PageSetup.Zoom = False
        ws.PageSetup.FitToPagesWide = 1 # Force all columns to fit on 1 page wide
        ws.PageSetup.FitToPagesTall = 1 # Force all rows/charts to fit on 1 page tall if possible
        
        # Set professional narrow margins (0.5 inches = 36 points)
        ws.PageSetup.LeftMargin = 36
        ws.PageSetup.RightMargin = 36
        ws.PageSetup.TopMargin = 36
        ws.PageSetup.BottomMargin = 36
        
        # Center horizontally
        ws.PageSetup.CenterHorizontally = True
        
        print("[>] Printing sheet to PDF vector format...")
        # 0 = xlTypePDF
        ws.ExportAsFixedFormat(0, abs_pdf)
        print(f"[+] SUCCESS: Perfect PDF generated successfully!")
        print(f"    File Path: {abs_pdf}")
        
    except Exception as e:
        print(f"[!] COM Error: {str(e)}")
        sys.exit(1)
    finally:
        # Clean shutdown of Excel COM objects (prevents ghost excel.exe processes in Task Manager)
        if wb:
            wb.Close(SaveChanges=False)
        if excel:
            excel.Quit()

if __name__ == "__main__":
    xlsx_file = "amazon_laptops_report.xlsx"
    pdf_file = "amazon_laptops_report.pdf"
    convert_excel_to_pdf(xlsx_file, pdf_file)
