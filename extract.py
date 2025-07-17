import requests
import time
import json
import pandas as pd

# --- Configuration (fill in from your mitmproxy capture) ---
BASE_URL = 'https://api.appname.com/v1/companies'
HEADERS = {
    'Authorization': 'Bearer YOUR_TOKEN_HERE',
    'User-Agent': 'AppName/1.0.0 (iOS 18.6; iPhone)',
    # any additional headers (e.g. Accept-Language, x-app-version)…
}

# --- Pagination & Data Collection ---
all_items = []
page = 1
while True:
    params = {'page': page, 'limit': 50}  # adjust keys per your API
    resp = requests.get(BASE_URL, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print(f'Stopping: received {resp.status_code} on page {page}')
        break
    data = resp.json()
    items = data.get('results') or data.get('companies') or []
    if not items:
        break
    all_items.extend(items)
    print(f'Page {page}: fetched {len(items)} items')
    page += 1
    time.sleep(0.5)  # be kind to their servers

# --- Save to disk ---
with open('data.json', 'w') as f:
    json.dump(all_items, f, indent=2)

df = pd.DataFrame(all_items)
df.to_csv('data.csv', index=False)
print(f'Exported {len(all_items)} records to data.csv')
