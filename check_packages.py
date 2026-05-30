import sys

print("Python version:", sys.version)
packages = [
    'playwright', 'selenium', 'requests', 'bs4', 
    'openpyxl', 'pandas', 'pywin32', 'curl_cffi', 
    'gspread', 'oauth2client', 'lxml'
]
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  {pkg}: installed")
    except ImportError:
        print(f"  {pkg}: NOT installed")

