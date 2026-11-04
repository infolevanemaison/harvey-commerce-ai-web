import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "monitor", Path(__file__).resolve().parents[1] / "scripts" / "monitor_oportunidades.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class ScoreTests(unittest.TestCase):
    def test_documented_workana_titles_pass(self):
        # Los tres anuncios públicos de docs/plan-workana-pph-20261104.md.
        cases = [
            ("Optimización de redacciones generadas por IA para descripciones de productos y contenido web",
             "Revisar descripciones de productos de tienda online"),
            ("Asistente de Shopify para carga recurrente de productos de ropa",
             "10 fichas de producto por semana en Shopify, tallas y colores"),
            ("Búsqueda de editores de contenido para agencia creativa de e-commerce",
             "Textos para e-commerce, blogs y copys de producto"),
        ]
        for title, summary in cases:
            self.assertGreaterEqual(mod.score(title, summary), 6, title)

    def test_off_target_titles_rejected(self):
        for title, summary in [
            ("Desarrollo de app móvil en Flutter", "Necesitamos una app"),
            ("Shopify store setup and theme development", "Build a full Shopify store"),
            ("Redactor de artículos médicos", "medical content for clinics"),
        ]:
            self.assertLess(mod.score(title, summary), 6, title)

    def test_only_workana_job_links(self):
        self.assertEqual(mod.normalise_link("https://www.workana.com/es/job/abc-def/"),
                         "https://www.workana.com/es/job/abc-def")
        self.assertIsNone(mod.normalise_link("https://www.freelancer.com/projects/x"))
        self.assertIsNone(mod.normalise_link("http://www.workana.com/job/x"))


if __name__ == "__main__":
    unittest.main()
