"""Controlli sugli export distribuiti (pip install -r requirements-model.txt)."""

import importlib.util
import json
import tempfile
import unittest
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"

spec = importlib.util.spec_from_file_location("prepare_stl", ROOT / "scripts" / "prepare_stl.py")
prepare_stl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare_stl)


class AssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.info = json.loads((ROOT / "character_info.json").read_text(encoding="utf-8"))
        cls.scene = trimesh.load(EXPORTS / "Hoshino_Chibi.glb", force="scene")
        cls.print_mesh = trimesh.load(EXPORTS / "Hoshino_Chibi.stl", force="mesh")

    def test_glb_matches_metadata_and_excludes_studio(self):
        self.assertEqual(sum(len(mesh.faces) for mesh in self.scene.geometry.values()), self.info["triangles"])
        self.assertGreaterEqual(len(self.scene.graph.nodes_geometry), self.info["meshes"])
        self.assertAlmostEqual(self.scene.extents[1], self.info["height_blender_units"], places=3)
        names = [name.lower() for name in self.scene.graph.nodes_geometry]
        self.assertFalse(any("studio" in name or "ground" in name for name in names))
        self.assertTrue(any("testa" in name for name in names))

    def test_stl_is_one_closed_volume_at_80mm(self):
        self.assertTrue(self.print_mesh.is_volume)
        self.assertEqual(len(self.print_mesh.split(only_watertight=False)), 1)
        self.assertAlmostEqual(self.print_mesh.extents[2], 80, places=2)
        scale = 80 / self.scene.extents[1]
        expected = [self.scene.extents[0] * scale, self.scene.extents[2] * scale, 80]
        np.testing.assert_allclose(self.print_mesh.extents, expected, atol=0.02)

    def test_obj_archive_contains_matching_material_file(self):
        with zipfile.ZipFile(EXPORTS / "Hoshino_Chibi_OBJ.zip") as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), {"Hoshino_Chibi.obj", "Hoshino_Chibi.mtl"})
            for name in archive.namelist():
                self.assertEqual(archive.read(name), (EXPORTS / name).read_bytes())
        obj = (EXPORTS / "Hoshino_Chibi.obj").read_text(encoding="utf-8")
        self.assertIn("mtllib Hoshino_Chibi.mtl", obj)
        self.assertIn("usemtl ", obj)

    def test_stl_postprocess_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "model.stl"
            target.write_bytes((EXPORTS / "Hoshino_Chibi.stl").read_bytes())
            prepare_stl.prepare(target)
            result = trimesh.load(target, force="mesh")
            self.assertTrue(result.is_volume)
            self.assertEqual(len(result.split(only_watertight=False)), 1)
            self.assertAlmostEqual(result.extents[2], 80, places=2)

    def test_disconnected_print_parts_do_not_overwrite_source(self):
        left = trimesh.creation.box(extents=[4, 4, 80])
        right = left.copy()
        left.apply_translation([-10, 0, 0])
        right.apply_translation([10, 0, 0])
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "disconnected.stl"
            trimesh.util.concatenate([left, right]).export(target)
            before = target.read_bytes()
            with self.assertRaisesRegex(ValueError, "componenti sostanziali"):
                prepare_stl.prepare(target)
            self.assertEqual(target.read_bytes(), before)

    def test_viewer_local_assets_exist(self):
        class LocalLinks(HTMLParser):
            def __init__(self):
                super().__init__()
                self.paths = []

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                for key in ("href", "src", "poster"):
                    value = attrs.get(key, "")
                    if value and not value.startswith(("#", "https://", "http://", "data:")):
                        self.paths.append(value)

        parser = LocalLinks()
        parser.feed((ROOT / "viewer.html").read_text(encoding="utf-8"))
        for path in parser.paths:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())


if __name__ == "__main__":
    unittest.main()
