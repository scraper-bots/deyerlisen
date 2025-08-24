# save_vt_proto.py
from mitmproxy import ctx, http
import os, time, hashlib, pathlib

OUTDIR = "captures"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)

class SaveVTProto:
    def response(self, flow: http.HTTPFlow):
        req = flow.request
        should_capture = False
        file_prefix = ""
        
        # Capture various Google Maps API endpoints
        if "/maps/vt/proto" in req.pretty_url:
            should_capture = True
            file_prefix = "vt"
        elif "/maps/api/" in req.pretty_url:
            should_capture = True
            file_prefix = "api"
        elif "/search" in req.pretty_url and "maps" in req.pretty_host:
            should_capture = True
            file_prefix = "search"
        elif "/place" in req.pretty_url:
            should_capture = True
            file_prefix = "place"
        elif "/nearby" in req.pretty_url:
            should_capture = True
            file_prefix = "nearby"
        elif "/json" in req.pretty_url and ("place" in req.pretty_url or "search" in req.pretty_url):
            should_capture = True
            file_prefix = "json"
        
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

addons = [SaveVTProto()]
