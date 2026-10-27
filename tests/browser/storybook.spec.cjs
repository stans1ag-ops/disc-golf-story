const {test,expect}=require('@playwright/test');
const fs=require('node:fs'),path=require('node:path');
const catalog=require('../../stories.json');
test('catalog search, empty state, reset, and favorites work',async({page})=>{
 await page.goto('/');await expect(page.locator('[data-card-id]')).toHaveCount(catalog.stories.length);
 await page.getByRole('searchbox').fill('gingerbread');await expect(page.locator('[data-card-id]:visible')).toHaveCount(1);await expect(page.locator('[data-card-id]:visible h3')).toHaveText('The Gingerbread Man');
 await page.getByRole('searchbox').fill('no such story xyz');await expect(page.getByRole('heading',{name:'No stories found'})).toBeVisible();await page.getByRole('button',{name:'Show all stories'}).click();await expect(page.locator('[data-card-id]:visible')).toHaveCount(catalog.stories.length);
 const favorite=page.locator('[data-card-id="tyson/pikachus-lost-ball"] [data-favorite]');await favorite.click();await page.locator('#favorites-filter').click();await expect(page.locator('[data-card-id]:visible')).toHaveCount(1);await page.reload();await page.locator('#favorites-filter').click();await expect(page.locator('[data-card-id]:visible')).toHaveCount(1);
});
test('duration and media filters use the actual story metadata',async({page})=>{
 await page.goto('/');await page.locator('#duration-filter').selectOption('short');const durations=await page.locator('[data-card-id]:visible').evaluateAll(cs=>cs.map(c=>Number(c.dataset.duration)));expect(durations.length).toBeGreaterThan(0);expect(durations.every(s=>s<300)).toBeTruthy();await page.locator('#media-filter').selectOption('video');expect(await page.locator('[data-card-id]:visible').evaluateAll(cs=>cs.every(c=>c.dataset.video==='true'))).toBeTruthy();await page.locator('#duration-filter').selectOption('all');await page.locator('#media-filter').selectOption('all');await page.locator('#sort-filter').selectOption('title');const titles=await page.locator('[data-card-id]:visible').evaluateAll(cs=>cs.map(c=>c.dataset.title));expect(titles).toEqual([...titles].sort((a,b)=>a.localeCompare(b)));await page.locator('#sort-filter').selectOption('collection');await expect(page.locator('[data-collection-section]:visible')).toHaveCount(catalog.collections.length);
});
test('themes and reading size persist between collections',async({page})=>{
 await page.goto('/');await page.locator('.theme-toggle').click();const theme=await page.locator('html').getAttribute('data-theme');await page.goto('/steadfast-tin-soldier/');await expect(page.locator('html')).toHaveAttribute('data-theme',theme);await page.locator('#font-increase').click();const size=await page.locator('html').evaluate(e=>e.style.getPropertyValue('--reading-size'));await page.goto('/tyson/pikachus-lost-ball/');await expect(page.locator('html')).toHaveAttribute('data-theme',theme);expect(await page.locator('html').evaluate(e=>e.style.getPropertyValue('--reading-size'))).toBe(size);
});
test('scene navigation, reading position, and continue reading work',async({page})=>{
 await page.goto('/steadfast-tin-soldier/');await page.locator('#scene-select').selectOption('scene-3');await expect.poll(()=>page.evaluate(()=>JSON.parse(localStorage.getItem('storybook-v1')).progress['steadfast-tin-soldier']?.scene)).toBe('scene-3');await page.goto('/');await expect(page.locator('#continue-panel')).toBeVisible();await page.locator('#continue-panel a').click();await expect(page.locator('#resume-notice')).toBeVisible();await page.locator('#restart-story').click();await expect.poll(()=>page.evaluate(()=>JSON.parse(localStorage.getItem('storybook-v1')).progress['steadfast-tin-soldier']?.scene)).toBe('scene-1');
});
test('illustration zoom supports Escape and returns keyboard focus',async({page})=>{
 await page.goto('/tyson/pikachus-lost-ball/');const zoom=page.locator('[data-zoom]').first();await zoom.click();await expect(page.locator('#illustration-dialog')).toBeVisible();await expect(page.locator('#enlarged-image')).toHaveAttribute('alt',/\S/);await page.keyboard.press('Escape');await expect(page.locator('#illustration-dialog')).not.toBeVisible();await expect(zoom).toBeFocused();
});
test('narration loads, plays, seeks, and preserves the exact speed label',async({page})=>{
 await page.goto('/steadfast-tin-soldier/');await page.locator('[data-mode="listen"]').click();await expect.poll(()=>page.locator('audio').evaluate(a=>a.currentTime),{timeout:20000}).toBeGreaterThan(.1);await page.locator('#audio-speed').selectOption('1.25');await expect(page.locator('#audio-speed')).toHaveValue('1.25');expect(await page.locator('audio').evaluate(a=>a.playbackRate)).toBe(1.25);await page.locator('audio').evaluate(a=>{a.pause();a.currentTime=40});await page.locator('#back-fifteen').click();expect(await page.locator('audio').evaluate(a=>a.currentTime)).toBeCloseTo(25,0);expect(await page.locator('audio').evaluate(a=>a.duration)).toBeGreaterThan(490);
});
test('video media supports range requests and has valid captions',async({page,request})=>{
 await page.goto('/steadfast-tin-soldier/');const src=await page.locator('video source').getAttribute('src');const response=await request.get(src,{headers:{Range:'bytes=0-1023'}});expect(response.status()).toBe(206);expect((await response.body()).length).toBe(1024);const captions=await page.locator('video track').getAttribute('src');expect((await request.get(captions)).status()).toBe(200);await page.locator('[data-mode="watch"]').click();await expect.poll(()=>page.locator('video').evaluate(v=>v.currentTime),{timeout:20000}).toBeGreaterThan(.1);await page.locator('[data-mode="listen"]').click();await expect.poll(()=>page.locator('audio').evaluate(a=>!a.paused)).toBeTruthy();expect(await page.locator('video').evaluate(v=>v.paused)).toBeTruthy();
});
test('every story renders with its scenes, images, and no horizontal overflow',async({page})=>{
 test.setTimeout(120000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const id of catalog.stories){const s=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../..',id,'story.json'),'utf8'));const response=await page.goto('/'+id+'/');expect(response.status(),id).toBe(200);await expect(page.locator('h1')).toHaveText(s.title);await expect(page.locator('.story-scene')).toHaveCount(s.scenes.length);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),id).toBeTruthy();await expect(page.locator('#story-audio')).toHaveCount(1)}
 expect(errors).toEqual([]);
});
test('legacy route redirects and collection pages stay usable without JavaScript',async({browser,request})=>{
 const res=await request.get('/the-houghton-lake-patrol/',{maxRedirects:0});expect(res.status()).toBe(308);expect(res.headers().location).toBe('/the-fish-that-pulled-back/');const ctx=await browser.newContext({javaScriptEnabled:false});const p=await ctx.newPage();await p.goto('http://127.0.0.1:4173/tyson/');await expect(p.locator('[data-card-id]')).toHaveCount(catalog.stories.filter((s)=>s.startsWith('tyson/')).length);await p.getByRole('heading',{name:'Tyson and Pikachu’s Lost Ball'}).getByRole('link').click();await expect(p.locator('.story-scene')).toHaveCount(4);await ctx.close();
});
test('capture representative layouts',async({page},info)=>{
 for(const [url,name] of [['/','library'],['/steadfast-tin-soldier/','classic'],['/tyson/pikachus-lost-ball/','early-reader']]){await page.goto(url);await page.evaluate(()=>document.fonts.ready);await page.screenshot({path:info.outputPath(name+'.png'),fullPage:false});}
 await page.locator('.theme-toggle').click();await page.locator('.theme-toggle').click();await page.screenshot({path:info.outputPath('night.png'),fullPage:false});
});
