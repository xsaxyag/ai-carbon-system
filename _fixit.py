import sqlite3

DB = r'D:\ai-carbon-system\backend\carbon.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute('SELECT name, industry, region FROM companies WHERE id=1')
row = cur.fetchone()

# Reverse interpretation: current wrong UTF-8 chars = GBK bytes interpreted as UTF-8
# So we re-encode as UTF-8 to get the original GBK bytes, then decode as GBK
def reverse_utf8_to_gbk(s):
    b = s.encode('utf-8')  # this gives us the bytes that Python THINKS are UTF-8 but are really GBK
    return b.decode('gbk')  # decode those bytes as GBK

name = reverse_utf8_to_gbk(row[0])
ind = reverse_utf8_to_gbk(row[1])
reg = reverse_utf8_to_gbk(row[2])

print('Fixed name:', name)
print('Fixed industry:', ind)
print('Fixed region:', reg)

# Update DB with correct UTF-8 values
cur.execute('UPDATE companies SET name=?, industry=?, region=? WHERE id=1',
           (name, ind, reg))
conn.commit()
print('DB updated OK')

# Delete duplicate records
cur.execute('DELETE FROM carbon_records WHERE id IN (5, 6, 7)')
conn.commit()
print('Deleted records 5/6/7 OK, rows affected:', cur.rowcount)

# Verify
cur.execute('SELECT name, industry FROM companies WHERE id=1')
r = cur.fetchone()
print('Verify name:', r[0])
print('Verify industry:', r[1])

cur.execute('SELECT id, scope, emission_source, quantity, unit, co2_emission FROM carbon_records ORDER BY id')
rows = cur.fetchall()
print('Carbon records:', len(rows))
s1 = s2 = s3 = 0
for r in rows:
    print('  [%d] %s %s qty=%.1f %s -> %.3f kgCO2' % (r[0], r[1], r[2], r[3], r[4], r[5]))
    if r[1]=='scope1': s1+=r[5]
    elif r[1]=='scope2': s2+=r[5]
    elif r[1]=='scope3': s3+=r[5]
print('  Totals: scope1=%.3f scope2=%.3f scope3=%.3f' % (s1, s2, s3))

conn.close()
print('DONE')
