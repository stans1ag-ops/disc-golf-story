'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'dist');
const loose=process.argv.includes('--allow-missing-media');
const read=p=>JSON.parse(fs.readFileSync(path.join(ROOT,p),'utf8'));
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(f=>f.isDirectory()?walk(path.join(dir,f.name)):[path.join(dir,f.name)])}
const errors=[],warnings=[];const assert=(condition,message)=>{if(!condition)errors.push(message)};
const catalog=read('stories.json'),ids=new Set(),inventory=read('media-inventory.json');
function sourceFile(p,label){assert(typeof p==='string'&&!p.startsWith('/')&&!p.split('/').includes('..'),`${label}: invalid source path ${p}`);if(!p)return;assert(loose?Boolean(inventory[p])||fs.existsSync(path.join(ROOT,p)):fs.existsSync(path.join(ROOT,p))&&fs.statSync(path.join(ROOT,p)).size>0,`${label}: missing or empty ${p}`)}
for(const id of catalog.stories){
  assert(!ids.has(id),'Duplicate story ID: '+id);ids.add(id);assert(/^[a-z0-9-]+(?:\/[a-z0-9-]+)?$/.test(id),'Invalid story ID: '+id);
  const s=read(id+'/story.json');assert(s.id===id,id+': ID differs from catalog');assert(s.schemaVersion===1,id+': schema version');assert(s.title&&s.description,id+': title and description required');assert(catalog.collections.some(c=>c.id===s.collection),id+': unknown collection');assert(s.scenes.length>0,id+': missing scenes');sourceFile(s.cover.src,id+' cover');
  const inputs=[s.title,s.narration?.voice||'af_heart',s.narration?.speed??.92,s.scenes.map(sc=>sc.blocks.filter(b=>b.type!=='image').map(b=>[b.type,b.html]))];const inputHash=crypto.createHash('sha256').update(JSON.stringify(inputs)).digest('hex');if(s.media.audio&&s.media.narrationInputHash)assert(inputHash===s.media.narrationInputHash,id+': narration is stale after a story-text or voice change; run the narration workflow');
  if(s.media.video&&s.media.videoNarrationHash)assert(s.media.videoNarrationHash===s.media.narrationInputHash,id+': video narration is stale; rerender the video');
  if(s.media.video&&s.media.videoVisualHash&&!loose){const inputImages=s.scenes.flatMap(sc=>sc.blocks.filter(b=>b.type==='image').map(b=>{const content=fs.readFileSync(path.join(ROOT,b.src));return [b.src,crypto.createHash('sha1').update(`blob ${content.length}\0`).update(content).digest('hex')]}));assert(crypto.createHash('sha256').update(JSON.stringify(inputImages)).digest('hex')===s.media.videoVisualHash,id+': video illustrations are stale; rerender the video')}
  const sceneIds=new Set();let last=-1,hasTimings=false,untimed=false;
  for(const sc of s.scenes){assert(!sceneIds.has(sc.id),id+': duplicate scene '+sc.id);sceneIds.add(sc.id);assert(sc.title&&sc.blocks.length,id+': empty scene '+sc.id);if(typeof sc.start==='number'){hasTimings=true;assert(sc.start>=0&&sc.start>last,id+': non-monotonic cues');last=sc.start}else untimed=true;
    for(const b of sc.blocks){assert(['paragraph','image','callout'].includes(b.type),id+': invalid block type');if(b.type==='image'){sourceFile(b.src,id+' image');assert(Boolean(b.alt?.trim()),id+': illustration needs alt text')}else{assert(Boolean(b.html?.trim()),id+': empty story text');assert(!/<\/?(?:script|iframe|object|embed)\b|\bon\w+\s*=|javascript:/i.test(b.html),id+': unsafe story HTML')}}
  }
  assert(!(hasTimings&&untimed),id+': partially timed scenes');if(s.media.audio)sourceFile(s.media.audio,id+' audio');if(s.media.video){sourceFile(s.media.video.src,id+' video');sourceFile(s.media.video.poster,id+' video poster')}
  if(s.media.captions){sourceFile(s.media.captions,id+' captions');const vtt=fs.readFileSync(path.join(ROOT,s.media.captions),'utf8');assert(vtt.startsWith('WEBVTT'),id+': captions must be WebVTT');const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3})\s+-->\s+(\d\d):(\d\d):(\d\d)\.(\d{3})/g)];assert(cues.length>0,id+': no caption cues');let end=-1,lastStart=-1;for(const c of cues){const start=(+c[1]*3600)+(+c[2]*60)+(+c[3])+(+c[4]/1000),finish=(+c[5]*3600)+(+c[6]*60)+(+c[7])+(+c[8]/1000);assert(start>=lastStart&&finish>start,id+': invalid caption cue');lastStart=start;end=Math.max(end,finish)}if(s.media.duration)assert(end<=s.media.duration+.3,id+': captions run past audio')}
  else if(s.media.video)warnings.push(id+': legacy video has no timed captions; the full story remains available as its transcript.');
}
if(fs.existsSync(OUT)){
 const report=read('dist/build-report.json');assert(loose||!report.sourceOnly,'A development build cannot be released');assert(report.stories===ids.size,'Built story count differs from catalog');
 const pages=walk(OUT).filter(p=>p.endsWith('.html'));
 for(const file of pages){const content=fs.readFileSync(file,'utf8'),rel=path.relative(OUT,file);const pageIds=[...content.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);assert(new Set(pageIds).size===pageIds.length,rel+': duplicate HTML IDs');assert((content.match(/<h1\b/g)||[]).length===1,rel+': expected one main heading');
  for(const m of content.matchAll(/\b(?:href|src|poster)="([^"]*)"/g)){const value=m[1];if(!value||value.startsWith('data:')||value.startsWith('http:')||value.startsWith('https:'))continue;const u=new URL(value,'https://local.test/'+rel);if(u.origin!=='https://local.test')continue;let target=path.join(OUT,decodeURIComponent(u.pathname));if(u.pathname.endsWith('/'))target=path.join(target,'index.html');assert(fs.existsSync(target),rel+': broken local reference '+value);if(u.hash&&target===file)assert(pageIds.includes(decodeURIComponent(u.hash.slice(1))),rel+': broken anchor '+value)}
  for(const m of content.matchAll(/<img\b[^>]*>/g)){const tag=m[0];if(tag.includes('id="enlarged-image"'))continue;assert(/\balt="/.test(tag),rel+': image without alt');assert(/\bwidth="/.test(tag)&&/\bheight="/.test(tag),rel+': image without dimensions');assert(/\bsrcset="/.test(tag),rel+': image without responsive sizes')}
 }
 console.log(`Validated ${ids.size} story records, ${pages.length} pages, media references, captions, IDs, links, and responsive images.`);
 if(report.coverReductionPercent<60)warnings.push('Cover image reduction is below 60%; inspect the build report.');
}else errors.push('Build output is missing. Run npm run build first.');
for(const w of warnings)console.log('NOTE: '+w);for(const e of errors)console.error('ERROR: '+e);if(errors.length)process.exitCode=1;
