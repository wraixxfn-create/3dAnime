# Guida Blender — Hoshino Chibi

Questa guida ti porta da zero al modellino completo in Blender.

## Requisiti

- Blender **3.6 LTS** o superiore (testato su 4.0, 4.2, 5.0)
- OS: Windows / macOS / Linux
- RAM: 4 GB minimo, 8 GB consigliati

## Installazione Blender

1. Scarica da https://www.blender.org/download/
2. Installa e avvia

## Generare Hoshino

### Metodo 1 — Script (consigliato, 1 click)

1. Apri Blender → File → New → General
2. In alto, cambia un pannello in **Text Editor** (icona documento)
3. `Text → Open` → seleziona `scripts/create_character.py`
4. Clicca ▶ **Run Script**
5. Il personaggio appare con luci e camera già configurate
6. Premi `Numpad 0` per vedere dalla camera, `F12` per render

### Metodo 2 — Import GLB

1. `File → Import → glTF 2.0 (.glb/.gltf)` → seleziona `exports/Hoshino_Chibi.glb`
2. Materiali PBR già presenti
3. Scala 1:1 corretta

## Struttura mesh generate

- **Head** (1.0, 0.95, 0.95) + Subsurf 2 + ears, nose, blush
- **Eyes** ×2: EyeWhite, Iris (emissiva), Pupil, 2 highlights, Brow torus
- **Hair**: Hair_Top, Bangs ×3, Side ×2 + Strand, Back, Twin ×2 + Ribbon, Highlight
- **Body**: Body cylinder, Belt torus, Buckle, ShoulderPad ×2 + Rim, Cape
- **Limbs**: Arm ×2, Hand ×2, Finger ×6, Leg ×2, Boot ×2, Sole ×2
- **Sword**: Blade box, Tip cone, Guard, Handle cylinder, Pommel sphere
- **Base**: Platform esagono (6 vertici), Rim, Rock ×3, Text3D "HOSHINO"
- **Env**: Camera 50mm, Sun Key/Fill/Rim, Ground shadow catcher, World bianco

## Materiali (Principled BSDF)

Tutti i materiali usano **Principled BSDF** con Base Color, Roughness, Metallic.
- Iris ha Emission Strength 0.3 per effetto anime brillante
- Blush ha blend_method = BLEND per trasparenza
- Armor Gold ha Metallic 0.7

## Modificatori usati

- **Subdivision Surface** (livelli 2) su Head, Body, Hair
- **Bevel** (width 0.02-0.08) su Bangs, BeltBuckle, Sole per ammorbidire spigoli
- **Mirror** potenziale per simmetria (se vuoi modellare da zero)

## Luci e Camera

- Camera: loc (2.2, -3.2, 1.3), rot (75°,0,35°), lens 50mm
- Key Sun: (3,-3,4) energy 6.0 warm
- Fill Sun: (-2,-2,3) energy 2.5 cool
- Rim Sun: (0,3,2) energy 3.0
- Ground Plane 10×10 con `is_shadow_catcher = True`

## Render

- Engine: `BLENDER_EEVEE_NEXT` (Blender 4.2+) o `BLENDER_EEVEE` o fallback `CYCLES`
- Risoluzione 2048×2048, film_transparent = True
- EEVEE: samples 64, soft_shadows True, bloom True (intensity 0.15)

Il script salva automaticamente:
- `Hoshino_Chibi.blend` nella root
- `exports/*.fbx, *.glb, *.obj, *.stl`
- `renders/preview.png` e `preview_closeup.png`

## Personalizzazione

### Cambiare colore capelli

Nel file script, cerca `create_materials()`:
```python
mats["Hair"] = new_material("Hair", (0.35, 0.78, 0.95, 1.0), roughness=0.5)
# Prova rosa: (0.95, 0.55, 0.75, 1.0)
# Prova biondo: (0.95, 0.85, 0.40, 1.0)
```

### Cambiare altezza

Modifica scala Head:
```python
head.scale = (1.0, 0.95, 0.95)  # prova (1.1, 1.0, 1.0) per testa più grande
```

### Aggiungere Rig per animazione

1. Genera il modello con lo script
2. Seleziona il Body → `Object → Add → Armature → Human (Meta-Rig)` con Rigify addon
3. Scala armature per contenere il chibi
4. Seleziona mesh → Shift-seleziona armature → `Ctrl+P → With Automatic Weights`
5. Entra in Pose Mode e anima

### Esportare per stampa 3D

- Seleziona tutto (`A`)
- `File → Export → Stl (.stl)` → spunta “Apply Modifiers”
- Scala: 0.08 = 8 cm (se vuoi 1 unità = 1 metro)

## Troubleshooting

- **SyntaxError: keyword argument repeated: scale** → già corretto in questa versione
- **ImportError: libXrender.so.1** → Blender va eseguito con GUI, non headless via pip bpy. Usa `scripts/build_trimesh.py` per headless
- **Mesh nere in render** → Normals: `Object → Shade Smooth` già applicato
- **Occhi spenti** → aumenta Emission Strength di Iris a 0.5

## Risorse

- [Blender Manual](https://docs.blender.org/manual/en/latest/)
- [EEVEE Render](https://docs.blender.org/manual/en/latest/render/eevee/index.html)
- [PBR Materials](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html)
