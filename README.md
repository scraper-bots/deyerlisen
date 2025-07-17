# 📱📊 Mobile Investment App Data Extraction via Traffic Interception

This project demonstrates a complete pipeline to extract financial and company data from a mobile investment application by intercepting mobile network traffic using `mitmproxy`. It is designed for experienced data analysts and scraping professionals who need access to structured data when no public API or web interface is available.

---

## 🔍 Purpose

Many financial and investment apps contain high‑value data—including company profiles, analyst ratings, stock fundamentals, and ETF holdings—but do not offer public APIs. This project outlines how to:

- Intercept mobile app HTTPS traffic
- Identify and reverse‑engineer hidden API endpoints
- Extract structured JSON data
- Automate and export data to CSV/JSON via Python

---

## ⚠️ Disclaimer

> This project is intended for **educational and personal use only**. Scraping or intercepting data from third‑party apps may violate their [Terms of Service](#) and local laws. Always obtain permission before using this technique for commercial or production purposes.

---

## 🧰 Tools & Technologies

| Tool                          | Purpose                                  |
|-------------------------------|------------------------------------------|
| [mitmproxy](https://mitmproxy.org/) | HTTPS traffic interception proxy       |
| Python                        | Data extraction and automation           |
| pandas                        | Data framing and CSV/JSON export         |
| Android Studio + Emulator     | Proxy target and pinning bypass          |
| Frida / Objection             | Certificate‑pinning bypass               |
| Wi‑Fi                         | Local network proxying                   |

---

## 📦 Project Structure

```bash
mobile-investment-data/
│
├── README.md
├── extract.py                # Python script to automate API calls
├── unpin.js                  # Frida script to bypass SSL pinning
├── patched-app.apk           # (Optional) Objection‑patched APK
├── sample_capture.har        # Example export from mitmweb
└── data/
    ├── companies.csv         # Exported CSV data
    └── data.json            # Raw JSON export
````

---

## ✅ Step‑by‑Step Guide

### 1. Install mitmproxy

```bash
# macOS (Homebrew)
brew install mitmproxy

# Ubuntu/Debian
sudo apt update && sudo apt install mitmproxy

# Windows
Download and install from https://mitmproxy.org/
```

### 2. Configure mitmproxy

```bash
mitmproxy \
  --set ssl_insecure=true \
  --set tls_version_client_min=SSL3 \
  --set tls_version_server_min=SSL3
```

* `ssl_insecure=true` disables upstream certificate validation.
* `tls_version_*_min=SSL3` allows TLS1.0–TLS1.3.

---

### 3. Android Emulator Setup & Pinning Bypass

#### A. Create & Configure Android AVD

1. **Install Android Studio** and open AVD Manager.
2. **Create** a new emulator (e.g., Pixel 4, Android 11).
3. **Launch** the emulator and connect it to the same Wi‑Fi network.

#### B. Proxy the Emulator

1. In emulator: **Settings > Network & Internet > Wi‑Fi**
2. Tap your network, **Modify** → **Advanced options** → **Proxy** → **Manual**

   * **Proxy hostname**: your host PC’s IP (e.g., `10.10.10.223`)
   * **Proxy port**: `8080`

#### C. Install mitmproxy CA into Emulator

```bash
adb root
adb remount
adb push ~/.mitmproxy/mitmproxy-ca-cert.cer /sdcard/
```

On the emulator:

* **Settings > Security > Install from SD card** → select `mitmproxy-ca-cert.cer`
* Trust it under **Wi‑Fi / VPN & apps**.

#### D. Bypass Certificate Pinning

##### Option 1: Objection (No Root Required)

```bash
objection patchapk --source path/to/YourApp.apk \
  --preserve-signature --remove-definitions android.ssl_pinning
adb install -r patched-app.apk
```

##### Option 2: Frida (Live Hooking)

Create `unpin.js`:

```js
Java.perform(function() {
  var TrustManager = Java.use('javax.net.ssl.X509TrustManager');
  var SSLContext = Java.use('javax.net.ssl.SSLContext');

  var TrustAll = Java.registerClass({
    name: 'com.proxy.TrustAll',
    implements: [ TrustManager ],
    methods: {
      checkClientTrusted: function(chain, authType) {},
      checkServerTrusted: function(chain, authType) {},
      getAcceptedIssuers: function(){ return []; }
    }
  });

  SSLContext.init.overload(
    '[Ljavax.net.ssl.KeyManager;',
    '[Ljavax.net.ssl.TrustManager;',
    'java.security.SecureRandom'
  ).implementation = function(km, tm, sr) {
    return this.init(km, [TrustAll.$new()], sr);
  };
});
```

Run:

```bash
frida -U -f com.your.app.package -l unpin.js --no-pause
```

---

### 4. Capture & Inspect Traffic

1. **Run mitmproxy** (or use `mitmweb --web-open-browser` at `http://localhost:8081`).
2. **Launch** the patched or hooked app in emulator.
3. **Filter** flows by keywords in mitmweb, e.g.:

   ```
   ~u invest
   ~u portfolio
   ~u companies
   ```
4. **Select** a representative `200` JSON flow and **Export** as cURL or HAR.

---

### 5. Build & Run `extract.py`

Below is a skeleton; customize with your captured details:

```python
import requests, time, json
import pandas as pd

BASE_URL = 'https://api.appname.com/v1/companies'
HEADERS = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'User-Agent': 'AppName/1.0 (Android 11)'
}

all_items, page = [], 1
while True:
    params = {'page': page, 'limit': 50}
    r = requests.get(BASE_URL, headers=HEADERS, params=params)
    if r.status_code != 200:
        break
    items = r.json().get('results', [])
    if not items:
        break
    all_items.extend(items)
    print(f'Page {page}: {len(items)} items')
    page += 1
    time.sleep(0.5)

with open('data.json', 'w') as f:
    json.dump(all_items, f, indent=2)
pd.DataFrame(all_items).to_csv('data/companies.csv', index=False)
print(f'Exported {len(all_items)} records')
```

#### Run:

```bash
pip install requests pandas
python extract.py
```

---

## 📌 Best Practices

* **Respect rate limits**: add delays, monitor status codes.
* **Rotate tokens/IPs** if scraping at scale.
* **Secure credentials**: don’t commit tokens to public repos.
* **Document endpoints**: keep request/response examples for future reference.