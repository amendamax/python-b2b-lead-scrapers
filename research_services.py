import subprocess

def run_ps(cmd):
    try:
        out = subprocess.check_output(f'powershell -Command "{cmd}"', shell=True)
        return out.decode('utf-8', errors='ignore')
    except Exception as e:
        return str(e)

print("--- Services ---")
print(run_ps("Get-Service | Where-Object { $_.Name -match 'Xbox|Gaming|Acrobat|Adobe|Daemon|DiscSoft|DTLite' -or $_.DisplayName -match 'Xbox|Gaming|Acrobat|Adobe|Daemon' } | Select-Object Name, DisplayName, Status, StartType | Format-Table -AutoSize"))

print("--- Startup Items ---")
print(run_ps("Get-CimInstance Win32_StartupCommand | Select-Object Name, command, Location | Format-Table -AutoSize"))

