"""One story workflow. Run `python scripts/story.py --help` from any directory.

Creation edits story.json; all text, narration inputs, and publishing metadata
derive from that record. Media jobs cache individual sentences and frames.
"""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape, escape
from datetime import datetime, timezone
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, wave
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache'/'storybook'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def load(slug):
    if not re.fullmatch(r'[a-z0-9-]+(?:/[a-z0-9-]+)?',slug):raise ValueError('Use a story slug such as the-princess-and-the-pea.')
    p=ROOT/slug/'story.json'
    return json.loads(p.read_text()),p

def save_json(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)

class SpokenHTML(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.stack=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);classes=a.get('class','');ignore=any(x in classes for x in ['chant-label','chant-header','sound-label','sound-header'])
        if tag=='br':self.parts.append(' ');return
        self.stack.append(ignore or bool(self.stack and self.stack[-1]))
    def handle_endtag(self,tag):
        if tag!='br' and self.stack:self.stack.pop()
        self.parts.append(' ')
    def handle_data(self,data):
        if not self.stack or not self.stack[-1]:self.parts.append(data)

def spoken(fragment):
    p=SpokenHTML();p.feed(fragment);return ' '.join(unescape(''.join(p.parts)).split())

def scene_text(scene):
    if scene.get('narrationOverride'):return scene['narrationOverride']
    return ' '.join(spoken(b['html']) for b in scene['blocks'] if b['type'] in ('paragraph','callout'))

def narration_fingerprint(s):
    return digest({'title':s['title'],'scenes':[scene_text(sc) for sc in s['scenes']],'voice':s.get('narration',{'voice':'af_heart','speed':0.92})})

def input_hash(s):
    voice=s.get('narration',{});value=[s['title'],voice.get('voice','af_heart'),voice.get('speed',.92),[[[b['type'],b['html']] for b in sc['blocks'] if b['type']!='image'] for sc in s['scenes']]]
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def visual_hash(s):
    result=[]
    for sc in s['scenes']:
        for b in sc['blocks']:
            if b['type']=='image':
                content=(ROOT/b['src']).read_bytes();result.append([b['src'],hashlib.sha1(f'blob {len(content)}\0'.encode()+content).hexdigest()])
    return hashlib.sha256(json.dumps(result,separators=(',',':')).encode()).hexdigest()

def state_path(s):return CACHE/'media'/s['id']/'state.json'
def checkpoint(s):
    p=state_path(s);return json.loads(p.read_text()) if p.exists() else {}

def export(s):
    directory=ROOT/s['id'];script=[s['title']+'.']+[scene_text(sc) for sc in s['scenes']]
    (directory/'story.txt').write_text('\n\n'.join(script)+'\n')
    md=['# '+s['title'],s.get('subtitle','')]
    if s.get('sourceUrl'):md+=['Source: '+s['sourceUrl']]
    for i,sc in enumerate(s['scenes'],1):
        md+=['\n## '+str(i)+'. '+sc['title']]
        for b in sc['blocks']:
            md.append(f"![{b['alt']}]({Path(b['src']).name})\n\n{b.get('caption','')}" if b['type']=='image' else spoken(b['html']))
    (directory/'story.md').write_text('\n\n'.join(md)+'\n')
    print('Exported story.md and exact narration input story.txt.')

def plan(s):
    prompts=[]
    for i,sc in enumerate(s['scenes'],1):
        pictures=[b for b in sc['blocks'] if b['type']=='image']
        prompts.append({'scene':i,'title':sc['title'],'narration':scene_text(sc),'illustrations':[{'file':b['src'],'prompt':b.get('prompt') or b['alt']} for b in pictures], 'style':s['artDirection']['style'],'references':s['artDirection'].get('referenceImages',[]),'continuity':'Preserve character faces, clothing, proportions, props, and setting landmarks across all images. Landscape storybook illustration; no text in the image.'})
    save_json(ROOT/s['id']/'illustration-plan.json',{'story':s['title'],'scenes':prompts})
    export(s);print('Saved illustration-plan.json. Supply the listed reference images when generating each scene.')

