#!/usr/bin/env python3
"""Monitor anónimo de pagos de Harvey (solo enlace, importe y estado).
No lee datos personales ni genera facturas. Avisos en Issues públicos sin PII.
"""
import hashlib
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

STRIPE_API = "https://api.stripe.com/v1/checkout/sessions"
GITHUB_API = "https://api.github.com"
LINK_ID = "plink_1UWy5mBWFeltZyxvmrvvaW77"
PRICE_CENTS = 14900
CURRENCY = "eur"
MAX_PAGES = 20
MAX_NOTICES = 8
MARKER = re.compile(r"harvey-payment:([0-9a-f]{24})")

def fingerprint(session_id):
    if not isinstance(session_id, str) or not session_id.startswith("cs_live_"):
        raise ValueError("La sesión no es de entorno real")
    return hashlib.sha256(session_id.encode("utf8")).hexdigest()[:24]

def is_paid(s):
    return (isinstance(s, dict)
            and s.get("object") == "checkout.session"
            and s.get("livemode") is True and s.get("status") == "complete"
            and s.get("payment_status") == "paid" and s.get("mode") == "payment"
            and s.get("payment_link") == LINK_ID and s.get("currency") == CURRENCY
            and s.get("amount_total") == PRICE_CENTS
            and isinstance(s.get("id"), str) and s["id"].startswith("cs_live_"))

def api(url, key, method="GET", body=None, stripe=False):
    headers = {"User-Agent": "HarveyCommerceAI-PaymentMonitor/1.0",
               "Authorization": "Bearer " + key,
               "Accept": "application/json" if stripe else "application/vnd.github+json"}
    if not stripe:
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    data = None if body is None else json.dumps(body).encode("utf8")
    if data is not None:
        headers["Content-Type"] = "application/json"
    try:
        with urlopen(Request(url, data=data, headers=headers, method=method), timeout=20) as response:
            return json.loads(response.read(3_000_000))
    except HTTPError as exc:
        raise RuntimeError(("Stripe" if stripe else "GitHub") + " HTTP " + str(exc.code)) from None
    except URLError:
        raise RuntimeError("No se puede acceder a " + ("Stripe" if stripe else "GitHub")) from None

def sessions_paid(key):
    if not isinstance(key, str) or not key.startswith("rk_live_"):
        raise ValueError("Se requiere clave restringida de Stripe live, no clave general")
    paid = []
    cursor = None
    for _ in range(MAX_PAGES):
        params = {"payment_link": LINK_ID, "status": "complete", "limit": 100}
        if cursor:
            params["starting_after"] = cursor
        payload = api(STRIPE_API + "?" + urlencode(params), key, stripe=True)
        items = payload.get("data")
        if not isinstance(items, list):
            raise RuntimeError("Stripe no ha devuelto una lista de sesiones")
        paid.extend(x for x in items if is_paid(x))
        if not payload.get("has_more"):
            return paid
        if not items or not isinstance(items[-1].get("id"), str):
            raise RuntimeError("Error de paginación de Stripe")
        cursor = items[-1]["id"]
    raise RuntimeError("Demasiadas sesiones; revisión de paginación requerida")

def seen_markers(repo, token):
    found = set()
    for page in range(1, MAX_PAGES + 1):
        q = urlencode({"state": "all", "per_page": 100, "page": page})
        issues = api(GITHUB_API + "/repos/" + repo + "/issues?" + q, token)
        if not isinstance(issues, list):
            raise RuntimeError("GitHub no devolvió una lista")
        for issue in issues:
            if "pull_request" not in issue:
                found.update(MARKER.findall(str(issue.get("body") or "")))
        if len(issues) < 100:
            return found
    raise RuntimeError("Demasiados Issues para garantizar antduplicados")

def alert_body(marker):
    return (
      "## Harvey Commerce AI: pago completado detectado en Stripe\n\n"
      "El detector encontró una sesión de Checkout en modo real, pago único de 149 EUR, "
      "estado completo y pagado, del enlace de Harvey. "
      "No se muestran datos personales en este repositorio público.\n\n"
      "Identificador anónimo: harvey-payment:" + marker + "\n\n"
      "Revisar la operación en la cuenta Stripe Harvey Commerce AI, comprobar "
      "posibles reembolsos, emitir la factura legalmente correcta por canal privado "
      "y gestionar el encargo con el cliente. "
      "El aviso no equivale a ingreso neto ni entrega terminada.\n"
    )

def notify(sessions, markers, repo, token):
    count = 0
    for s in sessions:
        mark = fingerprint(s["id"])
        if mark in markers:
            continue
        data = {
            "title": "[Harvey] Pago verificado: revisar pedido en Stripe",
            "body": alert_body(mark),
            "assignees": [repo.split("/")[0]]
        }
        api(GITHUB_API + "/repos/" + repo + "/issues", token, "POST", data)
        markers.add(mark)
        count += 1
        if count >= MAX_NOTICES:
            break
    return count

def main(env=None):
    e = env if env is not None else os.environ
    key, repo, token = (e.get("STRIPE_RESTRICTED_KEY", ""),
                         e.get("GITHUB_REPOSITORY", ""),
                         e.get("GITHUB_TOKEN", ""))
    if not key:
        print("PENDIENTE: no se ha configurado STRIPE_RESTRICTED_KEY en Secrets de GitHub Actions.")
        return 3
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo) or not token:
        print("ERROR: GitHub no está correctamente configurado.", file=sys.stderr)
        return 2
    try:
        paid = sessions_paid(key)
        marked = seen_markers(repo, token)
        new = notify(paid, marked, repo, token)
        print("Sesiones pagadas verificadas:", len(paid), "| Avisos nuevos:", new,
              "| Ningún dato personal registrado")
        if new == MAX_NOTICES:
            print("Límite de avisos alcanzado: el resto se revisará en la siguiente ejecución.")
        return 0
    except (ValueError, RuntimeError) as exc:
        print("ERROR de monitorización:", str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
