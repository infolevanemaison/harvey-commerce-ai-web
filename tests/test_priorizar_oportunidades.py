"""Pruebas sin red, con anuncios e incidencias ficticias."""
import importlib.util
import unittest
from pathlib import Path
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "priorizar_oportunidades.py"
spec = importlib.util.spec_from_file_location("harvey_leads", SCRIPT)
lead = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lead)
def item(number, title, body="", state="open"):
    return {"number": number, "title": title, "body": body, "state": state,
            "html_url": "https://github.com/acme/agency/issues/" + str(number)}

class LeadTests(unittest.TestCase):
    def test_good_shopify_copy_ranked(self):
        a = lead.assess(item(1, "[revisar-comercial] Descripciones de producto Shopify"))
        self.assertGreaterEqual(a["score"], 6)
    def test_theme_development_deprioritized(self):
        a = lead.assess(item(2, "[lead:abc] Shopify theme specialist development"))
        b = lead.assess(item(3, "[lead:def] Product descriptions Shopify"))
        self.assertLess(a["score"], b["score"])
    def test_budget_20_deprioritized(self):
        a = lead.assess(item(2, "[lead:abc] Shopify product descriptions The budget is $20."))
        b = lead.assess(item(3, "[lead:def] Shopify product descriptions"))
        self.assertLess(a["score"], b["score"])
    def test_disallows_normal_issues(self):
        self.assertIsNone(lead.assess(item(5, "Manual CI fixes")))
    def test_ignores_closed(self):
        self.assertEqual(lead.rank([item(1, "[lead:abc] Product descriptions", state="closed")]), [])
    def test_ignores_pull_requests(self):
        d = item(1, "[lead:abc] Product descriptions")
        d["pull_request"] = {"url": "https://github.com/acme/agency/pull/1"}
        self.assertEqual(lead.rank([d]), [])
    def test_limited_report(self):
        self.assertEqual(len(lead.rank([item(i, "[lead:x] Product descriptions") for i in range(32)])), 25)
    def test_url_is_extracted(self):
        d = item(1, "[lead:x] Descripciones de producto", "**Enlace:** https://www.workana.com/es/job/redaccion-comercial")
        self.assertEqual(lead.assess(d)["source_url"], "https://www.workana.com/es/job/redaccion-comercial")
    def test_no_recommendation_to_contact_automatically(self):
        s = lead.markdown(lead.rank([item(1, "[lead:x] Shopify Product descriptions")]))
        self.assertIn("No se envían mensajes", s)
    def test_rejects_invalid_repo(self):
        with self.assertRaises(ValueError):
            lead.fetch_issues("file:///etc/passwd", "token")

if __name__ == "__main__":
    unittest.main()
