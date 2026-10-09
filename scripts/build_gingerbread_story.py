"""Build the Gingerbread Man page using the existing Goldilocks layout.

Default builds require the finished illustrations, narration, and video.
Use --draft for a review page that omits media that has not been created.
"""
import argparse
import html
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STORY = json.loads((ROOT / 'scripts/gingerbread_story.json').read_text(encoding='utf-8'))
OUT = ROOT / STORY['slug']


def esc(value):
    return html.escape(str(value), quote=True)


def navigation(href, active=False):
    return f'''          <a href="{href}" class="story-menu-link{' active' if active else ''}" role="menuitem">
            <span class="menu-link-icon">🍪</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Gingerbread Man</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Run, Run, as Fast as You Can!</span>
            </div>
          </a>
'''


def figure(scene):
    if not (OUT / scene['image']).is_file():
        return ''
    from PIL import Image
    with Image.open(OUT / scene['image']) as image:
        width, height = image.size
    return f'''      <figure class="story-figure">
        <div class="figure-img-wrapper" onclick="openLightbox(this)">
          <img src="{scene['image']}" alt="{esc(scene['alt'])}" loading="{'eager' if scene['number'] == 1 else 'lazy'}" width="{width}" height="{height}">
          <span class="figure-overlay-hint">🔍 Zoom</span>
        </div>
        <figcaption>{esc(scene['caption'])}</figcaption>
      </figure>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    images = [s['image'] for s in STORY['scenes']]
    required = images + ['narration.mp3', 'narration.vtt', 'narration-timings.json',
                         'gingerbread_story_video.mp4', 'gingerbread_story_video_poster.jpg']
    missing = [name for name in required if not (OUT / name).is_file()]
    if missing and not args.draft:
        raise SystemExit('Finished media required before publishing: ' + ', '.join(missing))

    template = (ROOT / 'goldilocks-and-the-three-bears/index.html').read_text(encoding='utf-8')
    template = re.sub(r'          <a href="../the-gingerbread-man/".*?</a>\n', '', template, flags=re.S)
    template = template.replace('Goldilocks and the Three Bears', STORY['title'])
    template = template.replace('goldilocks_story_video', 'gingerbread_story_video')
    template = template.replace('Classic Fairy Tale • Too Hot, Too Cold, Just Right',
                                'Classic Fairy Tale • Run, Run, as Fast as You Can!')
    template = template.replace('🥣 Classic Fairy Tale', '🍪 Classic Fairy Tale')
    template = template.replace('<span class="menu-link-icon">🥣</span>', '<span class="menu-link-icon">🍪</span>', 1)
    template = template.replace('Goldilocks and the <span class="highlight-word">Three Bears</span>',
                                'The <span class="highlight-word">Gingerbread Man</span>')
    template = template.replace('The classic tale of three bears, three bowls of porridge — and one very curious little girl!', STORY['subtitle'])
    template = template.replace('Classic read-aloud voice narration with music and expressive sound',
                                'A complete read-aloud of the story')
    template = template.replace('Read The Gingerbread Man with 12 illustrations, full voice narration, and a narrated story video.',
                                'Read The Gingerbread Man, a classic fairy tale about a runaway cookie, with a complete read-aloud narration.' if args.draft else
                                'Read The Gingerbread Man with 12 watercolor illustrations, full voice narration, and a synchronized narrated story video.')
    words = sum(len(p.split()) for s in STORY['scenes'] for p in s['paragraphs'])
    words += sum(len(s.get('chant', '').split()) for s in STORY['scenes'])
    minutes = math.ceil(words / 160)
    template = template.replace('6-7 min read', f'{minutes} min read')
    available = sum((OUT / name).is_file() for name in images)
    if available == 0:
        template = template.replace('        <span class="meta-item">🎨 <strong>12 Story Illustrations</strong></span>\n        <span>•</span>\n', '')
    elif available != 12:
        template = template.replace('12 Story Illustrations', f'{available} Story Illustrations')

    timings_path = OUT / 'narration-timings.json'
    timings = json.loads(timings_path.read_text(encoding='utf-8')) if timings_path.is_file() else {}
    duration = timings.get('audio_duration', timings.get('duration', 0))
    template = template.replace('418.10', str(duration or 1))
    template = template.replace('6:58', f'{int(duration // 60)}:{int(duration % 60):02}')
    if timings.get('draft'):
        template = template.replace('A complete read-aloud of the story', 'Computer read-aloud narration')
    if not (OUT / 'narration.mp3').is_file():
        template = re.sub(r'      <!-- Audio Narration Player -->.*?      </div>\s*    </section>', '    </section>', template, flags=re.S)
        template = template.replace('        <span class="meta-item">🎙️ <strong>Voice Narration</strong></span>\n        <span>•</span>\n', '')

    articles = []
    manuscript = [f"# {STORY['title']}", STORY['subtitle']]
    for scene in STORY['scenes']:
        number = scene['number']
        lines = [f'    <article class="scene-section" id="scene-{number}">',
                 f'      <div class="scene-header"><span class="scene-pill">Scene {number} • {esc(scene["heading"])}</span></div>']
        manuscript.append(f'## {scene["heading"]}')
        for index, paragraph in enumerate(scene['paragraphs']):
            css = 'lead-paragraph story-text' if number == 1 and index == 0 else 'story-text'
            lines.append(f'      <p class="{css}">{esc(paragraph)}</p>')
            manuscript.append(paragraph)
        if scene.get('chant'):
            lines.append('      <div class="chant-box goldilocks"><div class="chant-speaker">🍪 The Gingerbread Man</div>'
                         f'<p class="chant-text story-text">{esc(scene["chant"])}</p></div>')
            manuscript.append(f'> {scene["chant"]}')
        lines.append(figure(scene))
        lines.append('    </article>')
        articles.append('\n'.join(lines))
    start = template.index('    <!-- SCENE 1 -->')
    end = template.index('    <!-- Full Narration with Synchronized Story Illustrations -->')
    template = template[:start] + '\n\n'.join(articles) + '\n\n' + template[end:]
    if not (OUT / 'gingerbread_story_video.mp4').is_file():
        start = template.index('    <!-- Full Narration with Synchronized Story Illustrations -->')
        end = template.index('    <!-- Footer -->', start)
        template = template[:start] + template[end:]
    source = ('A read-aloud retelling of the classic tale by George Haven Putnam. '
              '<a href="https://americanliterature.com/childrens-stories/the-gingerbread-man">Read the source story</a>.')
    template = template.replace('Classic Fairy Tale • Illustrated in vintage Edwardian storybook watercolor style', source)
    anchor = '          <a href="../little-red-riding-hood/"'
    goldilocks_nav = '''          <a href="../goldilocks-and-the-three-bears/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🥣</span><div class="menu-link-text">
              <strong class="menu-link-title">Goldilocks and the Three Bears</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Too Hot, Too Cold, Just Right</span>
            </div>
          </a>
