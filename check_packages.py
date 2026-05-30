import sys

print("Python version:", sys.version)
for pkg in ['playwright', 'selenium', 'requests', 'bs4', 'openpyxl', 'pandas', 'pywin32']:
    try:
        __import__(pkg)
        print(f"  {pkg}: installed")
    except ImportError:
        print(f"  {pkg}: NOT installed")
