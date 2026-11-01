"""Generador determinista de borradores para cinco fichas Shopify.

Uso: python3 scripts/generar_piloto.py --brief briefs/demo-productos.json --output /tmp/harvey-entrega
No llama a APIs, no envía emails, no cobra ni publica productos.
Requiere datos de producto verificados; deja explícitos los vacíos.
No colocar datos privados de clientes en repositorios públicos.
"""
import argparse
import csv
import json
import re
from pathlib import Path


def clean(value, max_length=1000):
    if value is None:
        return ""
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value[:max_length]


def seo_trim(value, limit):
    value = clean(value)
    if len(value) <= limit:
        return value
    return value[:limit - 1].rsplit(" ", 1)[0].rstrip(".,;:") + "…"


def safe_filename(value):
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", clean(value).lower()).strip("-")
    return (value[:60] or "producto")


def read_brief(filename):
    raw = json.loads(Path(filename).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("El brief debe ser un objeto JSON.")
    if len(raw.get("products", [])) != 5:
        raise ValueError("El piloto requiere exactamente 5 productos.")
    forbidden = {"customer_email", "customer_name", "phone", "password", "token", "api_key", "private_key", "payment_data"}
    if any(k in raw for k in forbidden):
        raise ValueError("Los datos personales o secretos no están permitidos en el brief.")
    for index, item in enumerate(raw["products"], 1):
        if not isinstance(item, dict) or not clean(item.get("name")) or not clean(item.get("category")):
            raise ValueError(f"El producto {index} requiere nombre y categoría.")
        attributes = item.get("attributes")
        if not isinstance(attributes, dict) or not any(clean(v) for v in attributes.values()):
            raise ValueError(f"El producto {index} necesita atributos confirmados.")
    return raw


def product_page(product, brand):
    name = clean(product["name"], 120)
    category = clean(product["category"], 100)
    attrs = [(clean(k, 60), clean(v, 180)) for k, v in product["attributes"].items() if clean(v)]
    summary = clean(product.get("verified_summary"), 350)
    audience = clean(product.get("occasion"), 150)
    options = clean(product.get("available_variants"), 250)
    title = f"{name} | {category}"
    lines = [
        f"# {title}", "",
        "**Estado:** borrador editorial generado automáticamente; comprobar antes de publicar.", "",
        "## Descripción comercial", "",
        f"**{name}** es un producto de la categoría {category.lower()}.",
    ]
    if summary:
        lines += ["", summary]
    lines += ["", "### Características comprobadas", ""]
    lines.extend([f"- **{key}:** {value}" for key, value in attrs])
    if audience:
        lines += ["", f"**Uso u ocasión indicada por el catálogo:** {audience}."]
    if options:
        lines += ["", f"**Variantes indicadas:** {options}."]
    lines += [
        "", "### Antes de comprar", "",
        "Consulta la guía de tallas, fotografías, disponibilidad y condiciones vigentes antes de decidir.",
        "No se afirman descuentos, escasez, plazos de entrega ni garantías no documentadas.", "",
        "### Metadatos SEO sugeridos", "",
        f"- **SEO title:** {seo_trim(title + ' - ' + brand, 60)}",
        f"- **Meta description:** {seo_trim(name + ': ' + '; '.join(f'{k}: {v}' for k, v in attrs) + '. Consulta los detalles antes de elegir.', 155)}",
        "", "### FAQ preliminar (requiere respuestas verificadas)", "",
        f"**¿Qué características tiene {name}?** " + "; ".join(f"{k}: {v}" for k, v in attrs) + ".",
        "**¿Qué tallas o variantes están disponibles?** " + (options + "." if options else "Dato pendiente de confirmar con la tienda."),
        "**¿Cómo se cuida?** " + (clean(product.get("care")) + "." if clean(product.get("care")) else "Dato pendiente de confirmar con la tienda."),
        "**¿Cuáles son los envíos y devoluciones?** Revisar enlaces a las políticas vigentes de la tienda.", "",
        "### Idea de contenido orgánico", "",
        f"**Hook:** «¿Buscas {category.lower()}? Descubre los detalles de {name}».",
        "**Visual sugerido:** mostrar el producto real y acercamientos a las características comprobadas.",
        "**CTA:** «Consulta las características y variantes en la ficha».", "",
        "### Control de calidad obligatorio", "",
    ]
    if not options:
        lines.append("- [ ] Confirmar tallas y variantes.")
    if not clean(product.get("care")):
        lines.append("- [ ] Confirmar cuidados y mantenimiento.")
    if not clean(product.get("image_url")):
        lines.append("- [ ] Confirmar imágenes y licencias de uso.")
    lines += [
        "- [ ] Comprobar precio y disponibilidad actual en el sistema del cliente.",
        "- [ ] Comprobar políticas reales de envío y devolución.",
        "- [ ] Revisar todas las afirmaciones con la fuente del cliente.",
        "- [ ] Revisar estilo, legibilidad móvil y SEO antes de aprobar.",
        "- [ ] Aprobar la versión final ANTES de publicar o entregar al cliente.", ""
    ]
    return "\n".join(lines), seo_trim(title + " - " + brand, 60)


def generate(brief, output):
    if output.exists() and any(output.iterdir()):
        raise ValueError("Directorio de salida no vacío; no sobrescribir entregas existentes.")
    output.mkdir(parents=True, exist_ok=True)
    brand = clean(brief.get("brand", "Marca del cliente"), 80)
    rows = []
    names = []
    for i, item in enumerate(brief["products"], 1):
        filename = f"{i:02}-{safe_filename(item['name'])}.md"
        body, title = product_page(item, brand)
        (output / filename).write_text(body + "\n", encoding="utf-8")
        names.append(filename)
        rows.append({"producto": clean(item["name"]), "seo_title": title, "archivo": filename})
    with (output / "index.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=["producto", "seo_title", "archivo"])
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "brand": brand, "type": "borrador editorial", "products": len(names),
        "files": names, "auto_sent": False, "auto_published": False,
        "payment_verified": False, "human_review_required": True,
    }
    (output / "manifiesto.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = [
        "# Entrega demostrativa Harvey Commerce AI", "",
        "**IMPORTANTE:** Borradores automáticos, no fichas publicadas ni servicio vendido.",
        "Fuente de atributos: brief facilitado; no se han verificado independientemente.",
        "Antes de entregar a un cliente se exige revisar datos, permisos y alcance acordado.", "",
        "## Archivos generados",
    ] + [f"- [{n}]({n})" for n in names] + [
        "- index.csv (índice)", "- manifiesto.json (trazabilidad)", "",
        "## Lo que NO hace este generador", "",
        "- No envía propuestas a Workana ni accede a cuentas de clientes.",
        "- No cobra, firma contratos ni confirma pagos.",
        "- No emplea un modelo generativo remoto: es una primera automatización estructurada, sin coste de API.",
        "- No sustituye la edición profesional ni la aprobación de los datos.", ""
    ]
    (output / "LEEME.md").write_text("\n".join(summary), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = Path(args.brief)
    if not source.name.startswith("demo-"):
        raise ValueError("Esta ejecución pública admite únicamente archivos demo-. Datos reales requieren entorno PRIVADO.")
    result = generate(read_brief(source), Path(args.output))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
