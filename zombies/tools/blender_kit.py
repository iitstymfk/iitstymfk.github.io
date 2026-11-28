"""Tiny helper kit for building game models with Blender (bpy) and exporting .glb.
Run:  python3 build_models.py   (needs: pip install bpy)
Units are metres, Y-up in the exported glb (three.js friendly)."""
import bpy, bmesh, math

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, rough=.7, metal=0.0, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = 2.0
    return m

def _fin(o, m, name):
    o.name = name
    if m: o.data.materials.append(m)
    return o

def box(name, size, loc, m=None, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 2
        bpy.ops.object.modifier_apply(modifier='bv')
    return _fin(o, m, name)

def cyl(name, r, h, loc, m=None, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=loc, rotation=rot)
    return _fin(bpy.context.active_object, m, name)

def sphere(name, r, loc, m=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=20, ring_count=12)
    o = bpy.context.active_object; o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    return _fin(o, m, name)

def join_all(name):
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.active_object; o.name = name
    return o

def export(path):
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_yup=True,
                              export_apply=True, export_materials='EXPORT')
    print('exported', path)

def preview(path, loc=(2.2, -2.6, 1.6), target=(0, 0, .4)):
    """Quick workbench render to a PNG so I can look at the model."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24
    w = bpy.data.worlds.new('w'); w.use_nodes = True; sc.world = w
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (.55, .6, .65, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.2
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 4)); bpy.context.active_object.data.energy = 3
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
    sc.render.resolution_x = 640; sc.render.resolution_y = 480
    sc.render.filepath = path
    bpy.ops.object.empty_add(location=target); tgt = bpy.context.active_object
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    c = cam.constraints.new('TRACK_TO'); c.target = tgt
    c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    sc.camera = cam
    bpy.ops.render.render(write_still=True)
