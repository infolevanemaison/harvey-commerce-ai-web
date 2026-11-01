import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("generar_piloto", ROOT / "scripts" / "generar_piloto.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestPiloto(unittest.TestCase):
    def test_demo_entrega(self):
        brief = mod.read_brief(ROOT / "briefs" / "demo-productos.json")
        with tempfile.TemporaryDirectory() as tmp:
            result = mod.generate(brief, pathlib.Path(tmp) / "entrega")
            self.assertEqual(result["products"], 5)
            self.assertFalse(result["auto_sent"])
            for n in result["files"]:
                txt = (pathlib.Path(tmp) / "entrega" / n).read_text(encoding="utf-8")
                self.assertIn("pendiente", txt.lower())
                self.assertIn("SEO title", txt)

    def test_secrets_rejected(self):
        brief = json.loads((ROOT / "briefs" / "demo-productos.json").read_text(encoding="utf-8"))
        brief["password"] = "test"
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "brief.json"
            path.write_text(json.dumps(brief), encoding="utf-8")
            with self.assertRaises(ValueError):
                mod.read_brief(path)

    def test_not_five_products_rejected(self):
        brief = json.loads((ROOT / "briefs" / "demo-productos.json").read_text(encoding="utf-8"))
        brief["products"] = brief["products"][:4]
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "brief.json"
            path.write_text(json.dumps(brief), encoding="utf-8")
            with self.assertRaises(ValueError):
                mod.read_brief(path)

if __name__ == "__main__":
    unittest.main()
