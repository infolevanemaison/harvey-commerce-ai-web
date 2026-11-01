#!/usr/bin/env python3
"""Diagnóstico heurístico de hasta 20 productos publicados en Shopify.
Solo catálogo JSON público, sin login, checkout, scraping masivo ni contacto.
Para pruebas usar --fixture (offline). El reporte NO mide ventas ni SEO real.
"""
import argparse
import html
import ipaddress
import json
import re
import socket
import sys
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

MAX_PRODUCTS = 20
MAX_BYTES = 2_000_000
AGENT = "HarveyCommerceAI-CatalogAudit/1.0 (manual; informational)"
GENERIC = re.compile(r"\b(?:alta calidad|gran calidad|ideal para cualquier ocasión|must.have|premium quality|best quality)\b", re.I)
SIZE_GUIDE = re.compile(r"gu[ií]a de tallas|tabla de tallas|tallaje|medidas|size chart|size guide|size & fit|guida taglie|guide des tailles", re.I)
LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.I)

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def clean(markup):
    parser = TextOnly()
    parser.feed(str(markup or "")[:100000])
    return re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()

def validate_store(url):
    if not isinstance(url, str) or len(url) > 250:
        raise ValueError("El dominio no es válido")
    parts = urlsplit(url if "://" in url else "https://" + url)
    if (parts.scheme != "https" or not parts.hostname or parts.username or parts.password
            or parts.port or parts.path not in ("", "/") or parts.query or parts.fragment):
        raise ValueError("Solo dominio público HTTPS, sin rutas ni credenciales")
    host = parts.hostname.lower().rstrip(".")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("No se permiten direcciones IP")
    labels = host.split(".")
    if len(labels) < 2 or any(not LABEL.fullmatch(x) for x in labels):
        raise ValueError("Nombre de dominio incorrecto")
    if labels[-1] in {"local", "localhost", "internal", "test", "invalid", "onion"}:
        raise ValueError("No es un dominio público")
    return host

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("No se siguen redirecciones")

def download(opener, url, limit):
    try:
        with opener.open(Request(url, headers={"User-Agent": AGENT, "Accept": "application/json, text/plain"}), timeout=12) as response:
            data = response.read(limit + 1)
            if len(data) > limit:
                raise ValueError("Respuesta excesivamente grande")
            return data
    except HTTPError as e:
        raise RuntimeError("Respuesta HTTP " + str(e.code)) from e
    except URLError as e:
        raise RuntimeError("No se puede consultar el catálogo público") from e

