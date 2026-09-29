// Render the reused Navet React primitives into static profile fragments.
const fs = require('node:fs');
const path = require('node:path');
const ts = require('typescript');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const root = path.resolve(__dirname, '..');
const build = path.join(root, '.build');
fs.mkdirSync(build, {recursive:true});
for (const file of fs.readdirSync(path.join(root,'src/navet'))) {
  const source = fs.readFileSync(path.join(root,'src/navet',file),'utf8');
  const {outputText} = ts.transpileModule(source,{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}});
  fs.writeFileSync(path.join(build,file.replace(/\.tsx?$/,'.js')),outputText);
}
const {CardMetric}=require(path.join(build,'card-metric.js'));
const {CardMetricActionLayout}=require(path.join(build,'card-metric-action-layout.js'));
const {EntityCardTitleBlock}=require(path.join(build,'entity-card-title-block.js'));
const data=JSON.parse(fs.readFileSync(path.join(root,'data/profile.json'),'utf8'));
const days=data.contributionsCollection.contributionCalendar.weeks.flatMap(w=>w.contributionDays);
let longest=0,run=0;for(const day of days){run=day.contributionCount?run+1:0;longest=Math.max(longest,run);}
const metrics=[[data.contributionsCollection.totalCommitContributions,'Commits'],[data.contributionsCollection.totalPullRequestContributions,'Pull requests'],[days.filter(d=>d.contributionCount).length,'Active days'],[longest,'Longest streak']];
const stats=metrics.map(([value,label],i)=>renderToStaticMarkup(React.createElement('section',{className:'card stat'},
  React.createElement(EntityCardTitleBlock,{title:label,subtitle:'Past year',layout:'title-first',titleClassName:'navet-card-title',subtitleClassName:'navet-card-subtitle'}),
  React.createElement(CardMetricActionLayout,{size:'small',metric:React.createElement(CardMetric,{value:value.toLocaleString()+(i===3?' days':''),size:'xl',isActive:i===0,accentClassName:'accent-text',theme:'dark'}),actions:React.createElement('span',{className:'stat-note'},['GitHub-reported commits','Opened pull requests','Days with contributions','Consecutive active days'][i])})
))).join('');
fs.writeFileSync(path.join(root,'data/components.json'),JSON.stringify({stats})+'\n');
console.log('Rendered CardMetric, CardMetricActionLayout, and EntityCardTitleBlock');
