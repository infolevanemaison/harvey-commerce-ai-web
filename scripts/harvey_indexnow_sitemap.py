#!/usr/bin/env python3
"""Harvey Commerce AI: avisa por IndexNow de cambios reales del sitemap propio.

--snapshot verifica clave pública y genera estado determinista para caché de Actions.
--submit vuelve a verificar antes de enviar; aceptar no significa indexación.
No accede a Levanemaison, credenciales, tiendas de terceros ni PII.
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

HOST = "harvey-commerce-ai.higgsfield.app"
KEY = "093953e4e8e9a68331c25ed028b7323d"  # Pública por diseño en el propio sitio.
BASE = f"https://{HOST}"
KEY_URL = f"{BASE}/{KEY}.txt"
SITEMAP_URL = f"{BASE}/sitemap.xml"
SNAPSHOT = Path(".indexnow-snapshot.json")
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def read(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "Harvey-Commerce-AI-IndexNow/1.0"})
    with urlopen(req, timeout=25) as response:
        if response.status != 200:
            raise RuntimeError(f"Lectura HTTP {response.status}: {url}")
        return response.read(512_000)


def current_snapshot() -> dict:
    if read(KEY_URL).decode("utf-8").strip() != KEY:
        raise ValueError("La clave pública de IndexNow no coincide con la web")

    root = ET.fromstring(read(SITEMAP_URL))
    rows = []
    for node in root.findall("sm:url", NS):
        raw_url = (node.findtext("sm:loc", default="", namespaces=NS) or "").strip()
        lastmod = (node.findtext("sm:lastmod", default="", namespaces=NS) or "").strip()
        parsed = urlparse(raw_url)
        if not (parsed.scheme == "https" and parsed.netloc == HOST and
                parsed.username is None and parsed.password is None and
                parsed.fragment == "" and raw_url.startswith(BASE + "/")):
            raise ValueError(f"URL ajena o inválida en sitemap: {raw_url[:120]}")
        if not lastmod or len(lastmod) < 10:
            raise ValueError(f"URL sin lastmod: {raw_url}")
        rows.append({"url": raw_url, "lastmod": lastmod})
    if not rows or len(rows) > 100:
        raise ValueError("Sitemap sin URLs o fuera del límite conservador 1-100")
    rows.sort(key=lambda x: x["url"])
    if len(set(x["url"] for x in rows)) != len(rows):
        raise ValueError("Sitemap contiene URLs duplicadas")
    for row in rows:
        if not row["lastmod"].startswith("20"):
            raise ValueError("Fecha lastmod inválida")
    return {"host": HOST, "key": KEY, "keyLocation": KEY_URL, "pages": rows}


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) == 2 else ""
    if mode not in ("--snapshot", "--submit"):
        print("Uso: harvey_indexnow_sitemap.py --snapshot|--submit")
        return 2
    snapshot = current_snapshot()
    if mode == "--snapshot":
        SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False,
                                       sort_keys=True, separators=(",", ":")) + "\n",
                            encoding="utf-8")
        print(f"Preflight OK: clave pública y sitemap correctos, {len(snapshot['pages'])} URL")
        return 0

    # Esta acción se ejecuta solo ante un hash de URL+lastmod nuevo en la caché.
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_URL,
        "urlList": [row["url"] for row in snapshot["pages"]],
    }
    req = Request("https://api.indexnow.org/indexnow",
                  data=json.dumps(payload).encode("utf-8"),
                  method="POST", headers={"Content-Type": "application/json; charset=utf-8",
                                          "User-Agent": "Harvey-Commerce-AI-IndexNow/1.0"})
    try:
        with urlopen(req, timeout=25) as response:
            status = response.status
    except HTTPError as e:
        print(f"IndexNow rechazó la solicitud: HTTP {e.code}")
        return 1
    if status not in (200, 202):
        print(f"IndexNow respondió HTTP {status} inesperado")
        return 1
    print(f"IndexNow aceptó HTTP {status} para {len(payload['urlList'])} URLs; "
          "aceptación no implica indexación")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, ET.ParseError, URLError) as exc:
        print(f"Error seguro de IndexNow: {exc}")
        sys.exit(2)
