#!/usr/bin/env python3
"""Harvey Commerce AI: local-first draft generator. Stdlib only.

Converts verified product facts into five structured, review-only Shopify copy drafts.
Never invents specs, makes financial commitments, publishes, emails or charges.
Never store actual client information in this public repository.
"""
import argparse
import csv
import json
import re
from pathlib import Path

MAX_PRODUCTS = 5
REQUIRED_FIELDS = ("id", "name", "type", "target_audience", "attributes", "benefits")
REQUIRED_BRIEF = ("client_alias", "language", "products")

def clean(value, max_len=400):
    if not isinstance(value, str):
        raise ValueError("El campo debe contener texto")
    value = re.sub(r"\s+", " ", value).strip()
    if not value or len(value) > max_len:
        raise ValueError("Campo vacío o longitud excesiva")
    if re.search(r"<script|<iframe|javascript:|[\r\n]", value, re.IGNORECASE):
        raise ValueError("Contenido de entrada no permitido")
    return value

def validate(brief):
    if not isinstance(brief, dict) or any(key not in brief for key in REQUIRED_BRIEF):
        raise ValueError("Faltan claves de briefing")
    alias = clean(brief["client_alias"], 80)
    if not re.fullmatch(r"[A-Za-z0-9_-]{2,60}", alias):
        raise ValueError("client_alias debe ser seudónimo sin datos personales")
    language = clean(brief["language"], 5)
    if language not in ("es", "fr", "en"):
        raise ValueError("Idioma no admitido")
    products = brief["products"]
    if not isinstance(products, list) or len(products) != MAX_PRODUCTS:
        raise ValueError("El piloto requiere exactamente 5 productos")
    seen = set()
    for item in products:
        if not isinstance(item, dict) or any(k not in item for k in REQUIRED_FIELDS):
            raise ValueError("Producto sin campos obligatorios")
        pid = clean(item["id"], 30)
        if not re.fullmatch(r"[A-Za-z0-9_-]+", pid) or pid in seen:
            raise ValueError("IDs incorrectos o duplicados")
        seen.add(pid)
        for key in ("name", "type", "target_audience"):
            clean(item[key], 150)
        for key in ("attributes", "benefits"):
            vals = item[key]
            if not isinstance(vals, list) or not 1 <= len(vals) <= 12:
                raise ValueError("attributes/benefits deben tener entre 1 y 12 elementos")
            for val in vals:
                clean(val, 220)
        for key in ("materials", "sizes", "care", "shipping", "returns"):
            if key in item and item[key] not in (None, ""):
                clean(item[key], 250)
    return alias, language, products

LANG = {
    "es": {"benefits":"Lo más importante", "features":"Características confirmadas", "faq":"Preguntas frecuentes",
           "more":"Consultar con la tienda", "cta":"Consulta disponibilidad y detalles antes de comprar",
           "unknown":"Pendiente de confirmar", "idea":"Idea de publicación orgánica",
           "size":"¿Qué tallas hay disponibles?", "material":"¿Cuál es el material?",
           "care":"¿Qué cuidados necesita?", "shipping":"¿Cómo funciona el envío?",
           "returns":"¿Cuál es la política de devolución?"},
    "fr": {"benefits":"Points essentiels","features":"Caractéristiques confirmées","faq":"Questions fréquentes",
           "more":"À confirmer auprès de la boutique","cta":"Consultez la disponibilité et les détails avant l'achat",
           "unknown":"À confirmer","idea":"Idée de contenu organique","size":"Quelles tailles sont disponibles ?",
           "material":"Quelle est la matière ?","care":"Comment entretenir cet article ?",
           "shipping":"Quelles sont les conditions de livraison ?","returns":"Quelle est la politique de retour ?"},
    "en": {"benefits":"Key points","features":"Confirmed features","faq":"Frequently asked questions",
           "more":"Ask the store to confirm","cta":"Check availability and details before ordering",
           "unknown":"Needs confirmation","idea":"Organic content idea","size":"Which sizes are available?",
           "material":"What material is it made of?","care":"How should it be cared for?",
           "shipping":"What are the shipping terms?","returns":"What is the returns policy?"}
}
FAQ_KEYS = (("size","sizes"),("material","materials"),("care","care"),
            ("shipping","shipping"),("returns","returns"))

