import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const base='D:/projects/hoi4_mod/1/outputs/01a16e22-a52a-7261-ab67-2140c18d1964';
const manifest=JSON.parse(await fs.readFile(base+'/_support/order-export-manifest.json','utf8'));
const workbook=await SpreadsheetFile.importXlsx(await FileBlob.load(base+'/国家修正统计_词条排序表_v0.1.6.xlsx'));
let checked=0;
for(const meta of manifest.sheets){
 const sheet=workbook.worksheets.getItem(meta.page);
 const expected=manifest.records.filter(r=>r.page===meta.page);
 const rows=sheet.getRange(`A8:I${meta.total+7}`).values;
 for(let i=0;i<rows.length;i++){
  const r=rows[i],e=expected[i];
  if(r[7]!==e.id||r[8]!==e.key||r[2]!==e.name||r[0]!==e.group||r[1]!==e.group_order||r[4]!==e.group||r[5]!==e.group_order)throw new Error(`Saved row mismatch ${meta.page}:${i}`);
  checked++;
 }
}
// A disposable imported workbook verifies the duplicate-input highlight.
const first=workbook.worksheets.getItem('政治');
first.getRange('F9').values=[[1]];
workbook.recalculate();
const duplicate=await workbook.inspect({kind:'computedStyle',sheetId:'政治',range:'E8:F9',maxChars:5000});
await fs.writeFile(base+'/_support/duplicate-highlight-check.ndjson',duplicate.ndjson);
console.log(duplicate.ndjson);
first.getRange('F9').values=[[2]];
workbook.recalculate();
const restored=await workbook.inspect({kind:'computedStyle',sheetId:'政治',range:'E8:F9',maxChars:5000});
await fs.writeFile(base+'/_support/restored-highlight-check.ndjson',restored.ndjson);
console.log(restored.ndjson);
console.log(JSON.stringify({saved_rows_verified:checked,expected:559,export_untouched:true}));
