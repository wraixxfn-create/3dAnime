#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hoshino: statuetta chibi procedurale e scena studio.

Eseguire in Blender 4.2+ (o con il modulo Python ``bpy``):
    blender --background --python scripts/create_character.py -- --export --render --save-blend

Senza opzioni lo script costruisce la scena, utile nel Text Editor di Blender.
Gli export includono solo il personaggio; il pavimento e le luci restano nella
scena di rendering. Lo STL è scalato a 80 mm di altezza (unità STL in mm).
"""

import argparse
import json
import math
import sys
import zipfile
from pathlib import Path

import bpy
from mathutils import Vector


def project_root():
    # In Blender il Text Editor può eseguire il codice senza un __file__ valido.
    try:
        candidate = Path(__file__).resolve().parent.parent
        if (candidate / "viewer.html").exists():
            return candidate
    except NameError:
        pass
    return Path.cwd()


ROOT = project_root()


def srgb(hex_color):
    """Interpreta una tinta esadecimale sRGB come colore lineare Blender."""
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb) + (1,)


def material(name, color, roughness=0.4, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = srgb(color)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = mat.diffuse_color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = metallic
    return mat


def make_materials():
    definitions = {
        "Skin": ("#F8C9B0", .5, 0),
        "SkinShadow": ("#DC9F91", .55, 0),
        "Blush": ("#F39DA4", .6, 0),
        "Hair": ("#6AB9D8", .38, 0),
        "HairLight": ("#8BCFE7", .38, 0),
        "HairMid": ("#58A4CC", .4, 0),
        "HairShadow": ("#3D80AE", .42, 0),
        "EyeOutline": ("#263B55", .42, 0),
        "EyeWhite": ("#F9FDFF", .22, 0),
        "IrisDark": ("#176AA7", .25, 0),
        "Iris": ("#2EA7D7", .25, 0),
        "IrisLight": ("#83DCF1", .24, 0),
        "Pupil": ("#132E4A", .25, 0),
        "Highlight": ("#FFFFFF", .18, 0),
        "Ivory": ("#F2F2EC", .42, 0),
        "Armor": ("#D9E7ED", .32, .15),
        "Gold": ("#D9AA55", .28, .55),
        "GoldLight": ("#F0D18C", .27, .48),
        "Cape": ("#244B82", .55, 0),
        "CapeLight": ("#396DA6", .52, 0),
        "Navy": ("#293D5D", .48, 0),
        "Leather": ("#755447", .55, 0),
        "Blade": ("#BCD4DF", .25, .55),
        "BladeLight": ("#EAF5F6", .24, .48),
        "BladeBlue": ("#4B99BF", .29, .32),
        "Base": ("#E8EEF0", .48, 0),
        "BaseTop": ("#F7F6F0", .5, 0),
        "BaseShadow": ("#8299A7", .5, .12),
        "Floor": ("#E5EFF2", .8, 0),
    }
    return {name: material(name, *args) for name, args in definitions.items()}


def set_active_collection(collection):
    layer = bpy.context.view_layer.layer_collection.children.get(collection.name)
    if layer:
        bpy.context.view_layer.active_layer_collection = layer


def finish(obj, name, mat, smooth=True):
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    if obj.type == "MESH" and smooth:
        for face in obj.data.polygons:
            face.use_smooth = True
    return obj


def sphere(name, location, scale, mat, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.scale = scale
    return finish(obj, name, mat)


def bevel(obj, width=.025, segments=3):
    mod = obj.modifiers.new("Bordi morbidi", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.affect = 'EDGES'
    mod.limit_method = 'ANGLE'
    return obj


def cylinder(name, location, radius, depth, mat, vertices=48, scale=(1, 1, 1), edge=.015):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(obj, name, mat)
    if edge:
        bevel(obj, edge)
    return obj


def between(name, a, b, radius, mat, radius_end=None, vertices=32, edge=.012):
    a, b = Vector(a), Vector(b)
    direction = b - a
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius,
                                    radius2=radius if radius_end is None else radius_end,
                                    depth=direction.length, location=(a + b) / 2)
    obj = bpy.context.object
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')
    finish(obj, name, mat)
    if edge:
        bevel(obj, edge)
    return obj


def torus(name, location, major, minor, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=10,
                                    location=location, major_radius=major, minor_radius=minor)
    obj = bpy.context.object
    obj.scale = scale
    return finish(obj, name, mat)


def mesh(name, verts, faces, mat, smooth=True):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, mat, smooth)


def line(name, points, radius, mat, cyclic=False, resolution=12):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = resolution
    data.bevel_depth = radius
    data.bevel_resolution = 3
    data.use_fill_caps = True
    spline = data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, mat)


def slab(name, points, front, thickness, mat, edge=.01):
    """Placca chiusa nel piano XZ, con il fronte rivolto verso -Y."""
    points = list(points)
    area = sum(points[i][0] * points[(i + 1) % len(points)][1]
               - points[(i + 1) % len(points)][0] * points[i][1] for i in range(len(points)))
    if area < 0:
        points.reverse()
    count = len(points)
    verts = [(x, front, z) for x, z in points] + [(x, front + thickness, z) for x, z in points]
    faces = [tuple(range(count)), tuple(reversed(range(count, 2 * count)))]
    faces += [(i, i + count, (i + 1) % count + count, (i + 1) % count) for i in range(count)]
    obj = mesh(name, verts, faces, mat, smooth=False)
    if edge:
        bevel(obj, edge, 3)
    return obj


def star(name, x, y, z, radius, mat, points=4, inner=.32, thickness=.025):
    coords = []
    for i in range(points * 2):
        a = math.pi / 2 + i * math.pi / points
        r = radius if i % 2 == 0 else radius * inner
        coords.append((x + math.cos(a) * r, z + math.sin(a) * r))
    return slab(name, coords, y, thickness, mat, .005)


def ring_body(name, sections, mat, steps=48):
    """Superficie chiusa ottenuta da sezioni orizzontali ellittiche."""
    verts, faces = [], []
    for z, rx, ry, cy in sections:
        for i in range(steps):
            a = 2 * math.pi * i / steps
            verts.append((rx * math.cos(a), cy + ry * math.sin(a), z))
    for j in range(len(sections) - 1):
        for i in range(steps):
            k = (i + 1) % steps
            faces.append((j * steps + i, j * steps + k, (j + 1) * steps + k, (j + 1) * steps + i))
    faces.append(tuple(reversed(range(steps))))
    faces.append(tuple((len(sections) - 1) * steps + i for i in range(steps)))
    return mesh(name, verts, faces, mat)


HAIR_CENTER = Vector((0, .03, 2.84))
HAIR_RADIUS = Vector((.93, .78, .98))


def hair_point(az, el, k=1.0):
    """Punto sull'ellissoide dei capelli: az=0 davanti, el=0 sulla cima."""
    az, el = math.radians(az), math.radians(el)
    direction = Vector((math.sin(el) * math.sin(az),
                        -math.sin(el) * math.cos(az),
                        math.cos(el)))
    return HAIR_CENTER + Vector((direction.x * HAIR_RADIUS.x,
                                 direction.y * HAIR_RADIUS.y,
                                 direction.z * HAIR_RADIUS.z)) * k


