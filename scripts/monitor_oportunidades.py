"""Detect publicly indexed job listings; record review-only opportunities in Issues.
No Workana login, scraping, client outreach, paid API or automatic applications.
An RSS entry does not prove that the job is currently open or new.
"""
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from html import unescape
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

QUERIES = (
    "site:workana.com/es/job/ Shopify productos SEO",
    "site:workana.com/es/job/ tienda online contenido descripciones",
    "site:workana.com/es/job/ moda e-commerce marketing",
)
PATTERN = re.compile(r"shopify|tienda|e-?commerce|seo|producto|catálogo|moda", re.I)
HOSTS = {"www.workana.com", "workana.com"}
BASE = "https://api.github.com"


def fetch(url, token=None, payload=None):
    headers = {"User-Agent": "HarveyCommerceAI-ProspectMonitor/1.0", "Accept": "application/vnd.github+json" if token else "application/rss+xml"}
    if token:
        headers.update({"Authorization": "Bearer " + token, "X-GitHub-Api-Version": "2022-11-28"})
    data = json.dumps(payload).encode("utf-8") if payload else None
    if data:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers)
    with urlopen(req, timeout=18) as response:
        return response.read()


def collect():
    result = {}
    for q in QUERIES:
        feed = "https://www.bing.com/search?" + urlencode({"q": q, "format": "rss"})
        try:
            root = ET.fromstring(fetch(feed))
        except Exception as exc:
            print("RSS no disponible:", type(exc).__name__, file=sys.stderr)
            continue
        for item in root.findall("./channel/item"):
            link = unescape(item.findtext("link", "")).strip()
            parts = urlsplit(link)
            clean = parts.scheme + "://" + parts.netloc + parts.path.rstrip("/")
            title = re.sub(r"\s+", " ", unescape(item.findtext("title", ""))).strip()[:130]
            summary = re.sub(r"<[^>]+>", "", unescape(item.findtext("description", ""))).strip()[:280]
            if parts.scheme == "https" and parts.netloc.lower() in HOSTS and re.fullmatch(r"/(?:es/)?job/[a-zA-Z0-9_-]+", parts.path.rstrip("/")) and PATTERN.search(title + " " + summary):
                result[clean] = (title, summary)
    return result


def main():
    token, repo = os.environ.get("GITHUB_TOKEN", ""), os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repo:
        print("Este monitor requiere el token integrado de GitHub Actions", file=sys.stderr)
        return 2
    seen = set()
    open_count = 0
    try:
        for page in range(1, 4):
            url = BASE + "/repos/" + repo + "/issues?" + urlencode({"state":"all", "per_page":100, "page":page})
            issues = json.loads(fetch(url, token))
            for issue in issues:
                if "pull_request" in issue:
                    continue
                if issue.get("state") == "open" and issue.get("title", "").startswith("[lead:"):
                    open_count += 1
                match = re.search(r"\[lead:([0-9a-f]{12})\]", issue.get("title", ""))
                if match:
                    seen.add(match.group(1))
            if len(issues) < 100:
                break
    except Exception as exc:
        print("No se pudo deduplicar. Se cancela por seguridad:", exc, file=sys.stderr)
        return 1
    if open_count >= 20:
        print("Tope de seguridad: 20 oportunidades abiertas; no se crean más hasta revisar y cerrar algunas.")
        return 0
    created = 0
    for url, (title, summary) in collect().items():
        digest = hashlib.sha256(url.encode()).hexdigest()[:12]
        if digest in seen:
            continue
        body = (
            "## Oferta de trabajo indexada — revisión pendiente\n\n"
            f"**Enlace:** {url}\n\n"
            f"**Resumen indexado (no verificado):** {summary}\n\n"
            "Comprobar publicación, vigencia, alcance, presupuesto y encaje real con Harvey. "
            "Una coincidencia de RSS NO confirma disponibilidad actual.\n\n"
            "**Estado:** pendiente de revisión, no contactado, propuesta NO enviada. "
            "No se ejecutan campañas ni se envían mensajes.\n\n"
            "**Controles:** no tratar datos personales, no saltar reglas de Workana, "
            "no aceptar proyectos sin compatibilidad militar ni presupuesto confirmado.\n\n"
            "**Propuesta inicial para REVISAR (NO enviada):**\n\n"
            f"Hola, he visto vuestro anuncio \"{title}\". Tengo experiencia práctica en Shopify y trabajo con IA "
            "para preparar fichas de producto claras, títulos, metadatos SEO y contenidos comerciales. "
            "¿Podríais confirmar cuántos productos o entregables necesitáis, qué materiales podéis aportar "
            "y vuestro presupuesto? Puedo preparar un piloto editorial de cinco fichas, sujeto a ajustar "
            "el alcance. El trabajo técnico de desarrollo o publicación directa en vuestra tienda se "
            "acordaría aparte.\n\n"
            "*Borrador automático que requiere verificación de la oferta, edición y autorización previa.*"
        )
        try:
            fetch(BASE + "/repos/" + repo + "/issues", token, {"title":f"[lead:{digest}] {title[:88]}", "body":body})
            created += 1
        except Exception as exc:
            print("No se pudo crear oportunidad:", type(exc).__name__, file=sys.stderr)
        if created >= min(3, 20 - open_count):
            break
    print("Oportunidades nuevas para revisar:", created, "| Propuestas enviadas: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