def escape_csv(text):
    # Prevent CSV formula injection when product fields are opened in spreadsheets.
    if text and text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text

def make_product(item, l):
    name = clean(item["name"],150)
    kind = clean(item["type"],150)
    benefits = [clean(x,220) for x in item["benefits"]]
    attrs = [clean(x,220) for x in item["attributes"]]
    # Only verbatim, user-verified facts. Do not assert benefits absent from source.
    seo_title = (name + " | " + kind)[:62].rstrip(" |")
    meta = (name + ". " + "; ".join(attrs[:2]) + ". " + l["cta"])[:155].rstrip(" ,;")
    bullets = "\n".join("- " + b for b in benefits)
    attrbullets = "\n".join("- " + a for a in attrs)
    faq = "\n".join(
        "**" + l[question] + "** " +
        (clean(item[field],250) if item.get(field) else l["unknown"])
        for question, field in FAQ_KEYS
    )
    missing = [key for _,key in FAQ_KEYS if not item.get(key)]
    doc = "\n".join([
        "# " + name,
        "",
        "## " + l["benefits"],
        bullets,
        "",
        "## " + l["features"],
        attrbullets,
        "",
        "## " + l["faq"],
        faq,
        "",
        "**CTA:** " + l["cta"],
        "",
        "**SEO title (borrador):** " + seo_title,
        "",
        "**Meta description (borrador):** " + meta,
        "",
        "**" + l["idea"] + ":** " + name + " — " + benefits[0],
        "",
        "> BORRADOR: Revisar lenguaje, afirmaciones y datos antes de usar en una tienda."
    ]) + "\n"
    return doc, seo_title, meta, missing

def generate(brief, output):
    alias, language, products = validate(brief)
    l = LANG[language]
    output.mkdir(parents=True, exist_ok=True)
    rows, pending, ideas = [], [], []
    for item in products:
        doc, seo, meta, missing = make_product(item,l)
        pid = item["id"]
        (output / (pid + ".md")).write_text(doc, encoding="utf-8")
        rows.append({"id":pid, "title":escape_csv(item["name"]),
                     "seo_title":escape_csv(seo), "meta_description":escape_csv(meta),
                     "status":"DRAFT_REVIEW_REQUIRED"})
        ideas.append("- " + clean(item["name"],150) + " — " + clean(item["benefits"][0],220))
        if missing:
            pending.append("- " + pid + ": " + ", ".join(missing))
    with (output / "shopify_seo_drafts.csv").open("w",newline="",encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output/"ideas_contenido.md").write_text("# 5 ideas orgánicas (borradores)\n\n"+"\n".join(ideas)+"\n",encoding="utf-8")
    report = (
        "# Control de calidad — "+alias+"\n\n"
        "Resultado: 5 borradores generados; NO se han publicado ni enviado a nadie.\n\n"
        "## Datos sin verificar antes de entregar\n" +
        ("\n".join(pending) if pending else "- Campos básicos aportados; verificar fuentes y precisión igualmente.") +
        "\n\n## Comprobaciones manuales obligatorias\n"
        "- Validar todas las afirmaciones y atribuciones frente a fuentes del cliente.\n"
        "- Revisar exactitud de tallas, tejidos, envíos, devoluciones y stock.\n"
        "- Revisar SEO, legibilidad en móvil, traducciones, voz de marca y derechos.\n"
        "- Confirmar precio final, impuestos, contrato y pago **por separado**, fuera de este generador.\n"
        "- No adjuntar información personal, correos ni nombres reales a repositorios públicos.\n"
        "- No prometer ventas o posicionamiento ni afirmar que el cliente aprobó los borradores.\n"
    )
    (output/"QA_PENDIENTES.md").write_text(report,encoding="utf-8")
    return {"drafts":len(rows),"missing_product_fields":len(pending),"status":"review_required"}

def main():
    parser=argparse.ArgumentParser(description="Harvey — preparación editorial local, sin acciones comerciales")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    if args.output.resolve()==args.input.resolve() or args.output.resolve().is_relative_to(args.input.resolve()):
        parser.error("Directorio de salida incorrecto")
    try:
        brief=json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(generate(brief,args.output),ensure_ascii=False))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

if __name__=="__main__":
    main()
