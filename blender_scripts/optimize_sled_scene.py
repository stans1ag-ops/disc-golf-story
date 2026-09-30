"""Batch rigid parts and procedural snowfall for the miniature 3D film."""
from collections import defaultdict
import bpy
from mathutils import Matrix


def join(objects,name):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    result=bpy.context.object
    result.name=name
    return result


def snow_components(mesh):
    neighbors=[[] for v in mesh.vertices]
    for e in mesh.edges:
        a,b=e.vertices
        neighbors[a].append(b);neighbors[b].append(a)
    seen=set();components=[]
    for v in mesh.vertices:
        if v.index in seen:
            continue
        pending=[v.index];part=[];seen.add(v.index)
        while pending:
            i=pending.pop();part.append(i)
            for j in neighbors[i]:
                if j not in seen:
                    seen.add(j);pending.append(j)
        components.append(part)
    return components


def configure_snowfall(obj):
    # Wrap each flake's center, preserving every vertex's offset. Wrapping
    # individual vertices can stretch a flake across the reset boundary.
    attr=obj.data.attributes.get('snow_center_z') or obj.data.attributes.new(name='snow_center_z',type='FLOAT',domain='POINT')
    for part in snow_components(obj.data):
        center=sum(obj.data.vertices[i].co.z for i in part)/len(part)
        for i in part:
            attr.data[i].value=center
    group=bpy.data.node_groups.new('Continuous gentle snowfall','GeometryNodeTree')
    group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    n=group.nodes;l=group.links
    inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput')
    center=n.new('GeometryNodeInputNamedAttribute');center.data_type='FLOAT'
    center.inputs['Name'].default_value='snow_center_z'
    time=n.new('GeometryNodeInputSceneTime')
    speed=n.new('ShaderNodeMath');speed.operation='MULTIPLY';speed.inputs[1].default_value=.4
    l.new(time.outputs['Seconds'],speed.inputs[0])
    fall=n.new('ShaderNodeMath');fall.operation='SUBTRACT'
    l.new(center.outputs['Attribute'],fall.inputs[0]);l.new(speed.outputs[0],fall.inputs[1])
    wrap=n.new('ShaderNodeMath');wrap.operation='FLOORED_MODULO';wrap.inputs[1].default_value=12
    l.new(fall.outputs[0],wrap.inputs[0])
    height=n.new('ShaderNodeMath');height.operation='ADD';height.inputs[1].default_value=1
    l.new(wrap.outputs[0],height.inputs[0])
    delta=n.new('ShaderNodeMath');delta.operation='SUBTRACT'
    l.new(height.outputs[0],delta.inputs[0]);l.new(center.outputs['Attribute'],delta.inputs[1])
    combine=n.new('ShaderNodeCombineXYZ')
    l.new(delta.outputs[0],combine.inputs['Z'])
    move=n.new('GeometryNodeSetPosition')
    l.new(inp.outputs['Geometry'],move.inputs['Geometry'])
    l.new(combine.outputs[0],move.inputs['Offset'])
    l.new(move.outputs['Geometry'],out.inputs['Geometry'])
    mod=obj.modifiers.get('Snowfall over time') or obj.modifiers.new('Snowfall over time','NODES')
    mod.node_group=group


def batch_snowfall(scene):
    flakes=[o for o in scene.objects if o.name.startswith('Falling snow')]
    if not flakes:
        return
    obj=join(flakes,'Procedural falling snow')
    world=obj.matrix_world.copy()
    obj.animation_data_clear()
    obj.data.transform(world)
    obj.matrix_world=Matrix.Identity(4)
    configure_snowfall(obj)
    print('Batched snowfall into one animated mesh',flush=True)


def optimize(scene):
    scene.frame_set(1135)
    print('Optimizing rigid geometry...',flush=True)
    groups=defaultdict(list)
    for obj in list(scene.objects):
        if obj.type not in {'MESH','CURVE'} or obj.animation_data or any(m.type=='NODES' for m in obj.modifiers):
            continue
        ancestor=obj.parent
        animated=False
        while ancestor:
            if ancestor.animation_data:
                animated=True
                break
            ancestor=ancestor.parent
        groups[obj.parent if animated else None].append(obj)
    for parent,objects in groups.items():
        if len(objects)<2:
            continue
        result=join(objects,(parent.name if parent else 'Winter landscape')+' • batched mesh')
        print('Batched',len(objects),'parts:',result.name,flush=True)
    batch_snowfall(scene)
    sh=scene.display.shading
    sh.show_specular_highlight=False
    sh.show_shadows=False
    sh.cavity_type='WORLD'
    sh.cavity_ridge_factor=.6
    sh.cavity_valley_factor=1.2
    scene.display.render_aa='5'
    scene.frame_start=1;scene.frame_end=1344;scene.frame_set(577)
    bpy.data.orphans_purge(do_recursive=True)


if __name__=='__main__':
    optimize(bpy.context.scene)
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