def new_story(args):
    slug=args.slug;dest=ROOT/slug/'story.json'
    if dest.exists():raise ValueError('This story already exists.')
    if not re.fullmatch(r'[a-z0-9-]+(?:/[a-z0-9-]+)?',slug):raise ValueError('Invalid story slug.')
    scene_count=args.scenes or (15 if args.collection=='classics' else 4)
    if scene_count<1:raise ValueError('A story needs at least one scene.')
    s={'schemaVersion':1,'id':slug,'title':args.title,'collection':args.collection,'order':999,'description':'','subtitle':'','readingLevel':'Read together' if args.collection=='classics' else 'Early reader','edition':'Illustrated classic' if args.collection=='classics' else 'Family original','sourceUrl':args.source or '', 'addedAt':datetime.now(timezone.utc).isoformat(),'cover':{'src':slug+'/scene-01.jpg','alt':''}, 'scenes':[{'id':f'scene-{i}','title':f'Scene {i}','blocks':[{'type':'paragraph','html':''},{'type':'image','src':slug+f'/scene-{i:02}.jpg','alt':'','caption':''}]} for i in range(1,scene_count+1)],'discussionHtml':'','narration':{'voice':'af_heart','speed':.92},'media':{'audio':None,'video':None,'captions':None,'duration':None},'artDirection':{'style':'Warm watercolor storybook art on cream paper with fine pencil details','referenceImages':[]}}
    save_json(dest,s);plan(s);print('Created draft; it will appear in the catalog after `publish`.')

def models_dir():return Path(os.environ.get('STORYBOOK_MODEL_DIR',str(ROOT/'.models'/'kokoro'))).expanduser()
def setup_models():
    folder=models_dir();folder.mkdir(parents=True,exist_ok=True)
    for name in ['kokoro-v1.0.onnx','voices-v1.0.bin']:
        p=folder/name
        if p.exists() and p.stat().st_size>100000:print('Already available:',name);continue
        url='https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/'+name
        temp=p.with_suffix(p.suffix+'.partial');print('Downloading',name,flush=True)
        with urlopen(url,timeout=60) as response, temp.open('wb') as out:shutil.copyfileobj(response,out)
        if temp.stat().st_size<100000:raise ValueError('Model download is incomplete: '+name)
        temp.replace(p)
    print('Free local narration model is ready in',folder)

def stamp(seconds):
    ms=round(seconds*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'

def narrate(s,p,force=False):
    fingerprint=narration_fingerprint(s);state=checkpoint(s);target=ROOT/s['id']/'narration.mp3'
    if not force and state.get('narration')==fingerprint and target.exists() and (ROOT/s['id']/'narration.vtt').exists():
        print('Narration is current; reused existing audio and captions.');return
    try:
        import numpy as np
        from kokoro_onnx import Kokoro
    except ImportError as e:raise RuntimeError('Install media tools: python -m pip install -r requirements-media.txt') from e
    folder=models_dir()
    if not all((folder/n).exists() for n in ['kokoro-v1.0.onnx','voices-v1.0.bin']):raise RuntimeError('Run: python scripts/story.py setup-models')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise RuntimeError('FFmpeg and FFprobe must be installed.')
    kokoro=Kokoro(str(folder/'kokoro-v1.0.onnx'),str(folder/'voices-v1.0.bin'))
    voice=s.get('narration',{}).get('voice','af_heart');speed=float(s.get('narration',{}).get('speed',.92))
    work=CACHE/'media'/s['id'];work.mkdir(parents=True,exist_ok=True)
    parts=[];sample_rate=None;position=0;captions=[];timed=[]
    def silence(seconds):
        nonlocal position
        chunk=np.zeros(round(seconds*sample_rate),dtype=np.float32);parts.append(chunk);position+=len(chunk)
    def speak(sentence):
        nonlocal sample_rate,position
        key=digest({'text':sentence,'voice':voice,'speed':speed,'engine':'kokoro-onnx-0.4.9','model':str(folder)})
        cached=work/(key+'.npz')
        if cached.exists():
            with np.load(cached) as packed:chunk=packed['audio'];rate=int(packed['rate'])
        else:
            chunk,rate=kokoro.create(sentence,voice=voice,speed=speed,lang='en-us');np.savez_compressed(cached,audio=chunk,rate=rate)
        if sample_rate is not None and sample_rate!=rate:raise ValueError('Narration sample rate changed between sentences.')
        sample_rate=rate;begin=position/rate;parts.append(chunk);position+=len(chunk);return begin,position/rate
    begin,end=speak(s['title']+'.');captions.append((begin,end,s['title']));silence(.65)
    for index,sc in enumerate(s['scenes']):
        start=position/sample_rate;sc['start']=0.0 if index==0 else round(start,3)
        pictures=[b for b in sc['blocks'] if b['type']=='image']
        if len(pictures)!=1:raise ValueError('Narration regeneration needs one visual beat per scene. Split scenes with multiple illustrations first; existing media is unchanged.')
        print(f"Narrating {index+1}/{len(s['scenes'])}: {sc['title']}",flush=True)
        for sentence in [x.strip() for x in re.split(r'(?<=[.!?])\s+',scene_text(sc)) if x.strip()]:
            begin,end=speak(sentence);captions.append((begin,end,sentence));silence(.25)
        timed.append({'image':Path(pictures[0]['src']).name,'start':sc['start'],'cue':sc['title']});silence(.6)
    silence(.6)
    wav=work/'narration.wav';pcm=np.clip(np.concatenate(parts),-1,1)
    with wave.open(str(wav),'wb') as out:out.setnchannels(1);out.setsampwidth(2);out.setframerate(sample_rate);out.writeframes((pcm*32767).astype('<i2').tobytes())
    temporary=target.with_name('narration.pending.mp3')
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000','-c:a','libmp3lame','-b:a','192k',str(temporary)],check=True)
    temporary.replace(target)
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(target)],text=True))
    vtt='WEBVTT\n\n'+'\n\n'.join(f'{stamp(a)} --> {stamp(b)}\n{t}' for a,b,t in captions)+'\n'
    (target.parent/'narration.vtt').write_text(vtt)
    save_json(target.parent/'narration-timings.json',{'audio':'narration.mp3','duration':duration,'timing_method':'Measured PCM sample positions','frame_size':[1280,720],'artwork_crop':None,'scenes':timed})
    s['media'].update(audio=s['id']+'/narration.mp3',captions=s['id']+'/narration.vtt',duration=duration,narrationInputHash=input_hash(s),provenance='Generated from canonical scene text using free local Kokoro narration')
    state['narration']=fingerprint;state['narrationOutput']=digest(target.read_bytes().hex());save_json(state_path(s),state);save_json(p,s);export(s)