def hair_normal(point):
    """Normale dell'ellissoide, più affidabile della direzione dal centro."""
    rel = point - HAIR_CENTER
    return Vector((rel.x / HAIR_RADIUS.x ** 2,
                   rel.y / HAIR_RADIUS.y ** 2,
                   rel.z / HAIR_RADIUS.z ** 2)).normalized()


def catmull_rom(points, samples):
    """Curva morbida che passa per i punti di controllo."""
    pts = [Vector(p) for p in points]
    padded = [pts[0]] + pts + [pts[-1]]
    segments = len(pts) - 1
    out = []
    per_segment = max(2, samples // segments)
    for s in range(segments):
        p0, p1, p2, p3 = padded[s], padded[s + 1], padded[s + 2], padded[s + 3]
        for i in range(per_segment):
            t = i / per_segment
            out.append(.5 * ((2 * p1) + (-p0 + p2) * t
                             + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                             + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return out


def hair_lock(name, keys, width, thickness, mat, samples=30, steps=16,
              taper=3.4, tip=.03, sharp=2.6, root=.14, flare=0.0):
    """Ciocca piatta e affusolata che aderisce alla calotta.

    ``keys`` sono tuple (azimut, elevazione, distanza) sull'ellissoide dei
    capelli, oppure vettori già pronti per ciocche fuori superficie (ahoge).
    ``flare`` allontana la punta dalla calotta, per ciocche che si sollevano.
    """
    control = [k if isinstance(k, Vector) else hair_point(*k) for k in keys]
    spine = catmull_rom(control, samples)
    width, thickness = width / 2, thickness / 2
    verts, faces = [], []
    for j, point in enumerate(spine):
        t = j / (len(spine) - 1)
        before = spine[max(0, j - 1)]
        after = spine[min(len(spine) - 1, j + 1)]
        tangent = (after - before)
        if tangent.length < 1e-6:
            tangent = Vector((0, 0, -1))
        tangent.normalize()
        normal = hair_normal(point)
        across = tangent.cross(normal)
        if across.length < 1e-5:
            across = tangent.cross(Vector((1, 0, 0)))
        across.normalize()
        normal = across.cross(tangent).normalized()
        # Radice stretta, corpo pieno, punta affilata: profilo da ciocca anime.
        profile = max(tip, (1 - t ** taper) ** .58) * (root + (1 - root) * min(1, t / .18))
        point = point + normal * (flare * t ** 2)
        for i in range(steps):
            a = 2 * math.pi * i / steps
            cos_a, sin_a = math.cos(a), math.sin(a)
            # Sezione a superellisse: fronte piatto, non tubo.
            cx = math.copysign(abs(cos_a) ** (2 / sharp), cos_a)
            cy = math.copysign(abs(sin_a) ** (2 / sharp), sin_a)
            offset = across * (width * profile * cx) + normal * (thickness * profile * cy)
            verts.append(tuple(point + offset))
    for j in range(len(spine) - 1):
        for i in range(steps):
            a = j * steps + i
            b = j * steps + (i + 1) % steps
            faces.append((a, a + steps, b + steps, b))
    faces.append(tuple(range(steps)))
    last = (len(spine) - 1) * steps
    faces.append(tuple(reversed([last + i for i in range(steps)])))
    return mesh(name, verts, faces, mat)


def smoothstep(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3 - 2 * value)


def hairline(az_deg):
    """Bordo dei capelli in elevazione: alto sul viso, basso su lati e nuca."""
    t = min(abs(az_deg), 180.0) / 180.0
    return 66.0 + 44.0 * (t ** .72)


def comb(az_deg, count, phase=0.0):
    """Scanalatura periodica con valli nette e creste morbide, in [-1, 1]."""
    a = math.radians(az_deg * count + phase)
    wave = math.sin(a)
    return math.copysign(abs(wave) ** .75, wave)


def hair_shell(name, mat, rings=26, cols=144):
    """Calotta unica con scanalature radiali e bordo anteriore a punte morbide.

    Una sola superficie (poi solidificata) evita sia le ciocche-tubo staccate
    sia l'effetto "a spicchi" di tante primitive affiancate.
    """
    verts = [tuple(HAIR_CENTER + Vector((0, 0, HAIR_RADIUS.z)))]
    for j in range(1, rings + 1):
        v = j / rings
        for i in range(cols):
            az = -180 + 360 * i / cols
            # Bordo: punte più lunghe al centro del viso e sui lati.
            base = hairline(az)
            front = max(0.0, 1 - abs(az) / 86.0)
            tips = 11.0 * (1 - comb(az, 6, 20) ** 2) ** 1.4 * (front ** .45)
            sides = 4.0 * (1 - comb(az, 3, 40) ** 2) * smoothstep((abs(az) - 70) / 40) * (1 - smoothstep((abs(az) - 120) / 40))
            # Anche la nuca chiude a punte, così il bordo non è un taglio netto.
            back = 6.5 * (1 - comb(az, 9, 60) ** 2) ** 1.3 * smoothstep((abs(az) - 110) / 50)
            el = (base + tips + sides + back) * v
            # Volume: le scanalature si aprono scendendo verso il bordo.
            k = 1.0 + .034 * comb(az, 13, 0) * (v ** 1.2) + .016 * comb(az, 26, 17) * (v ** 1.5)
            k += .012 * comb(az, 6, 20) * (v ** 2)
            k += .018 * (v ** 2.2)  # appena più volume verso le punte
            point = hair_point(az, el, k)
            verts.append(tuple(point))
    faces = []
    for i in range(cols):
        faces.append((0, 1 + i, 1 + (i + 1) % cols))
    for j in range(rings - 1):
        for i in range(cols):
            a = 1 + j * cols + i
            b = 1 + j * cols + (i + 1) % cols
            faces.append((a, a + cols, b + cols, b))
    obj = mesh(name, verts, faces, mat)
    solidify = obj.modifiers.new("Spessore", 'SOLIDIFY')
    solidify.thickness = .05
    solidify.offset = 1
    subdiv = obj.modifiers.new("Superficie morbida", 'SUBSURF')
    subdiv.levels = 1
    return obj


def build_head(m):
    sphere("Testa", (0, 0, 2.78), (.88, .70, .85), m["Skin"], 48, 32)
    for side in (-1, 1):
        label = 'S' if side < 0 else 'D'
        # Piccole orecchie e riflesso caldo.
        sphere(f"Orecchio_{label}", (side * .85, -.01, 2.69), (.12, .12, .20), m["Skin"])
        sphere(f"Orecchio_interno_{label}", (side * .892, -.095, 2.69), (.045, .025, .11), m["SkinShadow"])
        x = side * .32
        # Diversi strati chiusi costruiscono un occhio anime senza texture esterne.
        sphere(f"Occhio_contorno_{label}", (x, -.681, 2.78), (.234, .075, .281), m["EyeOutline"])
        sphere(f"Occhio_bianco_{label}", (x, -.744, 2.765), (.218, .031, .257), m["EyeWhite"])
        sphere(f"Iride_bordo_{label}", (x, -.768, 2.758), (.144, .027, .195), m["IrisDark"])
        sphere(f"Iride_{label}", (x, -.789, 2.745), (.12, .022, .167), m["Iris"])
        sphere(f"Iride_luce_{label}", (x, -.807, 2.68), (.09, .016, .065), m["IrisLight"])
        sphere(f"Pupilla_{label}", (x, -.813, 2.793), (.069, .02, .115), m["Pupil"])
        sphere(f"Riflesso_occhio_{label}", (x - .043, -.832, 2.854), (.043, .015, .048), m["Highlight"], 24, 16)
        sphere(f"Riflesso_piccolo_{label}", (x + .048, -.826, 2.71), (.022, .012, .024), m["Highlight"], 20, 12)
        # Le palpebre seguono la curvatura del viso.
        # Niente sopracciglia: con la frangia sopra gli occhi non si vedono
        # e da vicino sembravano spuntoni staccati dal viso.
        line(f"Palpebra_{label}", [(x - .22, -.69, 2.87), (x - .16, -.705, 2.99),
                                   (x, -.72, 3.04), (x + .16, -.705, 2.99),
                                   (x + .22, -.69, 2.87)], .022, m["EyeOutline"])
        sphere(f"Guancia_{label}", (side * .535, -.505, 2.48), (.078, .017, .032), m["Blush"], 24, 16)
    sphere("Naso", (0, -.696, 2.57), (.032, .022, .024), m["SkinShadow"], 24, 16)
    line("Sorriso", [(-.11, -.620, 2.385), (-.055, -.619, 2.365),
                     (0, -.616, 2.358), (.055, -.619, 2.365), (.11, -.620, 2.385)],
         .012, m["SkinShadow"])

    hair_shell("Capelli", m["Hair"])
    # Frangia: poche ciocche larghe che si sovrappongono alla calotta e
    # finiscono in punte nette. Insieme formano una massa, non tubi separati.
    for keys, width, thickness, color, flare, taper in (
        (((-30, 16, 1.02), (-36, 42, 1.05), (-43, 66, 1.075), (-47, 84, 1.10)),
         .30, .085, "Hair", .03, 2.9),
        (((-8, 12, 1.02), (-12, 40, 1.05), (-16, 65, 1.078), (-19, 88, 1.105)),
         .34, .095, "Hair", .034, 3.0),
        (((16, 14, 1.02), (22, 42, 1.05), (29, 67, 1.075), (34, 92, 1.10)),
         .32, .09, "HairLight", .032, 2.9),
        (((-54, 24, 1.02), (-64, 50, 1.045), (-74, 74, 1.07), (-80, 96, 1.095)),
         .24, .075, "HairMid", .028, 2.8),
        (((44, 22, 1.02), (54, 48, 1.045), (64, 72, 1.07), (70, 90, 1.09)),
         .26, .08, "Hair", .03, 2.8),
        (((-46, 40, 1.06), (-56, 62, 1.075), (-64, 84, 1.09), (-69, 100, 1.10)),
         .15, .055, "HairShadow", .02, 3.0),
        (((8, 44, 1.062), (12, 66, 1.078), (16, 90, 1.092)),
         .16, .058, "HairMid", .018, 3.0),
    ):
        hair_lock("Ciocca_frangia", keys, width, thickness, m[color],
                  samples=30, flare=flare, taper=taper, sharp=2.4)

    # Ciocche laterali davanti alle orecchie: cornice del viso.
    for side in (-1, 1):
        label = 'S' if side < 0 else 'D'
        hair_lock(f"Ciocca_laterale_{label}",
                  [(side * 84, 38, 1.025), (side * 92, 70, 1.045),
                   (side * 90, 100, 1.055), (side * 82, 126, 1.06)],
                  .155, .07, m["Hair"], samples=38, flare=.01, taper=2.4)
        hair_lock(f"Ciocca_guancia_{label}",
                  [(side * 104, 44, 1.015), (side * 110, 76, 1.035),
                   (side * 106, 104, 1.045), (side * 98, 124, 1.05)],
                  .125, .055, m["HairMid"], samples=36, flare=.008, taper=2.6)

    # Ahoge: ciuffo ribelle corto, firma tipica dei chibi.
    hair_lock("Ahoge",
              [Vector((0, .10, 3.62)), Vector((.01, .00, 3.84)),
               Vector((.06, -.10, 3.99)), Vector((.20, -.16, 4.02)),
               Vector((.30, -.13, 3.94))],
              .15, .07, m["HairLight"], samples=30, taper=1.9, sharp=2.3, tip=.14)

    # La stella dorata è appoggiata sopra una ciocca, non sospesa nel vuoto.
    clip = hair_point(52, 46, 1.115)
    normal = hair_normal(clip)
    pin = star("Fermaglio_stella", 0, 0, 0, .13, m["GoldLight"], inner=.3)
    pin.location = clip
    pin.rotation_euler = (-normal).to_track_quat('Y', 'Z').to_euler()
    gem = sphere("Fermaglio_gemma", tuple(clip + normal * .004), (.03, .022, .03), m["Iris"])
    gem.rotation_euler = (-normal).to_track_quat('Y', 'Z').to_euler()
    # Lo spillo attraversa le ciocche: la stella non resta sospesa e lo STL
    # rimane un volume unico.
    between("Fermaglio_spillo", tuple(clip - normal * .01),
            tuple(hair_point(52, 46, .99)), .018, m["Gold"], edge=0)


def cape_point(u, t):
    width = .50 + .52 * (t ** .72)
    x = u * width
    y = .34 + .18 * t + .035 * math.cos(u * math.pi * 3) * (t ** .7)
    z = 1.75 - 1.30 * t + .09 * (abs(u) ** 2) * t
    return (x, y, z)


def build_cape(m):
    cols, rows = 32, 18
    verts, faces = [], []
    for j in range(rows + 1):
        for i in range(cols + 1):
            verts.append(cape_point(-1 + 2 * i / cols, j / rows))
    for j in range(rows):
        for i in range(cols):
            a = j * (cols + 1) + i
            faces.append((a, a + 1, a + cols + 2, a + cols + 1))
    obj = mesh("Mantello", verts, faces, m["Cape"])
    solidify = obj.modifiers.new("Spessore stoffa", 'SOLIDIFY')
    solidify.thickness = .045
    subdiv = obj.modifiers.new("Pieghe morbide", 'SUBSURF')
    subdiv.levels = 1
    for side in (-1, 1):
        points = [cape_point(side * .985, t) for t in (.08, .3, .55, .8, 1)]
        line(f"Mantello_bordo_{side}", [(x, y - .025, z) for x, y, z in points], .022, m["Gold"])
    points = [cape_point(u, .99) for u in (-1, -.7, -.4, 0, .4, .7, 1)]
    line("Mantello_bordo_inferiore", [(x, y, z + .015) for x, y, z in points], .026, m["Gold"])
    line("Mantello_bordo_retro", [(x, y + .025, z + .015) for x, y, z in points], .026, m["Gold"])
    # Emblema sul retro, visibile ruotando il modello.
    # Il dorso è rivolto verso +Y, quindi la placca viene appoggiata a quella superficie.
    star("Stella_mantello", 0, .505, .79, .12, m["GoldLight"], inner=.35, thickness=.025)


def build_body(m):
    build_cape(m)
    # Stivali e gambe, con suola, punta e bordi metallici.
    for side in (-1, 1):
        label = 'S' if side < 0 else 'D'
        x = side * .285
        sphere(f"Gamba_{label}", (x, .01, .97), (.16, .16, .25), m["Skin"])
        sphere(f"Stivale_{label}", (x, .005, .62), (.19, .19, .32), m["Armor"])
        sphere(f"Punta_stivale_{label}", (x, -.115, .405), (.205, .28, .125), m["Ivory"])
        sphere(f"Suola_{label}", (x, -.11, .335), (.21, .28, .065), m["BaseShadow"])
        torus(f"Bordo_stivale_{label}", (x, .005, .87), .172, .021, m["Gold"], scale=(1, .98, 1))
        line(f"Decoro_stivale_{label}", [(x - .14, -.145, .66), (x, -.20, .59),
                                         (x + .14, -.145, .66)], .017, m["Gold"])
    # Gonnellino e corpo, entrambi chiusi e stondati.
    ring_body("Tunica_inferiore", [(.78, .43, .29, 0), (.88, .46, .30, 0),
                                   (1.15, .38, .27, 0), (1.28, .35, .25, 0)], m["Ivory"])
    ring_body("Corpetto", [(1.13, .35, .26, 0), (1.26, .39, .28, 0),
                            (1.62, .43, .29, 0), (1.78, .34, .25, 0)], m["Armor"])
    # Sopragonna sagomata con bordatura oro e interno chiaro.
    slab("Tabarro_bordo", [(-.22, 1.13), (-.27, .91), (0, .76), (.27, .91), (.22, 1.13)], -.315, .045, m["Gold"])
    slab("Tabarro", [(-.175, 1.09), (-.216, .93), (0, .82), (.216, .93), (.175, 1.09)], -.336, .035, m["Ivory"])
    for side in (-1, 1):
        coords = [(side * .26, 1.14), (side * .39, 1.10), (side * .47, .89),
                  (side * .33, .94)]
        if side < 0:
            coords.reverse()
        slab(f"Faldestra_{side}", coords, -.255, .14, m["Gold"])
        coords = [(side * .29, 1.10), (side * .37, 1.07), (side * .42, .94),
                  (side * .34, .97)]
        if side < 0:
            coords.reverse()
        slab(f"Faldestra_interno_{side}", coords, -.28, .04, m["CapeLight"])
    # Pettorale a più livelli, incorniciato e con gemma.
    slab("Pettorale_bordo", [(-.36, 1.72), (-.40, 1.54), (-.34, 1.36),
                              (0, 1.27), (.34, 1.36), (.40, 1.54), (.36, 1.72),
                              (.23, 1.79), (-.23, 1.79)], -.30, .09, m["Gold"], .025)
    slab("Pettorale", [(-.32, 1.69), (-.35, 1.54), (-.30, 1.40),
                        (0, 1.32), (.30, 1.40), (.35, 1.54), (.32, 1.69),
                        (.20, 1.74), (-.20, 1.74)], -.337, .055, m["Ivory"], .025)
    star("Gemma_pettorale_bordo", 0, -.355, 1.55, .085, m["Gold"], inner=.6, thickness=.04)
    sphere("Gemma_pettorale", (0, -.375, 1.55), (.038, .022, .055), m["Iris"])
    # Cintura ellittica e fibbia.
    cylinder("Cintura", (0, 0, 1.18), 1, .105, m["Leather"], scale=(.395, .29, 1), edge=.02)
    slab("Fibbia", [(-.105, 1.23), (-.105, 1.12), (.105, 1.12), (.105, 1.23)], -.315, .055, m["Gold"], .015)
    slab("Fibbia_interno", [(-.055, 1.208), (-.055, 1.145), (.055, 1.145), (.055, 1.208)], -.335, .025, m["Cape"], .008)
    # Collo e mantellina / sciarpa.
    cylinder("Collo", (0, 0, 1.87), .22, .22, m["Skin"], edge=.025)
    torus("Colletto_blu", (0, 0, 1.81), .30, .105, m["Cape"], scale=(1.25, .95, .78))
    sphere("Fermaglio_colletto", (-.22, -.278, 1.81), (.07, .035, .07), m["Gold"])
    sphere("Gemma_colletto", (-.22, -.315, 1.81), (.032, .02, .032), m["IrisLight"])
    for side in (-1, 1):
        label = 'S' if side < 0 else 'D'
        sphere(f"Spallaccio_{label}", (side * .52, -.01, 1.67), (.27, .24, .17), m["Armor"])
        line(f"Spallaccio_bordo_{label}", [(side * .31, -.155, 1.67), (side * .49, -.23, 1.58),
                                           (side * .68, -.14, 1.62)], .024, m["Gold"])
        between(f"Braccio_{label}", (side * .56, 0, 1.57), (side * .72, -.05, 1.32), .13, m["Skin"], .115)
        between(f"Manica_{label}", (side * .56, 0, 1.59), (side * .67, -.035, 1.41), .145, m["Ivory"], .14)
        between(f"Bracciale_{label}", (side * .71, -.05, 1.37), (side * .86, -.14, 1.14), .15, m["Armor"], .125)
        between(f"Polsino_oro_{label}", (side * .83, -.12, 1.20), (side * .87, -.145, 1.13), .144, m["Gold"], .13)
        sphere(f"Guanto_{label}", (side * .91, -.17, 1.10), (.14, .13, .145), m["Leather"])
        sphere(f"Pollice_{label}", (side * .81, -.255, 1.10), (.066, .06, .08), m["Leather"], 24, 16)


def blade_mesh(name, start, tip, width, mat1, mat2):
    a, b = Vector(start), Vector(tip)
    axis = b - a
    perpendicular = Vector((-axis.z, 0, axis.x)).normalized()
    # Coppie di spigoli e nervature formano quattro facce affilate.
    verts = []
    for t, w in ((0, width), (.75, width * .86)):
        p = a.lerp(b, t)
        verts += [tuple(p + perpendicular * w), (p.x, p.y - .045, p.z),
                  tuple(p - perpendicular * w), (p.x, p.y + .045, p.z)]
    verts.append(tuple(b))
    faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
             (4, 5, 8), (5, 6, 8), (6, 7, 8), (7, 4, 8), (3, 2, 1, 0)]
    obj = mesh(name, verts, faces, mat1, smooth=False)
    obj.data.materials.append(mat2)
    for i, poly in enumerate(obj.data.polygons):
        poly.material_index = 1 if i in (1, 5) else 0
    return axis.normalized(), perpendicular


def build_sword(m):
    guard = Vector((-1.08, -.18, 1.04))
    tip = Vector((-1.68, -.18, .36))
    axis, perpendicular = blade_mesh("Spada_lama", guard, tip, .112, m["Blade"], m["BladeLight"])
    handle_end = guard - axis * .35
    between("Spada_impugnatura", guard, handle_end, .055, m["Leather"], .048, edge=.008)
    sphere("Spada_pomo", handle_end, (.073, .073, .073), m["Gold"])
    # Traversino e gemma al centro della guardia.
    a, b = guard - perpendicular * .22, guard + perpendicular * .22
    between("Spada_guardia", a, b, .045, m["Gold"], edge=.01)
    sphere("Spada_guardia_sx", a, (.055, .055, .055), m["Gold"])
    sphere("Spada_guardia_dx", b, (.055, .055, .055), m["Gold"])
    sphere("Spada_gemma", (guard.x, guard.y - .056, guard.z), (.065, .027, .065), m["Iris"])
    # Un sottile solco azzurro evidenzia la sfaccettatura della lama.
    p1, p2 = guard.lerp(tip, .17), guard.lerp(tip, .78)
    line("Spada_riflesso", [(p1.x, p1.y - .048, p1.z), (p2.x, p2.y - .04, p2.z)], .012, m["BladeBlue"])


def build_base(m):
    # I tre gradini esagonali hanno veri bordi smussati.
    for name, z, radius, depth, mat, edge in [
        ("Base_inferiore", .075, 1.13, .15, "BaseShadow", .025),
        ("Base_fascia", .155, 1.15, .065, "Gold", .012),
        ("Base_superiore", .235, 1.12, .13, "Base", .025),
        ("Base_piano", .305, 1.055, .025, "BaseTop", .008),
    ]:
        obj = cylinder(name, (0, 0, z), radius, depth, m[mat], vertices=6, edge=edge)
        obj.rotation_euler[2] = math.radians(30)
    # Piccola placca centrale: il testo è geometria, non una texture.
    data = bpy.data.curves.new("Nome_Hoshino", 'FONT')
    data.body = "HOSHINO"
    data.align_x = 'CENTER'
    data.size = .12
    data.extrude = .004
    text = bpy.data.objects.new("Nome_Hoshino", data)
    bpy.context.collection.objects.link(text)
    # In rilievo sul piano, con una piccola intersezione per la stampa.
    text.location = (0, -.78, .315)
    data.materials.append(m["Gold"])


def convert_model_objects(collection):
    # Curve e testo diventano mesh: GLB, OBJ e STL condividono gli stessi dettagli.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in list(collection.objects):
        if obj.type in {'MESH', 'CURVE', 'FONT'}:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = next(obj for obj in collection.objects if obj.select_get())
    bpy.ops.object.convert(target='MESH')
    return [obj for obj in collection.objects if obj.type == 'MESH']


def set_render_scene(m):
    stage = bpy.data.collections.new("STUDIO (escluso dagli export)")
    bpy.context.scene.collection.children.link(stage)
    set_active_collection(stage)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.012))
    finish(bpy.context.object, "Studio_pavimento", m["Floor"], smooth=False)
    world = bpy.data.worlds.new("Studio_aurora") if not bpy.data.worlds else bpy.data.worlds[0]
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.72, .82, .9, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .45
    def light(name, location, energy, size, target):
        bpy.ops.object.light_add(type='AREA', location=location)
        obj = bpy.context.object
        obj.name = name
        obj.data.energy = energy
        obj.data.shape = 'DISK'
        obj.data.size = size
        obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()
    light("Studio_key", (-3.8, -5.5, 7), 520, 5.0, (0, 0, 2))
    light("Studio_fill", (4.2, -3.0, 4.5), 280, 4.0, (0, 0, 2))
    light("Studio_rim", (1.0, 4.0, 6), 700, 3.5, (0, 0, 2))
    bpy.ops.object.camera_add(location=(2.1, -9.5, 4.5))
    camera = bpy.context.object
    camera.name = "Camera_studio"
    camera.rotation_euler = (Vector((-.08, 0, 1.92)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 4.65
    bpy.context.scene.camera = camera
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    return camera


def select_model(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def model_height(objects):
    bpy.context.view_layer.update()
    zs = [(obj.matrix_world @ Vector(corner)).z for obj in objects for corner in obj.bound_box]
    return max(zs) - min(zs)


def export_model(objects):
    exports = ROOT / "exports"
    exports.mkdir(exist_ok=True)
    select_model(objects)
    glb = exports / "Hoshino_Chibi.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True)
    select_model(objects)
    bpy.ops.wm.obj_export(filepath=str(exports / "Hoshino_Chibi.obj"),
                          export_selected_objects=True, export_materials=True,
                          apply_modifiers=True, forward_axis='NEGATIVE_Y', up_axis='Z')
    select_model(objects)
    height = model_height(objects)
    bpy.ops.wm.stl_export(filepath=str(exports / "Hoshino_Chibi.stl"),
                          export_selected_objects=True, apply_modifiers=True,
                          global_scale=80.0 / height, forward_axis='Y', up_axis='Z')
    # OBJ e MTL devono essere distribuiti insieme per mantenere i materiali.
    with zipfile.ZipFile(exports / "Hoshino_Chibi_OBJ.zip", 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in ("Hoshino_Chibi.obj", "Hoshino_Chibi.mtl"):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (exports / name).read_bytes())
    for obj in objects:
        obj.data.calc_loop_triangles()
    triangles = sum(len(obj.data.loop_triangles) for obj in objects)
    materials = sorted({slot.material.name for obj in objects for slot in obj.material_slots if slot.material})
    info = {
        "name": "Hoshino - Chibi Guerriero dell'Aurora",
        "version": 3,
        "style": "Anime chibi, statuetta dell'aurora",
        "hair": "Calotta unica scanalata con ciocche sovrapposte, punte a zigzag e ahoge.",
        "meshes": len(objects),
        "triangles": triangles,
        "materials": materials,
        "height_blender_units": round(height, 4),
        "height_mm_print": 80,
        "rig": "Modello statico, non riggato.",
        "exports": {
            "blend": "exports/Hoshino_Chibi.blend",
            "glb": "exports/Hoshino_Chibi.glb",
            "obj": "exports/Hoshino_Chibi.obj",
            "mtl": "exports/Hoshino_Chibi.mtl",
            "obj_zip": "exports/Hoshino_Chibi_OBJ.zip",
            "stl": "exports/Hoshino_Chibi.stl"
        },
        "print_note": "Dopo l'export Blender, unire i volumi con scripts/prepare_stl.py e verificare supporti e spessori nello slicer."
    }
    (ROOT / "character_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Modello: {len(objects)} oggetti, {triangles} triangoli, altezza Blender {height:.3f}; STL scalato a 80 mm")


def render_model(quick=False):
    renders = ROOT / "renders"
    renders.mkdir(exist_ok=True)
    scene = bpy.context.scene
    if quick:
        scene.cycles.samples = 16
        scene.render.resolution_x = 700
        scene.render.resolution_y = 700
    scene.render.filepath = str(renders / "model_preview.png")
    bpy.ops.render.render(write_still=True)
    # Una seconda vista proviene dalla stessa scena e dagli stessi file 3D.
    camera = scene.camera
    camera.location = (2.4, 9.5, 4.2)
    camera.rotation_euler = (Vector((0, 0, 1.92)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(renders / "model_back.png")
    bpy.ops.render.render(write_still=True)
    camera.location = (2.1, -9.5, 4.5)
    camera.rotation_euler = (Vector((-.08, 0, 1.92)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(renders / "model_preview.png")


def main():
    parser = argparse.ArgumentParser(description="Crea Hoshino chibi in Blender.")
    parser.add_argument('--export', action='store_true', help='Rigenera GLB, OBJ/MTL e STL')
    parser.add_argument('--render', action='store_true', help='Genera due render reali del modello')
    parser.add_argument('--save-blend', action='store_true', help='Salva la scena modificabile in exports/')
    parser.add_argument('--quick', action='store_true', help='Render di prova più veloce')
    if '--' in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    elif Path(sys.argv[0]).name == 'create_character.py':
        # Esecuzione con il modulo bpy in Python, invece del binario Blender.
        args = parser.parse_args(sys.argv[1:])
    else:
        # Blender passa i propri argomenti in sys.argv; non sono opzioni dello script.
        args = parser.parse_args([])

    bpy.ops.wm.read_factory_settings(use_empty=True)
    model = bpy.data.collections.new("HOSHINO - modello")
    bpy.context.scene.collection.children.link(model)
    set_active_collection(model)
    mats = make_materials()
    build_base(mats)
    build_body(mats)
    build_head(mats)
    build_sword(mats)
    objects = convert_model_objects(model)
    set_render_scene(mats)
    if args.export:
        export_model(objects)
    if args.render:
        render_model(args.quick)
    if args.save_blend:
        (ROOT / 'exports').mkdir(exist_ok=True)
        # Percorso relativo al .blend, trasferibile su un'altra macchina.
        bpy.context.scene.render.filepath = '//../renders/model_preview.png'
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'exports' / 'Hoshino_Chibi.blend'), compress=True)
    print("Hoshino è pronto.")


if __name__ == '__main__':
    main()
