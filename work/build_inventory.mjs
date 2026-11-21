import fs from 'node:fs/promises';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
const deps='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1117-1425-0_26.1117.1425.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/';
const req=createRequire(deps+'__inventory_resolver__.js');
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir=new URL('.',import.meta.url);
const specs=JSON.parse(await fs.readFile(new URL('inventory_data.json',dir),'utf8'));
const wb=Workbook.create();
const widths=[
 [25,110],
 [35,28,42,75,62,30,43,24,54,35,58,60,60,52,45,65],
 [8,40,30,30,22,25,26,9,60,60,10,65,90],
 [20,12,65,78,90,65],
 [24,95,90,90],
 [28,52,100,100],
 [35,12,20,40,55],
 [12,12,12,45,18,18,30,70,65,80]
];
for(let i=0;i<specs.length;i++){
 const d=specs[i],s=wb.worksheets.add(d.name), data=[d.headers,...d.rows];
 s.showGridLines=false;
 const all=s.getRangeByIndexes(0,0,data.length,d.headers.length);
 all.values=data;
 all.format.font={name:'Arial',size:11,color:'#183247'};
 all.format.verticalAlignment='top';
 all.format.wrapText=true;
 all.format.horizontalAlignment='left';
 for(let r=1;r<data.length;r++){
  const lines=Math.max(...data[r].map((v,c)=>Math.ceil([...String(v??'')].reduce((n,ch)=>n+(ch.charCodeAt(0)>255?2:1),0)/(widths[i][c]*0.95))));
  s.getRangeByIndexes(r,0,1,d.headers.length).format.rowHeight=Math.max(25,lines*15+9);
 }
 for(let c=0;c<d.headers.length;c++)s.getRangeByIndexes(0,c,data.length,1).format.columnWidth=widths[i][c];
 const head=s.getRangeByIndexes(0,0,1,d.headers.length);
 head.format.fill='#243E55';
 head.format.font={name:'Arial',size:11,bold:true,color:'#FFFFFF'};
 head.format.rowHeight=40;
 head.format.verticalAlignment='center';
 head.format.horizontalAlignment='center';
 for(let r=2;r<data.length;r+=2)s.getRangeByIndexes(r,0,1,d.headers.length).format.fill='#F1F5F8';
 s.freezePanes.freezeRows(1);
 s.freezePanes.freezeColumns(i===1?1:i===2?2:1);
 const t=s.tables.add(s.getRangeByIndexes(0,0,data.length,d.headers.length),true,`Inventory${i+1}`);
 t.style='TableStyleMedium2';
 t.showFilterButton=true;
 if(i===2){
  s.getRangeByIndexes(1,0,d.rows.length,1).setNumberFormat('0');
  s.getRangeByIndexes(1,5,d.rows.length,1).setNumberFormat('0.###');
  s.getRangeByIndexes(1,6,d.rows.length,2).setNumberFormat('0');
  s.getRangeByIndexes(1,5,d.rows.length,3).format.horizontalAlignment='right';
 }
 if(i===7){
  s.getRangeByIndexes(1,0,d.rows.length,3).setNumberFormat('0');
  s.getRangeByIndexes(1,4,d.rows.length,1).setNumberFormat('0.00');
  s.getRangeByIndexes(1,4,d.rows.length,1).format.horizontalAlignment='right';
 }
 if(i===0)s.tabColor='#243E55';
}
wb.recalculate();
console.log((await wb.inspect({kind:'region',sheetId:'指标字典',range:'A1:H4',maxChars:2300,tableMaxCols:8,tableMaxRows:4})).ndjson);
console.log((await wb.inspect({kind:'region',sheetId:'24条走廊',range:'A3:H5',maxChars:1700,tableMaxCols:8,tableMaxRows:3})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:10},maxChars:1000})).ndjson);
const output=await SpreadsheetFile.exportXlsx(wb);
await output.save(fileURLToPath(new URL('../outputs/City_2024_指标与走廊审阅.xlsx',dir)));
for(let i=0;i<specs.length;i++){
 const ranges=['A1:B7','A1:F5','A1:H7','A1:E6','A1:D5','A1:D5','A1:E5','A1:H8'];
 const img=await wb.render({sheetName:specs[i].name,range:ranges[i],scale:1,format:'png'});
 await fs.writeFile(new URL(`sheet_${i+1}.png`,dir),new Uint8Array(await img.arrayBuffer()));
}
console.log(JSON.stringify(specs.map(s=>({sheet:s.name,rows:s.rows.length}))));
