from pathlib import Path

emperor_link = '''          <a href="../the-emperors-new-clothes/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">👑</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Emperor's New Clothes</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Honesty &amp; Truth</span>
            </div>
          </a>
'''

target_files = [
    'the-little-red-hen/index.html',
    'the-three-billy-goats-gruff/index.html',
    'the-princess-and-the-pea/index.html',
    'the-gingerbread-man/index.html',
    'goldilocks-and-the-three-bears/index.html',
    'little-red-riding-hood/index.html',
    'jack-and-the-beanstalk/index.html',
    'the-three-little-pigs/index.html'
]

for tf in target_files:
    f = Path(tf)
    if not f.exists():
        continue
    txt = f.read_text(encoding='utf-8')
    if 'the-emperors-new-clothes' in txt:
        print(f'{tf}: already has emperor link')
        continue
    if '          <a href="../the-great-pontoon-pike-escape/"' in txt:
        target = '          <a href="../the-great-pontoon-pike-escape/"'
        new_txt = txt.replace(target, emperor_link + target, 1)
        f.write_text(new_txt, encoding='utf-8')
        print(f'{tf}: inserted before pontoon pike')
    elif '          <a href="../the-three-little-pigs/"' in txt:
        target = '          <a href="../the-three-little-pigs/"'
        new_txt = txt.replace(target, emperor_link + target, 1)
        f.write_text(new_txt, encoding='utf-8')
        print(f'{tf}: inserted before three little pigs')
    else:
        print(f'{tf}: anchor not found')
