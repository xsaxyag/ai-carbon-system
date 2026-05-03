import sqlite3
import shutil

DB = r'D:\ai-carbon-system\backend\carbon.db'
BACKUP = r'D:\ai-carbon-system\backend\carbon.db.backup'

# Step 1: backup
shutil.copy2(DB, BACKUP)
print('[OK] Backup:', BACKUP)

# Step 2: read raw bytes from company row
conn_src = sqlite3.connect(DB)
conn_src.row_factory = sqlite3.Row
cur = conn_src.cursor()
cur.execute('SELECT * FROM companies WHERE id=1')
row = cur.fetchone()
print('[INFO] name bytes hex:', bytes(row['name'], 'latin1').hex())
print('[INFO] industry bytes hex:', bytes(row['industry'], 'latin1').hex())

# Step 3: GBK decode
def latin1_to_gbk(b):
    return bytes(b, 'latin1').decode('gbk')

company_name = latin1_to_gbk(bytes(row['name'], 'latin1'))
company_industry = latin1_to_gbk(bytes(row['industry'], 'latin1'))
company_region = latin1_to_gbk(bytes(row['region'], 'latin1'))
print('[OK] Company:', company_name)
print('[OK] Industry:', company_industry)

# Step 4: fix encoding - re-write as proper UTF-8
conn_write = sqlite3.connect(DB)
cw = conn_write.cursor()
cw.execute("UPDATE companies SET name=?, industry=?, region=? WHERE id=1",
           (company_name, company_industry, company_region))
conn_write.commit()
print('[OK] Fixed company name/industry/region encoding')

# Step 5: delete duplicate test records (435 kWh/L/GJ confusion)
cw.execute('DELETE FROM carbon_records WHERE id IN (5, 6, 7)')
conn_write.commit()
print('[OK] Deleted duplicate records (id 5,6,7), rows affected:', cw.rowcount)

# Step 6: verify
print('\n--- Company ---')
cw.execute('SELECT id, name, industry FROM companies WHERE id=1')
r = cw.fetchone()
print(' id=%s name=%s industry=%s' % (r[0], r[1], r[2]))

print('\n--- Carbon Records ---')
cw.execute('SELECT id, scope, emission_source, quantity, unit, co2_emission FROM carbon_records ORDER BY id')
rows = cw.fetchall()
print(' Total %d records:' % len(rows))
for r in rows:
    print('  [%d] %s %s qty=%s %s -> %.3f kgCO2' % (r[0], r[1], r[2], r[3], r[4], r[5]))

conn_write.close()
conn_src.close()
print('\n[OK] All done!')
