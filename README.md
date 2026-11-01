# Harvey Commerce AI — automatizaciones y referencia técnica

> **Estado actualizado (1 noviembre 2026):** La web comercial REAL está publicada en https://harvey-commerce-ai.higgsfield.app y alojada por Higgsfield, **no en este repositorio**. La cuenta Stripe de Harvey está conectada por separado, con un enlace real de pago único de 149 €: https://buy.stripe.com/aFa8wO55ycPd0BA8qtfMA01. La operación técnica de cobro funciona, pero **el aviso legal del sitio sigue pendiente de completar la identificación fiscal exigible**. No confundir capacidad de cobro con cumplimiento legal completo. No hay clientes ni pagos confirmados a fecha de verificación.
>
> Este repositorio incluye un **sitio HTML anterior, de referencia y sin publicar**; las instrucciones de no desplegar y de `noindex` que siguen en el README se refieren a ese prototipo, no a la web actual de Higgsfield.

## Herramienta nueva: diagnóstico público de catálogos Shopify
- Código: [scripts/diagnostico_catalogo.py](scripts/diagnostico_catalogo.py)
- Pruebas ficticias: [tests/test_diagnostico_catalogo.py](tests/test_diagnostico_catalogo.py)
- [Workflow en GitHub Actions](.github/workflows/harvey-diagnostico-catalogo.yml)
- El workflow prueba el diagnóstico en cada cambio de sus archivos y se puede iniciar manualmente desde Actions indicando el dominio público HTTPS de una tienda; si se deja vacío, solo ejecuta pruebas.
- Lee únicamente una muestra de hasta **20 productos** del catálogo JSON público de Shopify, comprobando permisos robots.txt y rechazando IP o dominios locales. Si la tienda bloquea el acceso, detiene el análisis.
- Detecta posibles descripciones cortas/vacías, títulos repetidos, pocas imágenes, ausencia de alt y guía de tallas. Son **señales editoriales**, no métricas de ventas ni una auditoría SEO completa.
- El informe se genera como artefacto temporal de GitHub Actions para revisión humana. **No accede a clientes, no envía propuestas, no cambia tiendas ni publica datos privados.** Las pruebas locales en entorno aislado comprobaron el tipo de análisis; el éxito de la nueva ejecución en la nube debe revisarse en Actions.

## Sitio anterior (archivo histórico, no desplegado por este repositorio)

Landing de presentación del servicio piloto de mejora de fichas Shopify. Proyecto **independiente** de Levanemaison.

## Estado
- Sitio preparado en GitHub; **no desplegar ni promocionar públicamente** antes de completar identificaciones y obligaciones legales.
- Contiene `noindex,nofollow`, aviso legal pendiente y llamadas a solicitar **información**, no a pagar.
- Sin formularios, scripts de analítica, cookies, checkout ni procesamiento de pagos.
- Email temporal de contacto: alias plus-addressing del buzón conectado de Levanemaison. Separar correo antes de lanzamiento comercial.
- Nombre y precios provisionales; la oferta piloto sugerida es 149 € por cinco fichas. Sin resultados garantizados.

## Checklist de lanzamiento
1. Confirmar autorización de compatibilidad para la actividad comercial, si corresponde, y obligaciones fiscales y de Seguridad Social.
2. Confirmar disponibilidad del nombre comercial.
3. Crear un buzón dedicado (sin mezclar clientes de Levanemaison), y reemplazar los enlaces mailto.
4. Completar `aviso-legal.html`: titular, NIF y dirección de contacto exigida, privacidad y condiciones del servicio, conforme a asesoramiento apropiado.
5. Revisar y confirmar alcance de la oferta, capacidad de entrega y proceso de facturación.
6. Eliminar `noindex,nofollow` solo cuando se cumplan los puntos anteriores y se quiera indexación.
7. **No usar GitHub Pages para el alojamiento comercial**: sus condiciones no permiten alojar allí como servicio gratuito un negocio orientado principalmente a transacciones comerciales. Usar GitHub solo como repositorio y controles.
8. Para alojamiento propuesto: **Cloudflare Pages Free**. Crear proyecto con conexión GitHub seleccionando únicamente `infolevanemaison/harvey-commerce-ai-web`, producción `main`, configuración de HTML estático (sin framework), comando de compilación `exit 0`, directorio de salida `.` (raíz). Consultar la interfaz actual antes de confirmar. Deploy automático tras cambios de `main`.
9. No difundir la URL ni activar cobros hasta completar identificaciones legales y obligaciones fiscales/Seguridad Social. Las páginas llevan `noindex` y cabeceras X-Robots-Tag provisionales.

## Documentación oficial alojamiento
- GitHub Pages límites: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Cloudflare Pages estático: https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- Git conectado a Cloudflare: https://developers.cloudflare.com/pages/get-started/git-integration/

## Automatización sin coste
`.github/workflows/verificar-sitio.yml` ejecuta comprobaciones automáticas del HTML y de enlaces internos en push y cada semana. **No envía mensajes comerciales** ni edita tiendas de clientes.

## Indicadores iniciales
Clientes reales: 0. Facturación cobrada: 0 €. Gasto nuevo previsto: 0 €. Ni estas cifras ni oportunidades investigadas deben confundirse con ventas.
