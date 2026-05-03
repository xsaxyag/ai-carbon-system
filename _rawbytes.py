import sqlite3

DB = r'D:\ai-carbon-system\backend\carbon.db'
conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b  # return raw bytes
cur = conn.cursor()
cur.execute('SELECT name FROM companies WHERE id=1')
row = cur.fetchone()
raw = row[0]
print('raw type:', type(raw))
print('raw bytes:', raw[:40])
print('hex:', raw[:40].hex())

# Try various decodings on the raw bytes
for enc in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']:
    try:
        decoded = raw.decode(enc)
        print('Decoded as %s: %s' % (enc, decoded))
    except Exception as e:
        print('Decoded as %s: FAIL - %s' % (enc, e))
conn.close()
