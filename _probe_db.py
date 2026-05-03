import sqlite3, shutil

DB = r'D:\ai-carbon-system\backend\carbon.db'
BACKUP = r'D:\ai-carbon-system\backend\carbon.db.backup'

# Step 1: backup
shutil.copy2(DB, BACKUP)
print('[1/5] Backup done:', BACKUP)

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Step 2: read current raw values
cur.execute('SELECT id, name, industry, region FROM companies WHERE id=1')
row = cur.fetchone()
print('[2/5] Current name repr:', repr(row[1]))

# Step 3: re-encode as latin-1 to get bytes back, then decode as GBK
def fix_encoding(s):
    b = s.encode('latin-1')  # reverse what sqlite3 did
    return b.decode('gbk')    # the real encoding

name_fixed = fix_encoding(row[1])
ind_fixed = fix_encoding(row[2])
reg_fixed = fix_encoding(row[3])
print('[3/5] Fixed name:', name_fixed)
print('     Fixed industry:', ind_fixed)
print('     Fixed region:', reg_fixed)

# Step 4: update
cur.execute('UPDATE companies SET name=?, industry=?, region=? WHERE id=1',
           (name_fixed, ind_fixed, reg_fixed))
conn.commit()
print('[4/5] DB encoding fixed and updated')

# Step 5: delete duplicates
cur.execute('DELETE FROM carbon_records WHERE id IN (5, 6, 7)')
conn.commit()
print('[5/5] Deleted duplicate records 5/6/7')

# Verify
cur.execute('SELECT id, name, industry FROM companies WHERE id=1')
r = cur.fetchone()
print('\n=== VERIFY ===')
print('Company: id=%d name=%s industry=%s' % (r[0], r[1], r[2]))

cur.execute('SELECT id, scope, emission_source, quantity, unit, co2_emission FROM carbon_records ORDER BY id')
rows = cur.fetchall()
print('\nCarbon records (%d):' % len(rows))
total_s1 = total_s2 = total_s3 = 0
for r2 in rows:
    print('  [%d] %-8s %-12s qty=%s %s -> %.3f kgCO2' % (r2[0], r2[1], r2[2], r2[3], r2[4], r2[5]))
    if r2[1] == 'scope1': total_s1 += r2[5]
    elif r2[1] == 'scope2': total_s2 += r2[5]
    elif r2[1] == 'scope3': total_s3 += r2[5]
print('  TOTAL: scope1=%.3f scope2=%.3f scope3=%.3f' % (total_s1, total_s2, total_s3))

conn.close()
print('\n[OK] All done!')
