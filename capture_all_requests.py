#!/usr/bin/env python3
# capture_all_requests.py
from mitmproxy import ctx, http
import os, time, hashlib, pathlib, json

OUTDIR = "captures"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)

class CaptureAllRequests:
    def response(self, flow: http.HTTPFlow):
        req = flow.request
        
        # Log all requests to understand what the app is calling
        log_entry = {
            'timestamp': int(time.time() * 1000),
            'method': req.method,
            'url': req.pretty_url,
            'host': req.pretty_host,
            'path': req.path,
            'status_code': flow.response.status_code,
            'content_type': flow.response.headers.get('content-type', ''),
            'content_length': len(flow.response.content)
        }
        
        # Log to a JSON lines file
        with open(os.path.join(OUTDIR, 'all_requests.jsonl'), 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        # Capture interesting responses
        should_capture = False
        file_prefix = ""
        
        # Look for various potential data sources
        url_lower = req.pretty_url.lower()
        
        if any(keyword in url_lower for keyword in [
            'search', 'place', 'nearby', 'poi', 'business', 
            'venue', 'location', 'maps/api', 'geocode'
        ]):
            should_capture = True
            file_prefix = "api"
        elif 'json' in flow.response.headers.get('content-type', '').lower():
            should_capture = True  
            file_prefix = "json"
        elif req.pretty_host and 'google' in req.pretty_host and len(flow.response.content) > 100:
            should_capture = True
            file_prefix = "google"
        
        if should_capture:
            # create stable filename from URL + timestamp
            h = hashlib.sha1(req.pretty_url.encode()).hexdigest()[:10]
            ts = int(time.time()*1000)
            
            # Use different extensions based on content type
            content_type = flow.response.headers.get("content-type", "")
            if "json" in content_type:
                ext = "json"
            elif "protobuf" in content_type or "octet-stream" in content_type:
                ext = "pbf"
            else:
                ext = "data"
            
            fname = f"{file_prefix}_{ts}_{h}.{ext}"
            outpath = os.path.join(OUTDIR, fname)
            
            try:
                data = flow.response.raw_content
            except Exception:
                data = flow.response.content
            
            with open(outpath, "wb") as f:
                f.write(data)
            ctx.log.info(f"Saved {req.pretty_url} -> {outpath}")
            
            # also save a small metadata file with the URL and headers
            meta = outpath + ".meta.txt"
            with open(meta, "w", encoding="utf8") as mf:
                mf.write(f"URL: {req.pretty_url}\n\n")
                mf.write("Request headers:\n")
                for k,v in req.headers.items():
                    mf.write(f"{k}: {v}\n")
                mf.write("\nResponse headers:\n")
                for k,v in flow.response.headers.items():
                    mf.write(f"{k}: {v}\n")
            ctx.log.info(f"Wrote metadata -> {meta}")

addons = [CaptureAllRequests()]