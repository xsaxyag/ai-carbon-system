import sqlite3

db = r'D:\ai-carbon-system\backend\carbon.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', [r[0] for r in cur.fetchall()])

# Companies
cur.execute('SELECT * FROM companies')
companies = cur.fetchall()
cur.execute('PRAGMA table_info(companies)')
cols = [c[1] for c in cur.fetchall()]
print(f'\nCompanies ({len(companies)}):')
for row in companies:
    print(' ', dict(zip(cols, row)))

# Carbon records
cur.execute('SELECT * FROM carbon_records ORDER BY id')
records = cur.fetchall()
cur.execute('PRAGMA table_info(carbon_records)')
cols = [c[1] for c in cur.fetchall()]
print(f'\nCarbon records ({len(records)}):')
for row in records:
    print(' ', dict(zip(cols, row)))
