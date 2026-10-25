import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = 'D:/projects/hoi4_mod/1';
const outputDir = root + '/outputs/01a16e22-a52a-7261-ab67-2140c18d1964';
const supportDir = outputDir + '/_support';
const indexPath = root + '/hoi4-national-buff/tools/data/metric-index.json';
const indexText = await fs.readFile(indexPath, 'utf8');
const catalog = JSON.parse(indexText);
const pages = ['政治', '工业', '陆军', '海军', '空军', '情报'];
const workbook = Workbook.create();
const headers = ['当前分组', '当前组内顺序', '词条名称', '当前行列', '新分组', '新组内顺序', '备注', '固定ID', '修正键'];
const widths = [92, 110, 348, 100, 102, 112, 220, 82, 520];
const colors = { header:'#34443A', input:'#FFF2CC', text:'#252C28', muted:'#64716A', high:'#EDF2EE', low:'#F6F7F5' };
const first = 8;
const outputRecords = [];
const summaries = [];

for (let pi = 0; pi < pages.length; pi++) {
  const page = pages[pi];
  const sheet = workbook.worksheets.add(page);
  sheet.showGridLines = false;
  sheet.tabColor = '#526657';
  const data = [];
  const pageRecords = [];
  const counts = {};
  for (const [band, label, columns] of [['high','常用',3],['low','其他修正',4]]) {
    const members = catalog.records.filter(r => r.category === page && r.display_priority_band === band);
    counts[label] = members.length;
    for (let i = 0; i < members.length; i++) {
      const row = members[i];
      const gridRow = Math.floor(i / columns) + 1;
      const gridColumn = i % columns + 1;
      data.push([label, i+1, row.name, `${gridRow}行${gridColumn}列`, label, i+1, '', row.id, row.key]);
      pageRecords.push({page, band, group:label, group_order:i+1, name:row.name, id:row.id, key:row.key, grid_row:gridRow, grid_column:gridColumn});
    }
  }
  const last = first + data.length - 1;
  sheet.getRange(`A1:I${last}`).format.font = { name:'Arial', size:11, color:colors.text };
  sheet.getRange(`A1:I${last}`).format.verticalAlignment = 'center';
  sheet.getRange(`A1:I${last}`).format.rowHeightPx = 30;
  widths.forEach((width, i) => sheet.getRangeByIndexes(0,i,last,1).format.columnWidthPx = width);
  sheet.getRange('A1:I1').format.rowHeightPx = 12;
  sheet.getRange('A2').values = [[`${page}词条排序`]];
  sheet.getRange('A2:I2').format.font = { name:'Arial', size:16, bold:true, color:colors.header };
  sheet.getRange('A2:I2').format.rowHeightPx = 36;
  sheet.getRange('A2:I2').format.borders = {bottom:{style:'thin',color:'#9BA99F'}};
  sheet.getRange('A3').values = [[`共 ${data.length} 项。常用 ${counts['常用']} 项（三列），其他修正 ${counts['其他修正']} 项（四列）。`]];
  sheet.getRange('A4').values = [['修改黄色列：新分组、新组内顺序。同组内数字越小越靠前，重号会标红。请保留固定ID和修正键。']];
  sheet.getRange('A5').values = [['来源：国家修正统计 UI 0.1.6 的当前列表。行列按“全部词条”状态、组内从左到右再从上到下计数。']];
  sheet.getRange('A3:I5').format.font = { name:'Arial', size:11, color:colors.muted };
  sheet.getRange('A6:I6').format.rowHeightPx = 10;
  sheet.getRange('A7:I7').values = [headers];
  sheet.getRange(`A${first}:I${last}`).values = data;
  const table = sheet.tables.add(`A7:I${last}`, true, `NBVOrderPage${pi+1}`);
  table.showFilterButton = true;
  table.style = 'TableStyleLight1';
  sheet.getRange('A7:I7').format = {fill:colors.header, font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'}, horizontalAlignment:'center', verticalAlignment:'center',rowHeightPx:34};
  sheet.getRange('A7:I7').format.borders = {insideVertical:{style:'thin',color:'#FFFFFF'}};
  sheet.getRange(`A${first}:I${last}`).format.fill = '#FFFFFF';
  sheet.getRange(`A${first}:A${first+counts['常用']-1}`).format.fill = colors.high;
  sheet.getRange(`A${first+counts['常用']}:A${last}`).format.fill = colors.low;
  sheet.getRange(`E${first}:F${last}`).format.fill = colors.input;
  sheet.getRange(`A${first}:A${last}`).format.horizontalAlignment = 'left';
  sheet.getRange(`C${first}:E${last}`).format.horizontalAlignment = 'left';
  sheet.getRange(`G${first}:I${last}`).format.horizontalAlignment = 'left';
  for (const col of ['B','F','H']) {
    sheet.getRange(`${col}${first}:${col}${last}`).setNumberFormat('0');
    sheet.getRange(`${col}${first}:${col}${last}`).format.horizontalAlignment = 'right';
  }
  sheet.getRange(`I${first}:I${last}`).format.font = {name:'Arial',size:11,color:colors.muted};
  sheet.getRange(`C${first}:C${last}`).format.wrapText = true;
  sheet.getRange(`I${first}:I${last}`).format.wrapText = true;
  const weightedLength = s => [...s].reduce((sum, ch) => sum + (ch.charCodeAt(0)>255?2:1),0);
  data.forEach((r,i) => {
    const lines = Math.max(Math.ceil(weightedLength(r[2])*7.4/332),Math.ceil(r[8].length*7.4/500),1);
    sheet.getRange(`A${first+i}:I${first+i}`).format.rowHeightPx = lines*20+10;
  });
  const split = first + counts['常用'];
  sheet.getRange(`A${split}:I${split}`).format.borders = {top:{style:'medium',color:'#9BA99F'}};
  sheet.getRange(`E${first}:E${last}`).dataValidation = {rule:{type:'list',values:['常用','其他修正']}};
  sheet.dataValidations.add({range:`F${first}:F${last}`,rule:{type:'whole',operator:'between',formula1:1,formula2:9999}});
  sheet.getRange(`E${first}:F${last}`).conditionalFormats.addCustom(
    `AND($F${first}<>"",COUNTIFS($E$${first}:$E$${last},$E${first},$F$${first}:$F$${last},$F${first})>1)`,
    {fill:'#FCE4D6',font:{color:'#9C0006',bold:true}}
  );
  sheet.freezePanes.freezeRows(7);
  sheet.freezePanes.freezeColumns(3);
  outputRecords.push(...pageRecords);
  summaries.push({page,total:data.length,common:counts['常用'],other:counts['其他修正'],range:`A7:I${last}`});
}

if (outputRecords.length !== 559 || new Set(outputRecords.map(r=>r.id)).size !== 559 || new Set(outputRecords.map(r=>r.key)).size !== 559) throw new Error('Incomplete/duplicate catalog');
for (const page of pages) {
  const sheet=workbook.worksheets.getItem(page);
  const expected=outputRecords.filter(r=>r.page===page);
  const actual=sheet.getRange(`A8:I${expected.length+7}`).values;
  if (JSON.stringify(actual.map(r=>r[7]))!==JSON.stringify(expected.map(r=>r.id))) throw new Error('Order mismatch: '+page);
}
workbook.recalculate();
console.log((await workbook.inspect({kind:'table',range:'政治!A7:I12',include:'values,formulas',tableMaxRows:6,tableMaxCols:9,maxChars:2200})).ndjson);
const errors=await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'error scan'});
console.log(errors.ndjson);
await fs.mkdir(supportDir,{recursive:true});
for (const page of pages) {
  const preview=await workbook.render({sheetName:page,range:'A1:I15',scale:1,format:'png'});
  await fs.writeFile(path.join(supportDir,`preview-${page}.png`),new Uint8Array(await preview.arrayBuffer()));
}
const file=path.join(outputDir,'国家修正统计_词条排序表_v0.1.6.xlsx');
await (await SpreadsheetFile.exportXlsx(workbook)).save(file);
await fs.writeFile(path.join(supportDir,'order-export-manifest.json'),JSON.stringify({version:'0.1.6',source_index_sha256:crypto.createHash('sha256').update(indexText).digest('hex'),record_count:559,sheets:summaries,records:outputRecords},null,2));
console.log(JSON.stringify({output:file,count:outputRecords.length,sheets:summaries}));
