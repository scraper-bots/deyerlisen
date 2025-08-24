#!/usr/bin/env python3
from mitmproxy import ctx, http
import os, time, hashlib, pathlib, json

OUTDIR = "captures"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)

class CaptureSearchData:
    def response(self, flow: http.HTTPFlow):
        req = flow.request
        url = req.pretty_url.lower()
        
        # Capture anything that looks like search/place data
        should_capture = False
        file_prefix = ""
        
        # Look for actual search APIs
        if any(keyword in url for keyword in [
            'search', 'place', 'nearby', 'poi', 'business', 'venue',
            'query', 'autocomplete', 'suggest', 'geocode', 'details'
        ]):
            should_capture = True
            file_prefix = "search"
        
        # Google APIs that might have place data
        elif any(pattern in url for pattern in [
            'googleapis.com', 'maps.google', 'places.google',
            '/rpc/', '/api/place', '/api/search', 'textsearch'
        ]):
            should_capture = True
            file_prefix = "google_api"
        
        # Any JSON response with substantial content
        elif ('json' in flow.response.headers.get('content-type', '') and 
              len(flow.response.content) > 100):
            should_capture = True
            file_prefix = "json_data"
        
        # Protobuf responses that might have place data
        elif ('protobuf' in flow.response.headers.get('content-type', '') or
              'application/x-protobuf' in flow.response.headers.get('content-type', '')):
            should_capture = True
            file_prefix = "protobuf"
        
        if should_capture:
            h = hashlib.sha1(req.pretty_url.encode()).hexdigest()[:10]
            ts = int(time.time()*1000)
            
            # Determine file extension
            content_type = flow.response.headers.get("content-type", "")
            if "json" in content_type:
                ext = "json"
            elif "protobuf" in content_type:
                ext = "pbf"
            else:
                ext = "data"
            
            fname = f"{file_prefix}_{ts}_{h}.{ext}"
            outpath = os.path.join(OUTDIR, fname)
            
            # Save response data
            try:
                data = flow.response.raw_content
            except Exception:
                data = flow.response.content
            
            with open(outpath, "wb") as f:
                f.write(data)
            
            # Save metadata with URL and headers
            meta = outpath + ".meta.txt"
            with open(meta, "w", encoding="utf8") as mf:
                mf.write(f"URL: {req.pretty_url}\n")
                mf.write(f"Method: {req.method}\n")
                mf.write(f"Status: {flow.response.status_code}\n")
                mf.write(f"Content-Type: {flow.response.headers.get('content-type', 'unknown')}\n")
                mf.write(f"Content-Length: {len(data)}\n\n")
                
                # Include request body if it's a POST
                if req.method == "POST" and req.content:
                    mf.write("Request Body:\n")
                    try:
                        body_text = req.content.decode('utf-8')
                        mf.write(f"{body_text}\n\n")
                    except:
                        mf.write(f"[Binary data: {len(req.content)} bytes]\n\n")
                
                mf.write("Request Headers:\n")
                for k, v in req.headers.items():
                    mf.write(f"{k}: {v}\n")
                mf.write("\nResponse Headers:\n")
                for k, v in flow.response.headers.items():
                    mf.write(f"{k}: {v}\n")
            
            ctx.log.info(f"Captured: {req.pretty_url} -> {outpath}")

addons = [CaptureSearchData()]