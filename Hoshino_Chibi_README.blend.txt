Hoshino_Chibi.blend — ISTRUZIONI

Questo file .blend viene GENERATO eseguendo lo script Blender.

Perché non è incluso come binario?
- Il progetto è pensato per essere leggero e riproducibile.
- Lo script `scripts/create_character.py` è la SORGENTE del modellino.
- Eseguendolo, ottieni un .blend completo con luci, camera e render.

COME GENERARE IL .blend:

1. Scarica e apri Blender (https://www.blender.org/download/)
2. Apri questo progetto (cartella 3dAnime)
3. In Blender: Text Editor → Open → scripts/create_character.py → Run Script ▶
4. Il modello appare in 3D Viewport
5. File → Save As → Hoshino_Chibi.blend (verrà salvato nella root del progetto)

In alternativa, importa il GLB già esportato:
  File → Import → glTF 2.0 → exports/Hoshino_Chibi.glb

GLI EXPORT SONO GIÀ PRONTI:
- exports/Hoshino_Chibi.glb (133 KB) — per web/giochi
- exports/Hoshino_Chibi.obj (375 KB) — per Blender/Maya
- exports/Hoshino_Chibi.stl (537 KB) — per stampa 3D

Per domande, leggi docs/BLENDER_GUIDA.md

— 3dAnime Team
