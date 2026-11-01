"""Unit tests using fictional catalogs only. No network."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "diagnostico_catalogo.py"
spec = importlib.util.spec_from_file_location("harvey_diagnostico_catalogo", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class CatalogTests(unittest.TestCase):
    def test_valid_store(self):
        self.assertEqual(audit.validate_store("https://shop.example.com/"), "shop.example.com")

    def test_domain_without_scheme(self):
        self.assertEqual(audit.validate_store("example.com"), "example.com")

    def test_refuses_localhost(self):
        with self.assertRaises(ValueError):
            audit.validate_store("https://localhost")

    def test_refuses_private_ip(self):
        with self.assertRaises(ValueError):
            audit.validate_store("https://127.0.0.1")

    def test_refuses_admin_path(self):
        with self.assertRaises(ValueError):
            audit.validate_store("https://shop.example.com/admin")

    def test_refuses_credentials(self):
        with self.assertRaises(ValueError):
            audit.validate_store("https://a:b@shop.example.com")

    def test_detects_empty_description(self):
        report = audit.inspect({"products": [{"title": "Vestido elegante floral", "body_html": "", "images": []}]})
        issues = [f["issue"] for p in report["findings"] for f in p["findings"]]
        self.assertIn("Falta descripción", issues)

    def test_detects_short_description(self):
        report = audit.inspect({"products": [{"title": "Vestido elegante floral", "body_html": "<p>Es bonito</p>"}]})
        self.assertIn("Descripción breve; faltan detalles verificables",
                      [f["issue"] for x in report["findings"] for f in x["findings"]])

    def test_detects_duplicate_title(self):
        report = audit.inspect({"products": [{"title": "Blazer estampado casual"}, {"title": "blazer estampado casual"}]})
        self.assertEqual(sum("repetido" in f["issue"] for x in report["findings"] for f in x["findings"]), 2)

    def test_detects_missing_size_guide(self):
        report = audit.inspect({"products": [{"title": "Conjunto midi elegante", "body_html": "<p>Colores rojo y azul.</p>",
                      "options": [{"name": "Talla"}], "images": [{"alt": "A"}, {"alt": "B"}]}]})
        self.assertTrue(any("tallaje" in f["issue"] for x in report["findings"] for f in x["findings"]))

    def test_size_guide_suppresses_warning(self):
        report = audit.inspect({"products": [{"title": "Conjunto midi elegante", "body_html": "Guía de tallas: S, M, L",
                      "options": [{"name": "Talla"}], "images": [{"alt": "A"}, {"alt": "B"}]}]})
        self.assertFalse(any("tallaje" in f["issue"] for x in report["findings"] for f in x["findings"]))

    def test_maximum_twenty(self):
        report = audit.inspect({"products": [{"title": f"Producto ejemplo {i}"} for i in range(42)]})
        self.assertEqual(report["sample_size"], 20)

    def test_report_discloses_limitations(self):
        self.assertIn("No equivale a una auditoría SEO", audit.markdown(audit.inspect({"products": []})))

if __name__ == "__main__":
    unittest.main()
