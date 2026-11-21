import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL,fileURLToPath} from 'node:url';
const deps=process.env.ARTIFACT_NODE_MODULES || 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1117-1425-0_26.1117.1425.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules';
const req=createRequire(path.join(deps,'__inventory_resolver__.js'));
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const schema=JSON.parse(await fs.readFile(path.join(root,'data/schema_v0.1.json'),'utf8'));
const records=JSON.parse(await fs.readFile(process.argv[2] || path.join(root,'data/workbook_records_v0.1.json'),'utf8'));
for(const key of ['data_dictionary','indicator_admission']){
 const wb=Workbook.create();
 const s=wb.worksheets.add(key==='data_dictionary'?'Data dictionary':'Indicator admission');
 const headers=schema[key],rows=(records[key]||[]).map(o=>headers.map(h=>o[h]??''));
 const matrix=[headers,...rows];
 const all=s.getRangeByIndexes(0,0,matrix.length,headers.length);
 all.values=matrix;
 all.format.font={name:'Arial',size:11,color:'#20374B'};
 all.format.wrapText=true;
 all.format.verticalAlignment='top';
 const widths=headers.map(h=>/definition|notes|reason/.test(h)?65:/source_locator|potential_overlap|comparability/.test(h)?42:/indicator_name/.test(h)?40:28);
 headers.forEach((h,c)=>s.getRangeByIndexes(0,c,matrix.length,1).format.columnWidth=widths[c]);
 for(let r=1;r<matrix.length;r++){
  const lines=Math.max(...matrix[r].map((v,c)=>Math.ceil(String(v).length/(widths[c]*0.9))));
  s.getRangeByIndexes(r,0,1,headers.length).format.rowHeight=Math.max(30,lines*15+12);
  if(r%2===0)s.getRangeByIndexes(r,0,1,headers.length).format.fill='#EEF3F7';
 }
 const head=s.getRangeByIndexes(0,0,1,headers.length);
 head.format.fill='#203D55';head.format.font={name:'Arial',size:11,bold:true,color:'#FFFFFF'};
 head.format.rowHeight=44;
 s.showGridLines=false;s.freezePanes.freezeRows(1);s.freezePanes.freezeColumns(1);
 if(rows.length){const t=s.tables.add(s.getRangeByIndexes(0,0,matrix.length,headers.length),true,key==='data_dictionary'?'DictionaryTable':'AdmissionTable');t.style='TableStyleMedium2';}
 wb.recalculate();
 console.log((await wb.inspect({kind:'region',sheetId:s.name,range:'A1:F4',maxChars:1600})).ndjson);
 const out=await SpreadsheetFile.exportXlsx(wb);await out.save(path.join(root,'data',key+'_v0.1.xlsx'));
 let column='';for(let n=headers.length;n>0;n=Math.floor((n-1)/26)){column=String.fromCharCode(65+(n-1)%26)+column;}
 const inspection=await wb.inspect({kind:'region',sheetId:s.name,range:`A1:${column}${matrix.length}`,maxChars:1000000});
 await fs.writeFile(path.join(root,'data',key+'_v0.1.xlsx.inspect.ndjson'),inspection.ndjson);
 if(process.env.SKIP_WORKBOOK_PREVIEWS!=='1'){
  const img=await wb.render({sheetName:s.name,range:`A1:F${Math.min(matrix.length+1,6)}`,scale:1,format:'png'});
  const preview=path.resolve(root,'../../work',key+'_preview.png');
  await fs.mkdir(path.dirname(preview),{recursive:true});await fs.writeFile(preview,new Uint8Array(await img.arrayBuffer()));
 }
}
