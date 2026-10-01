"""Tyson's first loose tooth: modeled family, animated trampoline and fairy.

Blender 4.3.2; no illustration planes are used in the film. Camera edits and
character actions follow the recorded stanza timings. The four page pictures
are authored storybook stills from these same reference-inspired characters.
"""
import argparse
import json
import math
from pathlib import Path
import random
import subprocess
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tyson' / 'the-tooth-that-took-a-bounce'
BUILD = ROOT / '.renders' / 'loose-tooth'
FPS = 12
random.seed(71)


def mat(name, rgb):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*rgb, 1)
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*rgb, 1)
    shader.inputs['Roughness'].default_value = .72
    return material


def attach(obj, name, material=None, parent=None):
    obj.name = name
    if material:
        obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    if obj.type == 'MESH':
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return obj


def group(name, location=(0, 0, 0), parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.parent = parent
    return obj


def ball(name, location, scale, material, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=location)
    obj = bpy.context.object
    obj.scale = scale
    return attach(obj, name, material, parent)


def cube(name, location, scale, material, parent=None, bevel=.035):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new('Rounded storybook edges', 'BEVEL')
        modifier.width, modifier.segments = bevel, 3
        obj.modifiers.new('Soft normals', 'WEIGHTED_NORMAL')
    attach(obj, name, material, parent)
    for polygon in obj.data.polygons:
        polygon.use_smooth = False
    return obj


def line(name, points, radius, material, parent=None, cyclic=False):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions, curve.bevel_depth, curve.bevel_resolution = '3D', radius, 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for vertex, point in zip(spline.points, points):
        vertex.co = (*point, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    return attach(obj, name, material, parent)


def ring(name, location, radius, thickness, material, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=10,
                                   location=location, major_radius=radius, minor_radius=thickness)
    return attach(bpy.context.object, name, material, parent)


def text(name, words, location, size, material, parent=None, rotation=(0, 0, 0)):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body, curve.size, curve.extrude = words, size, .0005
    curve.space_line = 1.3
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location, obj.rotation_euler = location, rotation
    return attach(obj, name, material, parent)


def pose(obj, seconds, **properties):
    for prop, value in properties.items():
        setattr(obj, prop, value)
        obj.keyframe_insert(data_path=prop, frame=round(seconds * FPS) + 1)


def character(name, location, shirt, adult=False, mom=False):
    """Reference palette: blue eyes/freckles, Alex's stubble, Theresa's glasses."""
    root = group(name, location)
    if adult:
        root.scale = (1.23, 1.23, 1.23)
    skin = M['skin']
    for side in [-1, 1]:
        ball(name + ' trouser leg', (side * .16, .04, .36), (.13, .14, .33), M['navy'], root)
        ball(name + ' shoe sole', (side * .16, -.07, .075), (.15, .24, .06), M['cream'], root)
        ball(name + ' shoes', (side * .16, -.06, .12), (.15, .22, .08), M['shoe'], root)
        line('Shoe laces', [(side * .16 - .07, -.22, .17), (side * .16 + .07, -.22, .17)], .012, M['cream'], root)
    ball(name + ' soft cloth shirt', (0, 0, .94), (.30, .18, .34), shirt, root)
    ball('Neck', (0, 0, 1.27), (.12, .12, .15), skin, root)
    head = group(name + ' head', (0, 0, 1.54), root)
    ball('Soft face', (0, 0, 0), (.36, .29, .40), skin, head)
    ball('Nose', (0, -.30, -.018), (.065, .077, .072), skin, head)
    for side in [-1, 1]:
        ball('Ear', (side * .36, -.005, -.01), (.073, .055, .105), skin, head)
        ball('Ear inner', (side * .395, -.043, -.014), (.028, .012, .05), M['blush'], head)
        ball('Rosy cheek', (side * .225, -.257, -.09), (.079, .012, .043), M['blush'], head)
        ball('Eye white', (side * .142, -.26, .083), (.101, .041, .107), M['white'], head)
        ball('Blue iris' if not mom else 'Brown iris', (side * .142, -.297, .083), (.048, .012, .066), M['brown'] if mom else M['blue'], head)
        ball('Pupil', (side * .14, -.309, .079), (.025, .007, .043), M['ink'], head)
        ball('Eye sparkle', (side * .14 - .018, -.318, .108), (.016, .007, .018), M['white'], head)
        line('Eyebrow', [(side * .142 - .08, -.264, .22), (side * .142, -.289, .239), (side * .142 + .08, -.264, .22)], .016, M['darkhair'] if mom else M['hair'], head)
        if not adult:
            for n in range(4):
                ball('Freckle', (side * (.17 + n * .027), -.265 + n * .008, -.065 + .02 * (n % 2)), (.008, .006, .008), M['freckle'], head)
    ball('Happy open smile', (0, -.272, -.185), (.156, .025, .062), M['mouth'], head)
    line('Lower lip', [(-.13, -.283, -.208), (0, -.299, -.247), (.13, -.283, -.208)], .013, M['blush'], head)
    for n in range(5):
        cube('Upper tooth', ((n - 2) * .043, -.305, -.153), (.044, .018, .032), M['white'], head, .006)
    loose = None
    for n in range(5):
        tooth = cube('First loose lower tooth' if n == 2 else 'Lower tooth', ((n - 2) * .043, -.304, -.216), (.041, .016, .024), M['white'], head, .005)
        if n == 2:
            loose = tooth
    hair = M['darkhair'] if mom else M['hair']
    if mom:
        ball('Shoulder length hair', (0, .14, -.05), (.405, .20, .53), hair, head)
        for side in [-1, 1]:
            for n in range(4):
                ball('Long hair curl', (side * (.31 + .018 * n), .025, .20 - .16 * n), (.07, .12, .16), hair, head)
            points = [(side * .142 + .116 * math.cos(t), -.319, .083 + .115 * math.sin(t)) for t in [i * math.tau / 32 for i in range(33)]]
            line('Theresa black glasses', points, .013, M['ink'], head)
            earring = ring('Gold hoop earring', (side * .381, -.042, -.10), .039, .009, M['gold'], head)
            earring.rotation_euler.x = math.pi / 2
        line('Glasses bridge', [(-.035, -.324, .10), (0, -.336, .12), (.035, -.324, .10)], .013, M['ink'], head)
    else:
        ball('Short hair back', (0, .105, .21), (.365, .21, .235), hair, head)
        if adult:
            for side in [-1, 1]:
                for n in range(8):
                    ball('Alex light beard stubble', (side * (.11 + n * .022), -.268 + n * .011, -.265 + n * .011), (.012, .004, .018), M['freckle'], head)
    for n in range(11):
        x = -.28 + n * .054
        ball('Swept hair lock', (x, -.07, .30 + .07 * math.sin(n * .6)), (.088, .18, .07), hair, head)
        line('Painted hair strand', [(x, -.22, .27), (x + .03, -.17, .37), (x + .045, -.02, .39)], .008, M['hairlight'], head)
    arms = []
    for side in [-1, 1]:
        arm = group('Left arm' if side < 0 else 'Right arm', (side * .31, 0, 1.16), root)
        ball('Sleeve', (side * .035, 0, -.07), (.14, .18, .19), shirt, arm)
        ball('Forearm', (side * .075, -.025, -.31), (.085, .09, .21), skin, arm)
        ball('Hand', (side * .078, -.06, -.49), (.092, .07, .106), skin, arm)
        ball('Thumb', (side * .01, -.104, -.465), (.036, .041, .06), skin, arm)
        for n in range(3):
            line('Finger detail', [(side * .065 + n * .025, -.126, -.52), (side * .065 + n * .025, -.127, -.57)], .003, M['blush'], arm)
        arms.append(arm)
    if not adult:
        def cloth_surface(x, z):
            return -.18 * math.sqrt(max(.01, 1 - (x / .30) ** 2 - ((z - .94) / .34) ** 2)) - .008
        for x in [-.2, -.1, 0, .1, .2]:
            points = [(x, cloth_surface(x, z), z) for z in [.76 + i * .018 for i in range(21)]]
            line('Blue checked shirt vertical', points, .011, M['check'], root)
        for z in [.75, .85, .95, 1.05, 1.15]:
            points = [(x, cloth_surface(x, z), z) for x in [-.22 + i * .022 for i in range(21)]]
            line('Blue checked shirt horizontal', points, .011, M['check'], root)
    else:
        for z in [.78, .92, 1.06]:
            ball('Shirt button', (0, -.18, z), (.014, .01, .014), M['cream'], root)
    return {'root': root, 'head': head, 'arms': arms, 'tooth': loose}


def room(name, x, wall):
    root = group(name, (x, 0, 0))
    cube('Wood floor', (0, 0, -.11), (7, 6, .2), M['wood'], root)
    for n in range(13):
        line('Floor plank seam', [(-3.5, n * .46 - 3, .002), (3.5, n * .46 - 3, .002)], .009, M['woodlight'], root)
    cube('Back wall', (0, 2.6, 1.7), (7, .16, 3.5), wall, root)
    cube('Baseboard', (0, 2.46, .13), (7, .09, .18), M['cream'], root)
    cube('Window sky', (-2.1, 2.46, 2.05), (1.25, .06, 1.25), M['sky'], root)
    for dx, dz, w, h in [(0, 0, 1.3, .045), (0, .64, 1.38, .07), (0, -.64, 1.38, .07), (-.65, 0, .07, 1.38), (.65, 0, .07, 1.38), (0, 0, .045, 1.3)]:
        cube('Window frame', (-2.1 + dx, 2.40, 2.05 + dz), (w, .08, h), M['white'], root)
    return root


def money(location, parent):
    bill = group('A single one-dollar bill', location, parent)
    cube('Dollar green paper', (0, 0, 0), (.56, .26, .012), M['money'], bill, .01)
    for x in [-.25, .25]:
        text('Dollar denomination', '1', (x - .025, -.055, .01), .09, M['cream'], bill)
    ring('Dollar portrait seal', (0, 0, .014), .071, .009, M['cream'], bill)
    ball('Dollar portrait', (0, 0, .012), (.031, .043, .006), M['cream'], bill)
    return bill


def build(data):
    global M
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    colors = {'skin': (.92, .66, .45), 'blush': (.87, .40, .35), 'white': (.99, .98, .91),
              'cream': (.94, .87, .69), 'blue': (.14, .45, .68), 'shirt': (.30, .55, .77),
              'check': (.78, .87, .94), 'navy': (.15, .22, .29), 'shoe': (.29, .35, .40),
              'hair': (.36, .20, .10), 'hairlight': (.55, .35, .18), 'darkhair': (.16, .085, .049),
              'brown': (.32, .16, .07), 'freckle': (.49, .29, .16), 'ink': (.055, .065, .08),
              'mouth': (.23, .07, .06), 'coral': (.76, .35, .29), 'gold': (.88, .62, .17),
              'wood': (.72, .50, .31), 'woodlight': (.81, .65, .44), 'mint': (.65, .78, .67),
              'wall': (.91, .84, .72), 'sky': (.57, .77, .88), 'grass': (.38, .56, .30),
              'leaf': (.24, .43, .24), 'pad': (.24, .55, .41), 'mat': (.15, .21, .23),
              'metal': (.49, .58, .56), 'lavender': (.66, .52, .80), 'wing': (.79, .84, .96),
              'blanket': (.35, .54, .64), 'night': (.22, .32, .49), 'money': (.41, .57, .34)}
    M = {name: mat(name, color) for name, color in colors.items()}
    bathroom = room('SUNLIT BATHROOM', 0, M['mint'])
    cube('Vanity cabinet', (0, 1.75, .52), (1.55, .67, 1.0), M['cream'], bathroom)
    cube('Sink countertop', (0, 1.75, 1.06), (1.72, .78, .13), M['white'], bathroom)
    ball('Sink bowl', (0, 1.59, 1.12), (.48, .29, .04), M['sky'], bathroom)
    line('Faucet', [(.4, 1.88, 1.11), (.4, 1.88, 1.40), (.4, 1.60, 1.40)], .04, M['metal'], bathroom)
    mirror = ball('Oval mirror', (0, 2.42, 2.02), (.60, .03, .77), M['sky'], bathroom)
    points = [(.66 * math.cos(t), 2.38, 2.02 + .83 * math.sin(t)) for t in [i * math.tau / 64 for i in range(65)]]
    line('Mirror warm gold rim', points, .036, M['gold'], bathroom)
    cube('Toothbrush cup', (-.55, 1.70, 1.24), (.16, .16, .23), M['coral'], bathroom)
    line('Toothbrush handle', [(-.55, 1.7, 1.26), (-.55, 1.7, 1.57)], .02, M['blue'], bathroom)
    cube('Soft toothbrush head', (-.55, 1.7, 1.58), (.09, .04, .13), M['white'], bathroom)
    first = character('TYSON first loose tooth', (0, .1, 0), M['shirt'])
    dad = character('ALEX bathroom', (-1.1, .42, 0), M['shirt'], adult=True)
    mom = character('THERESA bathroom', (1.1, .42, 0), M['coral'], adult=True, mom=True)
    dad['root'].rotation_euler.z = -.17
    mom['root'].rotation_euler.z = .17
    for t in range(0, round(data['scenes'][0]['end']) + 1, 2):
        pose(first['head'], t, rotation_euler=(0, .03 * math.sin(t), .04 * math.sin(t * 1.5)))
        pose(first['arms'][1], t, rotation_euler=(-1.9 + .08 * math.sin(t * 2), 0, -.65))
    garden = group('BACKYARD', (14, 0, 0))
    cube('Grassy lawn', (0, 0, -.13), (13, 12, .24), M['grass'], garden)
    for i in range(10):
        x, y = -5 + i, 3.3 + .3 * math.sin(i)
        line('Tree trunk', [(x, y, 0), (x, y, 2.5)], .14, M['wood'], garden)
        for j in range(4):
            ball('Watercolor green tree crown', (x + .3 * math.cos(j), y + .3 * math.sin(j), 2.35 + .3 * (j % 2)), (.78, .64, .85), M['leaf'] if j % 2 else M['pad'], garden)
    for i in range(31):
        x = -6 + i * .40
        cube('Garden fence picket', (x, 2.7, .62), (.24, .07, 1.1), M['cream'], garden)
    for z in [.40, .85]:
        cube('Fence rail', (0, 2.73, z), (12.4, .09, .08), M['woodlight'], garden)
    for i in range(60):
        x, y = random.uniform(-4, 4), random.uniform(-2.8, 2.6)
        if math.hypot(x, y) < 1.9:
            continue
        line('Grass blade', [(x, y, .01), (x + .045, y, .10)], .009, M['leaf'], garden)
        if i % 3 == 0:
            for j in range(5):
                ball('Daisy petal', (x + .035 * math.cos(j * math.tau / 5), y + .035 * math.sin(j * math.tau / 5), .16), (.03, .03, .011), M['cream'], garden)
            ball('Daisy center', (x, y, .174), (.017, .017, .013), M['gold'], garden)
    bpy.ops.mesh.primitive_cylinder_add(vertices=80, radius=1.47, depth=.06, location=(0, 0, .78))
    attach(bpy.context.object, 'Trampoline jumping mat', M['mat'], garden)
    ring('Padded green safety rim', (0, 0, .79), 1.54, .13, M['pad'], garden)
    for i in range(8):
        a = i * math.tau / 8
        x, y = 1.57 * math.cos(a), 1.57 * math.sin(a)
        line('Trampoline leg', [(x, y, .05), (x, y, .80)], .045, M['metal'], garden)
        if y > -.2 or abs(x) > 1.4:
            line('Padded enclosure post', [(x, y, .80), (x, y, 2.65)], .036, M['pad'], garden)
    # Closed rear mesh, sparse front mesh keeps modeled facial expressions visible.
    for i in range(49):
        a = i * math.pi / 48
        x, y = 1.56 * math.cos(a), 1.56 * math.sin(a)
        line('Enclosure vertical mesh', [(x, y, .9), (x, y, 2.6)], .006, M['metal'], garden)
    for z in [1.0 + i * .12 for i in range(14)]:
        line('Enclosure horizontal mesh', [(1.56 * math.cos(a), 1.56 * math.sin(a), z) for a in [i * math.pi / 48 for i in range(49)]], .005, M['metal'], garden)
    ring('Enclosure top rim', (0, 0, 2.65), 1.56, .017, M['pad'], garden)
    jumper = character('TYSON trampoline', (14, 0, .82), M['shirt'])
    gm = character('THERESA supervising', (11.6, .25, 0), M['coral'], adult=True, mom=True)
    gd = character('ALEX backyard', (16.4, .35, 0), M['shirt'], adult=True)
    section = data['scenes'][1]
    bounce_end = data['paragraphs'][7]['start']
    for i in range(round((bounce_end - section['start']) * 4) + 1):
        t = section['start'] + i * .25
        phase = (t - section['start']) * math.tau
        h = .82 + .37 * max(0, math.sin(phase))
        pose(jumper['root'], t, location=(14, 0, h), rotation_euler=(0, .028 * math.sin(phase), .035 * math.sin(phase)))
        for side, arm in zip([-1, 1], jumper['arms']):
            pose(arm, t, rotation_euler=(.15, .3 * side, .6 * side + .10 * math.sin(phase)))
    pose(jumper['root'], bounce_end + .5, location=(14, 0, .82), rotation_euler=(0, 0, 0))
    search_start = data['scenes'][2]['start']
    pose(jumper['root'], search_start - 1 / FPS, location=(14, 0, .82))
    pose(jumper['root'], search_start, location=(15.0, -.7, 0))
    for actor, location in [(gm, (13.2, -.8, 0)), (gd, (16.1, -.5, 0))]:
        initial = tuple(actor['root'].location)
        pose(actor['root'], 0, location=initial)
        pose(actor['root'], search_start - 1 / FPS, location=initial)
        pose(actor['root'], search_start, location=location)
        pose(actor['head'], 0, rotation_euler=(0, 0, 0))
        pose(actor['head'], search_start - 1 / FPS, rotation_euler=(0, 0, 0))
        pose(actor['head'], search_start, rotation_euler=(.32, 0, 0))
    drop = data['paragraphs'][5]['end'] - 2.0
    pose(jumper['tooth'], 0, hide_render=False)
    pose(jumper['tooth'], drop, hide_render=True)
    tooth = cube('The tiny lost tooth', (14, -.33, 2.15), (.058, .047, .07), M['white'], bevel=.015)
    pose(tooth, 0, hide_render=True)
    pose(tooth, drop, hide_render=False, location=(14, -.33, 2.3))
    pose(tooth, drop + .5, location=(14.8, -.8, 2.1), rotation_euler=(1, 1, .4))
    pose(tooth, drop + 1.1, location=(15.9, -1.2, .13), rotation_euler=(2, 1.6, .8))
    pose(tooth, drop + 1.3, hide_render=True)
    deskroom = room('LETTER AT DUSK', 28, M['wall'])
    writer = character('TYSON writing a note', (28, .28, .12), M['shirt'])
    writer['tooth'].hide_render = True
    character('ALEX reassures Tyson', (26.9, .7, 0), M['shirt'], adult=True)
    character('THERESA helps write', (29.05, .7, 0), M['coral'], adult=True, mom=True)
    cube('Writing table', (0, -.55, .87), (1.85, 1.05, .12), M['woodlight'], deskroom)
    for x in [-.78, .78]:
        for y in [-.91, -.19]:
            cube('Desk leg', (x, y, .42), (.09, .09, .82), M['wood'], deskroom)
    cube('Tyson handwritten letter', (0, -.61, .943), (1.46, .83, .012), M['white'], deskroom, .01)
    words = 'Dear Tooth Fairy,\nMy tooth came free while I bounced.\nI did not notice it fall.\nWe looked, but could not find it.\nPlease visit even though it is gone.\nLove, Tyson'
    text('Letter explaining the missing tooth', words, (-.66, -.32, .953), .063, M['ink'], deskroom)
    pencil = line('Yellow pencil', [(.42, -.93, .965), (.67, -.55, .965)], .022, M['gold'], deskroom)
    for arm in writer['arms']:
        arm.rotation_euler.x = -1.08
    for t in range(round(data['scenes'][2]['start']), round(data['scenes'][2]['end']) + 1):
        pose(writer['arms'][1], t, rotation_euler=(-1.10 + .025 * math.sin(t * 3), -.05, -.06 + .04 * math.sin(t * 3)))
    bedroom = room('BEDTIME AND MORNING', 42, M['night'])
    cube('Bed frame', (0, .25, .35), (1.6, 2.65, .27), M['woodlight'], bedroom)
    cube('Mattress', (0, .25, .56), (1.52, 2.55, .20), M['cream'], bedroom, .12)
    cube('Headboard', (0, 1.57, .87), (1.7, .12, 1.12), M['wood'], bedroom, .12)
    pillow = cube('Tyson pillow', (0, .95, .75), (1.12, .64, .20), M['white'], bedroom, .10)
    cube('Blue patchwork quilt', (0, -.22, .77), (1.45, 1.38, .14), M['blanket'], bedroom, .06)
    for x in [-.5, -.25, 0, .25, .5]:
        for y in [-.72, -.42, -.12, .18]:
            cube('Quilt stitched square', (x, y, .847), (.22, .27, .008), M['sky'] if round((x + y) * 4) % 2 else M['blanket'], bedroom, .01)
    sleeper = character('TYSON dreams', (42, -.6, .78), M['shirt'])
    sleeper['root'].rotation_euler.x = -math.pi / 2
    sleeper['tooth'].hide_render = True
    # Sleeping eyelids cover the whites during the night shots.
    for side in [-1, 1]:
        ball('Peaceful sleeping eyelid', (side * .142, -.326, .083), (.105, .023, .11), M['skin'], sleeper['head'])
        line('Closed eyelid smile', [(side * .142 - .07, -.351, .087), (side * .142, -.353, .066), (side * .142 + .07, -.351, .087)], .008, M['brown'], sleeper['head'])
    dawn_stanza = data['paragraphs'][14]
    morning = dawn_stanza['start'] + (dawn_stanza['end'] - dawn_stanza['start']) * .5
    pose(sleeper['root'], 0, scale=(1, 1, 1))
    pose(sleeper['root'], morning, scale=(0, 0, 0))
    awake = character('TYSON one dollar grin', (42, .25, .13), M['shirt'])
    awake['tooth'].hide_render = True
    pose(awake['root'], 0, scale=(0, 0, 0))
    pose(awake['root'], morning, scale=(1, 1, 1))
    for side, arm in zip([-1, 1], awake['arms']):
        arm.rotation_euler = (-1.2, 0, .25 * side)
    bd = character('ALEX morning hug', (40.65, .5, 0), M['shirt'], adult=True)
    bm = character('THERESA morning smile', (43.3, .5, 0), M['coral'], adult=True, mom=True)
    for actor in [bd, bm]:
        pose(actor['root'], 0, scale=(0, 0, 0))
        pose(actor['root'], morning, scale=(1.23, 1.23, 1.23))
    bill = money((0, .95, .64), bedroom)
    pose(pillow, 0, location=(0, .95, .75), rotation_euler=(0, 0, 0))
    pose(bill, 0, location=(0, .95, .64), rotation_euler=(0, 0, 0))
    pose(pillow, morning, location=(.52, 1.02, .75), rotation_euler=(0, 0, -.18))
    pose(bill, morning + .2, location=(.25, -.27, 1.11), rotation_euler=(math.pi / 2, 0, 0))
    fairy = character('THE TOOTH FAIRY', (42, 1.2, 2.8), M['lavender'])
    fairy['root'].scale = (.32, .32, .32)
    for side in [-1, 1]:
        wing = ball('Butterfly upper wing', (side * .45, .20, 1.18), (.37, .075, .62), M['wing'], fairy['root'])
        wing.rotation_euler.y = .3 * side
        for i in range(round((data['paragraphs'][14]['start'] - data['paragraphs'][13]['start']) * 6) + 1):
            t = data['paragraphs'][13]['start'] + i / 6
            pose(wing, t, rotation_euler=(0, side * (.3 + .28 * math.sin(i * math.pi / 2)), 0))
        ball('Butterfly lower wing', (side * .42, .22, .82), (.28, .07, .32), M['lavender'], fairy['root'])
        for n in range(5):
            ball('Wing pearl', (side * (.29 + n * .044), .11, 1.48 - n * .09), (.018, .018, .018), M['white'], fairy['root'])
    line('Fairy wand', [(.37, -.1, .7), (.44, -.1, 1.35)], .022, M['gold'], fairy['root'])
    for side in [-1, 1]:
        spike = cube('Wand star ray', (.44, -.1, 1.40), (.22, .04, .06), M['gold'], fairy['root'])
        spike.rotation_euler.y = side * .7
    fa = data['paragraphs'][13]['start']
    fb = data['paragraphs'][13]['end']
    pose(fairy['root'], 0, scale=(0, 0, 0))
    pose(fairy['root'], fa, scale=(.32, .32, .32), location=(40.9, .8, 2.35))
    pose(fairy['root'], fa + 2, location=(42.5, .45, 1.65))
    pose(fairy['root'], fb - 1.4, location=(42.7, .6, 1.45))
    pose(fairy['root'], fb, location=(42.7, .6, 1.45))
    pose(fairy['root'], dawn_stanza['start'] + 2, location=(40.8, 1.7, 2.3))
    pose(fairy['root'], morning, scale=(0, 0, 0))
    letter = group('Tyson note under his pillow', (0, .7, .642), bedroom)
    cube('Folded note paper', (0, 0, 0), (1.05, .61, .01), M['white'], letter, .006)
    text('The fairy reads Tyson note', 'Dear Tooth Fairy,\nMy tooth came free while I bounced.\nI did not notice it fall.\nWe looked, but could not find it.\nPlease visit even though it is gone.\nLove, Tyson',
         (-.47, .22, .01), .041, M['ink'], letter)
    pose(letter, 0, location=(0, .7, .642), rotation_euler=(0, 0, 0))
    pose(letter, fa + 1, location=(0, .7, .642), rotation_euler=(0, 0, 0))
    pose(letter, fa + 2, location=(.7, .33, 1.65), rotation_euler=(1.3, 0, 0))
    pose(letter, fb, location=(.7, .33, 1.65), rotation_euler=(1.3, 0, 0))
    pose(letter, dawn_stanza['start'] + 2, location=(-.5, .45, .65), rotation_euler=(0, 0, -.15))
    pose(bill, 0, hide_render=True)
    pose(bill, dawn_stanza['start'], hide_render=False, location=(.65, .35, 1.75), rotation_euler=(1.3, 0, 0))
    pose(bill, dawn_stanza['start'] + 2.0, location=(0, .95, .64), rotation_euler=(0, 0, 0))
    pose(bill, morning - 1 / FPS, location=(0, .95, .64), rotation_euler=(0, 0, 0))
    pose(bill, morning + .2, location=(.25, -.27, 1.11), rotation_euler=(math.pi / 2, 0, 0))
    for n in range(14):
        spark = ball('Fairy stardust', (41.6 + random.random() * 1.4, .5 + random.random() * .8, 1.1 + random.random() * 1.3), (.019, .019, .019), M['gold'])
        pose(spark, 0, scale=(0, 0, 0))
        pose(spark, fa, scale=(.0171, .0171, .0171))
        pose(spark, morning, scale=(0, 0, 0))
    camera = bpy.data.cameras.new('Story camera')
    cam = bpy.data.objects.new('Story camera', camera)
    bpy.context.collection.objects.link(cam)
    scene = bpy.context.scene
    scene.camera = cam
    camera.type, camera.ortho_scale = 'ORTHO', 5.5
    shots = [
        ((3.3, -7, 3.4), (0, .4, 1.35), 5.8),
        ((2.3, -7, 3.0), (0, .15, 1.4), 4.9),
        ((.8, -5, 2.3), (0, 0, 1.3), 3.7),
        ((3.4, -7, 3.1), (0, .3, 1.3), 5.9),
        ((17.8, -7, 4.6), (14, .2, 1.2), 8.3),
        ((16.5, -7, 3.8), (14, 0, 1.85), 5.8),
        ((16.6, -7, 3.5), (14.7, -.4, 1.45), 5.7),
        ((15.5, -5, 3.25), (14, 0, 2.05), 3.8),
        ((18, -7, 3.4), (14.8, -.4, .7), 7.5),
        ((30.8, -7, 3.5), (28, .1, 1.2), 5.8),
        ((29, -4.5, 4.2), (28, -.1, 1.1), 4.9),
        ((30.6, -7, 3.4), (28, .1, 1.25), 5.7),
        ((44.9, -6, 4.4), (42, .4, .85), 5.7),
        ((44.2, -5, 3.4), (42.2, .6, 1.3), 4.4),
        ((44.4, -6.3, 3.7), (42, .35, 1.55), 5.1),
        ((45.3, -7, 3.9), (42, .5, 1.5), 6.0),
    ]
    for i, (paragraph, shot) in enumerate(zip(data['paragraphs'], shots)):
        start = 0 if i == 0 else paragraph['start']
        end = data['paragraphs'][i + 1]['start'] - 1 / FPS if i < 15 else data['duration']
        location, target, scale = shot
        for t, factor in [(start, 1), (end, .97)]:
            cam.location = location
            cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
            cam.keyframe_insert('location', frame=round(t * FPS) + 1)
            cam.keyframe_insert('rotation_euler', frame=round(t * FPS) + 1)
            camera.ortho_scale = scale * factor
            camera.keyframe_insert('ortho_scale', frame=round(t * FPS) + 1)
        marker = scene.timeline_markers.new(f'Stanza {i + 1}: {paragraph["text"].splitlines()[0]}', frame=round(start * FPS) + 1)
    # Discrete visibility keys; linear motion/camera keys avoid overshoot across cuts.
    for obj in bpy.data.objects:
        if obj.animation_data and obj.animation_data.action:
            for curve in obj.animation_data.action.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation = 'CONSTANT' if 'hide_' in curve.data_path or curve.data_path == 'scale' else 'LINEAR'
    # The bill/pillow moves at dawn rather than drifting throughout the night.
    for obj in [pillow, bill]:
        if obj.animation_data:
            for curve in obj.animation_data.action.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation = 'CONSTANT'
    scene.render.engine = 'BLENDER_WORKBENCH'
    display = scene.display.shading
    display.light, display.studio_light, display.color_type = 'STUDIO', 'paint.sl', 'MATERIAL'
    display.show_shadows, display.show_cavity = True, True
    display.cavity_type = 'BOTH'
    display.curvature_ridge_factor, display.curvature_valley_factor = .55, .45
    display.cavity_ridge_factor, display.cavity_valley_factor = .6, .55
    display.shadow_intensity = .35
    display.show_specular_highlight = True
    display.background_type, display.background_color = 'WORLD', (.78, .86, .87)
    scene.world.color = (.78, .86, .87)
    scene.display.render_aa = '16'
    scene.view_settings.view_transform = 'Standard'
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1280, 720, 100
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, math.ceil(data['duration'] * FPS)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    sequence = scene.sequence_editor_create().sequences.new_sound('Complete neural story narration',
                     str(OUT / 'narration.mp3'), channel=1, frame_start=1)
    sequence.sound.pack()
    scene.render.use_sequencer = False
    return scene


def batch_rigid_geometry():
    """Bake stationary child geometry into one draw call per moving parent.

    Vertices are transformed into parent space; root/head/arm motion and the
    separately animated loose tooth remain editable. Curves/bevels are baked
    from the evaluated mesh once instead of being reevaluated every frame.
    """
    print('Batching rigid geometry...', flush=True)
    scene = bpy.context.scene
    scene.frame_set(1)
    zero_scales = []
    for obj in scene.objects:
        if any(abs(value) < 1e-6 for value in obj.scale):
            zero_scales.append((obj, tuple(obj.scale)))
            obj.scale = (1, 1, 1)
    bpy.context.view_layer.update()
    batches = {}
    for obj in list(scene.objects):
        if obj.type in {'MESH', 'CURVE', 'FONT'} and not obj.animation_data and not obj.hide_render:
            batches.setdefault(obj.parent, []).append(obj)
    count = 0
    for parent, objects in batches.items():
        if len(objects) < 2:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.join()
        bpy.context.object.name = 'Rigid geometry: ' + (parent.name if parent else 'world')
        count += len(objects)
        print('Batched', len(objects), 'parts:', bpy.context.object.name, flush=True)
    for obj, scale in zero_scales:
        obj.scale = scale
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.view_layer.update()
    print(f'Batched {count} rigid parts; {len(bpy.data.objects)} objects remain.', flush=True)


def encode(scene):
    missing = [frame for frame in range(1, scene.frame_end + 1)
               if not (BUILD / 'frames' / f'{frame:05d}.jpg').is_file()]
    if missing:
        raise RuntimeError(f'Film is incomplete: {len(missing)} missing frames; first missing frame is {missing[0]}.')
    duration = scene.frame_end / FPS
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i',
                    str(BUILD / 'frames' / '%05d.jpg'), '-i', str(OUT / 'narration.mp3'),
                    '-vf', 'fps=24', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-af', 'apad',
                    '-t', str(duration), '-movflags', '+faststart', str(OUT / 'tooth-bounce-3d.mp4')], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stills', action='store_true')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--preview', type=int)
    parser.add_argument('--encode-only', action='store_true')
    parser.add_argument('--load-scene', action='store_true')
    parser.add_argument('--start', type=int, default=1)
    parser.add_argument('--end', type=int)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    data = json.loads((OUT / 'narration-timings.json').read_text())
    BUILD.mkdir(parents=True, exist_ok=True)
    if args.load_scene:
        bpy.ops.wm.open_mainfile(filepath=str(BUILD / 'tooth-bounce.blend'))
        scene = bpy.context.scene
    else:
        scene = build(data)
        batch_rigid_geometry()
    if args.encode_only:
        encode(scene)
        return
    bpy.ops.wm.save_as_mainfile(filepath=str(BUILD / 'tooth-bounce.blend'), compress=True)
    if args.preview is not None:
        scene.frame_set(args.preview)
        scene.render.filepath = str(BUILD / f'preview_{args.preview:05}.png')
        bpy.ops.render.render(write_still=True)
    if args.stills:
        scene.render.resolution_x, scene.render.resolution_y = 1536, 1024
        for index, name in zip([1, 5, 10, 14], ['wiggle-wobble', 'trampoline-bounce', 'fairy-note', 'morning-dollar']):
            paragraph = data['paragraphs'][index]
            seconds = paragraph['start'] + (paragraph['end'] - paragraph['start']) * .8 if index == 14 else paragraph['start'] + 2.0
            frame = round(seconds * FPS) + 1
            scene.frame_set(frame)
            scene.render.filepath = str(BUILD / f'{name}.png')
            bpy.ops.render.render(write_still=True)
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', scene.render.filepath,
                            '-c:v', 'libwebp', '-quality', '92', str(OUT / f'{name}.webp')], check=True)
        scene.render.resolution_x, scene.render.resolution_y = 1280, 720
        scene.frame_set(round((data['paragraphs'][5]['start'] + 1) * FPS) + 1)
        scene.render.filepath = str(BUILD / 'poster.png')
        bpy.ops.render.render(write_still=True)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(BUILD / 'poster.png'),
                        '-q:v', '2', str(OUT / 'tooth-bounce-poster.jpg')], check=True)
    if args.render:
        (BUILD / 'frames').mkdir(exist_ok=True)
        scene.render.image_settings.file_format = 'JPEG'
        scene.render.image_settings.quality = 95
        # Ambient contact shading gives the same soft miniature finish as the
        # existing sled film, without expensive per-frame cast-shadow passes.
        scene.display.render_aa = '5'
        scene.display.shading.show_shadows = False
        scene.display.shading.show_specular_highlight = False
        scene.display.shading.cavity_type = 'WORLD'
        for frame in range(args.start, (args.end or scene.frame_end) + 1):
            target = BUILD / 'frames' / f'{frame:05d}.jpg'
            if target.exists():
                continue
            scene.frame_set(frame)
            scene.render.filepath = str(target)
            bpy.ops.render.render(write_still=True)
        if args.start == 1 and args.end is None:
            encode(scene)


if __name__ == '__main__':
    main()
