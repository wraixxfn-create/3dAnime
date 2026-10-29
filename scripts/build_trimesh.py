#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generatore legacy della prima versione approssimata (Trimesh).

Non genera il modello attuale: la sorgente della versione 2 è
create_character.py (Blender). Per evitare sovrascritture accidentali, gli
export legacy sono sempre scritti in exports/legacy/.
"""
import trimesh
import numpy as np
import pathlib
from trimesh.visual.material import PBRMaterial
from trimesh import Scene

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports" / "legacy"
RENDERS = ROOT / "renders"

EXPORTS.mkdir(parents=True, exist_ok=True)
RENDERS.mkdir(exist_ok=True)

def mat_rgba(r,g,b,a=255):
    return np.array([r,g,b,a], dtype=np.uint8)

def pbr(color_rgba, roughness=0.6, metallic=0.0, name="mat"):
    # color_rgba 0-255
    rgb = [c/255.0 for c in color_rgba[:3]]
    alpha = color_rgba[3]/255.0 if len(color_rgba)>3 else 1.0
    return PBRMaterial(
        name=name,
        baseColorFactor=[rgb[0], rgb[1], rgb[2], alpha],
        metallicFactor=metallic,
        roughnessFactor=roughness,
        doubleSided=False
    )

# Colori palette
C_SKIN = mat_rgba(252, 210, 186, 255)
C_SKIN_SHADOW = mat_rgba(242, 192, 168, 255)
C_HAIR = mat_rgba(90, 200, 242, 255)
C_HAIR_DARK = mat_rgba(56, 115, 191, 255)
C_HAIR_LIGHT = mat_rgba(192, 235, 255, 255)
C_EYE_WHITE = mat_rgba(255,255,255,255)
C_IRIS = mat_rgba(51, 140, 242, 255)
C_PUPIL = mat_rgba(13,13,20,255)
C_HIGHLIGHT = mat_rgba(255,255,255,255)
C_TUNIC = mat_rgba(242,242,245,255)
C_ARMOR = mat_rgba(217, 224, 235, 255)
C_GOLD = mat_rgba(242, 204, 64, 255)
C_CAPE = mat_rgba(46, 72, 166, 255)
C_GLOVES = mat_rgba(64,64,77,255)
C_BOOTS = mat_rgba(77, 56, 46, 255)
C_BLADE = mat_rgba(217,230,242,255)
C_HANDLE = mat_rgba(89,46,26,255)
C_BASE = mat_rgba(235,235,232,255)
C_BASE_DARK = mat_rgba(166, 179, 199,255)
C_BLUSH = mat_rgba(255,140,165,180)

def create_sphere(radius, subdivisions=2, color=C_SKIN, roughness=0.6, metallic=0.0, name="sphere"):
    m = trimesh.creation.icosphere(subdivisions=subdivisions, radius=radius)
    m.visual.material = pbr(color, roughness=roughness, metallic=metallic, name=name)
    return m

def create_cylinder(radius, height, color=C_SKIN, roughness=0.6, metallic=0.0, name="cyl", sections=32):
    m = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    m.visual.material = pbr(color, roughness=roughness, metallic=metallic, name=name)
    return m

def create_box(extents, color=C_SKIN, roughness=0.6, metallic=0.0, name="box"):
    m = trimesh.creation.box(extents=extents)
    m.visual.material = pbr(color, roughness=roughness, metallic=metallic, name=name)
    return m

def create_capsule(radius, height, color=C_SKIN, roughness=0.6, metallic=0.0, name="capsule"):
    # cylinder + two hemispheres
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=24)
    sphere = trimesh.creation.icosphere(subdivisions=2, radius=radius)
    # top sphere
    top = sphere.copy()
    top.apply_translation([0,0,height/2])
    bot = sphere.copy()
    bot.apply_translation([0,0,-height/2])
    m = trimesh.util.concatenate([cyl, top, bot])
    m.visual.material = pbr(color, roughness=roughness, metallic=metallic, name=name)
    return m

def add_mesh_to_scene(scene, mesh, translation=(0,0,0), scale=(1,1,1), rotation_euler=None, name=None):
    # rotation_euler: (rx, ry, rz) in radians
    if name:
        mesh.metadata = {'name': name}
    # apply scale
    if scale != (1,1,1):
        mesh.apply_scale(scale)
    # apply rotation
    if rotation_euler:
        rx, ry, rz = rotation_euler
        # Build rotation matrix
        # Use trimesh transformations
        if rx != 0:
            mesh.apply_transform(trimesh.transformations.rotation_matrix(rx, [1,0,0]))
        if ry != 0:
            mesh.apply_transform(trimesh.transformations.rotation_matrix(ry, [0,1,0]))
        if rz != 0:
            mesh.apply_transform(trimesh.transformations.rotation_matrix(rz, [0,0,1]))
    # apply translation
    mesh.apply_translation(translation)
    scene.add_geometry(mesh, node_name=name or f"mesh_{len(scene.geometry)}", geom_name=name)

def build_scene():
    scene = Scene()

    # HEAD - grande stile chibi
    head = create_sphere(0.95, subdivisions=3, color=C_SKIN, roughness=0.7, name="Head")
    head.apply_scale([1.0, 0.95, 0.95])
    add_mesh_to_scene(scene, head, translation=(0,0,1.45), name="Head")

    # Ears - pointed chibi
    for x in [-0.92, 0.92]:
        ear = create_sphere(0.20, subdivisions=2, color=C_SKIN, roughness=0.7, name=f"Ear_{'L' if x<0 else 'R'}")
        ear.apply_scale([0.4, 0.6, 1.0])
        add_mesh_to_scene(scene, ear, translation=(x, 0.0, 1.45), name=f"Ear_{'L' if x<0 else 'R'}")
        # tip cone
        tip = trimesh.creation.cone(radius=0.12, height=0.25, sections=16)
        tip.visual.material = pbr(C_SKIN, roughness=0.7, name=f"EarTip_{'L' if x<0 else 'R'}")
        tip.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [1,0,0]))
        add_mesh_to_scene(scene, tip, translation=(x*1.05, 0.0, 1.62), rotation_euler=(0,0,np.radians(30 if x>0 else -30)), name=f"EarTip_{'L' if x<0 else 'R'}")

    # Nose
    nose = create_sphere(0.06, subdivisions=1, color=C_SKIN_SHADOW, roughness=0.8, name="Nose")
    nose.apply_scale([1,0.5,0.7])
    add_mesh_to_scene(scene, nose, translation=(0, 0.90, 1.30), name="Nose")

    # Blush
    for x in [-0.38, 0.38]:
        blush = create_sphere(0.12, subdivisions=1, color=C_BLUSH, roughness=0.8, name=f"Blush_{'L' if x<0 else 'R'}")
        blush.apply_scale([1.2,0.4,0.8])
        add_mesh_to_scene(scene, blush, translation=(x, 0.82, 1.25), name=f"Blush_{'L' if x<0 else 'R'}")

    # EYES - anime grandi
    for x in [-0.35, 0.35]:
        side = 'L' if x<0 else 'R'
        # Eye white - flattened sphere
        eye_white = create_sphere(0.28, subdivisions=2, color=C_EYE_WHITE, roughness=0.2, name=f"EyeWhite_{side}")
        eye_white.apply_scale([1.15, 0.35, 1.3])
        add_mesh_to_scene(scene, eye_white, translation=(x, 0.84, 1.40), name=f"EyeWhite_{side}")
        # Iris
        iris = create_sphere(0.19, subdivisions=2, color=C_IRIS, roughness=0.3, name=f"Iris_{side}")
        iris.apply_scale([1.0, 0.25, 1.0])
        add_mesh_to_scene(scene, iris, translation=(x, 0.96, 1.38), name=f"Iris_{side}")
        # Pupil
        pupil = create_sphere(0.11, subdivisions=2, color=C_PUPIL, roughness=0.3, name=f"Pupil_{side}")
        pupil.apply_scale([1.0, 0.2, 1.2])
        add_mesh_to_scene(scene, pupil, translation=(x, 1.02, 1.38), name=f"Pupil_{side}")
        # Highlights
        hl1 = create_sphere(0.055, subdivisions=1, color=C_HIGHLIGHT, roughness=0.1, name=f"HL1_{side}")
        hl1.apply_scale([1,0.2,1.0])
        add_mesh_to_scene(scene, hl1, translation=(x-0.06, 1.06, 1.45), name=f"Highlight1_{side}")
        hl2 = create_sphere(0.03, subdivisions=1, color=C_HIGHLIGHT, roughness=0.1, name=f"HL2_{side}")
        hl2.apply_scale([1,0.2,1.0])
        add_mesh_to_scene(scene, hl2, translation=(x+0.07, 1.05, 1.32), name=f"Highlight2_{side}")

        # Eyebrow - small flattened box slightly curved
        brow = trimesh.creation.box(extents=[0.30, 0.04, 0.05])
        brow.visual.material = pbr(C_HAIR_DARK, roughness=0.6, name=f"Brow_{side}")
        add_mesh_to_scene(scene, brow, translation=(x, 0.80, 1.57), rotation_euler=(np.radians(85),0,0), name=f"Brow_{side}")

    # HAIR - calotta
    hair_top = create_sphere(0.98, subdivisions=3, color=C_HAIR, roughness=0.5, name="Hair_Top")
    hair_top.apply_scale([1.08,1.05,0.95])
    add_mesh_to_scene(scene, hair_top, translation=(0,0,1.70), name="Hair_Top")

    # Bangs 3 ciocche
    for i, (x, rot) in enumerate([(-0.35, -15),(0.0,0),(0.35,15)]):
        bangs = create_box(extents=[0.32,0.18,0.45], color=C_HAIR, roughness=0.5, name=f"Hair_Bangs_{i}")
        add_mesh_to_scene(scene, bangs, translation=(x,0.75,1.62), rotation_euler=(np.radians(25), np.radians(rot),0), name=f"Hair_Bangs_{i}")

    # Side hair
    for x in [-0.75, 0.75]:
        side='L' if x<0 else 'R'
        side_hair = create_box(extents=[0.28,0.35,1.0], color=C_HAIR, roughness=0.5, name=f"Hair_Side_{side}")
        add_mesh_to_scene(scene, side_hair, translation=(x,0.0,1.15), name=f"Hair_Side_{side}")
        # strand cone
        strand = trimesh.creation.cone(radius=0.12, height=0.7, sections=16)
        strand.visual.material = pbr(C_HAIR_DARK, roughness=0.6, name=f"HairStrand_{side}")
        strand.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [1,0,0]))
        add_mesh_to_scene(scene, strand, translation=(x*1.08, -0.15, 1.05), rotation_euler=(np.radians(-15),0,0), name=f"Hair_Strand_{side}")

    # Back hair
    hair_back = create_sphere(0.45, subdivisions=2, color=C_HAIR, roughness=0.5, name="Hair_Back")
    hair_back.apply_scale([1.1,0.7,1.2])
    add_mesh_to_scene(scene, hair_back, translation=(0,-0.85,1.25), name="Hair_Back")

    # Twin tails
    for x in [-0.55, 0.55]:
        side='L' if x<0 else 'R'
        twin = create_sphere(0.22, subdivisions=2, color=C_HAIR, roughness=0.5, name=f"HairTwin_{side}")
        twin.apply_scale([1,0.9,1.8])
        add_mesh_to_scene(scene, twin, translation=(x,-0.65,1.0), name=f"Hair_Twin_{side}")
        # ribbon torus approximated with small cylinder?
        ribbon = trimesh.creation.cylinder(radius=0.09, height=0.025, sections=12)
        ribbon.visual.material = pbr(C_GOLD, roughness=0.4, metallic=0.5, name=f"Ribbon_{side}")
        ribbon.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [1,0,0]))
        add_mesh_to_scene(scene, ribbon, translation=(x,-0.55,1.28), name=f"Ribbon_{side}")

    # Hair highlight
    hl = create_sphere(0.22, subdivisions=2, color=C_HAIR_LIGHT, roughness=0.4, name="HairHighlight")
    hl.apply_scale([1.5,0.4,0.6])
    add_mesh_to_scene(scene, hl, translation=(0.25,0.3,2.15), name="Hair_Highlight")

    # BODY / Tunic
    body = create_cylinder(radius=0.45, height=0.85, color=C_TUNIC, roughness=0.8, name="Body")
    body.apply_scale([1.0,0.85,1.0])
    add_mesh_to_scene(scene, body, translation=(0,0,0.55), name="Body")

    # Belt
    belt = trimesh.creation.cylinder(radius=0.46, height=0.06, sections=24)
    belt.visual.material = pbr(C_BOOTS, roughness=0.8, name="Belt")
    belt.apply_scale([1.0,0.85,1.0])
    belt.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [1,0,0]))
    add_mesh_to_scene(scene, belt, translation=(0,0,0.35), name="Belt")
    # Buckle
    buckle = create_box(extents=[0.14,0.06,0.14], color=C_GOLD, roughness=0.4, metallic=0.7, name="BeltBuckle")
    add_mesh_to_scene(scene, buckle, translation=(0,0.42,0.35), name="BeltBuckle")

    # Shoulders
    for x in [-0.48, 0.48]:
        side='L' if x<0 else 'R'
        shoulder = create_sphere(0.28, subdivisions=2, color=C_ARMOR, roughness=0.35, metallic=0.3, name=f"Shoulder_{side}")
        shoulder.apply_scale([1.0,0.85,0.6])
        add_mesh_to_scene(scene, shoulder, translation=(x,0,0.80), name=f"ShoulderPad_{side}")
        rim = trimesh.creation.cylinder(radius=0.22, height=0.03, sections=16)
        rim.visual.material = pbr(C_GOLD, roughness=0.4, metallic=0.7, name=f"ShoulderRim_{side}")
        rim.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [1,0,0]))
        add_mesh_to_scene(scene, rim, translation=(x,0,0.75), name=f"ShoulderRim_{side}")

    # Cape - flattened box behind
    cape = create_box(extents=[0.55,0.12,0.55], color=C_CAPE, roughness=0.9, name="Cape")
    add_mesh_to_scene(scene, cape, translation=(0,-0.35,0.55), rotation_euler=(np.radians(10),0,0), name="Cape")

    # ARMS
    for x in [-0.62, 0.62]:
        side='L' if x<0 else 'R'
        arm = create_cylinder(radius=0.13, height=0.45, color=C_TUNIC, roughness=0.8, name=f"Arm_{side}")
        arm.apply_transform(trimesh.transformations.rotation_matrix(np.radians(-10 if x>0 else 10), [0,0,1]))
        add_mesh_to_scene(scene, arm, translation=(x,0,0.60), name=f"Arm_{side}")
        hand = create_sphere(0.19, subdivisions=2, color=C_GLOVES, roughness=0.7, name=f"Hand_{side}")
        hand.apply_scale([1.0,0.85,1.0])
        add_mesh_to_scene(scene, hand, translation=(x*1.08,0,0.30), name=f"Hand_{side}")
        # fingers 3 small spheres
        for j in range(3):
            finger = create_sphere(0.06, subdivisions=1, color=C_GLOVES, roughness=0.7, name=f"Finger_{side}_{j}")
            add_mesh_to_scene(scene, finger, translation=(x*1.12 + (j-1)*0.07, 0.12, 0.28), name=f"Finger_{side}_{j}")

    # LEGS
    for x in [-0.22, 0.22]:
        side='L' if x<0 else 'R'
        leg = create_cylinder(radius=0.16, height=0.45, color=C_TUNIC, roughness=0.8, name=f"Leg_{side}")
        add_mesh_to_scene(scene, leg, translation=(x,0,0.05), name=f"Leg_{side}")
        boot = create_cylinder(radius=0.19, height=0.30, color=C_BOOTS, roughness=0.8, name=f"Boot_{side}")
        add_mesh_to_scene(scene, boot, translation=(x,0.05,-0.20), name=f"Boot_{side}")
        sole = create_box(extents=[0.28,0.42,0.06], color=C_BOOTS, roughness=0.8, name=f"Sole_{side}")
        add_mesh_to_scene(scene, sole, translation=(x,0.05,-0.36), name=f"Sole_{side}")

    # SWORD - chibi oversized on side
    blade = create_box(extents=[0.12,0.03,1.2], color=C_BLADE, roughness=0.2, metallic=0.8, name="SwordBlade")
    add_mesh_to_scene(scene, blade, translation=(0.75,0,0.45), rotation_euler=(np.radians(10), np.radians(5), np.radians(8)), name="Sword_Blade")
    # tip
    tip = trimesh.creation.cone(radius=0.06, height=0.25, sections=8)
    tip.visual.material = pbr(C_BLADE, roughness=0.2, metallic=0.8, name="SwordTip")
    # Correct orientation: cone points up Y by default? In trimesh cone points along +Z? Actually need check: cone height along Z
    # We'll place at top
    tip.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0,1,0]))
    add_mesh_to_scene(scene, tip, translation=(0.75,0,1.12), rotation_euler=(np.radians(10), np.radians(5), np.radians(8)), name="Sword_Tip")
    guard = create_box(extents=[0.22,0.08,0.06], color=C_GOLD, roughness=0.4, metallic=0.7, name="SwordGuard")
    add_mesh_to_scene(scene, guard, translation=(0.75,0,-0.15), rotation_euler=(np.radians(10), np.radians(5), np.radians(8)), name="Sword_Guard")
    handle = create_cylinder(radius=0.05, height=0.30, color=C_HANDLE, roughness=0.8, name="SwordHandle")
    add_mesh_to_scene(scene, handle, translation=(0.75,0,-0.32), rotation_euler=(np.radians(10), np.radians(5), np.radians(8)), name="Sword_Handle")
    pommel = create_sphere(0.07, subdivisions=2, color=C_GOLD, roughness=0.4, metallic=0.7, name="SwordPommel")
    add_mesh_to_scene(scene, pommel, translation=(0.75,0,-0.48), name="Sword_Pommel")

    # BASE esagonale
    base = trimesh.creation.cylinder(radius=0.95, height=0.12, sections=6)
    base.visual.material = pbr(C_BASE, roughness=0.9, name="BasePlatform")
    add_mesh_to_scene(scene, base, translation=(0,0,-0.45), name="Base_Platform")
    rim2 = trimesh.creation.cylinder(radius=0.98, height=0.04, sections=6)
    rim2.visual.material = pbr(C_BASE_DARK, roughness=0.8, name="BaseRim")
    add_mesh_to_scene(scene, rim2, translation=(0,0,-0.48), name="Base_Rim")
    for i in range(3):
        angle = i*120
        rad=0.6
        x = np.cos(np.radians(angle))*rad
        y = np.sin(np.radians(angle))*rad
        rock = create_sphere(0.08, subdivisions=1, color=C_BASE_DARK, roughness=0.8, name=f"Rock_{i}")
        rock.apply_scale([1,0.8,0.6])
        add_mesh_to_scene(scene, rock, translation=(x,y,-0.38), name=f"Base_Rock_{i}")

    # Ground plane (for shadow)
    ground = trimesh.creation.box(extents=[10,10,0.01])
    ground.visual.material = pbr(mat_rgba(245,245,246,255), roughness=0.95, name="Ground")
    ground.apply_translation([0,0,-0.52])
    add_mesh_to_scene(scene, ground, name="Ground")

    return scene

def export_scene(scene):
    print(f"Scene ha {len(scene.geometry)} mesh")

    # GLB
    glb_path = EXPORTS / "Hoshino_Chibi.glb"
    try:
        # trimesh export glb
        data = scene.export(file_type='glb')
        # data can be bytes
        if isinstance(data, dict):
            # sometimes returns dict?
            pass
        with open(glb_path, 'wb') as f:
            f.write(data)
        print(f"✓ GLB esportato: {glb_path} ({glb_path.stat().st_size/1024:.1f} KB)")
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"⚠ GLB errore: {e}")

    # OBJ + MTL
    obj_path = EXPORTS / "Hoshino_Chibi.obj"
    try:
        obj_data = scene.export(file_type='obj')
        # obj export returns str if scene, or dict
        if isinstance(obj_data, dict):
            # contains obj + mtl
            pass
        with open(obj_path, 'w', encoding='utf-8') as f:
            if isinstance(obj_data, bytes):
                f.write(obj_data.decode('utf-8'))
            else:
                f.write(obj_data)
        print(f"✓ OBJ esportato: {obj_path}")
        # trimesh automatically writes mtl? Check
        mtl_path = EXPORTS / "Hoshino_Chibi.mtl"
        if mtl_path.exists():
            print(f"✓ MTL trovato: {mtl_path}")
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"⚠ OBJ errore: {e}")

    # STL - need merged mesh
    stl_path = EXPORTS / "Hoshino_Chibi.stl"
    try:
        combined = trimesh.util.concatenate(tuple(scene.dump()))
        # dump returns list of meshes in scene with transforms applied
        # Actually scene.dump() gives meshes already transformed? Use to_mesh
        # Let's get combined via scene.to_mesh()
        try:
            combined2 = scene.to_mesh()
            if combined2 is not None:
                combined = combined2
        except:
            pass
        combined.export(stl_path)
        print(f"✓ STL esportato: {stl_path} ({stl_path.stat().st_size/1024:.1f} KB)")
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"⚠ STL errore: {e}")

    # FBX not natively supported by trimesh, create placeholder note
    fbx_note = EXPORTS / "Hoshino_Chibi_FBX_info.txt"
    fbx_note.write_text("Per FBX: aprite il file .blend in Blender ed esportate File > Export > FBX\nIl modello è stato progettato per Blender 3.x/4.x/5.x\n", encoding='utf-8')
    print(f"✓ Nota FBX creata")

    # Also export a single merged scene as glTF inspection
    # Save scene graph json
    info_path = EXPORTS / "character_info.json"
    import json
    info = {
        "name": "Hoshino - Chibi Guerriero dell'Aurora",
        "style": "Anime Chibi 2.5 heads, ispirato Genshin/Zelda",
        "height_m": 2.5,
        "height_cm_print": 8.0,
        "polygons": sum(len(m.faces) for m in scene.geometry.values()),
        "meshes": len(scene.geometry),
        "materials": list(set([m.visual.material.name for m in scene.geometry.values() if hasattr(m.visual, 'material') and m.visual.material is not None])),
        "exports": {
            "glb": str(glb_path.relative_to(ROOT)),
            "obj": str(obj_path.relative_to(ROOT)),
            "stl": str(stl_path.relative_to(ROOT))
        },
        "rig": "Non riggato (modellino statico). Per animazione, usare Blender script con Rigify.",
        "print_settings": {
            "scala": "1:1 = 8cm altezza",
            "supporti": "consigliati per spada e capelli",
            "resina": "consigliata per dettagli volto",
            "FDM": "0.12mm layer height, supporti ad albero"
        }
    }
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(f"✓ Info salvata: {info_path}")

if __name__ == "__main__":
    print("Costruzione della versione legacy in exports/legacy/ (non è il modello v2)...")
    scene = build_scene()
    export_scene(scene)
    print("✓ Completato!")
