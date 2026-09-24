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
    mat_grass = create_material("MeadowGrass", (0.32, 0.66, 0.26), roughness=0.8, specular=0.15)
    mat_trail = create_material("DirtTrail", (0.72, 0.58, 0.38), roughness=0.9, specular=0.1)
    mat_puddle = create_material("PuddleWater", (0.18, 0.55, 0.78), roughness=0.1, specular=0.95)
    mat_bike_blue = create_material("BikeBlue", (0.10, 0.45, 0.95), roughness=0.25, specular=0.9)
    mat_tire = create_material("TireRubber", (0.12, 0.12, 0.14), roughness=0.8, specular=0.2)
    mat_rim = create_material("RimSilver", (0.85, 0.88, 0.92), roughness=0.2, specular=0.9)
    mat_metal = create_material("FrameMetal", (0.75, 0.78, 0.82), roughness=0.3, specular=0.8)
    mat_seat = create_material("SeatBlack", (0.15, 0.15, 0.16), roughness=0.6, specular=0.3)
    mat_grip = create_material("GripRed", (0.95, 0.18, 0.15), roughness=0.4, specular=0.6)
    mat_bell = create_material("BellGold", (1.0, 0.82, 0.1), roughness=0.2, specular=0.95)
    mat_splash = create_material("SplashDrop", (0.82, 0.94, 1.0), roughness=0.1, specular=0.98)
    mat_fence = create_material("WoodFence", (0.50, 0.34, 0.20), roughness=0.8, specular=0.1)
    mat_tree = create_material("HillTree", (0.18, 0.48, 0.22), roughness=0.7, specular=0.2)

    # Camera
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 38
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (5.5, -6.8, 3.2)
    cam_obj.rotation_euler = (math.radians(72), 0, math.radians(40))

    # Landscape Ground
    bpy.ops.mesh.primitive_plane_add(size=35, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.data.materials.append(mat_grass)

    # Winding Trail (Curved Strip)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.02))
    trail = bpy.context.active_object
    trail.scale = (2.2, 32.0, 0.02)
    trail.data.materials.append(mat_trail)

    # Puddle (Elliptical glossy puddle on trail)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=0.04, location=(0, 0.5, 0.04))
    puddle = bpy.context.active_object
    puddle.scale = (0.9, 1.6, 1.0)
    puddle.data.materials.append(mat_puddle)
    set_smooth(puddle)

    # Trailside Wooden Fence Posts
    for y in [-8, -4, 0, 4, 8, 12]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.2, location=(-1.8, y, 0.6))
        post = bpy.context.active_object
        post.data.materials.append(mat_fence)
        set_smooth(post)

    # Background Trees on Rolling Hills
    for tx, ty in [(-4.5, 8.0), (-5.2, 2.0), (-4.8, -6.0), (4.5, 7.0), (5.2, 1.0), (4.8, -5.0)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.2, location=(tx, ty, 0.6))
        trunk = bpy.context.active_object
        trunk.data.materials.append(mat_fence)
        for layer, (cr, cz) in enumerate([(1.3, 1.4), (0.95, 2.1), (0.6, 2.7)]):
            bpy.ops.mesh.primitive_cone_add(radius1=cr, depth=1.1, location=(tx, ty, cz))
            cone = bpy.context.active_object
            cone.data.materials.append(mat_tree)
            set_smooth(cone)

    # ==================== SHANE'S BICYCLE ====================
    bike_root = bpy.data.objects.new("BikeRoot", None)
    scene.collection.objects.link(bike_root)

    # Front Wheel Assembly
    front_wheel_empty = bpy.data.objects.new("FrontWheelPivot", None)
    front_wheel_empty.location = (0, 1.25, 0.55)
    scene.collection.objects.link(front_wheel_empty)
    front_wheel_empty.parent = bike_root

    # Front Tire (Torus with axle along X axis)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.08, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    f_tire = bpy.context.active_object
    f_tire.data.materials.append(mat_tire)
    set_smooth(f_tire)
    f_tire.parent = front_wheel_empty

    # Front Rim & Spokes
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.04, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    f_rim = bpy.context.active_object
    f_rim.data.materials.append(mat_rim)
    f_rim.parent = front_wheel_empty

    # Rear Wheel Assembly
    rear_wheel_empty = bpy.data.objects.new("RearWheelPivot", None)
    rear_wheel_empty.location = (0, -1.25, 0.55)
    scene.collection.objects.link(rear_wheel_empty)
    rear_wheel_empty.parent = bike_root

    # Rear Tire
    bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.08, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    r_tire = bpy.context.active_object
    r_tire.data.materials.append(mat_tire)
    set_smooth(r_tire)
    r_tire.parent = rear_wheel_empty

    # Rear Rim
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.04, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    r_rim = bpy.context.active_object
    r_rim.data.materials.append(mat_rim)
    r_rim.parent = rear_wheel_empty

    # Main Frame (Diamond/Kid Geometry Tubes)
    # Bottom bracket to rear hub
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=1.35, location=(0, -0.65, 0.55), rotation=(math.radians(90), 0, 0))
    chainstay = bpy.context.active_object
    chainstay.data.materials.append(mat_bike_blue)
    chainstay.parent = bike_root

    # Seat tube (Vertical-ish)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=1.1, location=(0, -0.1, 1.05), rotation=(math.radians(-15), 0, 0))
    seattube = bpy.context.active_object
    seattube.data.materials.append(mat_bike_blue)
    seattube.parent = bike_root

    # Top tube (Horizontal)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=1.2, location=(0, 0.5, 1.35), rotation=(math.radians(90), 0, 0))
    toptube = bpy.context.active_object
    toptube.data.materials.append(mat_bike_blue)
    toptube.parent = bike_root

    # Down tube (Diagonal)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1.5, location=(0, 0.55, 0.95), rotation=(math.radians(45), 0, 0))
    downtube = bpy.context.active_object
    downtube.data.materials.append(mat_bike_blue)
    downtube.parent = bike_root

    # Front Fork
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=1.15, location=(0, 1.15, 0.95), rotation=(math.radians(-20), 0, 0))
    fork = bpy.context.active_object
    fork.data.materials.append(mat_bike_blue)
    fork.parent = bike_root

    # Handlebars & Stem
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.95, location=(0, 1.05, 1.55), rotation=(0, math.radians(90), 0))
    hbar = bpy.context.active_object
    hbar.data.materials.append(mat_metal)
    hbar.parent = bike_root

    # Grips
    for gx in [-0.45, 0.45]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.18, location=(gx, 1.05, 1.55), rotation=(0, math.radians(90), 0))
        grp = bpy.context.active_object
        grp.data.materials.append(mat_grip)
        grp.parent = bike_root

    # Bicycle Bell on right grip
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(0.32, 1.08, 1.62))
    bell = bpy.context.active_object
    bell.data.materials.append(mat_bell)
    set_smooth(bell)
    bell.parent = bike_root

    # Saddle / Seat
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.22, 1.55))
    saddle = bpy.context.active_object
    saddle.scale = (0.24, 0.48, 0.12)
    saddle.data.materials.append(mat_seat)
    saddle.parent = bike_root

    # Pedals
    for px, pdir in [(-0.35, 1), (0.35, -1)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, -0.05, 0.55 + 0.15 * pdir))
        pdl = bpy.context.active_object
        pdl.scale = (0.16, 0.22, 0.05)
        pdl.data.materials.append(mat_seat)
        pdl.parent = bike_root

    # ==================== SPLASH PARTICLES ====================
    splash_drops = []
    for i in range(20):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0.5, -1.0))
        drop = bpy.context.active_object
        drop.name = f"BikeSplash_{i}"
        drop.data.materials.append(mat_splash)
        set_smooth(drop)
        splash_drops.append(drop)

    # ==================== ANIMATIONS ====================
    # 1. Bike Forward Travel, Bounce & Jump
    # Path: rolls from y = -9 to y = 8
    travel_keys = [
        # Frame, (x, y, z), (roll, pitch, yaw)
        (1,  (0, -9.0, 0.0), (0, 0, 0)),
        (15, (0, -4.5, 0.0), (math.radians(2), 0, 0)),
        (25, (0, -0.5, 0.0), (0, 0, 0)),
        # Frame 28: Hits puddle!
        (28, (0, 0.5, -0.04), (math.radians(-3), 0, 0)),
        # Frame 32: Bounces over bump after puddle!
        (33, (0, 2.0, 0.12), (math.radians(2), math.radians(-8), 0)),
        (38, (0, 3.5, 0.45), (0, math.radians(-14), 0)), # Airborne wheelie bounce!
        (44, (0, 5.0, 0.18), (0, math.radians(6), 0)),   # Front lands
        (48, (0, 6.0, 0.02), (0, 0, 0)),                  # Rear settles
        (72, (0, 11.0, 0.5), (math.radians(2), math.radians(-6), 0)), # Zooming up Big Bumpy Hill!
    ]

    for f, loc, rot in travel_keys:
        bike_root.location = loc
        bike_root.rotation_euler = rot
        bike_root.keyframe_insert(data_path="location", frame=f)
        bike_root.keyframe_insert(data_path="rotation_euler", frame=f)

    # 2. Wheel Rotations in sync with speed
    for f in range(1, total_frames + 1):
        wheel_rot = -f * 0.45
        front_wheel_empty.rotation_euler.x = wheel_rot
        rear_wheel_empty.rotation_euler.x = wheel_rot
        front_wheel_empty.keyframe_insert(data_path="rotation_euler", frame=f)
        rear_wheel_empty.keyframe_insert(data_path="rotation_euler", frame=f)

    # 3. Puddle Splash Eruption (Frames 27 to 48)
    for i, drop in enumerate(splash_drops):
        side = -1.0 if (i % 2 == 0) else 1.0
        angle = (i / len(splash_drops)) * math.pi
        v_side = 1.2 + (i % 4) * 0.45
        v_fwd = 0.6 + (i % 3) * 0.3
        v_up = 2.4 + (i % 5) * 0.4

        drop.location = (0, 0.5, -1.0)
        drop.keyframe_insert(data_path="location", frame=1)
        drop.keyframe_insert(data_path="location", frame=27)

        for f in range(28, 46):
            dt = (f - 28) / 18.0
            dx = side * (0.3 + v_side * dt * 2.0)
            dy = 0.5 + v_fwd * dt * 2.5
            dz = 0.05 + v_up * dt * 2.0 - 0.5 * 9.8 * (dt ** 2) * 0.4
            drop.location = (dx, dy, dz)
            drop.keyframe_insert(data_path="location", frame=f)

        drop.location = (0, 0.5, -1.0)
        drop.keyframe_insert(data_path="location", frame=47)

    # 4. Camera tracking the bike as it splashes and flies over the hill
    cam_obj.location = (5.6, -4.5, 3.0)
    cam_obj.rotation_euler = (math.radians(70), 0, math.radians(48))
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.location = (5.2, -1.0, 2.7)
    cam_obj.keyframe_insert(data_path="location", frame=30)
    cam_obj.location = (4.8, 4.0, 3.2)
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

    # Poster image at frame 30 (water splash erupting around bike!)
    poster_src = os.path.join(output_dir, "frame_0030.png")
    if os.path.exists(poster_src):
        shutil.copyfile(poster_src, poster_path)

    shutil.rmtree(output_dir, ignore_errors=True)

if __name__ == "__main__":
    out_dir = r"c:\Users\stans\Stories\temp_frames_bike"
    target_mp4 = r"c:\Users\stans\Stories\the-bouncing-bicycle-brigade\biking_animation.mp4"
    target_poster = r"c:\Users\stans\Stories\the-bouncing-bicycle-brigade\biking_animation_poster.png"
    render_animation(out_dir, target_mp4, target_poster)
    print("BIKING_ANIMATION_COMPLETE")
