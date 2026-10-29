# Stampa 3D — Hoshino

`exports/Hoshino_Chibi.stl` contiene il personaggio e la base, senza pavimento di studio. Le coordinate STL sono da interpretare in **millimetri**: il modello è alto **80 mm**, con ingombro approssimativo di **56 × 39 mm** inclusa la spada. Lo STL non contiene colori; per i materiali usa il GLB o la scena Blender.

I componenti sono stati uniti con `scripts/prepare_stl.py`: il risultato è stato verificato come **un solo volume chiuso e orientato**. Questo controllo geometrico non sostituisce l'analisi dello slicer e non garantisce che ogni dettaglio sopravviva alla stampa.

## Prima di stampare

1. Apri lo STL nel tuo slicer (per esempio Lychee, Chitubox, PrusaSlicer, Cura o Bambu Studio) e verifica che sia importato in mm, alto 80 mm.
2. Ispeziona gli strati e i punti sottili: **spada, ciglia, punte delle ciocche e bordi dorati** potrebbero essere fragili o troppo piccoli per il tuo processo. Se necessario ingrandisci il modello o modifica e ispessisci i dettagli in Blender.
3. Aggiungi supporti agli sbalzi: in particolare lama, mani, capelli, bordi del mantello e sotto la base se l'orientamento scelto lo richiede. Controlla i supporti automaticamente proposti, non accettarli senza verifica.
4. Orienta la figura in base alla stampante e alla resina o al filamento utilizzati; effettua una stampa di prova prima di una tiratura.

Per dettagli così piccoli è generalmente preferibile la **resina**. Con FDM potrebbe essere necessario aumentare la scala o semplificare i dettagli. Le impostazioni di esposizione, layer, temperatura, lavaggio e polimerizzazione dipendono dal materiale: segui sempre le indicazioni del produttore e usa protezioni e ventilazione adeguate.

## Cambiare dimensione

Partendo dal file a 80 mm:

- 60 mm: scala al 75% (i dettagli diventano ancora più delicati).
- 100 mm: scala al 125%.
- 150 mm: scala al 187,5%.

Lo STL è un singolo volume: capelli e spada **non sono già separati**. Per stampare parti separate occorre modificarle o dividerle, aggiungendo eventualmente giunzioni, in Blender o in un software di modellazione adatto.

## Ricreare lo STL

```bash
blender --background --python scripts/create_character.py -- --export
python3 -m pip install -r requirements-model.txt
python3 scripts/prepare_stl.py
```

L'export Blender iniziale contiene volumi sovrapposti; lo script `prepare_stl.py` li unisce, verifica che il risultato sia un volume singolo e mantenga l'altezza di 80 mm, e sostituisce il file solo dopo i controlli. Se la geometria viene modificata e sono presenti parti scollegate, lo script si ferma senza sovrascrivere il file: correggi le intersezioni in Blender e riprova. È comunque necessario controllare lo spessore e i supporti nello slicer.
