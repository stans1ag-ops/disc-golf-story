from pathlib import Path

hen_link = '''          <a href="../the-little-red-hen/" class="story-menu-link" role="menuitem">
            <span class="menu-link-icon">🐔</span>
            <div class="menu-link-text">
              <strong class="menu-link-title">The Little Red Hen</strong>
              <span class="menu-link-desc">Classic Fairy Tale • Hard Work &amp; Golden Bread</span>
            </div>
          </a>
'''

target_files = [
    'the-three-billy-goats-gruff/index.html',
    'the-princess-and-the-pea/index.html',
    'the-gingerbread-man/index.html',
    'goldilocks-and-the-three-bears/index.html'
]

for tf in target_files:
    f = Path(tf)
    txt = f.read_text(encoding='utf-8')
    if 'the-little-red-hen' in txt:
        print(f'{tf}: already has hen link')
        continue
    if '          <a href="../the-great-pontoon-pike-escape/"' in txt:
        target = '          <a href="../the-great-pontoon-pike-escape/"'
        new_txt = txt.replace(target, hen_link + target, 1)
        f.write_text(new_txt, encoding='utf-8')
        print(f'{tf}: inserted before pontoon pike')
    elif '          <a href="../the-three-little-pigs/"' in txt:
        target = '          <a href="../the-three-little-pigs/"'
        new_txt = txt.replace(target, hen_link + target, 1)
        f.write_text(new_txt, encoding='utf-8')
        print(f'{tf}: inserted before three little pigs')
    else:
        print(f'{tf}: anchor not found')
