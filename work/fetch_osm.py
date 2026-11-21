import requests
from pathlib import Path
q='''[out:xml][timeout:90];(way["highway"]["name"="Sheppard Avenue West"](43.735,-79.48,43.78,-79.40);nwr["railway"="station"]["name"~"Sheppard"](43.735,-79.48,43.78,-79.40););out body;>;out skel qt;'''
Path('work/sheppard_overpass_query.txt').write_text(q)
for url in ['https://overpass.kumi.systems/api/interpreter','https://overpass-api.de/api/interpreter','https://overpass.private.coffee/api/interpreter']:
 try:
  r=requests.post(url,data={'data':q},timeout=90);r.raise_for_status();Path('work/sheppard_osm.osm').write_text(r.text,encoding='utf-8');print('OSM bytes',len(r.content),url);break
 except Exception as e:print(type(e).__name__,url,flush=True)
