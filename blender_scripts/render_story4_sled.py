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
    sh.shadow_intensity = 0.52
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.cavity_ridge_factor = 2.0
    sh.cavity_valley_factor = 1.6
    sh.show_object_outline = True
    sh.object_outline_color = (0.18, 0.20, 0.24)
    sh.show_specular_highlight = True

    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    total_frames = 72
    scene.frame_start = 1
    scene.frame_end = total_frames

    # Materials
    mat_snow = create_material("SnowWhite", (0.95, 0.97, 1.0), roughness=0.6, specular=0.85)
    mat_snow_powder = create_material("SnowPowder", (1.0, 1.0, 1.0), roughness=0.3, specular=0.95)
    mat_pine = create_material("SnowPine", (0.15, 0.40, 0.22), roughness=0.7, specular=0.2)
    mat_tree_snow = create_material("TreeSnowCap", (0.98, 0.99, 1.0), roughness=0.5, specular=0.7)
    mat_trunk = create_material("TrunkWood", (0.38, 0.24, 0.14), roughness=0.8, specular=0.1)
    mat_sled_red = create_material("SledRed", (0.94, 0.14, 0.14), roughness=0.2, specular=0.95)
    mat_steel = create_material("RunnerSteel", (0.86, 0.89, 0.93), roughness=0.2, specular=0.95)
    mat_wood = create_material("SledWood", (0.75, 0.52, 0.32), roughness=0.6, specular=0.3)
    mat_rope = create_material("SledRope", (0.96, 0.82, 0.25), roughness=0.7, specular=0.2)
    mat_mug_red = create_material("MugRed", (0.88, 0.12, 0.18), roughness=0.25, specular=0.85)
    mat_cocoa = create_material("HotCocoa", (0.30, 0.16, 0.10), roughness=0.2, specular=0.7)
    mat_marshmallow = create_material("Marshmallow", (0.98, 0.98, 0.95), roughness=0.4, specular=0.4)
    mat_steam = create_material("SteamSmoke", (0.95, 0.97, 1.0), roughness=0.3, specular=0.2)

    # Camera
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 38
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (6.0, -8.2, 4.5)
    cam_obj.rotation_euler = (math.radians(65), 0, math.radians(40))

    # Flat Snow Finish Area
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, -4.0, 0))
    snow_flat = bpy.context.active_object
    snow_flat.data.materials.append(mat_snow)

    # Snowy Hill Slope (Slopes up into the background)
    bpy.ops.mesh.primitive_plane_add(size=25, location=(0, 7.5, 1.8), rotation=(math.radians(16), 0, 0))
    snow_slope = bpy.context.active_object
    snow_slope.scale = (1.4, 1.0, 1.0)
    snow_slope.data.materials.append(mat_snow)

    # Pine Trees with Snow Caps (positioned on the sides)
    tree_coords = [
        (-5.5, 9.0, 2.5), (-5.0, 4.0, 1.2), (-4.8, -2.0, 0.0),
        (5.5, 9.5, 2.7), (5.2, 4.5, 1.3), (5.0, -1.5, 0.0)
    ]
    for tx, ty, tz in tree_coords:
        # Trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=1.6, location=(tx, ty, tz + 0.8))
        trunk = bpy.context.active_object
        trunk.data.materials.append(mat_trunk)

        # Foliage cones with snow caps
        for layer, (cr, cz) in enumerate([(1.4, 1.6), (1.1, 2.4), (0.75, 3.1)]):
            bpy.ops.mesh.primitive_cone_add(radius1=cr, depth=1.1, location=(tx, ty, tz + cz))
            fcone = bpy.context.active_object
            fcone.data.materials.append(mat_pine)
            set_smooth(fcone)

            bpy.ops.mesh.primitive_cone_add(radius1=cr * 0.92, depth=0.35, location=(tx, ty, tz + cz + 0.28))
            snowcap = bpy.context.active_object
            snowcap.data.materials.append(mat_tree_snow)
            set_smooth(snowcap)

    # Rustic Wood Stump with Hot Cocoa at the finish
    stump_pos = (2.2, -3.2, 0.45)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=0.9, location=stump_pos)
    stump = bpy.context.active_object
    stump.data.materials.append(mat_wood)
    set_smooth(stump)

    # Red Cocoa Mug
    mug_pos = (2.2, -3.2, 1.15)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=0.52, location=mug_pos)
    mug = bpy.context.active_object
    mug.data.materials.append(mat_mug_red)
    set_smooth(mug)

    # Cocoa liquid inside mug
    bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=0.04, location=(2.2, -3.2, 1.38))
    cocoa_liq = bpy.context.active_object
    cocoa_liq.data.materials.append(mat_cocoa)

    # Marshmallows
    for mx, my, mz in [(2.12, -3.15, 1.44), (2.28, -3.25, 1.44), (2.15, -3.32, 1.44)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.10, location=(mx, my, mz))
        msh = bpy.context.active_object
        msh.data.materials.append(mat_marshmallow)
        set_smooth(msh)

    # Cocoa Steam Puffs
    steam_puffs = []
    for i in range(4):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08 + i * 0.03, location=(2.2, -3.2, 1.55 + i * 0.2))
        steam = bpy.context.active_object
        steam.data.materials.append(mat_steam)
        set_smooth(steam)
        steam_puffs.append(steam)

    # ==================== RED ROCKET SLED ====================
    sled_root = bpy.data.objects.new("SledRoot", None)
    scene.collection.objects.link(sled_root)

    # Red Deck
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.32))
    sled_body = bpy.context.active_object
    sled_body.name = "SledBody"
    sled_body.scale = (1.1, 2.4, 0.12)
    sled_body.data.materials.append(mat_sled_red)
    set_smooth(sled_body)
    sled_body.parent = sled_root

    # Curved Front Cowling Nose
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.12, location=(0, 1.2, 0.42), rotation=(0, math.radians(90), 0))
    sled_nose = bpy.context.active_object
    sled_nose.data.materials.append(mat_sled_red)
    set_smooth(sled_nose)
    sled_nose.parent = sled_root

    # Dual Steel Runner Blades
    for rx in [-0.48, 0.48]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.4, location=(rx, 0, 0.12), rotation=(math.radians(90), 0, 0))
        runner = bpy.context.active_object
        runner.data.materials.append(mat_steel)
        set_smooth(runner)
        runner.parent = sled_root

        # Front curved runner tip
        bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.04, location=(rx, 1.15, 0.25), rotation=(0, math.radians(90), 0))
        tip = bpy.context.active_object
        tip.data.materials.append(mat_steel)
        set_smooth(tip)
        tip.parent = sled_root

        for sy in [-0.8, 0.0, 0.8]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.22, location=(rx, sy, 0.22))
            strut = bpy.context.active_object
            strut.data.materials.append(mat_steel)
            strut.parent = sled_root

    # Pull Rope
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.8, location=(0, 1.5, 0.55), rotation=(math.radians(-30), 0, 0))
    rope = bpy.context.active_object
    rope.data.materials.append(mat_rope)
    rope.parent = sled_root

    # Snow powder spray
    powder_particles = []
    for i in range(20):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075 + (i % 3) * 0.02, location=(0, 0, -2.0))
        p = bpy.context.active_object
        p.name = f"SnowPowder_{i}"
        p.data.materials.append(mat_snow_powder)
        set_smooth(p)
        powder_particles.append(p)

    # Falling Snowflakes
    snowflakes = []
    for i in range(16):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(-3.0 + (i % 5) * 1.5, -4.0 + (i // 5) * 3.0, 2.5 + (i % 4) * 0.8))
        flake = bpy.context.active_object
        flake.data.materials.append(mat_snow_powder)
        snowflakes.append(flake)

    # ==================== ANIMATIONS ====================
    # Sled keyframes: comes down the slope, hits flat ground, drifts sideways to a stop right by cocoa!
    sled_keyframes = [
        # Frame, (x, y, z), (roll, pitch, yaw)
        (1,  (-1.5, 11.0, 3.2),  (math.radians(-10), math.radians(-16), math.radians(12))),
        (14, (-0.8, 6.5, 1.8),   (math.radians(-12), math.radians(-16), math.radians(8))),
        (24, (0.0, 2.5, 0.75),   (math.radians(6),   math.radians(-14), math.radians(-5))),
        # Transitions to flat snow at y = 0
        (30, (0.1, 0.5, 0.25),   (0, math.radians(-5), 0)),
        (36, (0.1, -1.2, 0.35),  (0, math.radians(4), math.radians(-15))), # Air bounce over snow drift
        (42, (0.0, -2.5, 0.12),  (0, 0, math.radians(-35))),                # Lands on flat snow
        # Frame 48-56: Epic sideways drift stop!
        (48, (-0.3, -3.3, 0.12), (math.radians(-12), 0, math.radians(-65))),
        (54, (-0.6, -3.8, 0.12), (math.radians(-4),  0, math.radians(-85))),
        (60, (-0.7, -3.8, 0.12), (0, 0, math.radians(-90))), # Settled right next to hot cocoa!
        (72, (-0.7, -3.8, 0.12), (0, 0, math.radians(-90))),
    ]

    for f, loc, rot in sled_keyframes:
        sled_root.location = loc
        sled_root.rotation_euler = rot
        sled_root.keyframe_insert(data_path="location", frame=f)
        sled_root.keyframe_insert(data_path="rotation_euler", frame=f)

    # Snow spray during drift (frames 44 to 58)
    for i, p in enumerate(powder_particles):
        p.location = (0, 0, -2.0)
        p.keyframe_insert(data_path="location", frame=1)

        burst_f = 43 + (i % 6)
        p.keyframe_insert(data_path="location", frame=burst_f)

        side_sign = 1.0 if (i % 2 == 0) else -1.0
        v_h = 0.9 + (i % 4) * 0.35
        v_z = 1.3 + (i % 3) * 0.4

        for f in range(burst_f + 1, burst_f + 16):
            if f > 72: break
            dt = (f - burst_f) / 15.0
            px = -0.4 + side_sign * v_h * dt * 1.8
            py = -3.2 - v_h * dt * 0.7
            pz = 0.12 + v_z * dt * 1.4 - 0.5 * 9.8 * (dt ** 2) * 0.4
            p.location = (px, py, pz)
            p.keyframe_insert(data_path="location", frame=f)

        if burst_f + 16 <= 72:
            p.location = (0, 0, -2.0)
            p.keyframe_insert(data_path="location", frame=burst_f + 16)

    # Snowflakes
    for i, flake in enumerate(snowflakes):
        start_z = flake.location.z
        for f in range(1, total_frames + 1):
            fz = start_z - (f / total_frames) * 1.5
            fx = flake.location.x + math.sin(f * 0.1 + i) * 0.08
            fy = flake.location.y + math.cos(f * 0.1 + i) * 0.08
            flake.location = (fx, fy, fz)
            flake.keyframe_insert(data_path="location", frame=f)

    # Cocoa Steam Puffs
    for i, steam in enumerate(steam_puffs):
        for f in range(1, total_frames + 1):
            phase = (f / total_frames) * 2 * math.pi + i
            sz = 1.55 + i * 0.20 + math.sin(phase) * 0.05
            sx = 2.2 + math.cos(phase * 0.8) * 0.04
            steam.location = (sx, -3.2, sz)
            steam.keyframe_insert(data_path="location", frame=f)

    # Camera subtle glide
    cam_obj.location = (6.0, -8.2, 4.5)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.location = (5.2, -6.8, 3.8)
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

    # Poster at frame 52 (sled sideways drift next to cocoa!)
    poster_src = os.path.join(output_dir, "frame_0052.png")
    if os.path.exists(poster_src):
        shutil.copyfile(poster_src, poster_path)

    shutil.rmtree(output_dir, ignore_errors=True)

if __name__ == "__main__":
    out_dir = r"c:\Users\stans\Stories\temp_frames_sled"
    target_mp4 = r"c:\Users\stans\Stories\the-super-snowy-sled\sledding_animation.mp4"
    target_poster = r"c:\Users\stans\Stories\the-super-snowy-sled\sledding_animation_poster.png"
    render_animation(out_dir, target_mp4, target_poster)
    print("SLEDDING_ANIMATION_COMPLETE")
