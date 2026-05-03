import requests, json

BASE = 'http://127.0.0.1:8000/api/v1'

# Login
r = requests.post(f'{BASE}/auth/login', json={'username': 'admin', 'password': 'admin456'})
if r.status_code != 200:
    print(f"Login failed: {r.status_code} {r.text}")
    exit(1)
token = r.json()['data']['access_token']
h = {'Authorization': f'Bearer {token}'}

# 1. Create backup
print("=== Create Backup ===")
r = requests.post(f'{BASE}/backup/create?note=continuation-test', headers=h)
print(r.status_code, json.dumps(r.json(), ensure_ascii=False, indent=2))

# 2. List backups
print("\n=== List Backups ===")
r = requests.get(f'{BASE}/backup/list', headers=h)
data = r.json()
print(r.status_code, f"count={data['count']}")
for b in data['data']:
    print(f"  {b['filename']} ({b['size_mb']}MB)")

# 3. DB Stats
print("\n=== DB Stats ===")
r = requests.get(f'{BASE}/backup/stats', headers=h)
print(r.status_code, json.dumps(r.json(), ensure_ascii=False, indent=2))

# 4. Export
print("\n=== Export JSON ===")
r = requests.get(f'{BASE}/backup/export', headers=h)
export = r.json()
for table, info in export.get('tables', {}).items():
    print(f"  {table}: {info['count']} rows")

print("\nBackup API OK!")