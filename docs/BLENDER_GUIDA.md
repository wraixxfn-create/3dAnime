# Blender — Hoshino

## Aprire la scena già pronta

1. Installa **Blender 4.2 LTS o successivo**.
2. Apri `exports/Hoshino_Chibi.blend` con **File → Open**.
3. Nella collezione `HOSHINO - modello` trovi i singoli oggetti con nomi descrittivi e materiali modificabili. La collezione `STUDIO` contiene camera, luci e pavimento.
4. Usa **Material Preview** per vedere i colori oppure premi **F12** per renderizzare dalla camera salvata.
5. Salva una copia della scena prima di modificare il personaggio.

La scena è statica: non include rig, pesi o animazioni. La geometria contiene elementi sovrapposti, utile per modificare separatamente capelli, occhi, armatura e accessori; non è una singola mesh retopologizzata per l'animazione.

## Ricostruire la scena

In Blender apri uno spazio **Scripting**, quindi nel Text Editor scegli **Open** e apri `scripts/create_character.py`. Premi **Run Script**: lo script sostituisce la scena corrente e costruisce Hoshino e lo studio. Senza opzioni non salva e non esporta automaticamente; usa **File → Save As** se vuoi conservarla.

> Attenzione: lo script inizia con una scena vuota. Salva prima eventuali lavori aperti.

Per rigenerare anche i file inclusi nel progetto, dalla sua cartella:

```bash
blender --background --python scripts/create_character.py -- --export --render --save-blend
python3 -m pip install -r requirements-model.txt
python3 scripts/prepare_stl.py
```

`--export` riscrive GLB, OBJ/MTL, ZIP OBJ e STL; `--render` genera `renders/model_preview.png` e `renders/model_back.png`; `--save-blend` salva `exports/Hoshino_Chibi.blend`. Aggiungi `--quick` per render di prova. L'ultimo comando unisce i volumi dello STL: è necessario ripeterlo ogni volta che lo script Blender rigenera lo STL.

## Esportare a mano

- **GLB**: seleziona solo gli oggetti della collezione del modello e usa **File → Export → glTF 2.0**, abilitando *Selected Objects*. Mantiene i materiali PBR.
- **OBJ**: esporta gli stessi oggetti e conserva il file `.mtl` accanto all'`.obj`.
- **FBX**: seleziona solo il modello e usa **File → Export → FBX**, con *Selected Objects*. Per animarlo occorre prima creare un rig.
- **STL**: usa la pipeline sopra per ottenere lo STL scalato a 80 mm e unito. Un export manuale dalla scena Blender non è automaticamente un singolo volume e richiede una verifica della scala.

I render `model_preview.png` e `model_back.png` provengono dalla scena reale. `preview.png` e `turnaround.png` sono invece immagini di riferimento della versione precedente, non render degli export attuali.