'''
    template = template.replace(anchor, goldilocks_nav + anchor, 1)
    (OUT / 'index.html').write_text(template, encoding='utf-8')
    manuscript.append('---\nA fresh retelling of the cook, Mouser, Towser, Jocko, and Bobby version. '
                      f'[Source story]({STORY["source_url"]}). '
                      f'[Public-domain original by George Haven Putnam]({STORY["public_domain_source"]}).')
    (OUT / 'story.md').write_text('\n\n'.join(manuscript) + '\n', encoding='utf-8')

    hub_path = ROOT / 'index.html'
    hub = hub_path.read_text(encoding='utf-8')
    image = f'''<img src="{STORY['slug']}/gingerbread_07.jpg" alt="The gingerbread man laughing on the garden wall." loading="lazy" width="1280" height="720">''' if (OUT / 'gingerbread_07.jpg').is_file() else ''
    card = f'''        <!-- Classic Story 5: The Gingerbread Man -->
        <a href="the-gingerbread-man/" class="story-card">
          <div class="card-img-wrapper">
            {image}
            <span class="card-badge">🍪 Classic Tale</span>
            {'<span class="card-anim-tag">🎙️ Voice Narration</span>' if (OUT / 'narration.mp3').is_file() else ''}
            <span class="card-time">⏱️ {minutes} min</span>
          </div>
          <div class="card-body">
            <span class="card-theme-tag tag-red">Classic Fairy Tale{' • 12 Illustrations' if available == 12 else ''}</span>
            <h3 class="card-title">The Gingerbread Man</h3>
            <p class="card-chant-preview">&quot;Run, run, as fast as you can! You can&apos;t catch me, I&apos;m the Gingerbread Man!&quot;</p>
            <div class="card-footer"><span>Read Story &amp; Listen to Narration</span><span class="card-arrow">➔</span></div>
          </div>
        </a>
        <!-- End Gingerbread Man Card -->
'''
    marker = '        <!-- Classic Story 5: The Gingerbread Man -->'
    if marker in hub:
        hub = re.sub(re.escape(marker) + r'.*?        <!-- End Gingerbread Man Card -->\n', card, hub, flags=re.S)
    else:
        position = hub.index('      </div>\n    </section>', hub.index('id="classics-stories"'))
        hub = hub[:position] + card + '\n' + hub[position:]
    hub_path.write_text(hub, encoding='utf-8')
    for slug in ['goldilocks-and-the-three-bears', 'little-red-riding-hood', 'jack-and-the-beanstalk', 'the-three-little-pigs']:
        path = ROOT / slug / 'index.html'
        if not path.is_file():
            continue
        content = path.read_text(encoding='utf-8')
        if 'href="../the-gingerbread-man/"' not in content:
            content = content.replace('id="story-menu-dropdown" class="story-dropdown-menu" role="menu" aria-label="Bedtime stories list">',
                                      'id="story-menu-dropdown" class="story-dropdown-menu" role="menu" aria-label="Bedtime stories list">\n' + navigation('../the-gingerbread-man/'), 1)
            path.write_text(content, encoding='utf-8')
    print(f'Built {words}-word story in {len(STORY["scenes"])} scenes. Missing media: {len(missing)}. Draft: {args.draft}')


if __name__ == '__main__':
    main()
