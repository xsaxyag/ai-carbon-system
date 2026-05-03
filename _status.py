import urllib.request, json

# Get companies list
req = urllib.request.Request('http://127.0.0.1:8000/api/v1/carbon/company/')
r = urllib.request.urlopen(req, timeout=5)
companies = json.loads(r.read())
if isinstance(companies, dict):
    companies = companies.get('data', [])
print('Companies total:', len(companies))
for c in companies[:5]:
    print(f'  id={c["id"]} | {c["name"]} | industry={c.get("industry","")}')

# Get records for company 1
req2 = urllib.request.Request('http://127.0.0.1:8000/api/v1/carbon/records/?company_id=1&skip=0&limit=10')
r2 = urllib.request.urlopen(req2, timeout=5)
data2 = json.loads(r2.read())
records = data2.get('data', []) if isinstance(data2, dict) else data2
print('\nRecords for company 1:', len(records))
for rec in records[:5]:
    print(f'  {rec.get("record_date")} | scope{rec.get("scope")} | {rec.get("emission_source")} | {rec.get("co2_emission")}kg')

# Summary for company 1
req3 = urllib.request.Request('http://127.0.0.1:8000/api/v1/carbon/summary/1/')
r3 = urllib.request.urlopen(req3, timeout=5)
data3 = json.loads(r3.read())
print('\nSummary company 1:')
for key, val in data3.items():
    print(f'  {key}: {val}')
