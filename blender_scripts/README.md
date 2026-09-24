# 3D Blender Story Animations

This folder contains the automated Blender Python scripts used to generate the 3D animated scenes embedded at the bottom of each story page.

## Animations

1. **`render_story1_pontoon.py`**  
   *Story 1: The Houghton Lake Pontoon Patrol*  
   - 3D Aluminum pontoon boat bobbing and swaying on lake water waves.
   - Yellow fishing rod with dynamic tension bend.
   - Animated green bass fish leaping out of the water with animated splash droplets.

2. **`render_story2_disc.py`**  
   *Story 2: The Daring Disc Golf Dash*  
   - Whispering Woods fairway framed by stylized pine trees and tee pad.
   - Detailed disc golf basket with top band and dynamic swinging chains.
   - Orange "Roadrunner" disc carving an S-curve hyzer flight directly into the chains with celebratory sparks.

3. **`render_story3_bike.py`**  
   *Story 3: The Bouncing Bicycle Brigade*  
   - Kid's bicycle with spinning spoke wheels, handlebars, red grips, and bell.
   - Winding dirt trail and trailside fence posts.
   - Dynamic puddle impact with water droplet spray and hill crest jump.

4. **`render_story4_sled.py`**  
   *Story 4: The Super Snowy Sled*  
   - Cherry-red rocket sled with dual steel runners and pull rope.
   - Snowy mountain slope and snow-covered evergreen trees.
   - Downhill speed run, airborne jump, and sideways drift stop next to a steaming mug of hot cocoa with marshmallows.

5. **`render_story5_uno.py`**  
   *Story 5: The Wild Uno Uproar*  
   - Cozy oak dining table with draw pile and discard pile.
   - Game-winning Wild Draw Four card performing a 360° mid-air spin and impact slam.
   - Four penalty cards launching across the table to Dad with victory star fireworks.

## How to Run

Requirements: Blender 4.2+ and FFmpeg in PATH.

```powershell
& "path/to/blender.exe" -b -P blender_scripts/render_story1_pontoon.py
& "path/to/blender.exe" -b -P blender_scripts/render_story2_disc.py
& "path/to/blender.exe" -b -P blender_scripts/render_story3_bike.py
& "path/to/blender.exe" -b -P blender_scripts/render_story4_sled.py
& "path/to/blender.exe" -b -P blender_scripts/render_story5_uno.py
```
