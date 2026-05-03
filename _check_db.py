import sqlite3, json

db_path = r'D:\ai-carbon-system\backend\app\carbon.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', cur.fetchall())

# Companies
cur.execute('SELECT * FROM companies')
companies = cur.fetchall()
cur.execute('PRAGMA table_info(companies)')
cols = [c[1] for c in cur.fetchall()]
print(f'\nCompanies ({len(companies)} rows):')
for row in companies:
    print(' ', dict(zip(cols, row)))

# Carbon records
cur.execute('SELECT * FROM carbon_records')
records = cur.fetchall()
cur.execute('PRAGMA table_info(carbon_records)')
cols = [c[1] for c in cur.fetchall()]
print(f'\nCarbon records ({len(records)} rows):')
for row in records:
    print(' ', dict(zip(cols, row)))
