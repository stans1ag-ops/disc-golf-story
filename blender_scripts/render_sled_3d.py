"""The Red Sled Ride: a fully modeled, animated Blender short.

Run: blender -b -P blender_scripts/render_sled_3d.py -- --preview
     blender -b -P blender_scripts/render_sled_3d.py -- --render
The film uses a deliberate 12 fps miniature/stop-motion cadence, delivered at
24 fps. All meshes, poses, cameras and snowfall are authored here; no image
planes or existing story illustrations are used in the animation.
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
OUT = ROOT / "the-super-snowy-sled"
BUILD = ROOT / '.renders' / 'red-sled'
FPS = 12
DURATION = 112
random.seed(27)


def material(name, color, roughness=.7, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    return m


def attach(obj, name, mat, parent=None):
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.parent = parent
    return o


def ball(name, loc, scale, mat, parent=None, segments=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=12, location=loc)
    o = bpy.context.object
    o.scale = scale
    return attach(o, name, mat, parent)


def box(name, loc, scale, mat, parent=None, bevel=.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('Soft tailored edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        mod = o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return attach(o, name, mat, parent)


def tube(name, points, radius, mat, parent=None, cyclic=False):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 12
    c.bevel_depth = radius
    c.bevel_resolution = 3
    sp = c.splines.new('POLY')
    sp.points.add(len(points)-1)
    for p, co in zip(sp.points, points):
        p.co = (*co, 1)
    sp.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    return attach(o, name, mat, parent)


def cylinder(name, loc, radius, depth, mat, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc)
    return attach(bpy.context.object, name, mat, parent)


def key(obj, frame, prop):
    obj.keyframe_insert(data_path=prop, frame=frame)


def clamp(x):
    return max(0, min(1, x))


def ease(x):
    x = clamp(x)
    return x*x*(3-2*x)


def bump(t, center, width):
    return math.exp(-((t-center)/width)**2)


def snow_height(x, y):
    hill = 4.9 / (1+math.exp((y+12)/4.2))
    # Three small undulations on the sled's actual trail.
    bumps = sum(.18*math.exp(-((y-c)/.95)**2) for c in (-15, -10, -5))
    return hill + bumps + .055*math.sin(x*.7+y*.24)


def make_terrain():
    vertices, faces = [], []
    nx, ny = 65, 100
    for j in range(ny):
        y = -45+j*.75
        for i in range(nx):
            x = -24+i*.75
            z = snow_height(x, y)
            if abs(x) > 4:
                z += .3*math.sin(x*.4)*math.sin(y*.25)
            vertices.append((x, y, z))
    for j in range(ny-1):
        for i in range(nx-1):
            a = j*nx+i
            faces.append((a, a+1, a+nx+1, a+nx))
    mesh = bpy.data.meshes.new('Sculpted winter hill')
    mesh.from_pydata(vertices, [], faces)
    o = bpy.data.objects.new('Snowy hill with three gentle bumps', mesh)
    bpy.context.collection.objects.link(o)
    attach(o, o.name, M['snow'])
    # Tracks are shallow grooves in a slightly blue trail.
    for x in (-.42, .42):
        tube('Sled runner trail', [(x, y, snow_height(x, y)+.012) for y in range(-26, 8)], .024, M['track'])
    for y in range(-21, 4, 2):
        for x in (-1.65, -1.3):
            ball('Little boot print', (x, y+(x+1.65)*1.6, snow_height(x, y)+.02), (.12,.23,.018), M['track'], segments=12)


def tree(x, y, size):
    p = empty('Snow-laden spruce', (x, y, snow_height(x, y)))
    cylinder('Pine trunk', (0,0,size*.4), size*.08, size*.8, M['wood'], p)
    # Scalloped layered bough meshes rather than featureless cones.
    for tier in range(4):
        z = size*(.28+tier*.18)
        r = size*(.31-tier*.06)
        v, f = [], []
        n = 20
        for ring, (radius, height) in enumerate(((r,0),(r*.85,.15*size),(.015,.46*size))):
            for i in range(n):
                a = i*math.tau/n
                wav = 1+.075*math.sin(a*5)
                v.append((radius*wav*math.cos(a), radius*wav*math.sin(a), z+height+.025*size*math.cos(a*5)))
        for ring in range(2):
            for i in range(n):
                a=ring*n+i; b=ring*n+(i+1)%n
                f.append((a,b,b+n,a+n))
        mesh=bpy.data.meshes.new('Scalloped boughs'); mesh.from_pydata(v,[],f)
        o=bpy.data.objects.new('Evergreen bough tier',mesh); bpy.context.collection.objects.link(o)
        attach(o,o.name,M['pine'],p)
        # Snow sits over each bough, leaving a green lower edge.
        vs=[(xx*.95, yy*.95, zz+.07*size) for xx,yy,zz in v]
        mesh=bpy.data.meshes.new('Snow cap'); mesh.from_pydata(vs,[],f)
        o=bpy.data.objects.new('Powder on bough',mesh); bpy.context.collection.objects.link(o)
        attach(o,o.name,M['snow'],p)
    return p


def character(name, coat, hat, scale):
    root=empty(name)
    root.scale=(scale,)*3
    body=empty(name+' body', (0,0,0), root)
    ball('Rounded puffer jacket', (0,0,1.17), (.44,.28,.56), coat,body)
    # Quilted horizontal jacket seams and front zipper.
    for z in (.87,1.10,1.33,1.52):
        pts=[]
        for i in range(33):
            a=math.tau*i/32
            rr=math.sqrt(max(.15,1-((z-1.17)/.60)**2))
            pts.append((.444*rr*math.sin(a),.283*rr*math.cos(a),z))
        tube('Puffer stitching',pts,.012,M['red_seam'] if name=='Shane' else M['blue_seam'],body)
    tube('Cream zipper',[(0,-.29,.77),(0,-.291,1.58)],.017,M['cream'],body)
    box('Zipper pull',(0,-.305,1.42),(.047,.02,.07),M['metal'],body,.012)
    for x in (-.24,.24):
        tube('Pocket piping',[(x-.08,-.24,1.0),(x+.08,-.24,1.0)],.018,M['cream'],body)
    ball('Wool scarf collar',(0,0,1.63),(.33,.30,.11),M['gold'] if name=='Shane' else M['cream'],body)
    scarf=box('Scarf tail',(.23,-.28,1.39),(.15,.065,.37),M['gold'] if name=='Shane' else M['cream'],body,.04)
    scarf.rotation_euler.y=-.12
    head=empty(name+' head',(0,0,1.95),body)
    ball('Warm rounded face',(0,0,0),(.36,.32,.40),M['skin'],head)
    for x in (-.35,.35):
        ball('Ear',(x,0,0),(.07,.06,.105),M['skin'],head)
        ball('Rosy cheek',(x*.63,-.277,-.06),(.086,.018,.052),M['cheek'],head)
    ball('Button nose',(0,-.329,-.025),(.075,.072,.064),M['skin'],head)
    for x in (-.13,.13):
        ball('Eye white',(x,-.287,.08),(.086,.035,.101),M['white'],head)
        ball('Hazel iris',(x,-.318,.08),(.046,.016,.062),M['iris'],head)
        ball('Eye pupil',(x,-.332,.079),(.026,.013,.041),M['dark'],head)
        ball('Eye glint',(x-.013,-.344,.105),(.012,.006,.016),M['white'],head,12)
        tube('Friendly eyebrow',[(x-.07,-.288,.213),(x,-.31,.239),(x+.068,-.288,.219)],.018,M['hair'],head)
    mouth=ball('Happy mouth',(0,-.301,-.163),(.125,.03,.059),M['mouth'],head)
    ball('Smile teeth',(0,-.331,-.142),(.092,.008,.022),M['cream'],head)
    if name=='Dad':
        for i in range(19):
            a=math.pi*(i/18)
            ball('Soft beard detail',(.27*math.cos(a),-.213-.10*math.sin(a),-.20-.09*math.sin(a)),(.033,.022,.045),M['beard'],head,12)
    else:
        for i in range(5):
            tuft=ball('Brown fringe',(-.2+i*.09,-.233,.29),(.08,.05,.08),M['hair'],head)
            tuft.rotation_euler.y=.3
    cap=empty(name+' hat',(0,0,.29),head)
    ball('Knitted hat crown',(0,.012,.115),(.382,.337,.29),hat,cap)
    ball('Folded ribbed brim',(0,-.006,-.01),(.39,.347,.105),M['cream'] if name=='Shane' else M['blue_light'],cap)
    for i in range(36):
        a=i*math.tau/36
        tube('Brim knit rib',[(.389*math.sin(a),.348*math.cos(a),-.066),(.39*math.sin(a),.349*math.cos(a),.053)],.008,hat,cap)
    for i in range(12):
        a=i*math.tau/12
        pts=[(.38*math.sin(a)*math.cos(b),.34*math.cos(a)*math.cos(b),.115+.29*math.sin(b)) for b in (0,.3,.6,.9,1.2)]
        tube('Hat knit cable',pts,.009,M['cream'] if name=='Shane' else M['blue_light'],cap)
    ball('Pom pom',(0,0,.41),(.13,.13,.14),hat,cap)
    for i in range(20):
        a=random.random()*math.tau; z=random.uniform(-.1,.1); rr=math.sqrt(.014-z*z)
        ball('Pom pom tufts',(rr*math.cos(a),rr*math.sin(a),.41+z),(.04,.04,.04),hat,cap,12)
    arms=[]; legs=[]
    for side in (-1,1):
        arm=empty(name+' arm',(side*.38,0,1.51),body)
        ball('Puffy sleeve',(side*.04,0,-.24),(.16,.18,.30),coat,arm)
        tube('Sleeve quilt',[(side*.04+.15*math.sin(a),.18*math.cos(a),-.24) for a in [i*math.tau/20 for i in range(21)]],.012,M['cream'],arm)
        ball('Ribbed cuff',(side*.04,0,-.49),(.135,.14,.065),M['cream'],arm)
        ball('Wool mitten',(side*.04,-.01,-.60),(.145,.14,.17),M['blue_light'] if name=='Shane' else M['gold'],arm)
        ball('Mitten thumb',(side*.04-side*.10,-.04,-.55),(.065,.085,.10),M['blue_light'] if name=='Shane' else M['gold'],arm)
        arms.append(arm)
        leg=empty(name+' thigh',(side*.19,0,.77),root)
        ball('Snow pants thigh',(0,0,-.18),(.18,.19,.27),M['pants'],leg)
        shin=empty(name+' shin',(0,0,-.38),leg)
        ball('Snow pants calf',(0,0,-.13),(.16,.17,.23),M['pants'],shin)
        ball('Boot cuff',(0,0,-.27),(.185,.19,.075),M['cream'],shin)
        box('Winter boot',(0,-.085,-.37),(.34,.46,.21),M['boot'],shin,.09)
        box('Boot tread',(0,-.085,-.472),(.35,.46,.045),M['dark'],shin,.02)
        for j in range(3):
            tube('Boot lace',[(-.09,-.2+j*.055,-.26),(.09,-.2+j*.055,-.26)],.011,M['cream'],shin)
        legs.append((leg,shin))
    foam=ball('Marshmallow moustache',(0,-.351,-.10),(.11,.018,.026),M['white'],head)
    cup=empty(name+' cocoa cup',(0,-.50,1.14),body)
    cylinder('Glazed cocoa mug',(0,0,0),.12,.21,M['gold'] if name=='Shane' else M['red'],cup)
    cylinder('Cocoa surface',(0,0,.111),.102,.005,M['cocoa'],cup)
    cylinder('Floating marshmallow',(.01,-.018,.132),.037,.039,M['cream'],cup)
    tube('Mug handle',[(.12+.065*math.sin(a),0,.06*math.cos(a)) for a in [i*math.tau/24 for i in range(25)]],.022,M['gold'] if name=='Shane' else M['red'],cup)
    steam=[]
    for k in range(2):
        steam.append(tube('Curl of cocoa steam',[(.03*math.sin(j*.8+k),k*.04-.02,.15+j*.033) for j in range(12)],.006,M['white'],cup))
    return dict(root=root,body=body,head=head,cap=cap,arms=arms,legs=legs,foam=foam,cup=cup,steam=steam,mouth=mouth)


def sled():
    p=empty('Red sled')
    # Shaped shell with raised sides and a curled nose.
    vs, fs=[],[]
    rows=22
    for j in range(rows):
        y=-1.8+j*3.2/(rows-1)
        curl=.32*math.exp(-((y+1.8)/.40)**2)
        for i in range(9):
            x=-.70+i*.175
            z=.12+curl+.23*(abs(x)/.70)**6
            vs.append((x,y,z))
    for j in range(rows-1):
        for i in range(8):
            a=j*9+i; fs.append((a,a+1,a+10,a+9))
    mesh=bpy.data.meshes.new('Curved sled shell'); mesh.from_pydata(vs,[],fs)
    o=bpy.data.objects.new('Red molded sled',mesh); bpy.context.collection.objects.link(o)
    attach(o,o.name,M['red'],p)
    sub=o.modifiers.new('Smooth shell','SUBSURF'); sub.levels=1
    solid=o.modifiers.new('Shell thickness','SOLIDIFY'); solid.thickness=.06
    for side in (-1,1):
        tube('Polished rim',[(side*.70,-1.8+j*3.2/21,.35+.32*math.exp(-((-1.8+j*3.2/21+1.8)/.40)**2)) for j in range(22)],.046,M['red_light'],p)
        tube('Steel runner',[(side*.49,-1.7,0),(side*.49,1.40,0)],.055,M['metal'],p)
    for i in range(4):
        box('Sled footwell rib',(-.36+i*.24,-1.05,.145),(.035,.80,.035),M['red_light'],p,.013)
    tube('Front rim',[(-.7,-1.8,.66),(0,-1.87,.60),(.7,-1.8,.66)],.045,M['red_light'],p)
    rope=empty('Sled rope rig',parent=p)
    tube('Braided tow rope',[(-.60,-1.55,.42),(-.3,-2.5,.32),(0,-3.25,.72),(.3,-2.5,.32),(.60,-1.55,.42)],.022,M['gold'],rope)
    return p,rope


def bench():
    p=empty('Cocoa bench',(3.9,7.2,snow_height(3.9,7.2)))
    for x in (-1.4,1.4):
        for y in (-.26,.26):
            box('Bench iron leg',(x,y,.38),(.10,.10,.78),M['metal'],p,.025)
    for y in (-.3,-.1,.1,.3):
        box('Oak seat slat',(0,y,.83),(3.5,.17,.13),M['wood'],p,.035)
    for x in (-1.4,1.4):
        box('Backrest support',(x,.38,1.24),(.09,.1,1.0),M['metal'],p,.03)
    for z in (1.16,1.44,1.71):
        box('Oak back slat',(0,.42,z),(3.5,.13,.20),M['wood'],p,.035)
        box('Snow resting on bench',(0,.42,z+.11),(3.52,.15,.045),M['snow'],p,.02)
    thermos=cylinder('Silver cocoa thermos',(1.16,0,1.09),.15,.46,M['metal'],p)
    cylinder('Thermos shoulder',(1.16,0,1.34),.10,.08,M['cream'],p)
    lid=cylinder('Thermos lid',(1.16,0,1.40),.13,.08,M['blue'],p)
    return p,lid


def camera(name, lens=48):
    data=bpy.data.cameras.new(name)
    data.lens=lens
    data.clip_end=200
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o)
    return o


def aim(cam,loc,target,frame):
    cam.location=loc
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    key(cam,frame,'location'); key(cam,frame,'rotation_euler')


def set_pose(c, mode, t, frame, tilt=0):
    body=c['body']; head=c['head']
    body.location=(0,0,0)
    body.rotation_euler=(tilt,0,0)
    head.rotation_euler=(.025*math.sin(t*1.5),.025*math.sin(t),.025*math.sin(t*.8))
    for i,(thigh,shin) in enumerate(c['legs']):
        side=-1 if i==0 else 1
        thigh.rotation_euler=(0,0,0); shin.rotation_euler=(0,0,0)
        if mode=='walk':
            stride=.40*math.sin(t*5+math.pi*i)
            thigh.rotation_euler.x=stride
            shin.rotation_euler.x=-max(0,stride)*.65
            c['arms'][i].rotation_euler=(-stride*.6,0,side*.12)
        elif mode in ('ride','sit'):
            thigh.rotation_euler.x=-1.35
            shin.rotation_euler.x=.65 if mode=='ride' else 1.15
            c['arms'][i].rotation_euler=(-.75 if mode=='ride' else -1.05, side*.20,-side*.25)
        elif mode=='angel':
            thigh.rotation_euler.y=-side*(.12+.26*(.5+.5*math.sin(t*2.1)))
            c['arms'][i].rotation_euler=(0,-side*(.55+.6*(.5+.5*math.sin(t*2.1))),0)
        else:
            c['arms'][i].rotation_euler=(0,0,side*.12)
        key(thigh,frame,'rotation_euler'); key(shin,frame,'rotation_euler')
        key(c['arms'][i],frame,'rotation_euler')
    key(body,frame,'location'); key(body,frame,'rotation_euler'); key(head,frame,'rotation_euler')


def animate():
    climb=camera('01 • Up the hill',43)
    rest=camera('02 • Plenty of time',52)
    ready=camera('03 • Ready set whoosh',48)
    chase=camera('04 • Three snowy bumps',43)
    drift=camera('05 • A laughing landing',51)
    angels=camera('06 • Snow angels',40)
    cocoa=camera('07 • Warm hands',48)
    end=camera('08 • Tomorrow',45)
    cuts=[(0,climb),(20,rest),(29,ready),(42,chase),(59,drift),(77,angels),(84,cocoa),(103,end)]
    for time,cam in cuts:
        mark=S.timeline_markers.new(cam.name,frame=round(time*FPS)+1); mark.camera=cam
    S.camera=climb
    # Powder spray consists of real animated snow particles.
    spray=[]
    for i in range(55):
        o=ball('Powder plume', (0,0,-10), (.04,)*3,M['snow'],segments=12)
        spray.append((o,random.random(),random.uniform(-1,1),random.uniform(.4,1.4)))
    snowfall=[]
    for i in range(90):
        o=ball('Falling snow', (0,0,-10),(.025,)*3,M['snow'],segments=8)
        snowfall.append((o,random.uniform(-12,12),random.uniform(-28,14),random.uniform(0,12),random.uniform(.2,.5)))
    for frame in range(1,S.frame_end+1):
        t=(frame-1)/FPS
        # Climb and pause. The sled follows Dad on a taut rope.
        if t<29:
            progress=clamp(t/20)*.58 + clamp((t-24)/5)*.42
            y=3-progress*27
            for i,c in enumerate((SHANE,DAD)):
                x=-.65 if i==0 else .65
                yy=y-.25 if i==0 else y+.3
                c['root'].location=(x,yy,snow_height(x,yy)+.035+(0 if 20<=t<24 else .025*math.sin(t*10)))
                c['root'].rotation_euler=(0,0,0)
                set_pose(c,'idle' if 20<=t<24 else 'walk',t,frame)
            DAD['arms'][1].rotation_euler.x=.38
            key(DAD['arms'][1],frame,'rotation_euler')
            SLED.location=(.64,y+3.4,snow_height(.64,y+3.4)+.08)
            SLED.rotation_euler=(-.12,0,0)
            ROPE.scale=(1,1,1)
            aim(climb,(2.8,y-6.5,snow_height(0,y)+4.0),(0,y+.3,snow_height(0,y)+1.25),frame)
            aim(rest,(2.8,y-5,snow_height(0,y)+3.2),(0,y,snow_height(0,y)+1.4),frame)
        elif t<42:
            y=-24
            SLED.location=(0,y,snow_height(0,y)+.09)
            SLED.rotation_euler=(.02,0,math.pi)
            ROPE.scale=(1,.35,1)
            for i,c in enumerate((SHANE,DAD)):
                yy=y+(.63 if i==0 else -.65)
                seated= t>=(33 if i==0 else 31)
                c['root'].location=((0 if seated else (-.98 if i==0 else 1.04)),yy,snow_height(0,y)+(.02 if not seated else -.38*c['root'].scale.x)+.22)
                c['root'].rotation_euler=(0,0,math.pi if seated else .35)
                set_pose(c,'ride' if seated else 'idle',t,frame)
            # Shane brushes the sled, then gives a deliberate ready nod.
            if 29<=t<33:
                SHANE['arms'][1].rotation_euler.x=-.95+.25*math.sin(t*5)
                key(SHANE['arms'][1],frame,'rotation_euler')
            if 37<t<41:
                SHANE['head'].rotation_euler.x=.20*math.sin((t-37)*math.pi)
                key(SHANE['head'],frame,'rotation_euler')
            aim(ready,(2.8,y+7, snow_height(0,y)+3.5),(0,y,snow_height(0,y)+1.1),frame)
        elif t<77:
            run=clamp((t-42)/18)
            y=-24+32*(run*run*(3-2*run))
            bounce=.22*bump(t,47.7,.38)+.32*bump(t,51.4,.4)+.55*bump(t,56.1,.48)
            pitch=.1+.12*bump(t,47.7,.45)-.18*bump(t,56.1,.55)
            zz=snow_height(0,y)+.12+bounce
            SLED.location=(0,y,zz)
            SLED.rotation_euler=(pitch, .025*math.sin(t*5)*float(t<60),math.pi)
            ROPE.scale=(1,.35,1)
            for i,c in enumerate((SHANE,DAD)):
                yy=y+(.63 if i==0 else -.65)
                c['root'].location=(0,yy,zz-.38*c['root'].scale.x+.07)
                c['root'].rotation_euler=(pitch,0,math.pi)
                laugh= -.20*bump(t,68,2.8) if i==0 else -.1*bump(t,69,2.8)
                set_pose(c,'ride',t,frame,laugh)
                if 63<t<71:
                    c['head'].rotation_euler.x=-.14+.06*math.sin(t*6)
                    key(c['head'],frame,'rotation_euler')
            aim(chase,(2.8,y+8.6,zz+3.6),(0,y,zz+1.05),frame)
            aim(drift,(2.8,y+5.6,zz+2.6),(0,y,zz+1.10),frame)
        elif t<84:
            SLED.location=(1.6,7.4,snow_height(1.6,7.4)+.10)
            SLED.rotation_euler=(0,0,math.pi)
            for i,c in enumerate((SHANE,DAD)):
                x=-1.3 if i==0 else -3.6
                c['root'].location=(x,5.5,snow_height(x,5.5)+.15)
                c['root'].rotation_euler=(-math.pi/2,0,0)
                set_pose(c,'angel',t-77,frame)
            aim(angels,(1.8,11.6,12.0),(-1.5,5.6,.4),frame)
        else:
            SLED.location=(1.0,8.8,snow_height(1,8.8)+.10)
            SLED.rotation_euler=(0,0,-.25)
            for i,c in enumerate((SHANE,DAD)):
                x=3.2 if i==0 else 4.45
                ground=snow_height(3.9,7.2)
                c['root'].location=(x,7.1,ground+.86-.77*c['root'].scale.x)
                c['root'].rotation_euler=(0,-.09*ease((t-103)/4) if i==0 else 0,0)
                set_pose(c,'sit',t,frame)
                sip=.17*bump(t,92,1.5)+.17*bump(t,109,1.6)
                c['cup'].location=(0,-.47+ sip*.4,1.20+sip)
                c['cup'].rotation_euler.x=-sip*1.2
                key(c['cup'],frame,'location'); key(c['cup'],frame,'rotation_euler')
                if i==0:
                    # Both mittens cradle the warm cup, then wipe the cheek.
                    c['arms'][0].rotation_euler=(-1.05-sip, -.3,.38)
                    c['arms'][1].rotation_euler=(-1.05-sip,.3,-.38)
                    if 96<t<99:
                        c['arms'][0].rotation_euler=(-2.25,-.12,.18)
                    key(c['arms'][0],frame,'rotation_euler'); key(c['arms'][1],frame,'rotation_euler')
                else:
                    if 95<t<97:
                        c['arms'][0].rotation_euler.x=-2.10
                        key(c['arms'][0],frame,'rotation_euler')
                    if 99<t<102:
                        c['arms'][0].rotation_euler=(-1.80,.80,-.30)
                        key(c['arms'][0],frame,'rotation_euler')
            LID.location=(1.16,0,1.40-.36*ease((t-84)/2))
            key(LID,frame,'location')
            aim(cocoa,(2.8,0.0,3.3),(3.85,7.1,1.5),frame)
            a=ease((t-103)/9)
            aim(end,(2.8,-.8-a*5,4.3+a*2.5),(3.5,6.9,1.35),frame)
        for c in (SHANE,DAD):
            key(c['root'],frame,'location');key(c['root'],frame,'rotation_euler')
            c['cup'].scale=(1,1,1) if t>=84 else (0,0,0)
            key(c['cup'],frame,'scale')
            c['foam'].scale=(.11,.018,.026) if c is SHANE and 93<t<100 else (0,0,0)
            key(c['foam'],frame,'scale')
            c['cap'].rotation_euler=(0,-.42*ease((t-51.0)/.5) if c is DAD and 51<t<73 else 0,0)
            key(c['cap'],frame,'rotation_euler')
        key(SLED,frame,'location');key(SLED,frame,'rotation_euler');key(ROPE,frame,'scale')
        for o,phase,side,vel in spray:
            if 42<t<62:
                age=(t*1.5+phase)%1
                force=2.2 if 59<t<62 else .8
                o.location=(side*(.5+age*force), SLED.location.y-1.0-age*2, SLED.location.z+.15+math.sin(age*math.pi)*vel*force)
                o.scale=(.035*(1-age)+.006,)*3
            else:
                o.scale=(0,0,0)
            key(o,frame,'location');key(o,frame,'scale')
        for o,x,y,z,speed in snowfall:
            o.location=(x+.20*math.sin(t*.5+z),y, snow_height(x,y)+(z-t*speed)%12)
            key(o,frame,'location')
    # Densely baked poses use linear interpolation: renders remain deterministic
    # if the scene is reopened or rendered in independent frame ranges.
    for action in bpy.data.actions:
        for fc in action.fcurves:
            for k in fc.keyframe_points:
                k.interpolation='LINEAR'


def make_angels():
    for x,size in ((-1.3,.72),(-3.6,1.02)):
        y=5.5; z=snow_height(x,y)+.021
        ball('Angel body impression',(x,y+size*1.12,z),(.40*size,.84*size,.024),M['track'])
        ball('Angel head impression',(x,y+size*1.95,z),(.38*size,.38*size,.022),M['track'])
        for side in (-1,1):
            wing=ball('Angel swept wing',(x+side*.78*size,y+size*1.21,z),(.63*size,.72*size,.02),M['track'])
            wing.rotation_euler.z=side*.6
            for k in range(5):
                a=side*(.5+k*.18)
                tube('Feather in snow',[(x+math.sin(a)*r*size,y+size*1.5-math.cos(a)*r*size,z+.012) for r in (.5,.8,1.1)],.012,M['snow'])


def build(engine):
    global S,M,SHANE,DAD,SLED,ROPE,LID
    bpy.ops.wm.read_factory_settings(use_empty=True)
    S=bpy.context.scene
    S.frame_start=1; S.frame_end=FPS*DURATION
    S.render.fps=FPS
    S.render.resolution_x=1280; S.render.resolution_y=720
    S.render.resolution_percentage=100
    S.render.engine=engine
    S.render.image_settings.file_format='PNG'
    S.render.image_settings.color_mode='RGB'
    S.render.film_transparent=False
    S.view_settings.view_transform='Standard'
    S.view_settings.look='Medium High Contrast'
    if engine=='BLENDER_WORKBENCH':
        sh=S.display.shading
        sh.light='STUDIO'; sh.studiolight_rotate_z=.45
        sh.studio_light='paint.sl'; sh.color_type='MATERIAL'
        sh.show_shadows=True; sh.show_cavity=True
        sh.cavity_type='BOTH'; sh.curvature_ridge_factor=1.1; sh.curvature_valley_factor=1.0
        sh.cavity_ridge_factor=1.0; sh.cavity_valley_factor=1.3
        sh.show_specular_highlight=True
        sh.background_type='WORLD'; sh.show_object_outline=False
        S.display.render_aa='16'
    elif engine=='CYCLES':
        S.cycles.samples=24; S.cycles.use_denoising=True
        S.cycles.max_bounces=4
    else:
        S.eevee.taa_render_samples=16
    colors={
        'snow':(.84,.91,.98),'white':(.98,.98,.98),'track':(.61,.75,.84),
        'red':(.68,.055,.06),'red_light':(.93,.17,.12),'red_seam':(.40,.025,.04),
        'blue':(.075,.19,.31),'blue_light':(.27,.43,.55),'blue_seam':(.035,.1,.19),
        'gold':(.94,.58,.13),'cream':(.98,.89,.70),'pants':(.095,.18,.25),
        'skin':(.94,.63,.40),'cheek':(.92,.35,.30),'hair':(.18,.07,.035),
        'dark':(.025,.037,.051),'iris':(.17,.25,.24),'mouth':(.22,.035,.025),
        'beard':(.36,.20,.12),'boot':(.24,.14,.09),'wood':(.40,.21,.10),
        'pine':(.075,.25,.24),'metal':(.35,.44,.50),'cocoa':(.18,.067,.025),
    }
    M={n:material(n,c) for n,c in colors.items()}
    world=bpy.data.worlds.new('Pale winter sky'); S.world=world
    world.color=(.65,.78,.88); world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.78,.88,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
    make_terrain()
    for y in (-32,-25,-18,-11,-4,3,12,20):
        for side in (-1,1):
            tree(side*random.uniform(5.2,8.4),y+random.uniform(-2,2),random.uniform(3.5,6))
            tree(side*random.uniform(12,17),y+random.uniform(-2,2),random.uniform(4,7))
    for i in range(18):
        x=random.choice((-1,1))*random.uniform(8,20); y=random.uniform(-35,20)
        ball('Soft snow bank',(x,y,snow_height(x,y)),(random.uniform(1,2),random.uniform(1,2),.5),M['snow'])
    # Distant softly rounded hills keep the horizon inside the miniature world.
    for x in (-28,-14,0,14,28):
        ball('Distant white hills',(x,-49,1),(16,12,7+random.random()*3),M['track'])
    SHANE=character('Shane',M['red'],M['red'],.72)
    DAD=character('Dad',M['blue'],M['blue'],1.02)
    SLED,ROPE=sled()
    _,LID=bench()
    make_angels()
    for name,loc,power,size,color in (
        ('Winter sun',(-10,-12,18),2200,12,(1,.83,.64)),
        ('Blue sky fill',(9,6,12),1500,10,(.66,.81,1)),
        ('Soft rim',(0,-30,14),1800,9,(1,.93,.82)),
    ):
        d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; d.color=color
        o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc
        o.rotation_euler=(Vector((0,-10,2))-o.location).to_track_quat('-Z','Y').to_euler()
    animate()
    S.frame_set(48*FPS+1)


def encode():
    target=OUT/'sledding_3d.mp4'
    movie=BUILD/f'silent_0001-{FPS*DURATION:04d}.mkv'
    if not movie.exists():
        raise FileNotFoundError('Render the silent Blender film first')
    metadata=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
        '-of','json',str(movie)],capture_output=True,text=True,check=True)
    if abs(float(json.loads(metadata.stdout)['format']['duration'])-DURATION)>.1:
        raise ValueError('The lossless intermediate does not contain the complete film')
    filters=('fps=24,gblur=sigma=0.3,'
        "drawtext=text='THE RED SLED RIDE':fontcolor=0x15384d:fontsize=38:x=48:y=h-102:enable='lt(t,4)',"
        "drawtext=text='A snowy day with Shane and Dad':fontcolor=0x15384d:fontsize=22:x=50:y=h-52:enable='lt(t,4)',"
        'fade=t=in:st=0:d=0.5,fade=t=out:st=111:d=1')
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
        '-i',str(movie),
        '-i',str(OUT/'narration.mp3'),'-vf',filters,
        '-af','apad,afade=t=out:st=111:d=1', '-t',str(DURATION),
        '-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','96k','-movflags','+faststart',str(target)],check=True)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','48',
        '-i',str(target),'-frames:v','1','-q:v','2',str(OUT/'sledding_3d_poster.jpg')],check=True)
    print('ENCODED',target,flush=True)


def render_movie(scene,start,end,aa):
    scene.frame_start=start;scene.frame_end=end
    scene.display.render_aa=aa
    scene.render.image_settings.file_format='FFMPEG'
    scene.render.ffmpeg.format='MKV'
    scene.render.ffmpeg.codec='FFV1'
    scene.render.ffmpeg.audio_codec='NONE'
    scene.render.filepath=str(BUILD/'silent_')
    bpy.ops.render.render(animation=True)
    if start==1 and end==FPS*DURATION:
        encode()


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--preview',action='store_true')
    p.add_argument('--render',action='store_true')
    p.add_argument('--load-scene',action='store_true',help='Render the saved .blend without rebuilding')
    p.add_argument('--aa',choices=['OFF','5','8','16','32'],default='OFF')
    p.add_argument('--engine',choices=['BLENDER_WORKBENCH','CYCLES','BLENDER_EEVEE_NEXT'],default='BLENDER_WORKBENCH')
    p.add_argument('--frame',type=int,default=577)
    p.add_argument('--start',type=int,default=1)
    p.add_argument('--end',type=int,default=FPS*DURATION)
    p.add_argument('--encode-only',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    BUILD.mkdir(parents=True,exist_ok=True)
    if args.encode_only:
        encode(); sys.exit(0)
    if args.load_scene:
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender_scripts/red_sled_ride.blend'))
        S=bpy.context.scene
    else:
        build(args.engine)
        sys.path.insert(0,str(Path(__file__).resolve().parent))
        from optimize_sled_scene import optimize
        optimize(S)
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender_scripts/red_sled_ride.blend'),compress=True)
    if args.preview:
        S.frame_set(args.frame)
        S.render.filepath=str(BUILD/f'preview_{args.frame:04d}.png')
        bpy.ops.render.render(write_still=True)
    if args.render:
        render_movie(S,args.start,args.end,args.aa)
