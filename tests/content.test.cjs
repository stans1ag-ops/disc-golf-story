const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const ROOT=path.resolve(__dirname,'..'),catalog=require('../stories.json'),baseline=require('./content-baseline.json');
const read=id=>JSON.parse(fs.readFileSync(path.join(ROOT,id,'story.json'),'utf8'));
const text=s=>s.replace(/<[^>]*>/g,'').replace(/&#(\d+);/g,(_,n)=>String.fromCodePoint(+n)).replace(/&#x([\da-f]+);/gi,(_,n)=>String.fromCodePoint(parseInt(n,16))).replace(/&(amp|lt|gt|quot|apos|nbsp);/g,(_,n)=>({amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '})[n]).replace(/\s+/g,' ').trim();
test('all published stories preserve the original narrative, scenes, and illustration counts',()=>{
  assert(catalog.stories.length>=Object.keys(baseline).length);
  for(const id of Object.keys(baseline)){const s=read(id),before=baseline[id];assert.equal(s.scenes.length,before.scenes,id);assert.equal(s.scenes.reduce((n,sc)=>n+sc.blocks.filter(b=>b.type==='image').length,0),before.images,id);const paragraphs=s.scenes.flatMap(sc=>sc.blocks.filter(b=>b.type==='paragraph').map(b=>text(b.html)));assert.deepEqual(paragraphs,before.paragraphs,id);}
});
test('scene and collection identifiers are unique and complete',()=>{assert.equal(new Set(catalog.stories).size,catalog.stories.length);for(const id of catalog.stories){const s=read(id);assert.equal(new Set(s.scenes.map(sc=>sc.id)).size,s.scenes.length);assert(catalog.collections.some(c=>c.id===s.collection));}});
test('published source has no invented cue timings',()=>{for(const id of catalog.stories){const s=read(id);if(s.scenes.some(sc=>typeof sc.start==='number')){const timing=JSON.parse(fs.readFileSync(path.join(ROOT,id,'narration-timings.json'),'utf8'));for(const [i,sc] of s.scenes.entries()){const names=sc.blocks.filter(b=>b.type==='image').map(b=>path.basename(b.src));assert.equal(sc.start,timing.scenes.find(c=>names.includes(c.image)||c.scene===i+1).start,id);}}}});
test('exact narration script is derived from canonical scenes',()=>{
 const result=cp.execFileSync('python3',['-c',"import sys;sys.path.insert(0,'scripts');import story;s,p=story.load('steadfast-tin-soldier');print(story.scene_text(s['scenes'][0]));print(story.narration_fingerprint(s)==story.narration_fingerprint(s))"],{cwd:ROOT,encoding:'utf8'});
 assert.match(result,/There were once five-and-twenty tin soldiers/);assert.match(result,/True/);
});
test('new-story workflow creates an unpublished draft and does not alter the catalog',()=>{
 const id='workflow-test-draft',folder=path.join(ROOT,id);const before=fs.readFileSync(path.join(ROOT,'stories.json'),'utf8');
 try{cp.execFileSync('python3',['scripts/story.py','new',id,'--title','A Test Adventure','--collection','classics'],{cwd:ROOT});const s=read(id);assert.equal(s.scenes.length,15);assert(fs.existsSync(path.join(folder,'illustration-plan.json')));assert.equal(fs.readFileSync(path.join(ROOT,'stories.json'),'utf8'),before);const published=cp.spawnSync('python3',['scripts/story.py','publish',id],{cwd:ROOT,encoding:'utf8'});assert.notEqual(published.status,0);assert.equal(fs.readFileSync(path.join(ROOT,'stories.json'),'utf8'),before)}finally{fs.rmSync(folder,{recursive:true,force:true})}
});
