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
    sh.object_outline_color = (0.18, 0.20, 0.22)
    sh.show_specular_highlight = True

    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    total_frames = 72
    scene.frame_start = 1
    scene.frame_end = total_frames

    # Materials
    mat_grass = create_material("GrassGreen", (0.34, 0.68, 0.28), roughness=0.8, specular=0.15)
    mat_fairway = create_material("Fairway", (0.28, 0.60, 0.24), roughness=0.8, specular=0.15)
    mat_pine = create_material("PineGreen", (0.15, 0.44, 0.20), roughness=0.7, specular=0.2)
    mat_trunk = create_material("WoodTrunk", (0.42, 0.26, 0.16), roughness=0.8, specular=0.1)
    mat_metal = create_material("BasketMetal", (0.78, 0.82, 0.86), roughness=0.3, specular=0.85)
    mat_band = create_material("YellowBand", (1.0, 0.82, 0.05), roughness=0.25, specular=0.9)
    mat_disc = create_material("OrangeDisc", (1.0, 0.38, 0.04), roughness=0.2, specular=0.92)
    mat_disc_center = create_material("WhiteCenter", (0.98, 0.98, 0.98), roughness=0.2, specular=0.9)
    mat_chain = create_material("ChainSilver", (0.88, 0.90, 0.94), roughness=0.2, specular=0.95)
    mat_teepad = create_material("ConcretePad", (0.65, 0.65, 0.66), roughness=0.9, specular=0.1)
    mat_spark = create_material("GoldSpark", (1.0, 0.92, 0.2), roughness=0.1, specular=1.0)

    # Camera
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 40
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (5.6, -7.8, 3.6)
    cam_obj.rotation_euler = (math.radians(70), 0, math.radians(35))

    # Ground & Fairway
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.data.materials.append(mat_grass)

    # Tee Pad in background
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.5, 9.0, 0.03))
    teepad = bpy.context.active_object
    teepad.scale = (1.8, 3.2, 0.06)
    teepad.data.materials.append(mat_teepad)

    # Forest Trees framing the fairway (spaced out)
    tree_coords = [
        (-4.5, 5.0), (-5.0, 1.0), (-4.8, -2.8), (-3.5, 8.5),
        (4.2, 6.2), (5.0, 2.0), (5.2, -2.2), (4.5, 9.0)
    ]
    for tx, ty in tree_coords:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=1.6, location=(tx, ty, 0.8))
        trunk = bpy.context.active_object
        trunk.data.materials.append(mat_trunk)
        for layer, (cr, cz) in enumerate([(1.4, 1.8), (1.1, 2.6), (0.7, 3.3)]):
            bpy.ops.mesh.primitive_cone_add(radius1=cr, depth=1.3, location=(tx, ty, cz))
            cone = bpy.context.active_object
            cone.data.materials.append(mat_pine)
            set_smooth(cone)

    # ==================== DISC GOLF BASKET ====================
    # Center Pole
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=2.4, location=(0, 0, 1.2))
    pole = bpy.context.active_object
    pole.data.materials.append(mat_metal)
    set_smooth(pole)

    # Top Yellow Band
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=0.24, location=(0, 0, 2.12))
    band = bpy.context.active_object
    band.data.materials.append(mat_band)
    set_smooth(band)

    # Top Rim Cap
    bpy.ops.mesh.primitive_cylinder_add(radius=0.78, depth=0.04, location=(0, 0, 2.25))
    cap = bpy.context.active_object
    cap.data.materials.append(mat_metal)

    # Basket Cage (Lower Catch Tray)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.78, depth=0.38, location=(0, 0, 1.05))
    basket_outer = bpy.context.active_object
    basket_outer.data.materials.append(mat_metal)
    set_smooth(basket_outer)

    # Inner floor of basket
    bpy.ops.mesh.primitive_cylinder_add(radius=0.74, depth=0.04, location=(0, 0, 0.88))
    basket_floor = bpy.context.active_object
    basket_floor.data.materials.append(mat_metal)

    # Chains (12 outer chains hanging from top band to lower ring)
    chain_links = []
    num_chains = 12
    for i in range(num_chains):
        angle = (i / num_chains) * 2 * math.pi
        cx = math.cos(angle) * 0.52
        cy = math.sin(angle) * 0.52

        # Pivot empty at top band
        chain_pivot = bpy.data.objects.new(f"ChainPivot_{i}", None)
        chain_pivot.location = (cx, cy, 2.0)
        scene.collection.objects.link(chain_pivot)

        # Hanging chain cylinder
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.88, location=(0, 0, -0.44))
        chain = bpy.context.active_object
        chain.name = f"Chain_{i}"
        chain.data.materials.append(mat_chain)
        set_smooth(chain)
        chain.parent = chain_pivot
        chain_links.append((chain_pivot, angle))

    # ==================== FLYING DISC ====================
    disc_root = bpy.data.objects.new("DiscRoot", None)
    scene.collection.objects.link(disc_root)

    # Outer Orange Rim
    bpy.ops.mesh.primitive_cylinder_add(radius=0.38, depth=0.05, location=(0, 0, 0))
    disc_body = bpy.context.active_object
    disc_body.data.materials.append(mat_disc)
    set_smooth(disc_body)
    disc_body.parent = disc_root

    # Center Star Stamp
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.052, location=(0, 0, 0.002))
    disc_stamp = bpy.context.active_object
    disc_stamp.data.materials.append(mat_disc_center)
    set_smooth(disc_stamp)
    disc_stamp.parent = disc_root

    # ==================== VICTORY SPARKS ====================
    sparks = []
    for i in range(16):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(0, 0, 1.05))
        spk = bpy.context.active_object
        spk.name = f"Spark_{i}"
        spk.data.materials.append(mat_spark)
        set_smooth(spk)
        sparks.append(spk)

    # ==================== ANIMATIONS ====================
    # 1. Disc Flight Path (Frames 1 to 40)
    # Starts at tee pad in background, glides on beautiful S-curve hyzer flip into basket!
    flight_keyframes = [
        # Frame, (x, y, z), (roll, pitch, yaw)
        (1,  (-1.5, 9.0, 1.8),  (math.radians(-15), math.radians(10), 0)),
        (10, (-0.8, 6.5, 2.2),  (math.radians(-12), math.radians(6), 0)),
        (20, (0.6, 4.0, 2.1),   (math.radians(8), math.radians(4), 0)),
        (28, (0.4, 2.2, 1.85),  (math.radians(15), math.radians(2), 0)),
        (34, (0.05, 0.55, 1.55), (math.radians(20), math.radians(-5), 0)),
        # IMPACT WITH CHAINS at frame 36!
        (36, (0.0, 0.12, 1.48), (math.radians(35), math.radians(-15), 0)),
        # Deflect and drop into tray
        (40, (0.02, 0.05, 1.18), (math.radians(45), math.radians(-5), 0)),
        (44, (0.05, -0.05, 0.95), (math.radians(10), math.radians(5), 0)),
        (48, (0.08, -0.02, 0.92), (0, 0, 0)),
        (72, (0.08, -0.02, 0.92), (0, 0, 0)),
    ]

    for f, loc, rot in flight_keyframes:
        disc_root.location = loc
        disc_root.rotation_euler = rot
        disc_root.keyframe_insert(data_path="location", frame=f)
        disc_root.keyframe_insert(data_path="rotation_euler", frame=f)

    # Disc high-speed spin (rotates around its own local axis)
    for f in range(1, 41):
        disc_body.rotation_euler.z = f * 1.8
        disc_body.keyframe_insert(data_path="rotation_euler", frame=f)

    # 2. Chains Rattle / Reaction on Impact (Frames 35 to 65)
    for pivot, angle in chain_links:
        pivot.rotation_euler = (0, 0, 0)
        pivot.keyframe_insert(data_path="rotation_euler", frame=1)
        pivot.keyframe_insert(data_path="rotation_euler", frame=35)

        # Impact at frame 36-38: chains burst outward away from center!
        sway_dir_x = math.cos(angle) * math.radians(32)
        sway_dir_y = math.sin(angle) * math.radians(32)
        pivot.rotation_euler = (sway_dir_y, -sway_dir_x, 0)
        pivot.keyframe_insert(data_path="rotation_euler", frame=38)

        # Swing back inward and oscillate
        pivot.rotation_euler = (-sway_dir_y * 0.6, sway_dir_x * 0.6, 0)
        pivot.keyframe_insert(data_path="rotation_euler", frame=44)

        pivot.rotation_euler = (sway_dir_y * 0.3, -sway_dir_x * 0.3, 0)
        pivot.keyframe_insert(data_path="rotation_euler", frame=52)

        pivot.rotation_euler = (0, 0, 0)
        pivot.keyframe_insert(data_path="rotation_euler", frame=65)

    # 3. Victory Star Sparks (Frames 42 to 72)
    for i, spk in enumerate(sparks):
        spk.location = (0, 0, -1.0) # Hidden inside basket pole initially
        spk.keyframe_insert(data_path="location", frame=1)
        spk.keyframe_insert(data_path="location", frame=41)

        angle = (i / len(sparks)) * 2 * math.pi
        v_h = 0.8 + (i % 3) * 0.4
        v_z = 2.2 + (i % 4) * 0.5

        for f in range(42, 68):
            dt = (f - 42) / 24.0
            sx = math.cos(angle) * v_h * dt * 1.5
            sy = math.sin(angle) * v_h * dt * 1.5
            sz = 1.05 + v_z * dt * 1.8 - 0.5 * 9.8 * (dt ** 2) * 0.35
            spk.location = (sx, sy, sz)
            spk.keyframe_insert(data_path="location", frame=f)

        spk.location = (0, 0, -1.0)
        spk.keyframe_insert(data_path="location", frame=69)

    # 4. Camera subtle glide push-in for climax
    cam_obj.location = (5.6, -7.8, 3.6)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.location = (4.4, -6.0, 2.9)
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

    # Poster at frame 38 (moment of chain smash!)
    poster_src = os.path.join(output_dir, "frame_0038.png")
    if os.path.exists(poster_src):
        shutil.copyfile(poster_src, poster_path)

    shutil.rmtree(output_dir, ignore_errors=True)

if __name__ == "__main__":
    out_dir = r"c:\Users\stans\Stories\temp_frames_disc"
    target_mp4 = r"c:\Users\stans\Stories\the-daring-disc-dash\disc_golf_animation.mp4"
    target_poster = r"c:\Users\stans\Stories\the-daring-disc-dash\disc_golf_animation_poster.png"
    render_animation(out_dir, target_mp4, target_poster)
    print("DISC_GOLF_ANIMATION_COMPLETE")
