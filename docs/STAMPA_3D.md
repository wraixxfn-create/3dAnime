# Stampa 3D — Hoshino Chibi

Guida completa per stampare il modellino su stampante a resina (SLA/MSLA) e a filamento (FDM).

## File

- `exports/Hoshino_Chibi.stl` — STL manifold, stampabile direttamente
- `exports/Hoshino_Chibi.obj` — con materiali, utile per preview a colori
- Scala nativa: altezza ~8 cm, base esagonale ~4 cm

## Controllo prima di stampare

Apri lo STL in:
- **Chitubox** / **Lychee Slicer** (resina)
- **PrusaSlicer** / **Cura** / **Bambu Studio** (FDM)
- Verifica: nessun buco, tutto manifold ✔ (già garantito)

## Resina (consigliata — massima qualità)

### Impostazioni
- Layer: 0.05 mm (0.03 mm per ultra-dettaglio volto)
- Esposizione: secondo la tua resina (es. 2.2s per Anycubic Standard)
- Bottom exposure: 30s × 4 layer
- Lift: 6 mm, velocità 60 mm/min
- Orientamento: **15° inclinato all'indietro**, base a contatto con piatto
- Supporti: leggeri (light) su:
  - Punta della spada
  - Ciocche laterali dei capelli
  - Bordo inferiore del mantello
  - Sotto la base (opzionale, rimovibili)

### Post-produzione
1. Stacca dal piatto con spatola
2. Lava in IPA 99% per 4 min (agita)
3. Rimuovi supporti con tronchesino (prima del curing è più facile)
4. Curing UV 2-3 min per lato (non sovraesporre, ingiallisce)
5. Carteggia leggermente la base con 800 grit

### Pittura (opzionale ma consigliata)

Palette ufficiale:
- **Capelli**: base `#5AC8F2`, ombra `#3873BF` (wash), highlight `#C0EBFF` (dry brush)
- **Pelle**: `#FCD2BA` + blush `#FF8CA5` sulle guance (aerografo leggero)
- **Armatura**: perla `#D9E0EB` + oro `#F2CC40` (bordo dorato con pennello fine 00)
- **Mantello**: `#2E48A6` + highlight `#4A6BFF`
- **Occhi**: bianco + iride `#338CF2` + pupilla nera + doppio punto bianco highlight
- **Spada**: lama argento `#D9E0EB` metallico, elsa oro, impugnatura marrone `#592E1A`

Primer: bianco o grigio chiaro. Acrilici Vallejo / Citadel / Tamiya.

## FDM (filamento)

### Impostazioni
- Layer: 0.12 mm (0.08 mm per dettagli volto)
- Nozzle: 0.4 mm (0.2 mm per ultra-dettaglio)
- Velocità: 45 mm/s (30 mm/s per top layer)
- Supporti: **Tree / Albero** — solo su spada e capelli
- Riempimento: 15% gyroid
- Materiale: PLA Silk bianco (ottimo per pittura) o PLA+ per resistenza
- Temperatura: 205°C (PLA), piatto 60°C

### Orientamento
- Come per resina: 10-15° all'indietro
- Base piatta sul piatto → non servono supporti sotto la base

### Post-produzione
1. Rimuovi supporti con pinza
2. Leviga con carta 400→800 grit dove serve
3. Primer filler per nascondere layer lines sul viso
4. Pittura come per resina

## Divisione in parti (consigliato per FDM)

Per evitare supporti interni, dividi in 3 parti con Meshmixer / PrusaSlicer:

1. **Corpo + testa + base** (stampa verticale)
2. **Capelli twin-tails** (stampa separata, incolla con cianoacrilato)
3. **Spada** (stampa orizzontale, incolla alla mano)

In Blender, puoi separare: seleziona mesh capelli → `P` → By Loose Parts.

## Scala

Il file è già in scala 1:1 = 8 cm.

- Per 10 cm: scala 125% (10 / 8 = 1.25)
- Per 6 cm (keychain): scala 75% — usa resina, FDM perderà dettagli occhi
- Per 15 cm (statua): scala 187.5% — aumenta spessore spada se stampi FDM

## Costi indicativi

- Resina: ~15 ml → ~0.50 € + IPA
- FDM PLA: ~18 g → ~0.40 €
- Tempo: resina 2.5h, FDM 4-5h a 0.12 mm

## Sicurezza

- Resina: guanti nitrile, occhiali, ambiente ventilato. Non toccare resina liquida a mani nude
- FDM: attenzione a piatto caldo (60°C)

## Foto del risultato

Il render in `renders/preview.png` è il target. Con pittura accurata puoi ottenere lo stesso effetto Nendoroid.

Buona stampa! 🖨️✨
