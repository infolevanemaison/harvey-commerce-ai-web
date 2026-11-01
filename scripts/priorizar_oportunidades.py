#!/usr/bin/env python3
"""Harvey: prioriza oportunidades ya guardadas como GitHub Issues.
No envía mensajes, no presenta candidaturas y no acepta contratos.
Ejecuta a diario en GitHub Actions y guarda un informe temporal.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

MAX_ISSUES = 100
AGENT = "HarveyCommerceAI-LeadTriage/1.0"
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
HIGH_FIT = re.compile(
    r"fichas de producto|descripciones de producto|product descriptions?|product copy|"
    r"e.?commerce content|contenido e.?commerce|shopify (?:product|seo|catalog|content)|"
    r"editor(?:es)? de contenido|edici[oó]n de textos", re.I
)
ADJACENT = re.compile(r"seo|copywrit|redacci[oó]n|redes sociales|product listing|"
                      r"contenido|fichas shopify|textos para tienda", re.I)
OUT_SCOPE = re.compile(r"theme specialist|theme developer|website developer|"
                       r"full.stack|web development|a/?b testing|app development|"
                       r"google ads|facebook ads|meta ads", re.I)
HIGH_EFFORT = re.compile(r"\b(?:50|100|200|500)\s+(?:productos|products?|fichas)\b", re.I)
PRIOR_PROPOSALS = re.compile(r"\b(?:\d{2,3})\s+propuestas\b", re.I)
URL = re.compile(r"https://(?:www\.)?(?:workana\.com|freelancer\.com)/[^\s)<>]+", re.I)

def assess(issue, now=None):
    """Only rank recorded public opportunities; status is unverified until checked."""
    title = str(issue.get("title") or "")
    body = str(issue.get("body") or "")
    if not title.startswith(("[lead:", "[revisar-comercial]")):
        return None
    raw = title + " " + body[:12000]
    # El titular prohíbe gastos adicionales: los anuncios Freelancer
    # históricos no son oportunidades utilizables y no deben priorizarse.
    if "freelancer.com" in raw.lower():
        return None
    score, why, warnings = 0, [], []
    if HIGH_FIT.search(title):
        score += 6
        why.append("Encaja directamente con redacción/optimización de fichas")
    elif HIGH_FIT.search(raw):
        score += 3
        why.append("El anuncio menciona contenido de catálogo")
    if ADJACENT.search(title):
        score += 2
    if re.search(r"shopify|e.?commerce|tienda online", title, re.I):
        score += 2
    if re.search(r"\b(?:agency|agencia|recurrente|recurring|mensual)\b", raw, re.I):
        score += 2
        why.append("Posible relación recurrente, no confirmada")
    if OUT_SCOPE.search(title) or OUT_SCOPE.search(body[:650]):
        score -= 7
        warnings.append("Posible desarrollo de tema/Ads fuera del piloto de redacción")
    if HIGH_EFFORT.search(title):
        score -= 3
        warnings.append("Gran volumen: el piloto de 5 fichas no cubre todo el encargo")
    if re.search(r"\bbudget is \$(?:[0-9]|[12][0-9])\b|"
                 r"\bbudget:?\s*\$(?:[0-9]|[12][0-9])\b", title, re.I):
        score -= 5
        warnings.append("Título indica presupuesto muy bajo: comprobar condiciones")
    if re.search(r"propuestas", body, re.I):
        warnings.append("Revisar la competencia y vigencia del anuncio")
    if "workana.com" in raw.lower():
        warnings.append("Contratación y pagos dentro de Workana")
    if "freelancer.com" in raw.lower():
        warnings.append("No pagar pujas, depósitos ni sacar la contratación de Freelancer")
    created = (issue.get("created_at") or "")
    # No consideramos la fecha de creación de nuestro Issue fecha del anuncio.
    if "Publicación:" in raw or "Publicado el" in raw:
        warnings.append("Confirmar antigüedad del anuncio en la plataforma")
    link = URL.search(body)
    external = link.group(0).rstrip(".,") if link else None
    return {
        "number": issue.get("number") or issue.get("issue_number"),
        "title": title[:150],
        "score": score,
        "why": why,
        "warnings": warnings,
        "source_url": external,
        "issue_url": issue.get("html_url") or issue.get("url"),
        "stage": "Borrador sin enviar; requiere validación en plataforma"
    }

def rank(issues):
    rows = []
    for issue in issues:
        if issue.get("pull_request") or issue.get("state", "open") != "open":
            continue
        item = assess(issue)
        if item:
            rows.append(item)
    return sorted(rows, key=lambda x: (-x["score"], str(x["title"])))[:25]

def fetch_issues(repo, token):
    if not REPO_PATTERN.fullmatch(repo):
        raise ValueError("Repositorio inválido")
    if not token:
        raise ValueError("Falta GITHUB_TOKEN")
    results = []
    for page in (1, 2):
        endpoint = (f"https://api.github.com/repos/{repo}/issues?"
                    f"state=open&per_page={MAX_ISSUES}&page={page}")
        request = Request(endpoint, headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": AGENT
        })
        with urlopen(request, timeout=20) as response:
            payload = json.load(response)
        if not isinstance(payload, list):
            raise ValueError("Respuesta inesperada de GitHub")
        results.extend(payload)
        if len(payload) < MAX_ISSUES:
            break
    return results

def markdown(rows):
    lines = [
        "# Harvey Commerce AI — bandeja de oportunidades priorizadas",
        "",
        "Generado: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "",
        "**Importante:** solicitudes públicas no son contactos entrantes, propuestas presentadas ni clientes.",
        "No se envían mensajes ni se realiza ningún gasto. Verificar disponibilidad, presupuesto y reglas",
        "de cada plataforma antes de solicitar un proyecto. Las puntuaciones son heurísticas, no ventas.",
        "",
        f"Oportunidades revisadas y ordenadas: {len(rows)}",
        ""
    ]
    for pos, row in enumerate(rows, 1):
        lines += [
            f"## {pos}. {row['title']}",
            f"- Puntuación editorial: {row['score']}",
            f"- GitHub: {row['issue_url']}",
            f"- Anuncio original: {row['source_url'] or 'No encontrado en Issue'}",
            f"- Estado: {row['stage']}"
        ]
        lines += ["- Encaje: " + x for x in row["why"]]
        lines += ["- Advertencia: " + x for x in row["warnings"]]
        lines.append("")
    if not rows:
        lines.append("No hay oportunidades abiertas clasificables.")
    lines.append("Próximo paso: preparar propuesta individual únicamente en el canal de la plataforma.")
    return "\n".join(lines) + "\n"

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", type=Path, help="Archivo JSON de Issues ficticios, sin red")
    ap.add_argument("--output", type=Path, default=Path("harvey-oportunidades.md"))
    args = ap.parse_args(argv)
    try:
        issues = (json.loads(args.fixture.read_text(encoding="utf8"))
                  if args.fixture else fetch_issues(os.environ.get("GITHUB_REPOSITORY", ""),
                                                    os.environ.get("GITHUB_TOKEN", "")))
        report = markdown(rank(issues))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf8")
        print(f"Informe: {args.output} | cero mensajes enviados")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("No se pudo clasificar:", str(exc)[:180], file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
