from pathlib import Path
import requests,json,time
W=Path(__file__).resolve().parent
url='https://gis.toronto.ca/arcgis/rest/services/cot_geospatial/FeatureServer/2/query'
p={'f':'geojson','where':"LINEAR_NAME_FULL IN ('Sheppard Ave W','Yonge St','Allen Rd')",'outFields':'CENTRELINE_ID,LINEAR_NAME_FULL,FROM_INTERSECTION_ID,TO_INTERSECTION_ID,FEATURE_CODE,FEATURE_CODE_DESC','outSR':4326,'returnGeometry':'true','resultRecordCount':2000}
r=requests.get(url,params=p,timeout=90);r.raise_for_status()
(W/'sheppard_roads.geojson').write_text(r.text,encoding='utf-8')
d=r.json();print('Road features',len(d.get('features',[])), 'error',d.get('error'))
print('QGIS plugin download metadata')
r=requests.get('https://plugins.qgis.org/plugins/QuickOSM/',timeout=60)
(W/'quickosm_page.html').write_text(r.text,encoding='utf-8')
import re
print(re.findall(r'href="([^"]*(?:download|versions)[^"]*)"',r.text)[-15:])
