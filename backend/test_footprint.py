import requests, json

BASE = 'http://127.0.0.1:8000/api/v1'
r = requests.post(f'{BASE}/auth/login', json={'username': 'admin', 'password': 'admin456'})
token = r.json()['data']['access_token']
h = {'Authorization': f'Bearer {token}'}

# 1. Stages
print("=== Stages ===")
r = requests.get(f'{BASE}/footprint/stages')
print(r.status_code, json.dumps(r.json(), ensure_ascii=False)[:200])

# 2. Create product
print("\n=== Create Product ===")
r = requests.post(f'{BASE}/footprint/products', json={
    'product_name': '智能电表A型',
    'product_code': 'SM-A001',
    'category': '电子产品',
    'functional_unit': '台',
    'lifespan_years': 5.0,
    'description': '生命周期5年'
}, headers=h)
print(r.status_code, r.text[:300])

if r.status_code != 200:
    print("Create failed, trying simpler payload...")
    r = requests.post(f'{BASE}/footprint/products', json={
        'product_name': '测试产品'
    }, headers=h)
    print(r.status_code, r.text[:300])

if r.status_code == 200:
    prod_a = r.json()['data']['id']
    print(f"Product created: {prod_a}")

    # 3. Add stage
    r = requests.post(f'{BASE}/footprint/products/{prod_a}/stages', json={
        'stage': 'production',
        'material_name': '电力消耗',
        'quantity': 15.0,
        'unit': 'kWh'
    }, headers=h)
    print(f"\nAdd stage: {r.status_code} {r.text[:150]}")

    # 4. Calculate
    r = requests.post(f'{BASE}/footprint/products/{prod_a}/calculate', headers=h)
    print(f"Calculate: {r.status_code}")
    if r.status_code == 200:
        data = r.json()['data']
        print(f"  Total: {data['total_emission_kgco2']} kgCO2")
        for st, info in data['stage_summary'].items():
            pct = data['stage_percentages'].get(st, 0)
            print(f"  {info['name']}: {info['emission']:.2f} kgCO2 ({pct}%)")

print("\nDone.")