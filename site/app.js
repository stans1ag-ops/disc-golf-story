(() => {
  'use strict';
  const KEY='storybook-v1';
  const $=(s,root=document)=>root.querySelector(s), $$=(s,root=document)=>[...root.querySelectorAll(s)];
  const safeText=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let prefs={};try{prefs=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){}
  if(!prefs||typeof prefs!=='object'||Array.isArray(prefs))prefs={};
  if(!Array.isArray(prefs.favorites))prefs.favorites=[];
  if(!prefs.progress||typeof prefs.progress!=='object')prefs.progress={};
  function save(){try{localStorage.setItem(KEY,JSON.stringify(prefs))}catch(e){}}
  let toastTimer;
  function toast(message){const el=$('#toast');if(!el)return;el.textContent=message;el.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('visible'),2200)}
  const reduceMotion=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
  function go(el){if(el)el.scrollIntoView({behavior:reduceMotion()?'instant':'smooth',block:'start'})}
  const themes=['light','sepia','night'];
  function theme(value){prefs.theme=themes.includes(value)?value:'light';document.documentElement.dataset.theme=prefs.theme;const b=$('.theme-toggle');if(b){b.textContent={light:'☾',sepia:'☀',night:'◐'}[prefs.theme];b.setAttribute('aria-label',`Color theme: ${{light:'Day',sepia:'Sepia',night:'Night'}[prefs.theme]}. Change theme.`)}save()}
  theme(prefs.theme||document.documentElement.dataset.theme||'light');
  $('.theme-toggle')?.addEventListener('click',()=>{theme(themes[(themes.indexOf(prefs.theme)+1)%3]);toast(`${{light:'Day',sepia:'Sepia',night:'Night'}[prefs.theme]} theme`)});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')$$('.mobile-menu[open]').forEach(m=>m.open=false)});
  document.addEventListener('click',e=>{$$('.mobile-menu[open]').forEach(m=>{if(!m.contains(e.target))m.open=false})});
  function refreshFavorites(){
    $$('[data-favorite]').forEach(b=>{const on=prefs.favorites.includes(b.dataset.favorite);b.setAttribute('aria-pressed',String(on));if(b.classList.contains('favorite-label'))b.textContent=on?'♥ Saved story':'♡ Save story';else b.textContent=on?'♥':'♡';const card=b.closest('[data-card-id]');const title=card?$('h3',card).textContent:document.title.split(' · ')[0];b.setAttribute('aria-label',`${on?'Remove':'Save'} ${title} ${on?'from':'to'} favorites`)});
  }
  document.addEventListener('click',e=>{const b=e.target.closest('[data-favorite]');if(!b)return;const id=b.dataset.favorite;const on=prefs.favorites.includes(id);prefs.favorites=on?prefs.favorites.filter(x=>x!==id):[...prefs.favorites,id];save();refreshFavorites();toast(on?'Removed from favorites':'Saved to favorites');if($('#catalog-filters'))filter()});
  refreshFavorites();
  let favoritesOnly=false;
  const cards=$$('[data-card-id]');
  function filter(){
    if(!$('#catalog-filters'))return;
    const q=($('#story-search').value||'').toLocaleLowerCase().trim(),duration=$('#duration-filter').value,media=$('#media-filter').value,sort=$('#sort-filter').value;
    let count=0;
    for(const c of cards){const sec=Number(c.dataset.duration);const durationOK=duration==='all'||(duration==='short'&&sec<300)||(duration==='medium'&&sec>=300&&sec<600)||(duration==='long'&&sec>=600);const visible=c.dataset.search.includes(q)&&durationOK&&(media!=='video'||c.dataset.video==='true')&&(!favoritesOnly||prefs.favorites.includes(c.dataset.cardId));c.hidden=!visible;if(visible)count++}
    const sorted=sort!=='collection';let sortedGrid=$('#sorted-grid');
    if(!sortedGrid){sortedGrid=document.createElement('div');sortedGrid.id='sorted-grid';sortedGrid.className='story-grid';$('#story-sections').before(sortedGrid)}
    if(sorted){const ordered=[...cards].sort((a,b)=>sort==='title'?a.dataset.title.localeCompare(b.dataset.title):sort==='shortest'?Number(a.dataset.duration)-Number(b.dataset.duration):(b.dataset.added||'').localeCompare(a.dataset.added||''));ordered.forEach(c=>sortedGrid.append(c));sortedGrid.hidden=count===0;$$('[data-collection-section]').forEach(s=>s.hidden=true)}
    else{sortedGrid.hidden=true;for(const c of cards){const grid=$(`[data-collection-section="${c.dataset.collection}"] .story-grid`);grid?.append(c)}}
    for(const section of $$('[data-collection-section]')){
      if(sorted)continue;
      const grid=$('.story-grid',section);let ordered=$$('[data-card-id]',grid);
      ordered.sort((a,b)=>sort==='title'?a.dataset.title.localeCompare(b.dataset.title):sort==='shortest'?Number(a.dataset.duration)-Number(b.dataset.duration):sort==='newest'?(b.dataset.added||'').localeCompare(a.dataset.added||'')||Number(b.dataset.order)-Number(a.dataset.order):Number(a.dataset.order)-Number(b.dataset.order));
      ordered.forEach(c=>grid.append(c));section.hidden=ordered.every(c=>c.hidden);
    }
    $('#results-count').textContent=`${count} ${count===1?'story':'stories'}${q||duration!=='all'||media!=='all'||favoritesOnly?' found':' to explore'}`;
    $('#empty-results').hidden=count>0;
  }
  function reset(){const f=$('#catalog-filters');if(!f)return;f.reset();favoritesOnly=false;$('#favorites-filter').setAttribute('aria-pressed','false');filter();$('#story-search').focus()}
  if($('#catalog-filters')){
    $('#catalog-filters').addEventListener('submit',e=>e.preventDefault());
    $('#story-search').addEventListener('input',filter);for(const s of ['#duration-filter','#media-filter','#sort-filter'])$(s).addEventListener('change',filter);
    $('#favorites-filter').addEventListener('click',()=>{favoritesOnly=!favoritesOnly;$('#favorites-filter').setAttribute('aria-pressed',String(favoritesOnly));filter()});
    $('#catalog-filters').addEventListener('reset',()=>{favoritesOnly=false;$('#favorites-filter').setAttribute('aria-pressed','false');setTimeout(filter,0)});
    $('#clear-filters').addEventListener('click',reset);
    const params=new URLSearchParams(location.search);if(params.has('q'))$('#story-search').value=params.get('q');filter();
    const scope=$('.library-main').dataset.scope;
    const last=Object.entries(prefs.progress).filter(([id,p])=>!p.completed&&cards.some(c=>c.dataset.cardId===id)&&(scope==='all'||cards.find(c=>c.dataset.cardId===id)?.dataset.collection===scope)).sort((a,b)=>(b[1].updatedAt||0)-(a[1].updatedAt||0))[0];
    if(last){const [id,p]=last,c=cards.find(c=>c.dataset.cardId===id),panel=$('#continue-panel');panel.innerHTML=`<div><p class="eyebrow">A story waiting for you</p><h2>${safeText($('h3',c).textContent)}</h2><p>Continue where you left off.</p></div><a class="primary-button" href="/${encodeURI(id)}/#${encodeURIComponent(p.scene||'scene-1')}">Continue reading →</a>`;panel.hidden=false}
  }
  const dataElement=$('#story-data');if(!dataElement)return;
  const story=JSON.parse(dataElement.textContent),audio=$('#story-audio'),video=$('#story-video');
  let activeScene=0,lastStored=0,hasInteracted=false,saveTimer;
  let font=Number(prefs.fontSize);
  if(!Number.isFinite(font)){for(const key of ['shane-stories-fontsize','shane-stories-font-size','disc-golf-story-fontsize']){try{font=Number(localStorage.getItem(key));if(font>=16)break}catch(e){}}}
  if(!Number.isFinite(font)||font<16)font=20;
  function setFont(size){font=Math.max(16,Math.min(30,size));prefs.fontSize=font;document.documentElement.style.setProperty('--reading-size',font+'px');$('#font-decrease').disabled=font<=16;$('#font-increase').disabled=font>=30;save()}
  setFont(font);$('#font-decrease').addEventListener('click',()=>setFont(font-2));$('#font-increase').addEventListener('click',()=>setFont(font+2));
  const previous={...(prefs.progress[story.id]||{})};
  function storeProgress(force=false){if(!hasInteracted)return;clearTimeout(saveTimer);if(!force&&Date.now()-lastStored<1000){saveTimer=setTimeout(()=>storeProgress(true),1000-(Date.now()-lastStored));return}lastStored=Date.now();const p=prefs.progress[story.id]||{};prefs.progress[story.id]={...p,scene:story.scenes[activeScene]?.id||'scene-1',time:audio?.currentTime||p.time||0,videoTime:video?.currentTime||p.videoTime||0,updatedAt:Date.now(),completed:p.completed||false};save()}
  for(const event of ['pointerdown','keydown','wheel','touchstart'])document.addEventListener(event,()=>{hasInteracted=true},{passive:true});
  window.addEventListener('pagehide',()=>storeProgress(true));document.addEventListener('visibilitychange',()=>{if(document.hidden)storeProgress(true)});
  const progress=$('#reading-progress'),scenes=$$('.story-scene');
  const sceneObserver=new IntersectionObserver(entries=>{const candidates=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);if(!candidates.length)return;const index=Number(candidates[0].target.dataset.sceneIndex);activeScene=index;$('#scene-select').value=story.scenes[index].id;progress.style.width=((index+1)/scenes.length*100)+'%';storeProgress()},{rootMargin:'-155px 0px -50% 0px',threshold:0});scenes.forEach(s=>sceneObserver.observe(s));
  $('#scene-select').addEventListener('change',e=>{hasInteracted=true;activeScene=story.scenes.findIndex(s=>s.id===e.target.value);storeProgress(true);go(document.getElementById(e.target.value));history.replaceState(null,'','#'+e.target.value);if(prefs.follow&&audio&&!audio.paused&&story.hasCues){const cue=story.scenes.find(s=>s.id===e.target.value);audio.currentTime=cue.start}});
  if(previous.scene||previous.time){const notice=$('#resume-notice');notice.innerHTML=`<span>Welcome back. Your place in this story is saved.</span><div><button type="button" id="resume-story">Resume</button><button type="button" id="restart-story">Start over</button></div>`;notice.hidden=false;$('#resume-story').addEventListener('click',()=>{go(document.getElementById(previous.scene||'scene-1'));notice.hidden=true});$('#restart-story').addEventListener('click',()=>{if(audio)audio.currentTime=0;if(video)video.currentTime=0;prefs.progress[story.id]={scene:'scene-1',time:0,videoTime:0,updatedAt:Date.now(),completed:false};save();go(scenes[0]);notice.hidden=true})}
  const status=$('#audio-status');
  async function playAudio(){if(!audio)return;hasInteracted=true;if(status)status.textContent='Loading narration…';try{await audio.play();if(status)status.textContent=''}catch(e){if(status)status.textContent='Tap the audio player to start. If the audio does not load, check your connection.'}}
  if(audio){
    const speeds=$('#audio-speed');const rate=[.75,.9,1,1.25,1.5].includes(Number(prefs.rate))?Number(prefs.rate):1;audio.playbackRate=rate;speeds.value=String(rate);
    speeds.addEventListener('change',()=>{audio.playbackRate=Number(speeds.value);if(video)video.playbackRate=audio.playbackRate;prefs.rate=audio.playbackRate;save()});
    $('#back-fifteen').addEventListener('click',()=>{hasInteracted=true;audio.currentTime=Math.max(0,audio.currentTime-15);storeProgress(true)});
    const follow=$('#follow-narration');if(follow){follow.checked=Boolean(prefs.follow);follow.addEventListener('change',()=>{prefs.follow=follow.checked;save()})}
    audio.addEventListener('loadedmetadata',()=>{if(previous.time>0&&previous.time<audio.duration-1)audio.currentTime=previous.time});
    audio.addEventListener('play',()=>{hasInteracted=true;video?.pause();if(status)status.textContent='';setMode('listen')});
    audio.addEventListener('pause',()=>storeProgress(true));audio.addEventListener('error',()=>{if(status)status.textContent='The narration could not load. Check your connection and try again.'});
    audio.addEventListener('waiting',()=>{if(status&&!audio.paused)status.textContent='Buffering narration…'});audio.addEventListener('playing',()=>{if(status)status.textContent=''});
    let lastCue=-1;
    audio.addEventListener('timeupdate',()=>{if(story.hasCues){let index=0;story.scenes.forEach((s,i)=>{if(s.start<=audio.currentTime)index=i});if(index!==lastCue){lastCue=index;scenes.forEach((el,i)=>el.classList.toggle('narrating',i===index));if(prefs.follow&&!audio.paused){activeScene=index;go(scenes[index]);$('#scene-select').value=story.scenes[index].id}}}storeProgress()});
    audio.addEventListener('ended',()=>{prefs.progress[story.id]={...(prefs.progress[story.id]||{}),completed:true,time:0,updatedAt:Date.now()};save();toast('The end. A lovely adventure!')});
  }
  if(video){video.playbackRate=audio?.playbackRate||1;video.addEventListener('loadedmetadata',()=>{if(previous.videoTime>0&&previous.videoTime<video.duration-1)video.currentTime=previous.videoTime});video.addEventListener('play',()=>{hasInteracted=true;audio?.pause();setMode('watch')});video.addEventListener('pause',()=>storeProgress(true));video.addEventListener('timeupdate',()=>storeProgress());video.addEventListener('error',()=>{$('#video-status').textContent='The video could not load. Check your connection and try again.'});video.addEventListener('ended',()=>{prefs.progress[story.id]={...(prefs.progress[story.id]||{}),completed:true,videoTime:0,updatedAt:Date.now()};save()})}
  function setMode(mode){$$('[data-mode]').forEach(b=>{const active=b.dataset.mode===mode;b.classList.toggle('active',active);if(active)b.setAttribute('aria-current','true');else b.removeAttribute('aria-current')})}
  $$('[data-mode]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();const mode=b.dataset.mode;setMode(mode);if(mode==='read'){audio?.pause();video?.pause();go(scenes[activeScene]||scenes[0])}else if(mode==='listen'){go($('#listen'));playAudio()}else {audio?.pause();go($('#watch'));video?.play().catch(()=>{$('#video-status').textContent='Tap the video player to begin.'})}}));
  const dialog=$('#illustration-dialog');let trigger;
  $$('[data-zoom]').forEach(button=>button.addEventListener('click',()=>{trigger=button;const enlarged=$('#enlarged-image');enlarged.src=button.dataset.zoom;enlarged.alt=$('img',button).alt;$('#enlarged-caption').textContent=button.dataset.caption;dialog.showModal();document.body.style.overflow='hidden'}));
  $('#close-illustration').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}});dialog.addEventListener('close',()=>{document.body.style.overflow='';$('#enlarged-image').removeAttribute('src');trigger?.focus()});
})();