def video(s,p,force=False):
    from PIL import Image,ImageOps,ImageFilter
    if s['media'].get('narrationInputHash')!=input_hash(s):raise ValueError('Narration is stale. Regenerate it before rendering the video.')
    timing=ROOT/s['id']/'narration-timings.json'
    if not timing.exists():raise ValueError('Generate narration and measured cues before rendering a new video.')
    timeline=json.loads(timing.read_text());audio=ROOT/s['media']['audio']
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(audio)],text=True))
    if abs(duration-timeline['duration'])>.1:raise ValueError('Narration changed. Regenerate timings before rendering.')
    cues=timeline['scenes'];starts=[c['start'] for c in cues]
    if not starts or starts[0]!=0 or any(a>=b for a,b in zip(starts,starts[1:])) or starts[-1]>=duration:raise ValueError('Scene cues must begin at zero and increase within the narration duration.')
    work=CACHE/'media'/s['id'];work.mkdir(parents=True,exist_ok=True);frames=[]
    for cue,end in zip(cues,starts[1:]+[duration]):
        source=ROOT/s['id']/cue['image'];key=digest({'file':hashlib.sha256(source.read_bytes()).hexdigest(),'size':[1280,720],'version':1});frame=work/(key+'.jpg')
        if not frame.exists():
            original=ImageOps.exif_transpose(Image.open(source)).convert('RGB');bg=ImageOps.fit(original,(1280,720)).filter(ImageFilter.GaussianBlur(28));bg=Image.eval(bg,lambda x:int(x*.4));fg=ImageOps.contain(original,(1280,720));bg.paste(fg,((1280-fg.width)//2,(720-fg.height)//2));bg.save(frame,quality=93)
        frames.append((frame,end-cue['start']))
    fingerprint=digest({'timing':timeline,'frames':[f.name for f,_ in frames],'audio':hashlib.sha256(audio.read_bytes()).hexdigest(),'encoding':'h264-crf21-aac192-v1'})
    state=checkpoint(s);output=ROOT/s['id']/'story-video.mp4'
    if not force and state.get('video')==fingerprint and output.exists():print('Video is current; reused the existing render.');return
    concat=work/'frames.txt';lines=[]
    for frame,length in frames:lines += ["file '"+frame.as_posix()+"'",'option framerate 24',f'duration {length:.6f}']
    lines += ["file '"+frames[-1][0].as_posix()+"'",'option framerate 24'];concat.write_text('\n'.join(lines)+'\n')
    pending=output.with_name('story-video.pending.mp4')
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(audio),'-t',str(duration),'-c:v','libx264','-preset','fast','-tune','stillimage','-crf','21','-pix_fmt','yuv420p','-vf','fps=24:round=near','-c:a','aac','-b:a','192k','-movflags','+faststart',str(pending)],check=True)
    pending.replace(output);poster=ROOT/s['id']/'story-video-poster.jpg';shutil.copyfile(frames[0][0],poster)
    s['media']['video']={'src':s['id']+'/story-video.mp4','poster':s['id']+'/story-video-poster.jpg'};s['media']['videoNarrationHash']=input_hash(s);s['media']['videoVisualHash']=visual_hash(s);save_json(p,s);state['video']=fingerprint;save_json(state_path(s),state);print('Rendered synchronized story-video.mp4.')

