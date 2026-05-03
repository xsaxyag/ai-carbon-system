import re, os
d = r'D:\ai-carbon-system\frontend\src\views'
for f in os.listdir(d):
    path = os.path.join(d, f)
    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
        content = fh.read()
    base_urls = re.findall(r'http[s]?://[^\s"\'`]+', content)
    print(f'=== {f} ===')
    for u in base_urls:
        print(f'  {u}')
    if not base_urls:
        print('  (no hardcoded URLs)')