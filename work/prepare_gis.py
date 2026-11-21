from pathlib import Path
import requests,json,time
W=Path(__file__).resolve().parent
s=requests.Session()
url='https://download.qgis.org/downloads/QGIS-OSGeo4W-3.44.15-2.msi'
target=W/'QGIS-OSGeo4W-3.44.15-2.msi'
if not target.exists():
    with s.get(url,stream=True,timeout=(30,120)) as r:
        r.raise_for_status(); print('Installer bytes:',r.headers.get('Content-Length'),flush=True)
        done=0;last=time.monotonic()
        with target.with_suffix('.partial').open('wb') as f:
            for b in r.iter_content(4*1024*1024):
                f.write(b);done+=len(b)
                if time.monotonic()-last>20:print('Downloaded MB:',round(done/1e6),flush=True);last=time.monotonic()
        target.with_suffix('.partial').rename(target)
print('Installer ready',target.stat().st_size,flush=True)
