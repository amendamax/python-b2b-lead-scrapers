import difflib
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

file1_path = r"C:\Users\bratu\Desktop\New folder\AUR_FTMO\live_exec.py"
file2_path = r"C:\Users\bratu\Desktop\New folder\XAUUSD\live_exec.py"

with open(file1_path, 'r', encoding='utf-8', errors='replace') as f1:
    lines1 = f1.readlines()

with open(file2_path, 'r', encoding='utf-8', errors='replace') as f2:
    lines2 = f2.readlines()

diff = difflib.unified_diff(
    lines1, lines2,
    fromfile="AUR_FTMO/live_exec.py",
    tofile="XAUUSD/live_exec.py",
    n=3
)

print("Unified diff between the two live_exec.py scripts:")
print("==================================================")
sys.stdout.writelines(diff)
