import sqlite3, shutil

DB = r'D:\ai-carbon-system\backend\carbon.db'
BACKUP = r'D:\ai-carbon-system\backend\carbon.db.backup'

shutil.copy2(DB, BACKUP)
print('[1] Backup:', BACKUP)

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Read all records before deletion
cur.execute('SELECT id, scope, emission_source, quantity, unit, co2_emission FROM carbon_records ORDER BY id')
rows = cur.fetchall()
print('[2] Current records (%d):' % len(rows))
for r in rows:
    print('  [%d] %s %s qty=%.1f %s -> %.3f kgCO2' % (r[0], r[1], r[2], r[3], r[4], r[5]))

# Delete records 5, 6, 7 (test duplicates: 435 L/kWh/GJ - same emission = wrong units)
cur.execute('DELETE FROM carbon_records WHERE id IN (5, 6, 7)')
conn.commit()
print('[3] Deleted records 5/6/7, rows affected:', cur.rowcount)

# Re-check remaining
cur.execute('SELECT id, scope, emission_source, quantity, unit, co2_emission FROM carbon_records ORDER BY id')
rows2 = cur.fetchall()
print('[4] Remaining records (%d):' % len(rows2))
s1 = s2 = s3 = 0
for r in rows2:
    print('  [%d] %s %s qty=%.1f %s -> %.3f kgCO2' % (r[0], r[1], r[2], r[3], r[4], r[5]))
    if r[1] == 'scope1': s1 += r[5]
    elif r[1] == 'scope2': s2 += r[5]
    elif r[1] == 'scope3': s3 += r[5]
print('     Totals: scope1=%.3f scope2=%.3f scope3=%.3f total=%.3f kgCO2' % (s1, s2, s3, s1+s2+s3))

conn.close()
print('[OK] Database cleanup done!')