def status(s):
    state=checkpoint(s);current=state.get('narration')==narration_fingerprint(s)
    stale=s['media'].get('narrationInputHash')!=input_hash(s)
    print(json.dumps({'story':s['title'],'scenes':len(s['scenes']),'illustrations':sum(b['type']=='image' for sc in s['scenes'] for b in sc['blocks']),'narration':'needs rebuild' if stale else 'current' if current else 'existing published audio' if s['media'].get('audio') and not state else 'needs rebuild','video':bool(s['media'].get('video')),'captions':bool(s['media'].get('captions')),'checkpoints':str(state_path(s).relative_to(ROOT))},indent=2))

def publish(s):
    images=[b for sc in s['scenes'] for b in sc['blocks'] if b['type']=='image']
    if not s['description'] or any(not scene_text(sc) for sc in s['scenes']):raise ValueError('Complete the description and every scene first.')
    if s['collection']=='classics' and len(images)<12:raise ValueError('New classic stories need at least 12 finished illustrations; target 15 or more.')
    for image in images:
        if not image.get('alt') or not (ROOT/image['src']).exists():raise ValueError('Finish illustrations and alt text: '+image['src'])
    for field in ['audio','captions']:
        if not s['media'].get(field) or not (ROOT/s['media'][field]).exists():raise ValueError('Generate '+field+' first.')
    if s['collection']=='classics' and not s['media'].get('video'):raise ValueError('Render the classic story video first.')
    if checkpoint(s).get('narration')!=narration_fingerprint(s):raise ValueError('Narration is stale. Regenerate it from the final story text before publishing.')
    catalog=json.loads((ROOT/'stories.json').read_text())
    if s['id'] not in catalog['stories']:catalog['stories'].append(s['id']);save_json(ROOT/'stories.json',catalog)
    print('Added to the catalog. Run build and checks to prepare the website preview.')

def main():
    parser=argparse.ArgumentParser(description=__doc__);subs=parser.add_subparsers(dest='command',required=True)
    create=subs.add_parser('new');create.add_argument('slug');create.add_argument('--title',required=True);create.add_argument('--collection',choices=['shane','tyson','classics'],required=True);create.add_argument('--source');create.add_argument('--scenes',type=int)
    for command in ['plan','export','status','narrate','video','publish']:
        sub=subs.add_parser(command);sub.add_argument('slug')
        if command in ['narrate','video']:sub.add_argument('--force',action='store_true')
    subs.add_parser('setup-models');subs.add_parser('build');args=parser.parse_args()
    if args.command=='new':new_story(args);return
    if args.command=='setup-models':setup_models();return
    if args.command=='build':subprocess.run(['npm','run','build'],cwd=ROOT,check=True);subprocess.run(['npm','run','check'],cwd=ROOT,check=True);return
    s,p=load(args.slug)
    if args.command=='narrate':narrate(s,p,args.force)
    elif args.command=='video':video(s,p,args.force)
    elif args.command=='publish':publish(s)
    else:globals()[args.command](s)

if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError,FileNotFoundError,subprocess.CalledProcessError) as e:print('Story workflow:',e,file=sys.stderr);sys.exit(1)
