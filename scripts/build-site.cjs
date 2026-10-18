'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { createRequire } = require('node:module');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'dist');
const CACHE = path.join(ROOT, '.cache', 'storybook');
const loose = process.argv.includes('--allow-missing-media');
const get = p => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const catalog = get('stories.json');
const inventory = get('media-inventory.json');
const stories = catalog.stories.map(id => get(id + '/story.json'));
let sharp;
try { sharp = require('sharp'); } catch (e) {
  if (!process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES) throw e;
  sharp = createRequire(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES, '_storybook.cjs'))('sharp');
}
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const plain = s => String(s || '').replace(/<[^>]*>/g, ' ').replace(/\s+/g,' ').trim();
const hash = s => crypto.createHash('sha256').update(s).digest('hex').slice(0,16);
const write = (p, s) => { const f=path.join(OUT,p); fs.mkdirSync(path.dirname(f),{recursive:true}); fs.writeFileSync(f,s); };
const exists = p => fs.existsSync(path.join(ROOT,p));
const fileHashes = new Map();
function fileHash(p) {
  if (fileHashes.has(p)) return fileHashes.get(p);
  const h=crypto.createHash('sha256'), fd=fs.openSync(path.join(ROOT,p),'r'), buf=Buffer.alloc(1024*1024);
  let n; while ((n=fs.readSync(fd,buf,0,buf.length,null))) h.update(buf.subarray(0,n)); fs.closeSync(fd);
  const value=h.digest('hex').slice(0,16);fileHashes.set(p,value);return value;
}
const mediaMap = new Map();
function media(src) {
  if (!src) return '';
  if (mediaMap.has(src)) return mediaMap.get(src);
  if (!exists(src) || fs.statSync(path.join(ROOT,src)).size===0) {
    if (!loose) throw Error('Missing source media: '+src);
    const remote='https://story-nu-wheat.vercel.app/'+src+'?v='+(inventory[src]?.sha.slice(0,12)||'legacy');
    mediaMap.set(src,remote);return remote;
  }
  const target='assets/media/'+fileHash(src)+'-'+path.basename(src);
  fs.mkdirSync(path.dirname(path.join(OUT,target)),{recursive:true});
  fs.copyFileSync(path.join(ROOT,src),path.join(OUT,target));
  mediaMap.set(src,'/'+target);return '/'+target;
}
function mp3Duration(src) {
  if (!exists(src)) return null;
  const stat=fs.statSync(path.join(ROOT,src));const fd=fs.openSync(path.join(ROOT,src),'r');
  if(!stat.size){fs.closeSync(fd);return null;}
  const b=Buffer.alloc(Math.min(stat.size,1024*1024));fs.readSync(fd,b,0,b.length,0);fs.closeSync(fd);
  let start=0;
  if(b.toString('ascii',0,3)==='ID3')start=10+((b[6]&127)<<21)+((b[7]&127)<<14)+((b[8]&127)<<7)+(b[9]&127);
  for(let i=start;i<b.length-100;i++) {
    const h=b.readUInt32BE(i);if((h>>>21)!==2047)continue;
    const version=(h>>>19)&3,layer=(h>>>17)&3,br=(h>>>12)&15,sr=(h>>>10)&3;
    if(version===1||layer!==1||br===0||br===15||sr===3)continue;
    const rate=[44100,48000,32000][sr]/(version===3?1:version===2?2:4);
    const mono=((h>>>6)&3)===3,side=version===3?(mono?17:32):(mono?9:17),samples=version===3?1152:576;
    const x=i+4+side+(((h>>>16)&1)?0:2),tag=b.toString('ascii',x,x+4);
    if((tag==='Xing'||tag==='Info')&&(b.readUInt32BE(x+4)&1))return b.readUInt32BE(x+8)*samples/rate;
    const v=i+36;if(b.toString('ascii',v,v+4)==='VBRI')return b.readUInt32BE(v+14)*samples/rate;
    const kbps=(version===3?[0,32,40,48,56,64,80,96,112,128,160,192,224,256,320]:[0,8,16,24,32,40,48,56,64,80,96,112,128,144,160])[br];
    return (stat.size-i)*8/(kbps*1000);
  }
  throw Error('No supported MP3 frame header: '+src);
}
const time = seconds => `${Math.floor(seconds/60)}:${String(Math.floor(seconds%60)).padStart(2,'0')}`;
const images=new Map();
async function image(src) {
  if(images.has(src))return images.get(src);
  if(!exists(src)||fs.statSync(path.join(ROOT,src)).size===0){
    if(!loose)throw Error('Missing illustration: '+src);
    const url='https://story-nu-wheat.vercel.app/'+src+'?v='+(inventory[src]?.sha.slice(0,12)||'legacy');
    const original={url,width:1376,height:768,bytes:inventory[src]?.size||0};
    const result={sources:[original],small:original,large:original,originalBytes:original.bytes};images.set(src,result);return result;
  }
  const input=path.join(ROOT,src),meta=await sharp(input).metadata();
  const widths=[...new Set([384,768,1440,1920].map(w=>Math.min(w,meta.autoOrient?.width||meta.width)))];
  const sources=[];const sourceHash=fileHash(src);
  for(const width of widths) {
    const key=hash(sourceHash+'-webp-v1-'+width),name=key+'-'+width+'.webp';
    const cached=path.join(CACHE,'images',name);fs.mkdirSync(path.dirname(cached),{recursive:true});
    if(!fs.existsSync(cached))await sharp(input).rotate().resize({width,withoutEnlargement:true}).webp({quality:width<=768?78:87,effort:5}).toFile(cached);
    const target='assets/images/'+name;fs.mkdirSync(path.dirname(path.join(OUT,target)),{recursive:true});fs.copyFileSync(cached,path.join(OUT,target));
    const result=await sharp(cached).metadata();sources.push({url:'/'+target,width:result.width,height:result.height,bytes:fs.statSync(cached).size});
  }
  const result={sources,small:sources.find(s=>s.width>=768)||sources.at(-1),large:sources.at(-1),originalBytes:fs.statSync(input).size};
  images.set(src,result);return result;
}
function img(src,alt,{cover=false,eager=false}={}) {
  const i=images.get(src);if(!i)throw Error('Unprepared image: '+src);
  const selected=cover?i.small:i.sources.find(s=>s.width>=1440)||i.large;
  return `<img src="${selected.url}" srcset="${i.sources.map(s=>`${s.url} ${s.width}w`).join(', ')}" sizes="${cover?'(min-width: 900px) 360px, (min-width: 640px) 46vw, 92vw':'(min-width: 900px) 800px, 94vw'}" width="${selected.width}" height="${selected.height}" alt="${esc(alt)}" loading="${eager?'eager':'lazy'}" decoding="async"${eager?' fetchpriority="high"':''}>`;
}
function collectionUrl(id){return id==='tyson'?'/tyson/':'/'+id+'/';}
function shell(title,description,body,{story=false,slug='',collection=''}={}) {
  const nav=catalog.collections.map(c=>`<a href="${collectionUrl(c.id)}" ${collection===c.id?'aria-current="page"':''}>${esc(c.title)}</a>`).join('');
  return `<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="description" content="${esc(description)}"><meta name="theme-color" content="#fbf7ef"><title>${esc(title)} · Our Storybook</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="canonical" href="https://story-nu-wheat.vercel.app/${slug?slug+'/':''}"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(description)}"><meta property="og:type" content="${story?'article':'website'}"><script>try{var p=JSON.parse(localStorage.getItem('storybook-v1')||'{}');var t=p.theme||localStorage.getItem('shane-stories-theme')||localStorage.getItem('bedtime-story-theme')||localStorage.getItem('disc-golf-story-theme');if(!t&&matchMedia('(prefers-color-scheme:dark)').matches)t='night';if(['light','sepia','night'].includes(t))document.documentElement.dataset.theme=t;if(p.fontSize)document.documentElement.style.setProperty('--reading-size',Math.min(30,Math.max(16,p.fontSize))+'px')}catch(e){}</script><link rel="stylesheet" href="${cssUrl}"><script src="${jsUrl}" defer></script><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600&family=Lora:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet"></head><body data-page="${story?'story':'catalog'}" ${story?`data-story-id="${esc(slug)}"`:''}><a class="skip-link" href="#main">Skip to ${story?'story':'stories'}</a><header class="site-header"><div class="header-inner"><a class="brand" href="/" aria-label="Our Storybook home"><span class="brand-mark" aria-hidden="true">✦</span> Our Storybook</a><nav class="desktop-nav" aria-label="Story collections">${nav}</nav><div class="header-actions"><button class="theme-toggle icon-button" type="button" aria-label="Change color theme" title="Change color theme">☾</button><details class="mobile-menu"><summary aria-label="Open navigation">☰</summary><nav aria-label="Navigation"><a href="/">All stories</a>${nav}</nav></details></div></div></header>${body}<footer class="site-footer"><a class="brand" href="/">✦ Our Storybook</a><p>Stories to share. Adventures to remember.</p><p class="footer-links"><a href="/">All ${stories.length} stories</a> · ${catalog.collections.map(c=>`<a href="${collectionUrl(c.id)}">${esc(c.title)}</a>`).join(' · ')}</p></footer><div id="toast" class="toast" role="status" aria-live="polite"></div></body></html>`;
}
function card(s,index) {
  return `<article class="story-card" data-card-id="${esc(s.id)}" data-title="${esc(s.title.toLowerCase())}" data-search="${esc((s.title+' '+s.description+' '+s.subtitle).toLowerCase())}" data-collection="${s.collection}" data-duration="${s.duration}" data-video="${Boolean(s.media.video)}" data-added="${esc(s.addedAt||'')}" data-order="${index}"><a href="/${s.id}/" class="card-art" tabindex="-1" aria-hidden="true">${img(s.cover.src,s.cover.alt,{cover:true,eager:index===0})}<span class="duration-badge">${time(s.duration)}</span></a><div class="card-body"><div class="card-kicker">${esc(s.readingLevel)} <span aria-hidden="true">·</span> ${s.imageCount} pictures</div><h3><a href="/${s.id}/">${esc(s.title)}</a></h3><p class="card-description">${esc(s.description)}</p><div class="card-bottom"><a href="/${s.id}/" class="card-open">Read story <span aria-hidden="true">↗</span></a><span class="media-badges" aria-label="${s.media.audio?'Narration available':''}${s.media.video?', Video available':''}">${s.media.audio?'♫':''}${s.media.video?' ▷':''}</span><button type="button" class="favorite-button icon-button" data-favorite="${esc(s.id)}" aria-pressed="false" aria-label="Save ${esc(s.title)} to favorites">♡</button></div></div></article>`;
}
function hub(collection) {
  const scope=collection?stories.filter(s=>s.collection===collection.id):stories;
  const title=collection?collection.title:'A little wonder, before bedtime.';
  const sections=(collection?[collection]:catalog.collections).map(c=>{const group=scope.filter(s=>s.collection===c.id);return `<section class="collection-section" id="${c.id}-stories" data-collection-section="${c.id}"><div class="section-heading"><div><p class="eyebrow">${group.length} illustrated stories</p><h2>${esc(c.title)}</h2><p>${esc(c.description)}</p></div>${collection?'':`<a class="text-link" href="${collectionUrl(c.id)}">Explore collection <span aria-hidden="true">→</span></a>`}</div><div class="story-grid">${group.map((s,i)=>card(s,stories.indexOf(s))).join('')}</div></section>`}).join('');
  const body=`<main id="main" class="library-main" data-scope="${collection?.id||'all'}"><section class="library-hero"><div class="hero-copy"><p class="eyebrow">The family story collection</p><h1>${esc(title)}</h1><p class="hero-description">${esc(collection?collection.description:'Find a familiar favorite or discover your next adventure. Read together, listen along, or settle in for a storybook video.')}</p><p class="library-count">${scope.length} stories <span aria-hidden="true">·</span> ${collection?'One wonderful collection':'Three wonderful collections'}</p></div><div class="hero-art" aria-hidden="true"><span class="hero-star star-one">✦</span><span class="hero-book">📖</span><span class="hero-star star-two">✧</span><span class="hero-orbit"></span></div></section><nav class="collection-tabs" aria-label="Choose a collection"><a href="/" ${!collection?'aria-current="page"':''}>All stories <span>${stories.length}</span></a>${catalog.collections.map(c=>`<a href="${collectionUrl(c.id)}" ${collection?.id===c.id?'aria-current="page"':''}>${esc(c.title)} <span>${stories.filter(s=>s.collection===c.id).length}</span></a>`).join('')}</nav><section class="continue-panel" id="continue-panel" hidden aria-label="Continue your story"></section><form class="catalog-tools" role="search" id="catalog-filters"><label class="search-field"><span aria-hidden="true">⌕</span><span class="sr-only">Search stories</span><input type="search" id="story-search" placeholder="Find a story…" autocomplete="off"></label><div class="filter-row"><label><span class="sr-only">Story length</span><select id="duration-filter"><option value="all">Any length</option><option value="short">Under 5 minutes</option><option value="medium">5–10 minutes</option><option value="long">10+ minutes</option></select></label><label><span class="sr-only">Available media</span><select id="media-filter"><option value="all">Read, listen & watch</option><option value="video">With video</option></select></label><label><span class="sr-only">Sort stories</span><select id="sort-filter"><option value="collection">Collection order</option><option value="title">Title A–Z</option><option value="shortest">Shortest first</option><option value="newest">Recently added</option></select></label><button type="button" id="favorites-filter" class="filter-button" aria-pressed="false">♡ Favorites</button><button type="reset" class="text-button" id="reset-filters">Reset</button></div></form><p id="results-count" class="results-count" aria-live="polite">${scope.length} stories to explore</p><div id="story-sections">${sections}</div><div id="empty-results" class="empty-state" hidden><span aria-hidden="true">✧</span><h2>No stories found</h2><p>Try another search or clear your filters.</p><button type="button" class="primary-button" id="clear-filters">Show all stories</button></div><noscript><p class="notice">All stories are available below. Search, favorites, and saved progress work when JavaScript is enabled.</p></noscript></main>`;
  return shell(collection?collection.title:'Our Storybook',collection?.description||'Illustrated stories for Shane, Tyson, and the whole family.',body,{collection:collection?.id,slug:collection?collectionUrl(collection.id).slice(1,-1):''});
}
function scene(s,sc,index) {
  return `<article class="story-scene" id="${sc.id}" data-scene-index="${index}"><div class="scene-heading"><span class="scene-number">${String(index+1).padStart(2,'0')}</span><h2>${esc(sc.title)}</h2></div>${sc.blocks.map(b=>b.type==='image'?`<figure class="story-figure"><button type="button" class="image-zoom" data-zoom="${images.get(b.src).large.url}" data-caption="${esc(b.caption)}" aria-label="Enlarge illustration: ${esc(b.alt)}">${img(b.src,b.alt,{eager:index===0})}<span class="zoom-hint" aria-hidden="true">⤢ Enlarge</span></button>${b.caption?`<figcaption>${esc(b.caption)}</figcaption>`:''}</figure>`:b.type==='paragraph'?`<p class="story-text">${b.html}</p>`:`<aside class="story-callout">${b.html}</aside>`).join('')}</article>`;
}
function storyPage(s) {
  const c=catalog.collections.find(c=>c.id===s.collection),next=stories.filter(t=>t.collection===s.collection&&t.id!==s.id).slice(0,3);
  const hasCues=s.scenes.every(sc=>typeof sc.start==='number');
  const data={id:s.id,title:s.title,duration:s.duration,scenes:s.scenes.map(sc=>({id:sc.id,start:sc.start??null})),hasCues};
  const audio=s.media.audio?`<section class="audio-panel" id="listen" aria-label="Listen to ${esc(s.title)}"><div class="audio-heading"><span class="audio-symbol" aria-hidden="true">♫</span><div><h2>Listen to the story</h2><p>${time(s.duration)} of narrated adventure</p></div></div><audio id="story-audio" controls preload="none" aria-label="${esc(s.title)} narration" src="${media(s.media.audio)}"></audio><div class="audio-options"><button type="button" class="small-button" id="back-fifteen" aria-label="Rewind narration 15 seconds">↶ 15s</button><label class="speed-control">Speed <select id="audio-speed" aria-label="Narration playback speed"><option value="0.75">0.75×</option><option value="0.9">0.9×</option><option value="1" selected>1×</option><option value="1.25">1.25×</option><option value="1.5">1.5×</option></select></label>${hasCues?'<label class="follow-control"><input type="checkbox" id="follow-narration"> Follow scenes</label>':''}</div><p class="media-status" id="audio-status" role="status" aria-live="polite"></p></section>`:'';
  const video=s.media.video?`<section class="video-section" id="watch"><div class="section-heading"><div><p class="eyebrow">Settle in and watch</p><h2>The story on screen</h2><p>${s.imageCount} illustrations brought together in a storybook video.</p></div></div><video id="story-video" controls playsinline preload="none" poster="${images.get(s.media.video.poster)?.small.url||images.get(s.cover.src).small.url}" aria-label="${esc(s.title)} storybook video"><source src="${media(s.media.video.src)}" type="video/mp4">${s.media.captions?`<track kind="captions" src="${media(s.media.captions)}" srclang="en" label="English">`:''}Your browser cannot play this video. <a href="${media(s.media.video.src)}">Download the video</a>.</video><p id="video-status" class="media-status" role="status"></p></section>`:'';
  const body=`<main id="main" class="reader-main"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">All stories</a><span aria-hidden="true">/</span><a href="${collectionUrl(c.id)}">${esc(c.title)}</a></nav><header class="story-heading"><p class="eyebrow">${esc(s.edition)} <span aria-hidden="true">·</span> ${esc(s.readingLevel)}</p><h1>${esc(s.title)}</h1><p class="story-subtitle">${esc(s.subtitle||s.description)}</p><div class="story-facts"><span>${time(s.duration)} narration</span><span>${s.imageCount} illustrations</span><span>${s.scenes.length} scenes</span></div><div class="story-heading-actions"><button type="button" class="favorite-label" data-favorite="${esc(s.id)}" aria-pressed="false">♡ Save story</button>${s.sourceUrl?`<a class="source-link" href="${esc(s.sourceUrl)}" target="_blank" rel="noopener noreferrer">Story source ↗</a>`:''}</div></header><div class="reader-toolbar" aria-label="Reading controls"><div class="mode-buttons"><a class="mode-button active" data-mode="read" href="#scene-1">Read</a>${s.media.audio?'<a class="mode-button" data-mode="listen" href="#listen">♫ Listen</a>':''}${s.media.video?'<a class="mode-button" data-mode="watch" href="#watch">▷ Watch</a>':''}</div><div class="reading-settings"><button type="button" class="font-button" id="font-decrease" aria-label="Decrease story text size">A−</button><button type="button" class="font-button" id="font-increase" aria-label="Increase story text size">A+</button><label><span class="sr-only">Jump to a scene</span><select id="scene-select">${s.scenes.map((sc,i)=>`<option value="${sc.id}">${i+1}. ${esc(sc.title)}</option>`).join('')}</select></label></div><div class="reading-progress" id="reading-progress" aria-hidden="true"></div></div><div class="resume-notice" id="resume-notice" hidden></div>${audio}<div class="story-content">${s.scenes.map((sc,i)=>scene(s,sc,i)).join('')}</div>${s.discussionHtml?`<section class="discussion-panel" aria-label="Talk about the story">${s.discussionHtml}</section>`:''}${video}<section class="next-stories"><div class="section-heading"><div><p class="eyebrow">One more adventure?</p><h2>Keep exploring</h2></div><a class="text-link" href="${collectionUrl(c.id)}">All ${esc(c.title)} →</a></div><div class="story-grid">${next.map((t,i)=>card(t,i+1)).join('')}</div></section><dialog id="illustration-dialog" class="illustration-dialog" aria-label="Enlarged story illustration"><button type="button" id="close-illustration" class="dialog-close" aria-label="Close enlarged illustration">×</button><figure><img id="enlarged-image" alt=""><figcaption id="enlarged-caption"></figcaption></figure></dialog><script type="application/json" id="story-data">${JSON.stringify(data).replace(/</g,'\\u003c')}</script></main>`;
  return shell(s.title,s.description,body,{story:true,slug:s.id,collection:s.collection});
}
let cssUrl,jsUrl;
async function main() {
  fs.rmSync(OUT,{recursive:true,force:true});fs.mkdirSync(OUT,{recursive:true});
  for(const [source,dest] of [['site/styles.css','css'],['site/app.js','js']]){const content=fs.readFileSync(path.join(ROOT,source));const name=`assets/${hash(content)}.${dest}`;write(name,content);if(dest==='css')cssUrl='/'+name;else jsUrl='/'+name;}
  const sources=new Set();for(const s of stories){sources.add(s.cover.src);for(const sc of s.scenes)for(const b of sc.blocks)if(b.type==='image')sources.add(b.src);if(s.media.video?.poster&&exists(s.media.video.poster))sources.add(s.media.video.poster);}
  // Bound concurrency so the build has predictable memory use even as the catalog grows.
  const queue=[...sources];let complete=0;await Promise.all(Array.from({length:4},async()=>{while(queue.length){const src=queue.shift();await image(src);if(++complete%50===0)console.log(`Prepared ${complete}/${sources.size} illustrations`);}}));
  for(const s of stories){s.duration=mp3Duration(s.media.audio)||s.media.duration||60;s.imageCount=s.scenes.reduce((n,sc)=>n+sc.blocks.filter(b=>b.type==='image').length,0);if(s.media.duration&&Math.abs(s.duration-s.media.duration)>.25)throw Error(`Narration timing mismatch: ${s.id} (${s.duration} vs ${s.media.duration})`);}
  write('index.html',hub(null));for(const c of catalog.collections)write(collectionUrl(c.id).slice(1)+'index.html',hub(c));
  for(const s of stories)write(s.id+'/index.html',storyPage(s));
  write('assets/catalog.json',JSON.stringify(stories.map(s=>({id:s.id,title:s.title,collection:s.collection,description:s.description,duration:s.duration,cover:images.get(s.cover.src).small.url,addedAt:s.addedAt||null}))));
  write('favicon.svg','<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#376354"/><text x="32" y="47" text-anchor="middle" font-size="48" fill="#fff5db">✦</text></svg>');
  write('404.html',shell('A story waiting to be found','Find your next illustrated adventure.', '<main id="main" class="empty-state"><h1>This page has wandered off.</h1><p>Let’s find you another adventure.</p><a class="primary-button" href="/">Back to the story collection</a></main>'));
  write('robots.txt','User-agent: *\nAllow: /\nSitemap: https://story-nu-wheat.vercel.app/sitemap.xml\n');
  write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+['',...catalog.collections.map(c=>collectionUrl(c.id).slice(1)),...stories.map(s=>s.id+'/')].map(p=>`<url><loc>https://story-nu-wheat.vercel.app/${p}</loc></url>`).join('')+'</urlset>');
  const coverOriginal=stories.reduce((n,s)=>n+images.get(s.cover.src).originalBytes,0),coverOptimized=stories.reduce((n,s)=>n+images.get(s.cover.src).small.bytes,0);
  const report={stories:stories.length,scenes:stories.reduce((n,s)=>n+s.scenes.length,0),illustrations:sources.size,coverOriginalBytes:coverOriginal,coverOptimizedBytes:coverOptimized,coverReductionPercent:Math.round((1-coverOptimized/coverOriginal)*100),sourceOnly:loose,assets:Object.fromEntries([...images].map(([src,i])=>[src,i.sources])),durations:Object.fromEntries(stories.map(s=>[s.id,s.duration]))};
  write('build-report.json',JSON.stringify(report,null,2)+'\n');console.log(`Built ${stories.length} stories; cover image bytes reduced ${report.coverReductionPercent}%.`);
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
module.exports={mp3Duration,esc,plain,time};
