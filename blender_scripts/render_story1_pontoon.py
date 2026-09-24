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

    # Workbench render settings
    scene.render.engine = 'BLENDER_WORKBENCH'
    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'MATERIAL'
    sh.show_shadows = True
    sh.shadow_intensity = 0.5
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.cavity_ridge_factor = 2.0
    sh.cavity_valley_factor = 1.5
    sh.show_object_outline = True
    sh.object_outline_color = (0.18, 0.22, 0.26)
    sh.show_specular_highlight = True

    # Resolution & Frame Rate
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    total_frames = 72
    scene.frame_start = 1
    scene.frame_end = total_frames

    # Materials
    mat_water = create_material("Water", (0.16, 0.62, 0.88), roughness=0.1, specular=0.95)
    mat_pontoon = create_material("PontoonAluminum", (0.85, 0.88, 0.90), roughness=0.25, specular=0.85)
    mat_deck = create_material("WoodDeck", (0.78, 0.60, 0.42), roughness=0.7, specular=0.2)
    mat_rail = create_material("WhiteRail", (0.96, 0.96, 0.98), roughness=0.2, specular=0.7)
    mat_canopy = create_material("NavyCanopy", (0.10, 0.25, 0.55), roughness=0.5, specular=0.4)
    mat_frame = create_material("FrameSilver", (0.4, 0.42, 0.46), roughness=0.3, specular=0.7)
    mat_seat = create_material("SeatBlue", (0.2, 0.45, 0.75), roughness=0.5, specular=0.4)
    mat_rod = create_material("YellowRod", (1.0, 0.78, 0.05), roughness=0.2, specular=0.9)
    mat_fish_body = create_material("BassGreen", (0.24, 0.70, 0.35), roughness=0.2, specular=0.9)
    mat_fish_belly = create_material("BassBelly", (0.95, 0.94, 0.78), roughness=0.3, specular=0.6)
    mat_fish_fin = create_material("BassFin", (0.42, 0.85, 0.50), roughness=0.25, specular=0.8)
    mat_eye_white = create_material("EyeWhite", (1.0, 1.0, 1.0), roughness=0.1, specular=0.95)
    mat_eye_pupil = create_material("EyePupil", (0.05, 0.05, 0.05), roughness=0.1, specular=0.95)
    mat_splash = create_material("SplashWater", (0.85, 0.95, 1.0), roughness=0.1, specular=0.98)
    mat_shore = create_material("ShorePine", (0.16, 0.40, 0.20), roughness=0.8, specular=0.1)
    mat_trunk = create_material("TrunkBrown", (0.42, 0.26, 0.15), roughness=0.8, specular=0.1)

    # Camera positioned for a dynamic, expansive storybook view
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 45
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (8.5, -10.5, 5.8)
    cam_obj.rotation_euler = (math.radians(62), 0, math.radians(40))

    # Water Plane
    bpy.ops.mesh.primitive_plane_add(size=35, location=(0, 0, -0.05))
    water = bpy.context.active_object
    water.name = "WaterSurface"
    water.data.materials.append(mat_water)

    # Distant Shoreline trees
    for i in range(-7, 8):
        tx = i * 2.5 + (i % 2) * 0.5
        ty = 13.0 + (abs(i) % 3) * 1.2
        # Trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.0, location=(tx, ty, 0.5))
        ctrunk = bpy.context.active_object
        ctrunk.data.materials.append(mat_trunk)
        # Foliage cones
        for layer, (cr, cz) in enumerate([(1.2, 1.5), (0.9, 2.3), (0.6, 3.0)]):
            bpy.ops.mesh.primitive_cone_add(radius1=cr, depth=1.2, location=(tx, ty, cz))
            cf = bpy.context.active_object
            cf.data.materials.append(mat_shore)
            set_smooth(cf)

    # ==================== PONTOON BOAT ASSEMBLY ====================
    boat_root = bpy.data.objects.new("BoatRoot", None)
    boat_root.location = (-0.5, 0.0, 0.0)
    scene.collection.objects.link(boat_root)

    # Aluminum Pontoons
    for side, y_offset in [("Left", -1.35), ("Right", 1.35)]:
        # Cylinder tube
        bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=5.4, location=(0, y_offset, 0.25), rotation=(0, math.radians(90), 0))
        tube = bpy.context.active_object
        tube.name = f"PontoonTube_{side}"
        tube.data.materials.append(mat_pontoon)
        set_smooth(tube)
        tube.parent = boat_root

        # Front tapered cone nose
        bpy.ops.mesh.primitive_cone_add(radius1=0.45, depth=1.2, location=(3.3, y_offset, 0.25), rotation=(0, math.radians(90), 0))
        nose = bpy.context.active_object
        nose.name = f"PontoonNose_{side}"
        nose.data.materials.append(mat_pontoon)
        set_smooth(nose)
        nose.parent = boat_root

    # Deck Floor
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.72))
    deck = bpy.context.active_object
    deck.scale = (5.6, 3.4, 0.12)
    deck.data.materials.append(mat_deck)
    deck.parent = boat_root

    # Perimeter Rails
    # Left & Right Rails
    for y, name in [(-1.65, "RailLeft"), (1.65, "RailRight")]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y, 1.25))
        rail = bpy.context.active_object
        rail.name = name
        rail.scale = (5.4, 0.08, 0.95)
        rail.data.materials.append(mat_rail)
        rail.parent = boat_root

    # Front & Back Rails
    for x, name in [(2.7, "RailFront"), (-2.7, "RailBack")]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 1.25))
        rail = bpy.context.active_object
        rail.name = name
        rail.scale = (0.08, 3.3, 0.95)
        rail.data.materials.append(mat_rail)
        rail.parent = boat_root

    # Bimini Canopy Top
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.9, 0, 2.9))
    canopy = bpy.context.active_object
    canopy.name = "Canopy"
    canopy.scale = (2.8, 3.3, 0.12)
    canopy.data.materials.append(mat_canopy)
    canopy.parent = boat_root

    # Canopy Frame Poles
    for cx in [-2.1, 0.3]:
        for cy in [-1.58, 1.58]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.9, location=(cx, cy, 1.95))
            cpole = bpy.context.active_object
            cpole.data.materials.append(mat_frame)
            cpole.parent = boat_root

    # Steering Console
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, 0.7, 1.25))
    console = bpy.context.active_object
    console.scale = (0.9, 0.9, 0.95)
    console.data.materials.append(mat_pontoon)
    console.parent = boat_root

    # Steering Wheel
    bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.04, location=(0.4, 0.7, 1.6), rotation=(0, math.radians(45), 0))
    wheel = bpy.context.active_object
    wheel.data.materials.append(mat_frame)
    wheel.parent = boat_root

    # Comfortable Captain & Passenger Seats
    for sx, sy in [(-1.5, -0.9), (-1.5, 0.9), (0.7, -0.9)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, sy, 1.05))
        seat = bpy.context.active_object
        seat.scale = (1.1, 0.85, 0.55)
        seat.data.materials.append(mat_seat)
        seat.parent = boat_root

    # ==================== FISHING ROD ====================
    rod_empty = bpy.data.objects.new("RodPivot", None)
    rod_empty.location = (2.2, -1.65, 1.45)
    rod_empty.rotation_euler = (math.radians(-12), math.radians(22), math.radians(-32))
    scene.collection.objects.link(rod_empty)
    rod_empty.parent = boat_root

    # Rod Shaft
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=2.5, location=(0, 0, 1.25))
    rod = bpy.context.active_object
    rod.name = "FishingRod"
    rod.data.materials.append(mat_rod)
    rod.parent = rod_empty

    # Reel
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.15, location=(0.08, 0, 0.45), rotation=(math.radians(90), 0, 0))
    reel = bpy.context.active_object
    reel.data.materials.append(mat_frame)
    reel.parent = rod_empty

    # Bobber in water
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(3.8, -3.2, 0.0))
    bobber = bpy.context.active_object
    bobber.name = "Bobber"
    bobber.data.materials.append(mat_rod)
    set_smooth(bobber)

    # ==================== BASS FISH MESH ====================
    fish_root = bpy.data.objects.new("FishRoot", None)
    fish_root.location = (3.8, -3.2, -1.8)
    scene.collection.objects.link(fish_root)

    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(0, 0, 0))
    fish_body = bpy.context.active_object
    fish_body.scale = (1.5, 0.45, 0.75)
    fish_body.data.materials.append(mat_fish_body)
    set_smooth(fish_body)
    fish_body.parent = fish_root

    # Belly
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.48, location=(0.05, 0, -0.15))
    fish_belly = bpy.context.active_object
    fish_belly.scale = (1.3, 0.40, 0.5)
    fish_belly.data.materials.append(mat_fish_belly)
    set_smooth(fish_belly)
    fish_belly.parent = fish_root

    # Tail fin
    bpy.ops.mesh.primitive_cone_add(radius1=0.48, depth=0.6, location=(-1.05, 0, 0), rotation=(0, math.radians(-90), 0))
    fish_tail = bpy.context.active_object
    fish_tail.scale = (0.2, 0.85, 1.25)
    fish_tail.data.materials.append(mat_fish_fin)
    set_smooth(fish_tail)
    fish_tail.parent = fish_root

    # Dorsal fin
    bpy.ops.mesh.primitive_cone_add(radius1=0.38, depth=0.55, location=(0.1, 0, 0.55), rotation=(math.radians(20), 0, 0))
    fish_dorsal = bpy.context.active_object
    fish_dorsal.scale = (0.85, 0.15, 0.95)
    fish_dorsal.data.materials.append(mat_fish_fin)
    set_smooth(fish_dorsal)
    fish_dorsal.parent = fish_root

    # Big cartoon eyes
    for ey in [0.24, -0.24]:
        # White
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(0.60, ey, 0.16))
        eye_w = bpy.context.active_object
        eye_w.data.materials.append(mat_eye_white)
        set_smooth(eye_w)
        eye_w.parent = fish_root
        # Pupil
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0.68, ey * 1.08, 0.17))
        eye_p = bpy.context.active_object
        eye_p.data.materials.append(mat_eye_pupil)
        set_smooth(eye_p)
        eye_p.parent = fish_root

    # Splash droplets
    splash_drops = []
    for i in range(16):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(3.8, -3.2, -2.0))
        drop = bpy.context.active_object
        drop.name = f"SplashDrop_{i}"
        drop.data.materials.append(mat_splash)
        set_smooth(drop)
        splash_drops.append(drop)

    # ==================== KEYFRAMES ====================
    # 1. Boat gentle bobbing & rocking
    for frame in range(1, total_frames + 1):
        t = frame / total_frames * 2 * math.pi * 3
        bz = math.sin(t) * 0.07
        b_roll = math.cos(t) * math.radians(2.0)
        b_pitch = math.sin(t * 0.8) * math.radians(1.4)

        boat_root.location.z = bz
        boat_root.rotation_euler = (b_roll, b_pitch, 0)
        boat_root.keyframe_insert(data_path="location", frame=frame)
        boat_root.keyframe_insert(data_path="rotation_euler", frame=frame)

        # Bobber bobbing & bite dip
        bob_z = math.sin(t * 1.5) * 0.04
        if 20 <= frame <= 34:
            bob_z -= 0.4 * math.sin((frame - 20) / 14 * math.pi)
        bobber.location.z = bob_z
        bobber.keyframe_insert(data_path="location", frame=frame)

        # Rod bending under fish tension
        rod_bend = 0.0
        if 22 <= frame <= 58:
            rod_bend = math.radians(24) * math.sin((frame - 22) / 36 * math.pi)
        rod_empty.rotation_euler.x = math.radians(-12) - rod_bend
        rod_empty.keyframe_insert(data_path="rotation_euler", frame=frame)

    # 2. Fish leap arc
    fish_root.location = (3.8, -3.2, -1.8)
    fish_root.rotation_euler = (0, 0, math.radians(-45))
    fish_root.keyframe_insert(data_path="location", frame=1)
    fish_root.keyframe_insert(data_path="rotation_euler", frame=1)
    fish_root.keyframe_insert(data_path="location", frame=24)

    # Apex at frame 42
    fish_root.location = (3.4, -2.4, 1.9)
    fish_root.rotation_euler = (math.radians(-22), math.radians(35), math.radians(32))
    fish_root.keyframe_insert(data_path="location", frame=42)
    fish_root.keyframe_insert(data_path="rotation_euler", frame=42)

    # Splashdown at frame 58
    fish_root.location = (2.7, -1.7, -1.8)
    fish_root.rotation_euler = (math.radians(-38), math.radians(-48), math.radians(65))
    fish_root.keyframe_insert(data_path="location", frame=58)
    fish_root.keyframe_insert(data_path="rotation_euler", frame=58)

    fish_root.location = (2.7, -1.7, -2.5)
    fish_root.keyframe_insert(data_path="location", frame=72)

    # Tail flapping
    for frame in range(25, 59):
        tw = math.sin((frame - 25) * 1.3) * math.radians(38)
        fish_tail.rotation_euler.z = tw
        fish_tail.keyframe_insert(data_path="rotation_euler", frame=frame)

    # 3. Splash droplets
    for i, drop in enumerate(splash_drops):
        angle = (i / len(splash_drops)) * 2 * math.pi
        speed_h = 0.9 + (i % 3) * 0.4
        speed_v = 1.7 + (i % 4) * 0.35

        drop.location = (3.8, -3.2, -1.5)
        drop.keyframe_insert(data_path="location", frame=1)
        drop.keyframe_insert(data_path="location", frame=26)

        # Eruption 1: Fish breach (frame 27 to 44)
        for f in range(27, 45):
            dt = (f - 27) / 17.0
            dx = math.cos(angle) * speed_h * dt * 1.6
            dy = math.sin(angle) * speed_h * dt * 1.6
            dz = speed_v * dt * 2.3 - 0.5 * 9.8 * (dt ** 2) * 0.42
            drop.location = (3.8 + dx, -3.2 + dy, dz)
            drop.keyframe_insert(data_path="location", frame=f)

        # Eruption 2: Splash back down (frame 56 to 68)
        drop.location = (2.7, -1.7, -1.5)
        drop.keyframe_insert(data_path="location", frame=55)
        for f in range(56, 69):
            dt = (f - 56) / 12.0
            dx = math.cos(angle * 1.4) * speed_h * dt * 1.3
            dy = math.sin(angle * 1.4) * speed_h * dt * 1.3
            dz = speed_v * dt * 1.9 - 0.5 * 9.8 * (dt ** 2) * 0.46
            drop.location = (2.7 + dx, -1.7 + dy, dz)
            drop.keyframe_insert(data_path="location", frame=f)

        drop.location = (2.7, -1.7, -2.0)
        drop.keyframe_insert(data_path="location", frame=72)

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

    # Save Poster image at peak of jump (frame 42)
    poster_src = os.path.join(output_dir, "frame_0042.png")
    if os.path.exists(poster_src):
        shutil.copyfile(poster_src, poster_path)

    # Cleanup temp
    shutil.rmtree(output_dir, ignore_errors=True)

if __name__ == "__main__":
    out_dir = r"c:\Users\stans\Stories\temp_frames_pontoon"
    target_mp4 = r"c:\Users\stans\Stories\the-houghton-lake-patrol\pontoon_animation.mp4"
    target_poster = r"c:\Users\stans\Stories\the-houghton-lake-patrol\pontoon_animation_poster.png"
    render_animation(out_dir, target_mp4, target_poster)
    print("PONTOON_ANIMATION_COMPLETE")
