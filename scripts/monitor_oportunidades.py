"""Monitor of PUBLIC project RSS feeds. Never logs into marketplaces or contacts anyone.
Results are review-only. A feed entry never confirms a job is still open.
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

BING_QUERIES = (
    "site:workana.com/es/job/ shopify",
    "site:workana.com/es/job/ ecommerce seo productos",
    "site:workana.com/es/job/ marketing contenidos",
)
# Excluir Freelancer: exige saldo mínimo para pujar, incompatible con 0 EUR.
# Se mantienen exclusivamente búsquedas públicas de Workana para revisión.
FEEDS = []
for query in BING_QUERIES:
    FEEDS.append(("Bing Workana", "https://www.bing.com/search?" + urlencode({"q":query,"format":"rss"})))

KEYWORDS = re.compile(
    r"shopify|e.?commerce|online store|online shop|product listing|product description|"
    r"copywriting|copywriter|content writ|seo|marketing content|"
    r"fichas de producto|descripciones|catálogo|catalogo|contenido comercial|"
    r"tienda online|redes sociales|woocommerce", re.I
)
SKIP = re.compile(
    r"full.?time|30\+ hours|senior developer|backend engineer|"
    r"wordpress (?:website|site)|website (?:development|build|design)|"
    r"(?:shopify|online) store (?:build|setup|development)|"
    r"web (?:developer|design)|label redesign|meta ads specialist|"
    r"medical content|native english writer|job posting guide|copywriting project posting guide|"
    r"google ads specialist|e.?commerce product label", re.I
)
STRONG = re.compile(
    r"product (?:listing|upload|entry|descriptions?|copy|content)|"
    r"shopify (?:seo|product|catalog|content)|"
    r"e.?commerce (?:seo|copy|content)|"
    r"seo|copywriter|copywriting|content writ|"
    r"social media (?:posts|copy|content)|"
    r"fichas de productos?|descripciones? de productos?|"
    r"cat[aá]logo|optimizaci[oó]n de productos?|"
    r"contenido para (?:redes|e.?commerce)|publicaciones para redes|"
    # Títulos de Workana en español (03/11: 30 ítems/ejecución y 0 aceptados).
    r"(?:carga|alta|subida) (?:recurrente )?de productos|"
    r"editor(?:es|a)? de contenidos?|redact(?:or|ora|ores|ar)\b|redacci[oó]n|"
    r"textos? (?:para|de) (?:tienda|productos?|e.?commerce)|contenidos? (?:web|seo)|"
    r"asistente (?:de |para )?shopify", re.I
)
# No aceptar trabajos que prohíben IA ni idiomas que no podamos revisar con fiabilidad.
INCOMPATIBLE = re.compile(
    r"no\s+(?:ai|chatgpt|artificial intelligence)\s+(?:tools?|generated|content|drafts?)?|"
    r"without\s+(?:ai|chatgpt)|human.?written only|"
    r"bahasa indonesia|indonesian language|native (?:uk|us|english)|"
    r"only\s+\$?15\b|urgent immediate (?:full.?time|hours)", re.I
)
CONTEXT = re.compile(
    r"shopify|woocommerce|online store|online shop|e.?commerce|"
    r"product|catalog|cat[aá]logo|fashion|moda|beauty|belleza|retail|storefront", re.I
)
DIRECT_TITLE = re.compile(
    r"shopify|product (?:listing|upload|entry|descriptions?|copy|content)|"
    r"e.?commerce|online store|fichas de producto|cat[aá]logo|descripciones de producto", re.I
)

def score(title, summary):
    raw = title+" "+summary
    if SKIP.search(title) or INCOMPATIBLE.search(raw):
        return -100
    if not STRONG.search(title) or not CONTEXT.search(raw):
        return -100
    value = (6 if DIRECT_TITLE.search(title) else 2)
    value += (4 if re.search(r"shopify|online store|e.?commerce|product", summary, re.I) else 0)
    value += (2 if re.search(r"fashion|moda|beauty|belleza|retail", raw, re.I) else 0)
    return value

BASE = "https://api.github.com"

def fetch(url, token=None, payload=None):
    headers = {
        "User-Agent": "HarveyCommerceAI-OpportunityMonitor/2.0",
        "Accept": "application/vnd.github+json" if token else "application/rss+xml, application/xml",
    }
    if token:
        headers.update({"Authorization": "Bearer " + token, "X-GitHub-Api-Version": "2022-11-28"})
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    with urlopen(Request(url, data=data, headers=headers), timeout=14) as resp:
        return resp.read()

def normalise_link(link):
    parts = urlsplit(link)
    host = parts.netloc.lower()
    if parts.scheme != "https":
        return None
    if host in {"www.workana.com", "workana.com"} and re.fullmatch(
        r"/(?:es/)?job/[\w-]+", parts.path.rstrip("/")
    ):
        return parts.scheme+"://"+host+parts.path.rstrip("/")
    return None

def source_coverage(items_seen, workana_links):
    """Only label the public RSS source healthy when it yields Workana URLs."""
    if items_seen == 0:
        return "SIN_DATOS_RSS"
    if workana_links == 0:
        return "SIN_ENLACES_WORKANA"
    return "ENLACES_WORKANA_PRESENTES"


def collect():
    result = {}
    total_seen = 0
    total_valid_links = 0
    for source, url in FEEDS:
        count = 0
        accepted = 0
        bad_link = 0
        low_score = 0
        try:
            root = ET.fromstring(fetch(url))
            items = root.findall(".//item")
            count = len(items)
            total_seen += count
            for item in items:
                raw_link = unescape(item.findtext("link", "") or item.findtext("guid", "")).strip()
                link = normalise_link(raw_link)
                if not link:
                    bad_link += 1
                    continue
                total_valid_links += 1
                title = re.sub(r"\s+", " ", unescape(item.findtext("title", ""))).strip()[:125]
                raw_description = unescape(item.findtext("description", ""))
                summary = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw_description)).strip()[:260]
                quality = score(title, summary)
                if not title or quality < 6:
                    low_score += 1
                    continue
                result[link] = (title, summary, source, quality)
                accepted += 1
            # Desglose para que un 0 sostenido no pase por funcionamiento correcto.
            print("Fuente:", source, "| ítems:", count, "| relevantes:", accepted,
                  "| descartes enlace:", bad_link, "| descartes filtro:", low_score)
        except Exception as exc:
            print("Fuente no accesible:", source, type(exc).__name__, str(exc)[:100], file=sys.stderr)
    coverage = source_coverage(total_seen, total_valid_links)
    message = (f"Salud de fuente: {coverage} | ítems RSS: {total_seen} "
               f"| enlaces válidos a Workana: {total_valid_links} "
               f"| anuncios aceptados: {len(result)}")
    print(message)
    if coverage != "ENLACES_WORKANA_PRESENTES":
        print("AVISO: el RSS externo no aporta anuncios verificables de Workana; "
              "un workflow verde no equivale a captación ni a proyectos disponibles. "
              "No se hará scraping directo de Workana.", file=sys.stderr)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        try:
            with open(summary_path, "a", encoding="utf-8") as summary:
                summary.write("### Harvey · cobertura de oportunidades Workana\n\n"
                              + message + "\n\n")
        except OSError as exc:
            print("Aviso: no se pudo escribir resumen GitHub:", type(exc).__name__, file=sys.stderr)
    return result

def main():
    token, repo = os.environ.get("GITHUB_TOKEN", ""), os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repo:
        print("Falta token integrado en GitHub Actions", file=sys.stderr)
        return 2
    known = set()
    open_count = 0
    try:
        for page in range(1, 4):
            url = BASE+"/repos/"+repo+"/issues?"+urlencode({"state":"all","per_page":100,"page":page})
            issues = json.loads(fetch(url, token))
            for issue in issues:
                if "pull_request" in issue:
                    continue
                if issue.get("state") == "open" and issue.get("title","").startswith("[lead:"):
                    open_count += 1
                digest = re.search(r"\[lead:([0-9a-f]{12})\]", issue.get("title",""))
                if digest:
                    known.add(digest.group(1))
                # También deduplicar las oportunidades creadas a mano en Issues.
                for raw_url in re.findall(r"https://(?:www\.)?(?:freelancer\.com|workana\.com)/[^\s\)<>]+", issue.get("body") or ""):
                    canonical = normalise_link(raw_url.rstrip(".,"))
                    if canonical:
                        known.add(hashlib.sha256(canonical.encode()).hexdigest()[:12])
            if len(issues) < 100:
                break
    except Exception as exc:
        print("Error comprobando duplicados; cancelamos el alta:", type(exc).__name__, file=sys.stderr)
        return 1
    if open_count >= 30:
        print("Límite de seguridad: 30 oportunidades sin revisar. Cerrar primero las descartadas.")
        return 0
    candidates = collect()
    created = 0
    errors = 0
    for link, (title, summary, source, quality) in sorted(candidates.items(), key=lambda x: x[1][3], reverse=True):
        digest = hashlib.sha256(link.encode()).hexdigest()[:12]
        if digest in known:
            continue
        body = (
            "## Oportunidad indexada — PENDIENTE DE REVISIÓN\n\n"
            f"**Fuente del índice:** {source}\n"
            f"**Puntuación automática de afinidad (no valida disponibilidad):** {quality}/12\n"
            "**Plataforma:** Workana requiere la aprobación del perfil antes de presentar propuestas. No gastar dinero.\n"
            f"**Anuncio original:** {link}\n"
            f"**Título en el RSS:** {title}\n\n"
            f"**Descripción pública (texto externo no verificado):** {summary}\n\n"
            "Este anuncio NO equivale a cliente, lead entrante ni oferta vigente. "
            "Verificar fecha, estado, presupuesto, trabajo exacto y condiciones antes de actuar.\n\n"
            "### Borrador genérico para adaptar y revisar, NO ENVIADO\n"
            "Hola, he visto vuestro proyecto y me gustaría confirmar el volumen real de trabajo y "
            "los materiales que tenéis disponibles. Tengo experiencia práctica con una tienda Shopify "
            "propia y puedo preparar un piloto acotado de contenido para cinco productos: títulos, "
            "descripciones SEO y preguntas frecuentes, siempre basados en datos verificables. "
            "¿Qué plataforma y entregables necesitáis? Los cambios técnicos, anuncios y vídeos "
            "terminados no se incluyen sin presupuesto y validación separados.\n\n"
            "**Control:** no contacto externo ni aplicación automática. "
            "No usar cuentas de compradores ni hacer mailing indiscriminado. "
            "No contratar hasta verificar compatibilidad militar y condiciones del servicio."
        )
        try:
            fetch(BASE+"/repos/"+repo+"/issues", token,
                  {"title":f"[lead:{digest}] {title[:85]}","body":body})
            created += 1
            known.add(digest)
        except Exception as exc:
            errors += 1
            print("No se pudo registrar una oportunidad:", type(exc).__name__, file=sys.stderr)
        if created >= min(5,30-open_count):
            break
    print("Resultados:",len(candidates),"| Oportunidades nuevas:",created,
          "| Fallos:",errors,"| Propuestas enviadas: 0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
