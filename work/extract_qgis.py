from pathlib import Path
import ctypes as C,subprocess,json,time
W=Path(__file__).resolve().parent
DEST=W/'tools/QGIS'
DEST.mkdir(parents=True,exist_ok=True)
m=C.WinDLL('msi')
H=C.c_uint;U=C.c_uint;S=C.c_wchar_p
m.MsiOpenDatabaseW.argtypes=[S,S,C.POINTER(H)]
m.MsiDatabaseOpenViewW.argtypes=[H,S,C.POINTER(H)]
m.MsiViewExecute.argtypes=[H,H];m.MsiViewFetch.argtypes=[H,C.POINTER(H)]
m.MsiRecordGetStringW.argtypes=[H,U,S,C.POINTER(U)]
m.MsiRecordReadStream.argtypes=[H,U,C.c_void_p,C.POINTER(U)]
def check(code):
 if code:raise OSError(code)
db=H();check(m.MsiOpenDatabaseW(str(W/'QGIS-OSGeo4W-3.44.15-2.msi'),None,C.byref(db)))
def query(sql,n):
 view=H();check(m.MsiDatabaseOpenViewW(db,sql,C.byref(view)));check(m.MsiViewExecute(view,0))
 result=[]
 while True:
  rec=H();c=m.MsiViewFetch(view,C.byref(rec))
  if c==259:break
  check(c);row=[]
  for i in range(1,n+1):
   size=U(32768);buf=C.create_unicode_buffer(size.value);check(m.MsiRecordGetStringW(rec,i,buf,C.byref(size)));row.append(buf.value)
  result.append(row);m.MsiCloseHandle(rec)
 m.MsiCloseHandle(view);return result
dirs={a:(b,c) for a,b,c in query('SELECT Directory,Directory_Parent,DefaultDir FROM Directory',3)}
components={a:b for a,b in query('SELECT Component,Directory_ FROM Component',2)}
files=query('SELECT File,Component_,FileName FROM File',3)
def directory(key):
 if key in ['INSTALLDIR','TARGETDIR'] or key not in dirs:return DEST
 par,name=dirs[key];name=name.split(':')[0].split('|')[-1]
 return directory(par) if name=='.' else directory(par)/name
manifest=[]
for fid,comp,name in files:
 target=directory(components[comp])/name.split('|')[-1]
 if not target.resolve().is_relative_to(DEST.resolve()):raise ValueError(target)
 manifest.append((fid,str(target)))
(W/'qgis_file_manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
cab=W/'qgis_application.cab'
if not cab.exists():
 view=H();check(m.MsiDatabaseOpenViewW(db,"SELECT Data FROM _Streams WHERE Name='application.cab'",C.byref(view)));check(m.MsiViewExecute(view,0));rec=H();check(m.MsiViewFetch(view,C.byref(rec)))
 buf=C.create_string_buffer(8*1024*1024)
 with cab.open('wb') as f:
  while True:
   size=U(len(buf));check(m.MsiRecordReadStream(rec,1,buf,C.byref(size)))
   if not size.value:break
   f.write(buf.raw[:size.value])
 m.MsiCloseHandle(rec);m.MsiCloseHandle(view)
print('Extracting cabinet',cab.stat().st_size,flush=True)
temp=W/'qgis_cab';temp.mkdir(exist_ok=True)
subprocess.run(['tar','-xf',str(cab),'-C',str(temp)],check=True)
print('Restoring installed paths',len(manifest),flush=True)
for fid,target in manifest:
 source=temp/fid;target=Path(target)
 if source.exists():
  target.parent.mkdir(parents=True,exist_ok=True);source.replace(target)
 elif not target.exists():print('Missing',fid,target,flush=True)
print('Portable files ready:',DEST,flush=True)
m.MsiCloseHandle(db)
