import sqlite3

def check(db, name):
    try:
        c = sqlite3.connect(db).cursor()
        tables = [t[0] for t in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f'{name} tables: {tables}')
        for table in tables:
            count = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {count} rows")
    except Exception as e:
        print(f'{name} error: {e}')

check('dating-photo-checker/database.db', 'VerifyDating')
check('job-scam-radar/database.db', 'JobScamRadar')
check('pill-scam-radar/database.db', 'PillScam/IsBroker')
