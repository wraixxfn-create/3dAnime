#!/usr/bin/env python3
"""Unisci le mesh STL esportate da Blender in un unico volume per lo slicer.

Richiede: pip install -r requirements-model.txt
Eseguire dopo l'export Blender: python scripts/prepare_stl.py
Il file originale viene sostituito solo dopo tutti i controlli.
"""

import argparse
import io
import os
import stat
import tempfile
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]


def load_stl(data):
    return trimesh.load(io.BytesIO(data), file_type="stl", force="mesh", process=True)


def prepare(path):
    original = trimesh.load(path, force="mesh", process=True)
    if not isinstance(original, trimesh.Trimesh) or not len(original.faces):
        raise ValueError("Il file non contiene una mesh STL valida.")
    if abs(float(original.extents[2]) - 80.0) > 0.02:
        raise ValueError("L'altezza STL non è 80 mm: controlla scala e orientamento dell'export.")

    pieces = original.split(only_watertight=False)
    if any(not piece.is_volume for piece in pieces):
        raise ValueError("Almeno un componente non è un volume chiuso e orientato correttamente.")
    if len(pieces) == 1:
        combined = pieces[0]
    else:
        # manifold3d calcola una vera unione, non una semplice concatenazione di gusci.
        combined = trimesh.boolean.union(pieces, engine="manifold", check_volume=True)
    if combined is None or not combined.is_volume:
        raise ValueError("Unione non riuscita: il risultato non è un volume chiuso.")

    # STL usa float32: il passaggio a precisione singola può creare coppie di
    # triangoli a volume zero. Si eliminano soltanto quelle coppie degeneri,
    # mai componenti sostanziali; in tal caso si interrompe senza scrivere.
    rounded = load_stl(combined.export(file_type="stl"))
    components = rounded.split(only_watertight=False)
    solids = []
    for part in components:
        # Scarta solo triangoli collassati o coppie di facce coincidenti:
        # nessuno dei due casi può racchiudere un volume utile.
        if all(len(set(face)) < 3 for face in part.faces):
            continue
        if len(part.faces) == 2 and set(part.faces[0]) == set(part.faces[1]):
            continue
        solids.append(part)
    if len(solids) != 1 or not solids[0].is_volume:
        raise ValueError(f"L'unione contiene {len(solids)} componenti sostanziali; controlla le parti scollegate.")
    output = solids[0].export(file_type="stl")
    check = load_stl(output)
    if not check.is_volume or len(check.split(only_watertight=False)) != 1:
        raise ValueError("Il controllo finale STL non è riuscito; il file originale non è stato modificato.")
    if abs(float(check.extents[2]) - 80.0) > 0.02:
        raise ValueError("La scala è cambiata durante l'unione; il file originale non è stato modificato.")

    permissions = stat.S_IMODE(path.stat().st_mode)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".stl.tmp", delete=False) as file:
            temporary = Path(file.name)
            file.write(output)
        os.chmod(temporary, permissions)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    print(f"STL unito: {len(check.faces):,} triangoli, un volume chiuso, altezza {check.extents[2]:.2f} mm.")
    print("Verifica comunque spessori, dettagli e supporti nel tuo slicer.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=ROOT / "exports" / "Hoshino_Chibi.stl")
    args = parser.parse_args()
    try:
        prepare(args.path)
    except (OSError, ValueError, ImportError) as exc:
        parser.exit(1, f"Errore: {exc}\n")


if __name__ == "__main__":
    main()
