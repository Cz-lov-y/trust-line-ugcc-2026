from pathlib import Path
import os,sys,json,traceback
W=Path(__file__).resolve().parent;Q=W/'tools/QGIS';OUT=W.parent/'outputs/project/outputs/sheppard_west_pilot'
sys.path[:0]=[str(Q/'apps/qgis-ltr/python'),str(Q/'apps/qgis-ltr/python/plugins'),str(W/'qgis_profiles/profiles/default/python/plugins')]
from qgis.core import QgsApplication,QgsProject,QgsVectorLayer,QgsCoordinateReferenceSystem,QgsVectorFileWriter,QgsFillSymbol,QgsLineSymbol,QgsMarkerSymbol,QgsSettings,Qgis
app=QgsApplication([],True);QgsApplication.setPrefixPath(str(Q/'apps/qgis-ltr'),True);app.initQgis()
status={'qgis_version':Qgis.QGIS_VERSION,'runtime_mode':'local standalone extracted from signed official MSI; not registered with Windows Installer'}
project=QgsProject.instance();project.setCrs(QgsCoordinateReferenceSystem('EPSG:2952'))
for name,file,style in [('500 m corridor buffer','corridor_01_buffer_500m.geojson','polygon'),('Sheppard Ave West road proxy','corridor_01_centerline.geojson','line'),('Station-area junction proxies','corridor_01_endpoints.geojson','point')]:
 layer=QgsVectorLayer(str(OUT/file),name,'ogr');assert layer.isValid(),file
 if style=='polygon':layer.renderer().setSymbol(QgsFillSymbol.createSimple({'color':'65,170,177,65','outline_color':'8,127,140,255','outline_width':'0.6'}))
 elif style=='line':layer.renderer().setSymbol(QgsLineSymbol.createSimple({'line_color':'227,90,62,255','line_width':'1.0'}))
 else:layer.renderer().setSymbol(QgsMarkerSymbol.createSimple({'color':'32,60,81,255','size':'3.5'}))
 project.addMapLayer(layer)
 if style=='polygon':extent=layer.extent()
project.viewSettings().setDefaultViewExtent(__import__('qgis.core',fromlist=['QgsReferencedRectangle']).QgsReferencedRectangle(extent,QgsCoordinateReferenceSystem('EPSG:4326')))
project.setTitle('Corridor 01: Sheppard West boundary pilot')
assert project.write(str(OUT/'corridor_01_pilot.qgz'))
status['project_layers']=len(project.mapLayers())
(OUT/'qgis_setup_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
print('QGIS project written; testing QuickOSM provider',flush=True)
try:
 import processing
 print('Imported processing',flush=True)
 from QuickOSM.quick_osm_processing.provider import Provider
 provider=Provider()
 status['provider_registered']=QgsApplication.processingRegistry().addProvider(provider)
 provider.loadAlgorithms()
 provider.refreshAlgorithms()
 status['quickosm_algorithms']=[a.id() for a in QgsApplication.processingRegistry().algorithms() if a.id().startswith('quickosm:')]
 status['quickosm_loaded']=True
except Exception:
 status['quickosm_loaded']=False;status['plugin_error']=traceback.format_exc()
(OUT/'qgis_setup_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
print(json.dumps(status,indent=2),flush=True)
