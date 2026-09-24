import bpy
import math
import os
import shutil
import subprocess

def create_material(name, diffuse_color, roughness=0.5, specular=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = (*diffuse_color, 1.0)
    mat.roughness = roughness
    mat.specular_intensity = specular
    return mat

def set_smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True

def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    scene.render.engine = 'BLENDER_WORKBENCH'
    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'MATERIAL'
    sh.show_shadows = True
    sh.shadow_intensity = 0.55
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.cavity_ridge_factor = 2.2
    sh.cavity_valley_factor = 1.6
    sh.show_object_outline = True
    sh.object_outline_color = (0.15, 0.15, 0.18)
    sh.show_specular_highlight = True

    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    total_frames = 72
    scene.frame_start = 1
    scene.frame_end = total_frames

    # Materials
    mat_table = create_material("OakTable", (0.58, 0.36, 0.20), roughness=0.4, specular=0.6)
    mat_card_back = create_material("CardBackBlack", (0.12, 0.12, 0.14), roughness=0.3, specular=0.8)
    mat_card_red = create_material("UnoRed", (0.92, 0.14, 0.14), roughness=0.25, specular=0.85)
    mat_card_blue = create_material("UnoBlue", (0.08, 0.45, 0.95), roughness=0.25, specular=0.85)
    mat_card_green = create_material("UnoGreen", (0.18, 0.72, 0.28), roughness=0.25, specular=0.85)
    mat_card_yellow = create_material("UnoYellow", (1.0, 0.84, 0.08), roughness=0.25, specular=0.85)
    mat_card_white = create_material("CardWhite", (0.98, 0.98, 0.98), roughness=0.2, specular=0.9)
    mat_sparkle_gold = create_material("SparkGold", (1.0, 0.90, 0.15), roughness=0.1, specular=1.0)
    mat_sparkle_cyan = create_material("SparkCyan", (0.2, 0.90, 1.0), roughness=0.1, specular=1.0)
    mat_shockwave = create_material("Shockwave", (1.0, 1.0, 0.8), roughness=0.2, specular=0.9)

    # Camera - Dynamic tabletop view capturing both draw and discard piles
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 34
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0.0, -5.6, 4.4)
    cam_obj.rotation_euler = (math.radians(52), 0, 0)

    # Tabletop Surface
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.2))
    table = bpy.context.active_object
    table.scale = (16.0, 12.0, 0.4)
    table.data.materials.append(mat_table)

    # Helper function to create an Uno card
    def create_card(name, mat_front, location, rotation=(0, 0, 0), scale=(1.1, 1.6, 0.015)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
        card = bpy.context.active_object
        card.name = name
        card.scale = scale
        card.data.materials.append(mat_front)
        set_smooth(card)
        return card

    # ==================== DRAW PILE ====================
    # Stack of cards on left
    draw_pile_root = bpy.data.objects.new("DrawPile", None)
    draw_pile_root.location = (-1.8, 0.2, 0.0)
    scene.collection.objects.link(draw_pile_root)

    for i in range(12):
        c = create_card(f"DrawCard_{i}", mat_card_back, (-1.8, 0.2, 0.01 + i * 0.02), rotation=(0, 0, math.radians((i % 3) * 1.5)))
        c.parent = draw_pile_root

    # Top Draw Card with red oval
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.018, location=(-1.8, 0.2, 0.25), rotation=(0, 0, math.radians(45)))
    c_oval = bpy.context.active_object
    c_oval.scale = (0.7, 1.2, 1.0)
    c_oval.data.materials.append(mat_card_red)
    set_smooth(c_oval)
    c_oval.parent = draw_pile_root

    # ==================== DISCARD PILE ====================
    # Cards already played
    discard_root = bpy.data.objects.new("DiscardPile", None)
    discard_root.location = (0.2, 0.0, 0.0)
    scene.collection.objects.link(discard_root)

    # Under cards
    c_blue = create_card("Discard_Blue7", mat_card_blue, (0.15, -0.05, 0.01), rotation=(0, 0, math.radians(-12)))
    c_blue.parent = discard_root

    c_green = create_card("Discard_GreenRev", mat_card_green, (0.25, 0.08, 0.025), rotation=(0, 0, math.radians(18)))
    c_green.parent = discard_root

    c_yellow = create_card("Discard_YellowSkip", mat_card_yellow, (0.20, 0.02, 0.04), rotation=(0, 0, math.radians(-5)))
    c_yellow.parent = discard_root

    # ==================== SHANE'S WILD DRAW FOUR CARD ====================
    wild_root = bpy.data.objects.new("WildCardRoot", None)
    scene.collection.objects.link(wild_root)

    # Card base body (Black border)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    wild_card = bpy.context.active_object
    wild_card.name = "WildCard"
    wild_card.scale = (1.15, 1.65, 0.02)
    wild_card.data.materials.append(mat_card_back)
    set_smooth(wild_card)
    wild_card.parent = wild_root

    # Inner 4-Color Quadrant Oval
    quadrant_colors = [
        (mat_card_red,    (-0.22,  0.30)),
        (mat_card_blue,   ( 0.22,  0.30)),
        (mat_card_yellow, (-0.22, -0.30)),
        (mat_card_green,  ( 0.22, -0.30))
    ]
    for q_mat, (qx, qy) in quadrant_colors:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(qx, qy, 0.015))
        quad = bpy.context.active_object
        quad.scale = (0.42, 0.58, 0.01)
        quad.data.materials.append(q_mat)
        set_smooth(quad)
        quad.parent = wild_root

    # White Center "+4" emblem
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.025, location=(0, 0, 0.02))
    emblem = bpy.context.active_object
    emblem.data.materials.append(mat_card_white)
    set_smooth(emblem)
    emblem.parent = wild_root

    # ==================== 4 FLYING PENALTY CARDS FOR DAD ====================
    penalty_cards = []
    pen_mats = [mat_card_red, mat_card_blue, mat_card_green, mat_card_yellow]
    for i, pmat in enumerate(pen_mats):
        c = create_card(f"PenaltyCard_{i}", pmat, (0, 0, -1.0))
        penalty_cards.append(c)

    # ==================== IMPACT SHOCKWAVE ====================
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.03, location=(0.2, 0.0, 0.05))
    shockwave = bpy.context.active_object
    shockwave.name = "ImpactShockwave"
    shockwave.data.materials.append(mat_shockwave)
    set_smooth(shockwave)

    # ==================== CELEBRATION SPARKS ====================
    sparks = []
    for i in range(24):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(0.2, 0.0, -1.0))
        spk = bpy.context.active_object
        spk.name = f"UnoSpark_{i}"
        s_mat = mat_sparkle_gold if (i % 2 == 0) else mat_sparkle_cyan
        spk.data.materials.append(s_mat)
        set_smooth(spk)
        sparks.append(spk)

    # ==================== ANIMATIONS ====================
    # 1. Wild Card Swoop, 360 Spin, & Slam Down!
    wild_keyframes = [
        # Frame, (x, y, z), (roll, pitch, yaw)
        (1,  (0.0, -3.2, 1.8),  (math.radians(-45), 0, 0)),
        (15, (0.0, -2.6, 2.2),  (math.radians(-25), math.radians(45), math.radians(90))),
        (25, (0.1, -1.2, 2.5),  (math.radians(-10), math.radians(120), math.radians(180))),
        (32, (0.2, -0.4, 1.4),  (math.radians(-5),  math.radians(240), math.radians(270))),
        # Frame 36: SLAM DOWN IMPACT!
        (36, (0.2, 0.0, 0.06),  (0, 0, math.radians(360))),
        # Bounce rebound
        (39, (0.2, 0.0, 0.18),  (math.radians(4), math.radians(-3), math.radians(362))),
        # Settle flat on discard pile
        (43, (0.2, 0.0, 0.065), (0, 0, math.radians(360))),
        (72, (0.2, 0.0, 0.065), (0, 0, math.radians(360))),
    ]

    for f, loc, rot in wild_keyframes:
        wild_root.location = loc
        wild_root.rotation_euler = rot
        wild_root.keyframe_insert(data_path="location", frame=f)
        wild_root.keyframe_insert(data_path="rotation_euler", frame=f)

    # 2. Impact Shockwave Expansion (Frames 36 to 48)
    shockwave.scale = (0.1, 0.1, 0.1)
    shockwave.location = (0.2, 0.0, -1.0) # Hidden
    shockwave.keyframe_insert(data_path="scale", frame=1)
    shockwave.keyframe_insert(data_path="location", frame=1)
    shockwave.keyframe_insert(data_path="location", frame=35)

    shockwave.location = (0.2, 0.0, 0.055)
    shockwave.keyframe_insert(data_path="location", frame=36)
    shockwave.scale = (0.4, 0.4, 0.4)
    shockwave.keyframe_insert(data_path="scale", frame=36)

    shockwave.scale = (3.2, 3.2, 0.1)
    shockwave.keyframe_insert(data_path="scale", frame=46)

    shockwave.location = (0.2, 0.0, -1.0)
    shockwave.keyframe_insert(data_path="location", frame=47)

    # 3. 4 Penalty Cards Shoot to Dad Alex's Side (Frames 38 to 60)
    for i, c in enumerate(penalty_cards):
        c.location = (0.2, 0.0, -1.0)
        c.keyframe_insert(data_path="location", frame=1)
        c.keyframe_insert(data_path="location", frame=37)

        # Starts at discard pile at frame 38
        c.location = (0.2, 0.0, 0.1 + i * 0.02)
        c.rotation_euler = (0, 0, 0)
        c.keyframe_insert(data_path="location", frame=38)
        c.keyframe_insert(data_path="rotation_euler", frame=38)

        # Flies across table toward Dad (positive Y)
        target_x = -1.2 + i * 0.8
        target_y = 2.4
        c.location = (target_x * 0.6, 1.2, 0.8 + (i % 2) * 0.2)
        c.rotation_euler = (math.radians(-15), math.radians((i - 1.5) * 15), math.radians((i - 1.5) * 20))
        c.keyframe_insert(data_path="location", frame=46)
        c.keyframe_insert(data_path="rotation_euler", frame=46)

        # Lands neatly in Dad's penalty hand
        c.location = (target_x, target_y, 0.02 + i * 0.015)
        c.rotation_euler = (math.radians(-5), 0, math.radians((i - 1.5) * 12))
        c.keyframe_insert(data_path="location", frame=56)
        c.keyframe_insert(data_path="rotation_euler", frame=56)

        c.keyframe_insert(data_path="location", frame=72)
        c.keyframe_insert(data_path="rotation_euler", frame=72)

    # 4. Victory Sparks Shower (Frames 38 to 70)
    for i, spk in enumerate(sparks):
        spk.location = (0.2, 0.0, -1.0)
        spk.keyframe_insert(data_path="location", frame=1)
        spk.keyframe_insert(data_path="location", frame=37)

        angle = (i / len(sparks)) * 2 * math.pi
        v_h = 0.9 + (i % 4) * 0.4
        v_z = 2.2 + (i % 5) * 0.45

        for f in range(38, 68):
            dt = (f - 38) / 28.0
            sx = 0.2 + math.cos(angle) * v_h * dt * 2.2
            sy = math.sin(angle) * v_h * dt * 2.2
            sz = 0.1 + v_z * dt * 2.4 - 0.5 * 9.8 * (dt ** 2) * 0.45
            spk.location = (sx, sy, sz)
            spk.keyframe_insert(data_path="location", frame=f)

        spk.location = (0.2, 0.0, -1.0)
        spk.keyframe_insert(data_path="location", frame=69)

    # 5. Camera cinematic push-in
    cam_obj.location = (0.0, -5.6, 4.4)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.location = (0.1, -4.2, 3.4)
    cam_obj.keyframe_insert(data_path="location", frame=72)

    return scene

def render_animation(output_dir, video_path, poster_path):
    os.makedirs(output_dir, exist_ok=True)
    scene = build_scene()

    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        frame_file = os.path.join(output_dir, f"frame_{f:04d}.png")
        scene.render.filepath = frame_file
        bpy.ops.render.render(write_still=True)

    # Encode with FFmpeg
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-i", os.path.join(output_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-crf", "22",
        "-movflags", "+faststart",
        video_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)

    # Poster at frame 42 (Wild Card slam + penalty cards flying + sparks!)
    poster_src = os.path.join(output_dir, "frame_0042.png")
    if os.path.exists(poster_src):
        shutil.copyfile(poster_src, poster_path)

    shutil.rmtree(output_dir, ignore_errors=True)

if __name__ == "__main__":
    out_dir = r"c:\Users\stans\Stories\temp_frames_uno"
    target_mp4 = r"c:\Users\stans\Stories\the-wild-uno-uproar\uno_animation.mp4"
    target_poster = r"c:\Users\stans\Stories\the-wild-uno-uproar\uno_animation_poster.png"
    render_animation(out_dir, target_mp4, target_poster)
    print("UNO_ANIMATION_COMPLETE")