def fetch_shop(host):
    addresses = {info[4][0] for info in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
    if not addresses or any(not ipaddress.ip_address(x).is_global for x in addresses):
        raise ValueError("El dominio resuelve a una IP no pública")
    opener = build_opener(NoRedirect)
    robots = RobotFileParser()
    try:
        txt = download(opener, "https://" + host + "/robots.txt", 150000)
    except RuntimeError as e:
        if "HTTP 404" in str(e):
            txt = b""
        else:
            raise RuntimeError("No se pudo comprobar robots.txt; se detiene") from e
    robots.parse(txt.decode("utf-8", errors="replace").splitlines())
    url = "https://" + host + "/products.json?limit=20"
    if not robots.can_fetch(AGENT, url):
        raise RuntimeError("robots.txt no autoriza consultar products.json")
    payload = json.loads(download(opener, url, MAX_BYTES).decode("utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("products"), list):
        raise ValueError("No hay catálogo Shopify público JSON compatible")
    return payload

def inspect(payload, domain="ejemplo ficticio"):
    products = payload.get("products") if isinstance(payload, dict) else None
    if not isinstance(products, list):
        raise ValueError("El archivo debe contener una lista products")
    sample = products[:MAX_PRODUCTS]
    titles = Counter(clean(p.get("title")).casefold() for p in sample if isinstance(p, dict))
    findings = []
    for index, p in enumerate(sample, 1):
        if not isinstance(p, dict):
            continue
        title = clean(p.get("title"))
        body = clean(p.get("body_html"))
        images = p.get("images") if isinstance(p.get("images"), list) else []
        options = p.get("options") if isinstance(p.get("options"), list) else []
        variants = p.get("variants") if isinstance(p.get("variants"), list) else []
        flags = []
        if not title:
            flags.append(("alta", "Título vacío"))
        elif len(title) < 14:
            flags.append(("media", "Título muy breve"))
        if title and titles[title.casefold()] > 1:
            flags.append(("media", "Título repetido en la muestra"))
        if not body:
            flags.append(("alta", "Falta descripción"))
        elif len(body) < 160:
            flags.append(("media", "Descripción breve; faltan detalles verificables"))
        if body and GENERIC.search(body):
            flags.append(("baja", "Texto genérico, concretar beneficios verificables"))
        if len(images) <= 1:
            flags.append(("media", "Solo una imagen o ninguna"))
        elif any(isinstance(im, dict) and not str(im.get("alt") or "").strip() for im in images):
            flags.append(("baja", "Imagen sin texto alternativo en el catálogo"))
        has_size = any(re.search(r"talla|size|taille|taglia", str(x.get("name", "")), re.I)
                       for x in options if isinstance(x, dict))
        has_size = has_size or any(re.search(r"talla|size|taille|taglia", str(v.get(k, "")), re.I)
                                   for v in variants if isinstance(v, dict)
                                   for k in ("option1", "option2", "option3"))
        if has_size and not SIZE_GUIDE.search(body):
            flags.append(("media", "Hay tallas pero no se ve una guía de tallaje"))
        if flags:
            findings.append({"index": index, "product": title[:100] or "Producto sin título",
                             "findings": [{"severity": a, "issue": b} for a, b in flags]})
    return {"store": domain, "checked_at": datetime.now(timezone.utc).isoformat(),
            "sample_size": len(sample), "products_with_observations": len(findings),
            "findings": findings,
            "limitations": ["Solo muestra pública de máximo 20 productos.",
                            "No analiza datos de ventas, retención, metadatos SEO reales ni conversiones.",
                            "Señales editoriales orientativas; revisión humana necesaria."]}

def markdown(report):
    lines = ["# Diagnóstico preliminar de catálogo público Shopify", "",
             "- Tienda: " + report["store"],
             "- Productos revisados: " + str(report["sample_size"]),
             "- Productos con observaciones: " + str(report["products_with_observations"]),
             "- No equivale a una auditoría SEO ni a un análisis de ventas.", ""]
    for item in report["findings"]:
        lines.append("## " + item["product"])
        for f in item["findings"]:
            lines.append("- [" + f["severity"] + "] " + f["issue"])
        lines.append("")
    if not report["findings"]:
        lines.append("No se detectaron estas señales en la muestra. No demuestra optimización.")
    lines += ["", "## Limitaciones"] + ["- " + x for x in report["limitations"]]
    lines.append("No se envían mensajes, propuestas ni correos automáticos.")
    return "\n".join(lines) + "\n"

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", type=Path)
    mode.add_argument("--store")
    p.add_argument("--json", type=Path, default=Path("diagnostico.json"))
    p.add_argument("--markdown", type=Path, default=Path("diagnostico.md"))
    args = p.parse_args(argv)
    try:
        domain = validate_store(args.store) if args.store else "catálogo ficticio"
        payload = fetch_shop(domain) if args.store else json.loads(args.fixture.read_text(encoding="utf-8"))
        report = inspect(payload, domain)
        for path, content in ((args.json, json.dumps(report, indent=2, ensure_ascii=False)),
                              (args.markdown, markdown(report))):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content + "\n", encoding="utf-8")
        print("Diagnóstico:", report["sample_size"], "fichas;",
              report["products_with_observations"], "con observaciones.")
        return 0
    except (ValueError, RuntimeError, OSError) as e:
        print("No se pudo diagnosticar:", str(e)[:170], file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
