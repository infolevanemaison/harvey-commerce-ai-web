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

STATS = {"paginas_stripe": 0, "sesiones_completas_devueltas": 0}

def sessions_paid(key):
    if not isinstance(key, str) or not key.startswith("rk_live_"):
        raise ValueError("Se requiere clave restringida de Stripe live (rk_live_), no clave general ni de prueba")
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
        STATS["paginas_stripe"] += 1
        STATS["sesiones_completas_devueltas"] += len(items)
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

ALERT_MARK = "harvey-alerta:monitor-pagos"
ALERT_TITLE = "[Harvey][ALERTA] El monitor de pagos de Stripe no está operativo"

def open_alerts(repo, token):
    q = urlencode({"state": "open", "per_page": 100})
    issues = api(GITHUB_API + "/repos/" + repo + "/issues?" + q, token)
    return [i for i in issues if isinstance(i, dict) and "pull_request" not in i
            and ALERT_MARK in str(i.get("body") or "")]

def raise_alert(repo, token, reason):
    """Abre UNA alerta (si ya hay una abierta no crea otra). Sin datos personales ni claves."""
    if open_alerts(repo, token):
        return False
    body = ("## El monitor de pagos de Harvey Commerce AI no puede comprobar Stripe\n\n"
            "Motivo: " + reason + "\n\n"
            "Mientras esta alerta siga abierta, **no hay vigilancia automática de pagos**: "
            "un cobro real podría pasar sin aviso. Revisa Stripe a mano hasta resolverlo.\n\n"
            "Se cerrará sola en la primera ejecución que consulte Stripe correctamente.\n\n"
            "<!-- " + ALERT_MARK + " -->\n")
    api(GITHUB_API + "/repos/" + repo + "/issues", token, "POST",
        {"title": ALERT_TITLE, "body": body, "assignees": [repo.split("/")[0]]})
    return True

def resolve_alerts(repo, token, resumen):
    for issue in open_alerts(repo, token):
        n = str(issue.get("number"))
        api(GITHUB_API + "/repos/" + repo + "/issues/" + n + "/comments", token, "POST",
            {"body": "Resuelto: el monitor ha consultado Stripe correctamente. " + resumen})
        api(GITHUB_API + "/repos/" + repo + "/issues/" + n, token, "PATCH",
            {"state": "closed", "state_reason": "completed"})

def summary(text, e):
    path = e.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf8") as fh:
            fh.write(text + "\n")

def main(env=None):
    e = env if env is not None else os.environ
    key, repo, token = (e.get("STRIPE_RESTRICTED_KEY", ""),
                         e.get("GITHUB_REPOSITORY", ""),
                         e.get("GITHUB_TOKEN", ""))
    github_ok = bool(re.fullmatch(r"[\w.-]+/[\w.-]+", repo)) and bool(token)
    if not key:
        motivo = "falta el secreto STRIPE_RESTRICTED_KEY en GitHub Actions."
        print("ALERTA: " + motivo, file=sys.stderr)
        summary("### ALERTA: monitor de pagos NO operativo\n" + motivo, e)
        if github_ok:
            try:
                raise_alert(repo, token, motivo)
            except RuntimeError as exc:
                print("No se pudo abrir la alerta:", str(exc), file=sys.stderr)
        return 3
    if not github_ok:
        print("ERROR: GitHub no está correctamente configurado.", file=sys.stderr)
        return 2
    try:
        paid = sessions_paid(key)
        marked = seen_markers(repo, token)
        new = notify(paid, marked, repo, token)
        resumen = ("Stripe consultado: " + str(STATS["paginas_stripe"]) + " página(s), "
                   + str(STATS["sesiones_completas_devueltas"]) + " sesión(es) completadas del enlace, "
                   + str(len(paid)) + " pago(s) reales de 149 EUR, " + str(new) + " aviso(s) nuevos. "
                   "Ningún dato personal registrado.")
        print(resumen)
        summary("### Monitor de pagos operativo\n" + resumen, e)
        resolve_alerts(repo, token, resumen)
        if new == MAX_NOTICES:
            print("Límite de avisos alcanzado: el resto se revisará en la siguiente ejecución.")
        return 0
    except (ValueError, RuntimeError) as exc:
        motivo = "error al consultar Stripe o GitHub: " + str(exc)
        print("ERROR de monitorización:", motivo, file=sys.stderr)
        summary("### ALERTA: monitor de pagos NO operativo\n" + motivo, e)
        try:
            raise_alert(repo, token, motivo)
        except RuntimeError:
            pass
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
