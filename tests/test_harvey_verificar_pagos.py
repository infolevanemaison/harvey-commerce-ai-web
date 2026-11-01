"""Pruebas offline: ningún acceso a Stripe o GitHub real."""
import importlib.util
import unittest
from unittest.mock import patch
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "scripts" / "harvey_verificar_pagos.py"
spec = importlib.util.spec_from_file_location("harvey_pagos", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

SESSION = {
    "object": "checkout.session", "id": "cs_live_TESTFICTICIO123",
    "livemode": True, "status": "complete", "payment_status": "paid",
    "mode": "payment", "payment_link": m.LINK_ID,
    "currency": "eur", "amount_total": m.PRICE_CENTS
}

class PaidTests(unittest.TestCase):
    def test_paid_correct(self):
        self.assertTrue(m.is_paid(dict(SESSION)))

    def test_not_unpaid(self):
        self.assertFalse(m.is_paid(dict(SESSION, payment_status="unpaid")))

    def test_not_pending(self):
        self.assertFalse(m.is_paid(dict(SESSION, status="open")))

    def test_not_test_mode(self):
        self.assertFalse(m.is_paid(dict(SESSION, livemode=False)))

    def test_not_different_link(self):
        self.assertFalse(m.is_paid(dict(SESSION, payment_link="plink_other")))

    def test_not_different_price(self):
        self.assertFalse(m.is_paid(dict(SESSION, amount_total=14901)))

    def test_not_subscription(self):
        self.assertFalse(m.is_paid(dict(SESSION, mode="subscription")))

    def test_not_different_currency(self):
        self.assertFalse(m.is_paid(dict(SESSION, currency="usd")))

    def test_no_key_means_pending(self):
        with patch.object(m, "api", return_value=[]):
            self.assertEqual(m.main({"GITHUB_TOKEN": "x", "GITHUB_REPOSITORY": "org/repo"}), 3)

    def test_weak_key_fails(self):
        with self.assertRaises(ValueError):
            m.sessions_paid("sk_live_this_is_not_restricted")

    def test_hash_is_deterministic(self):
        self.assertEqual(m.fingerprint(SESSION["id"]), m.fingerprint(SESSION["id"]))
        self.assertEqual(len(m.fingerprint(SESSION["id"])), 24)

    def test_hash_rejects_test(self):
        with self.assertRaises(ValueError):
            m.fingerprint("cs_test_123")

    def test_no_duplicate_notifications(self):
        marker = m.fingerprint(SESSION["id"])
        with patch.object(m, "api") as api:
            self.assertEqual(m.notify([dict(SESSION)], {marker}, "org/repo", "gittoken"), 0)
            api.assert_not_called()

    def test_one_new_issue_without_private_information(self):
        with patch.object(m, "api", return_value={"number": 1}) as api:
            self.assertEqual(m.notify([dict(SESSION)], set(), "org/repo", "gittoken"), 1)
            body = api.call_args.args[3]["body"]
            self.assertNotIn(SESSION["id"], body)
            self.assertNotIn("gmail", body)
            self.assertIn("harvey-payment:", body)

    def test_sessions_filter_and_pagination(self):
        with patch.object(m, "api", side_effect=[
            {"data": [dict(SESSION, payment_status="unpaid"),
                      dict(SESSION, id="cs_live_one")], "has_more": True},
            {"data": [dict(SESSION, id="cs_live_two")], "has_more": False}
        ]) as api:
            matches = m.sessions_paid("rk_live_FAKE_ONLY_FOR_TEST")
        self.assertEqual(len(matches), 2)
        self.assertEqual(api.call_count, 2)

    def test_api_not_called_when_key_missing(self):
        with patch.object(m, "api") as api:
            self.assertEqual(m.main({}), 3)
            api.assert_not_called()

    def test_bad_repo(self):
        self.assertEqual(m.main({"GITHUB_TOKEN": "x", "GITHUB_REPOSITORY": "untrusted",
                                 "STRIPE_RESTRICTED_KEY": "rk_live_FAKE"}), 2)

if __name__ == "__main__":
    unittest.main()


class FakeGitHub:
    """Simula Stripe y GitHub en memoria: registra cada llamada, sin red."""
    def __init__(self, sessions=None, open_issues=None, stripe_error=None):
        self.sessions, self.issues, self.stripe_error = sessions or [], list(open_issues or []), stripe_error
        self.calls = []

    def __call__(self, url, key, method="GET", body=None, stripe=False):
        self.calls.append((method, url, body))
        if stripe:
            if self.stripe_error:
                raise RuntimeError(self.stripe_error)
            return {"data": self.sessions, "has_more": False}
        if method == "GET":
            return [i for i in self.issues if i.get("state", "open") == "open"]
        if method == "POST" and url.endswith("/issues"):
            self.issues.append({"number": len(self.issues) + 1, "body": body["body"], "title": body["title"]})
            return self.issues[-1]
        if method == "PATCH":
            n = int(url.rsplit("/", 1)[1])
            for i in self.issues:
                if i["number"] == n:
                    i["state"] = body["state"]
        return {}

    def created(self):
        return [c for c in self.calls if c[0] == "POST" and c[1].endswith("/issues")]


ENV = {"GITHUB_TOKEN": "x", "GITHUB_REPOSITORY": "org/repo"}


class AlertTests(unittest.TestCase):
    def setUp(self):
        m.STATS.update(paginas_stripe=0, sesiones_completas_devueltas=0)

    def test_missing_key_opens_one_alert_and_fails(self):
        fake = FakeGitHub()
        with patch.object(m, "api", fake):
            self.assertEqual(m.main(dict(ENV)), 3)
            self.assertEqual(m.main(dict(ENV)), 3)
        self.assertEqual(len(fake.created()), 1)           # una sola alerta, sin duplicados
        self.assertIn(m.ALERT_MARK, fake.issues[0]["body"])
        self.assertNotIn("rk_live", fake.issues[0]["body"])

    def test_stripe_error_opens_alert_and_fails(self):
        fake = FakeGitHub(stripe_error="Stripe HTTP 401")
        with patch.object(m, "api", fake):
            self.assertEqual(m.main(dict(ENV, STRIPE_RESTRICTED_KEY="rk_live_FICTICIA")), 2)
        self.assertEqual(len(fake.created()), 1)
        self.assertIn("401", fake.issues[0]["body"])

    def test_test_mode_key_is_rejected_with_alert(self):
        fake = FakeGitHub()
        with patch.object(m, "api", fake):
            self.assertEqual(m.main(dict(ENV, STRIPE_RESTRICTED_KEY="rk_test_FICTICIA")), 2)
        self.assertEqual(len(fake.created()), 1)

    def test_success_reports_real_query_and_closes_alert(self):
        alerta = {"number": 7, "state": "open", "title": m.ALERT_TITLE, "body": "<!-- " + m.ALERT_MARK + " -->"}
        fake = FakeGitHub(sessions=[dict(SESSION)], open_issues=[alerta])
        with patch.object(m, "api", fake), patch("builtins.print") as out:
            self.assertEqual(m.main(dict(ENV, STRIPE_RESTRICTED_KEY="rk_live_FICTICIA")), 0)
        texto = " ".join(str(a) for c in out.call_args_list for a in c.args)
        self.assertIn("Stripe consultado: 1 página(s), 1 sesión(es)", texto)
        self.assertEqual(alerta["state"], "closed")
        pagos = [c for c in fake.created() if "Pago verificado" in c[2]["title"]]
        self.assertEqual(len(pagos), 1)
        self.assertNotIn("cs_live_", pagos[0][2]["body"])   # nunca el ID real ni datos personales

    def test_zero_sales_is_still_a_real_query(self):
        fake = FakeGitHub(sessions=[])
        with patch.object(m, "api", fake), patch("builtins.print") as out:
            self.assertEqual(m.main(dict(ENV, STRIPE_RESTRICTED_KEY="rk_live_FICTICIA")), 0)
        texto = " ".join(str(a) for c in out.call_args_list for a in c.args)
        self.assertIn("1 página(s), 0 sesión(es)", texto)
        self.assertEqual(fake.created(), [])
