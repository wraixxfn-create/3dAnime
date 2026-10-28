#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modellino 3D Chibi Anime - Personaggio Videogioco
Stile: Hoshino - Chibi Guerriero dell'Aurora
Ispirato a Genshin / Zelda / Ni no Kuni
Compatibile bpy 4.x / 5.x
"""
import bpy
import math
import mathutils
from pathlib import Path


# --------------------------------------------------
# UTILS
# --------------------------------------------------
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Rimuove tutto
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

def new_material(name, base_color, roughness=0.6, metallic=0.0, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (300, 0)
    princ = nodes.new("ShaderNodeBsdfPrincipled")
    princ.location = (0, 0)
    # Colore base
    princ.inputs["Base Color"].default_value = base_color
    princ.inputs["Roughness"].default_value = roughness
    if "Metallic" in princ.inputs:
        princ.inputs["Metallic"].default_value = metallic
    # Emission per occhi
    if emission_strength > 0:
        if "Emission Strength" in princ.inputs:
            princ.inputs["Emission Strength"].default_value = emission_strength
            if "Emission Color" in princ.inputs:
                princ.inputs["Emission Color"].default_value = base_color
    links.new(princ.outputs["BSDF"], out.inputs["Surface"])
    return mat

def shade_smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True

def add_subsurf(obj, levels=2):
    mod = obj.modifiers.new("Subdivision", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels

def add_mirror(obj, axis='X'):
    mod = obj.modifiers.new("Mirror", "MIRROR")
    mod.use_axis[0] = axis == 'X'
    mod.use_axis[1] = axis == 'Y'
    mod.use_axis[2] = axis == 'Z'

# --------------------------------------------------
# MATERIALI
# --------------------------------------------------
def create_materials():
    mats = {}
    mats["Skin"] = new_material("Skin", (0.98, 0.82, 0.73, 1.0), roughness=0.7)
    mats["SkinShadow"] = new_material("SkinShadow", (0.95, 0.75, 0.65, 1.0), roughness=0.8)
    mats["Hair"] = new_material("Hair", (0.35, 0.78, 0.95, 1.0), roughness=0.5)  # azzurro anime
    mats["HairDark"] = new_material("HairDark", (0.22, 0.45, 0.75, 1.0), roughness=0.6)
    mats["HairLight"] = new_material("HairLight", (0.75, 0.92, 1.0, 1.0), roughness=0.4)
    mats["EyeWhite"] = new_material("EyeWhite", (1.0, 1.0, 1.0, 1.0), roughness=0.2)
    mats["Iris"] = new_material("Iris", (0.20, 0.55, 0.95, 1.0), roughness=0.3, emission_strength=0.3)
    mats["Pupil"] = new_material("Pupil", (0.05, 0.05, 0.08, 1.0), roughness=0.3)
    mats["EyeHighlight"] = new_material("EyeHighlight", (1.0, 1.0, 1.0, 1.0), roughness=0.1)
    mats["Tunic"] = new_material("Tunic", (0.95, 0.95, 0.98, 1.0), roughness=0.8)
    mats["Armor"] = new_material("Armor", (0.85, 0.88, 0.92, 1.0), roughness=0.35, metallic=0.3)
    mats["ArmorGold"] = new_material("ArmorGold", (0.95, 0.80, 0.25, 1.0), roughness=0.4, metallic=0.7)
    mats["Cape"] = new_material("Cape", (0.18, 0.28, 0.65, 1.0), roughness=0.9)
    mats["Gloves"] = new_material("Gloves", (0.25, 0.25, 0.30, 1.0), roughness=0.7)
    mats["Boots"] = new_material("Boots", (0.30, 0.22, 0.18, 1.0), roughness=0.8)
    mats["SwordBlade"] = new_material("SwordBlade", (0.85, 0.90, 0.95, 1.0), roughness=0.2, metallic=0.8)
    mats["SwordHandle"] = new_material("SwordHandle", (0.35, 0.18, 0.10, 1.0), roughness=0.8)
    mats["Base"] = new_material("Base", (0.92, 0.92, 0.90, 1.0), roughness=0.9)
    mats["BaseDark"] = new_material("BaseDark", (0.65, 0.70, 0.78, 1.0), roughness=0.8)
    mats["Blush"] = new_material("Blush", (1.0, 0.55, 0.65, 1.0), roughness=0.8)
    return mats

# --------------------------------------------------
# CREAZIONE PERSONAGGIO
# --------------------------------------------------
def create_head(mats):
    # Testa - sfera grande stile chibi (rapporto 1:1.5)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.95, location=(0, 0, 1.45))
    head = bpy.context.active_object
    head.name = "Head"
    head.scale = (1.0, 0.95, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    head.data.materials.append(mats["Skin"])
    shade_smooth(head)
    add_subsurf(head, 2)

    # Guance blush
    for x in [-0.38, 0.38]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.12, location=(x, 0.82, 1.25))
        blush = bpy.context.active_object
        blush.name = f"Blush_{'L' if x<0 else 'R'}"
        blush.scale = (1.2, 0.4, 0.8)
        bpy.ops.object.transform_apply(scale=True)
        blush.data.materials.append(mats["Blush"])
        shade_smooth(blush)
        # trasparenza via alpha
        blush.data.materials[0].blend_method = 'BLEND'
        # Parent a testa
        blush.parent = head

    # Naso piccolo
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.06, location=(0, 0.90, 1.30))
    nose = bpy.context.active_object
    nose.name = "Nose"
    nose.scale = (1, 0.5, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    nose.data.materials.append(mats["SkinShadow"])
    nose.parent = head

    # Orecchie
    for x in [-0.92, 0.92]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.20, location=(x, 0.0, 1.45))
        ear = bpy.context.active_object
        ear.name = f"Ear_{'L' if x<0 else 'R'}"
        ear.scale = (0.4, 0.6, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        ear.data.materials.append(mats["Skin"])
        shade_smooth(ear)
        ear.parent = head

    # Orecchie a punta leggere (elfiche)
        bpy.ops.mesh.primitive_cone_add(radius1=0.12, depth=0.25, location=(x*1.05, 0.0, 1.62))
        tip = bpy.context.active_object
        tip.name = f"EarTip_{'L' if x<0 else 'R'}"
        tip.rotation_euler = (0, 0, math.radians(30 if x>0 else -30))
        tip.data.materials.append(mats["Skin"])
        shade_smooth(tip)
        tip.parent = head

    return head

def create_eyes(mats, parent):
    # Occhi anime grandi
    for x in [-0.35, 0.35]:
        side = 'L' if x<0 else 'R'
        # Sclera (bianco occhio) - forma ovale appiattita
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.28, location=(x, 0.84, 1.40))
        eye_white = bpy.context.active_object
        eye_white.name = f"EyeWhite_{side}"
        eye_white.scale = (1.15, 0.35, 1.3)
        bpy.ops.object.transform_apply(scale=True)
        # Appiattiamo leggermente verso testa per integrazione
        eye_white.data.materials.append(mats["EyeWhite"])
        shade_smooth(eye_white)
        eye_white.parent = parent

        # Iride grande anime
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.19, location=(x, 0.96, 1.38))
        iris = bpy.context.active_object
        iris.name = f"Iris_{side}"
        iris.scale = (1.0, 0.25, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        iris.data.materials.append(mats["Iris"])
        shade_smooth(iris)
        iris.parent = parent

        # Pupilla
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.11, location=(x, 1.02, 1.38))
        pupil = bpy.context.active_object
        pupil.name = f"Pupil_{side}"
        pupil.scale = (1.0, 0.2, 1.20)
        bpy.ops.object.transform_apply(scale=True)
        pupil.data.materials.append(mats["Pupil"])
        shade_smooth(pupil)
        pupil.parent = parent

        # Highlight principale
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.055, location=(x-0.06, 1.06, 1.45))
        hl1 = bpy.context.active_object
        hl1.name = f"Highlight1_{side}"
        hl1.scale = (1, 0.2, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        hl1.data.materials.append(mats["EyeHighlight"])
        hl1.parent = parent

        # Highlight secondario piccolo
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.03, location=(x+0.07, 1.05, 1.32))
        hl2 = bpy.context.active_object
        hl2.name = f"Highlight2_{side}"
        hl2.scale = (1, 0.2, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        hl2.data.materials.append(mats["EyeHighlight"])
        hl2.parent = parent

    # Sopracciglia / contorno occhi (sottile)
    for x in [-0.35, 0.35]:
        side = 'L' if x<0 else 'R'
        bpy.ops.mesh.primitive_torus_add(major_radius=0.28, minor_radius=0.02, major_segments=16, minor_segments=8, location=(x, 0.80, 1.55))
        brow = bpy.context.active_object
        brow.name = f"Brow_{side}"
        brow.scale = (1.15, 0.35, 0.6)
        brow.rotation_euler = (math.radians(85), 0, 0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        brow.data.materials.append(mats["HairDark"])
        brow.parent = parent

def create_hair(mats, parent):
    # Capelli anime - caschetto voluminoso
    # Base capelli superiore (calotta)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.98, location=(0, 0, 1.70))
    hair_top = bpy.context.active_object
    hair_top.name = "Hair_Top"
    hair_top.scale = (1.08, 1.05, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    hair_top.data.materials.append(mats["Hair"])
    shade_smooth(hair_top)
    add_subsurf(hair_top, 1)
    hair_top.parent = parent

    # Frangia frontale - 3 ciocche principali
    for i, (x, rot) in enumerate([(-0.35, -15), (0.0, 0), (0.35, 15)]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.75, 1.62))
        bangs = bpy.context.active_object
        bangs.name = f"Hair_Bangs_{i}"
        bangs.scale = (0.32, 0.18, 0.45)
        bangs.rotation_euler = (math.radians(25), math.radians(rot), 0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        # Bevel per ammorbidire
        mod = bangs.modifiers.new("Bevel", "BEVEL")
        mod.width = 0.08
        mod.segments = 2
        add_subsurf(bangs, 1)
        bangs.data.materials.append(mats["Hair"])
        shade_smooth(bangs)
        bangs.parent = parent

    # Ciocche laterali lunghe (hime cut)
    for x in [-0.75, 0.75]:
        side = 'L' if x<0 else 'R'
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.0, 1.15))
        side_hair = bpy.context.active_object
        side_hair.name = f"Hair_Side_{side}"
        side_hair.scale = (0.28, 0.35, 1.0)
        # Curva verso interno in basso
        mod = side_hair.modifiers.new("Bevel", "BEVEL")
        mod.width = 0.06
        add_subsurf(side_hair, 1)
        side_hair.data.materials.append(mats["Hair"])
        shade_smooth(side_hair)
        side_hair.parent = parent

        # Codina laterale / ciocca dietro orecchio
        bpy.ops.mesh.primitive_cone_add(radius1=0.12, depth=0.7, location=(x*1.08, -0.15, 1.05))
        strand = bpy.context.active_object
        strand.name = f"Hair_Strand_{side}"
        strand.rotation_euler = (math.radians(-15), 0, 0)
        strand.data.materials.append(mats["HairDark"])
        shade_smooth(strand)
        strand.parent = parent

    # Ciuffo posteriore / coda bassa
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.45, location=(0, -0.85, 1.25))
    hair_back = bpy.context.active_object
    hair_back.name = "Hair_Back"
    hair_back.scale = (1.1, 0.7, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    hair_back.data.materials.append(mats["Hair"])
    shade_smooth(hair_back)
    hair_back.parent = parent

    # Due codini bassi stile twin-tails chibi (opzionale)
    for x in [-0.55, 0.55]:
        side = 'L' if x<0 else 'R'
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.22, location=(x, -0.65, 1.0))
        twin = bpy.context.active_object
        twin.name = f"Hair_Twin_{side}"
        twin.scale = (1, 0.9, 1.8)
        bpy.ops.object.transform_apply(scale=True)
        twin.data.materials.append(mats["Hair"])
        shade_smooth(twin)
        twin.parent = parent

        # Nastrino
        bpy.ops.mesh.primitive_torus_add(major_radius=0.09, minor_radius=0.025, major_segments=12, minor_segments=6, location=(x, -0.55, 1.28))
        ribbon = bpy.context.active_object
        ribbon.name = f"Ribbon_{side}"
        ribbon.rotation_euler = (math.radians(90), 0, 0)
        ribbon.data.materials.append(mats["ArmorGold"])
        ribbon.parent = parent

    # Riflesso chiaro sulla sommità
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.22, location=(0.25, 0.3, 2.15))
    highlight = bpy.context.active_object
    highlight.name = "Hair_Highlight"
    highlight.scale = (1.5, 0.4, 0.6)
    bpy.ops.object.transform_apply(scale=True)
    highlight.data.materials.append(mats["HairLight"])
    highlight.parent = parent

def create_body(mats):
    # Corpo / Tunica
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.85, location=(0, 0, 0.55))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (1.0, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(mats["Tunic"])
    shade_smooth(body)
    add_subsurf(body, 1)

    # Cintura
    bpy.ops.mesh.primitive_torus_add(major_radius=0.46, minor_radius=0.06, major_segments=20, minor_segments=8, location=(0, 0, 0.35))
    belt = bpy.context.active_object
    belt.name = "Belt"
    belt.rotation_euler = (math.radians(90), 0, 0)
    belt.scale = (1.0, 0.85, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    belt.data.materials.append(mats["Boots"])

    # Fibbia cintura
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0.42, 0.35))
    buckle = bpy.context.active_object
    buckle.name = "BeltBuckle"
    buckle.scale = (0.7, 0.3, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    buckle.data.materials.append(mats["ArmorGold"])
    mod = buckle.modifiers.new("Bevel", "BEVEL")
    mod.width = 0.02

    # Spallacci armatura
    for x in [-0.48, 0.48]:
        side = 'L' if x<0 else 'R'
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.28, location=(x, 0, 0.80))
        shoulder = bpy.context.active_object
        shoulder.name = f"ShoulderPad_{side}"
        shoulder.scale = (1.0, 0.85, 0.6)
        bpy.ops.object.transform_apply(scale=True)
        shoulder.data.materials.append(mats["Armor"])
        shade_smooth(shoulder)
        # Bordo dorato
        bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.03, major_segments=16, minor_segments=6, location=(x, 0, 0.75))
        rim = bpy.context.active_object
        rim.name = f"ShoulderRim_{side}"
        rim.rotation_euler = (math.radians(90), 0, 0)
        rim.data.materials.append(mats["ArmorGold"])

    # Mantellina corta
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.55, location=(0, -0.28, 0.55))
    cape = bpy.context.active_object
    cape.name = "Cape"
    cape.scale = (1.0, 0.45, 1.0)
    cape.rotation_euler = (math.radians(10), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Taglia metà davanti per effetto mantello
    cape.data.materials.append(mats["Cape"])
    shade_smooth(cape)

    return body

def create_limbs(mats, body):
    # Braccia
    for x in [-0.62, 0.62]:
        side = 'L' if x<0 else 'R'
        # Braccio superiore
        bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.45, location=(x, 0, 0.60))
        arm = bpy.context.active_object
        arm.name = f"Arm_{side}"
        arm.rotation_euler = (0, 0, math.radians(-10 if x>0 else 10))
        arm.data.materials.append(mats["Tunic"])
        shade_smooth(arm)

        # Guanto / mano chibi grande
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.19, location=(x*1.08, 0, 0.30))
        hand = bpy.context.active_object
        hand.name = f"Hand_{side}"
        hand.scale = (1.0, 0.85, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        hand.data.materials.append(mats["Gloves"])
        shade_smooth(hand)

        # Dita stilizzate (3)
        for j in range(3):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.06, location=(x*1.12 + (j-1)*0.07, 0.12, 0.28))
            finger = bpy.context.active_object
            finger.name = f"Finger_{side}_{j}"
            finger.data.materials.append(mats["Gloves"])
            finger.parent = hand

    # Gambe
    for x in [-0.22, 0.22]:
        side = 'L' if x<0 else 'R'
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.45, location=(x, 0, 0.05))
        leg = bpy.context.active_object
        leg.name = f"Leg_{side}"
        leg.data.materials.append(mats["Tunic"])
        shade_smooth(leg)

        # Stivale
        bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.30, location=(x, 0.05, -0.20))
        boot = bpy.context.active_object
        boot.name = f"Boot_{side}"
        boot.data.materials.append(mats["Boots"])
        shade_smooth(boot)

        # Suola
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.05, -0.36))
        sole = bpy.context.active_object
        sole.name = f"Sole_{side}"
        sole.scale = (0.28, 0.42, 0.06)
        sole.data.materials.append(mats["Boots"])
        mod = sole.modifiers.new("Bevel", "BEVEL")
        mod.width = 0.02

def create_sword(mats):
    # Spada chibi sovradimensionata
    # Lama
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.75, 0, 0.45))
    blade = bpy.context.active_object
    blade.name = "Sword_Blade"
    blade.scale = (0.12, 0.03, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    mod = blade.modifiers.new("Bevel", "BEVEL")
    mod.width = 0.02
    blade.data.materials.append(mats["SwordBlade"])
    # Punta
    bpy.ops.mesh.primitive_cone_add(radius1=0.12, depth=0.25, location=(0.75, 0, 1.15))
    tip = bpy.context.active_object
    tip.name = "Sword_Tip"
    tip.scale = (1, 0.25, 1)
    tip.rotation_euler = (0, 0, 0)
    tip.data.materials.append(mats["SwordBlade"])
    # Elimina congiunzione via parent
    tip.parent = blade

    # Guardia
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.75, 0, -0.15))
    guard = bpy.context.active_object
    guard.name = "Sword_Guard"
    guard.scale = (0.22, 0.08, 0.06)
    guard.data.materials.append(mats["ArmorGold"])
    guard.parent = blade

    # Impugnatura
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.30, location=(0.75, 0, -0.30))
    handle = bpy.context.active_object
    handle.name = "Sword_Handle"
    handle.data.materials.append(mats["SwordHandle"])
    handle.parent = blade

    # Pomolo
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.07, location=(0.75, 0, -0.45))
    pommel = bpy.context.active_object
    pommel.name = "Sword_Pommel"
    pommel.data.materials.append(mats["ArmorGold"])
    pommel.parent = blade

    # Inclinazione per pose carina
    blade.rotation_euler = (math.radians(10), math.radians(5), math.radians(8))

    # Mano destra che tiene (collega)
    return blade

def create_base(mats):
    # Base espositiva esagonale
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.95, depth=0.12, location=(0, 0, -0.45))
    base = bpy.context.active_object
    base.name = "Base_Platform"
    base.data.materials.append(mats["Base"])
    shade_smooth(base)
    # Bordo scuro
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.98, depth=0.04, location=(0, 0, -0.48))
    rim = bpy.context.active_object
    rim.name = "Base_Rim"
    rim.data.materials.append(mats["BaseDark"])
    # Effetto erba / dettagli
    for i in range(3):
        angle = i * 120
        rad = 0.6
        x = math.cos(math.radians(angle)) * rad
        y = math.sin(math.radians(angle)) * rad
        bpy.ops.mesh.primitive_icosphere_add(subdivisions=1, radius=0.08, location=(x, y, -0.38))
        rock = bpy.context.active_object
        rock.name = f"Base_Rock_{i}"
        rock.data.materials.append(mats["BaseDark"])
        rock.scale = (1, 0.8, 0.6)

    # Nome inciso (testo 3D)
    bpy.ops.object.text_add(location=(0, 0.75, -0.39))
    text = bpy.context.active_object
    text.name = "Base_Text"
    text.data.body = "HOSHINO"
    text.data.align_x = 'CENTER'
    text.data.align_y = 'CENTER'
    text.data.extrude = 0.015
    text.scale = (0.18, 0.18, 0.18)
    text.rotation_euler = (math.radians(90), 0, 0)
    mat_text = new_material("TextMat", (0.18, 0.28, 0.65, 1.0), roughness=0.7)
    text.data.materials.append(mat_text)

def setup_environment():
    # World light
    world = bpy.data.worlds['World']
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs[0].default_value = (0.95, 0.96, 0.99, 1.0)
        bg.inputs[1].default_value = 1.0

    # Camera
    bpy.ops.object.camera_add(location=(2.2, -3.2, 1.3), rotation=(math.radians(75), 0, math.radians(35)))
    cam = bpy.context.active_object
    cam.name = "Camera_Main"
    bpy.context.scene.camera = cam
    cam.data.lens = 50
    cam.data.dof.use_dof = False

    # Tre luci studio
    # Key light
    bpy.ops.object.light_add(type='SUN', location=(3, -3, 4))
    sun = bpy.context.active_object
    sun.name = "Sun_Key"
    sun.data.energy = 6.0
    sun.data.color = (1.0, 0.98, 0.95)
    sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))

    # Fill
    bpy.ops.object.light_add(type='SUN', location=(-2, -2, 3))
    fill = bpy.context.active_object
    fill.name = "Sun_Fill"
    fill.data.energy = 2.5
    fill.data.color = (0.75, 0.85, 1.0)

    # Rim light
    bpy.ops.object.light_add(type='SUN', location=(0, 3, 2))
    rim = bpy.context.active_object
    rim.name = "Sun_Rim"
    rim.data.energy = 3.0
    rim.data.color = (1.0, 1.0, 1.0)

    # Ground shadow catcher
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.52))
    ground = bpy.context.active_object
    ground.name = "Ground_Shadow"
    mat_ground = bpy.data.materials.new("GroundMat")
    mat_ground.use_nodes = True
    nodes = mat_ground.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    princ = nodes.new("ShaderNodeBsdfDiffuse")
    princ.inputs["Color"].default_value = (0.95, 0.95, 0.96, 1.0)
    mat_ground.node_tree.links.new(princ.outputs["BSDF"], out.inputs["Surface"])
    ground.data.materials.append(mat_ground)
    ground.is_shadow_catcher = True if hasattr(ground, "is_shadow_catcher") else False

def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in bpy.context.preferences.addons else 'CYCLES'
    # Tenta EEVEE, fallback CYCLES
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT' if bpy.app.version >= (4,2,0) else 'BLENDER_EEVEE'
    except:
        try:
            scene.render.engine = 'BLENDER_EEVEE'
        except:
            scene.render.engine = 'CYCLES'

    scene.render.resolution_x = 2048
    scene.render.resolution_y = 2048
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.display_settings.display_device = 'sRGB'
    # EEVEE settings
    if 'EEVEE' in scene.render.engine:
        scene.eevee.taa_render_samples = 64
        try:
            scene.eevee.use_soft_shadows = True
            scene.eevee.use_bloom = True
            scene.eevee.bloom_intensity = 0.15
            scene.eevee.bloom_threshold = 1.0
        except:
            pass
    else:
        scene.cycles.samples = 128

def build_character():
    clear_scene()
    mats = create_materials()
    head = create_head(mats)
    create_eyes(mats, head)
    create_hair(mats, head)
    body = create_body(mats)
    create_limbs(mats, body)
    create_sword(mats)
    create_base(mats)
    setup_environment()
    setup_render()
    # Parent head to body for unity
    head.parent = body
    # Seleziona tutto per vista
    bpy.ops.object.select_all(action='SELECT')
    print("✓ Personaggio Hoshino creato con successo!")

def main():
    build_character()
    # Paths
    root = Path(__file__).resolve().parents[1]
    blend_path = root / "Hoshino_Chibi.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(f"✓ Salvato .blend in {blend_path}")

    # Export
    exports = root / "exports"
    exports.mkdir(exist_ok=True)

    # Seleziona solo mesh per export
    bpy.ops.object.select_all(action='SELECT')
    # FBX
    fbx_path = exports / "Hoshino_Chibi.fbx"
    try:
        bpy.ops.export_scene.fbx(filepath=str(fbx_path), apply_scale_options='FBX_SCALE_ALL', use_selection=True, object_types={'MESH','ARMATURE'})
        print(f"✓ FBX esportato: {fbx_path}")
    except Exception as e:
        print(f"⚠ FBX errore: {e}")

    # glTF / GLB
    glb_path = exports / "Hoshino_Chibi.glb"
    try:
        bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format='GLB')
        print(f"✓ GLB esportato: {glb_path}")
    except Exception as e:
        print(f"⚠ GLB errore: {e}")

    # OBJ
    obj_path = exports / "Hoshino_Chibi.obj"
    try:
        bpy.ops.wm.obj_export(filepath=str(obj_path), export_selected_objects=True, apply_modifiers=True)
        print(f"✓ OBJ esportato: {obj_path}")
    except:
        try:
            bpy.ops.export_scene.obj(filepath=str(obj_path), use_selection=True)
            print(f"✓ OBJ esportato (legacy): {obj_path}")
        except Exception as e:
            print(f"⚠ OBJ errore: {e}")

    # STL per stampa 3D
    stl_path = exports / "Hoshino_Chibi.stl"
    try:
        bpy.ops.wm.stl_export(filepath=str(stl_path), export_selected_objects=True, apply_modifiers=True)
        print(f"✓ STL esportato: {stl_path}")
    except:
        try:
            bpy.ops.export_mesh.stl(filepath=str(stl_path), use_selection=True)
            print(f"✓ STL esportato (legacy): {stl_path}")
        except Exception as e:
            print(f"⚠ STL errore: {e}")

    # Render preview
    renders = root / "renders"
    renders.mkdir(exist_ok=True)
    render_path = renders / "preview.png"
    bpy.context.scene.render.filepath = str(render_path)
    # Assicurati camera attiva
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            bpy.context.scene.camera = obj
            break
    try:
        bpy.ops.render.render(write_still=True)
        print(f"✓ Render salvato: {render_path}")
    except Exception as e:
        print(f"⚠ Render errore: {e}")

    # Render vista extra - close up volto
    try:
        cam = bpy.context.scene.camera
        cam.location = (0.4, -1.5, 1.45)
        cam.rotation_euler = (math.radians(78), 0, 0)
        bpy.context.scene.render.filepath = str(renders / "preview_closeup.png")
        bpy.ops.render.render(write_still=True)
        print(f"✓ Closeup salvato")
        # Ripristina
        cam.location = (2.2, -3.2, 1.3)
        cam.rotation_euler = (math.radians(75), 0, math.radians(35))
    except Exception as e:
        print(f"⚠ Closeup errore: {e}")

if __name__ == "__main__":
    main()
