# Harvey Commerce AI — fichas Shopify, claridad comercial y SEO

Ayudamos a tiendas Shopify a presentar sus productos de forma más clara: títulos, descripciones, metadatos SEO y contenido orgánico **basados en información verificable**.

**Recursos gratuitos, sin registro ni acceso a Shopify:**

- [Test interactivo para revisar una ficha Shopify](https://harvey-commerce-ai.higgsfield.app/test-ficha-producto-shopify.html): seis preguntas, puntuación orientativa y tres recomendaciones calculadas localmente en el navegador. No es una auditoría remota de tu web ni mide conversiones reales.
- [Guía práctica de fichas Shopify](https://harvey-commerce-ai.higgsfield.app/guia-fichas-producto-shopify.html): ejemplos, buenas prácticas y checklist.
- [Solicita una revisión inicial gratuita](https://harvey-commerce-ai.higgsfield.app/#diagnostico): hasta cinco enlaces públicos de producto y un breve resumen de hasta tres posibles mejoras, sin compromiso.

**Contratación de pago temporalmente suspendida (01/11/2026):** precio informativo previsto de **149 €** para cinco fichas Shopify, sujeto a habilitación profesional, fiscal y legal. **No se aceptan pedidos ni pagos**. El enlace de Stripe LIVE anterior está **desactivado** (`active=false`, comprobado en Stripe) y el botón de compra fue retirado de Higgsfield. Se mantienen únicamente los recursos gratuitos y las consultas informativas, sin compromiso de contratación ni garantía de ventas.

[Conoce Harvey Commerce AI](https://harvey-commerce-ai.higgsfield.app/)

---

## Información técnica para colaboradores

Este repositorio **no aloja la web comercial**: la web pública se administra y despliega de forma independiente en Higgsfield. Aquí se mantienen utilidades de diagnóstico y monitorización, pruebas, documentación y un prototipo histórico HTML. No introducir claves, datos personales ni material confidencial en este repositorio público. Tampoco hay automatización autorizada para enviar publicidad no solicitada.

## Herramienta nueva: diagnóstico público de catálogos Shopify
- Código: [scripts/diagnostico_catalogo.py](scripts/diagnostico_catalogo.py)
- Pruebas ficticias: [tests/test_diagnostico_catalogo.py](tests/test_diagnostico_catalogo.py)
- [Workflow en GitHub Actions](.github/workflows/harvey-diagnostico-catalogo.yml)
- El workflow prueba el diagnóstico en cada cambio de sus archivos y se puede iniciar manualmente desde Actions indicando el dominio público HTTPS de una tienda; si se deja vacío, solo ejecuta pruebas.
- Lee únicamente una muestra de hasta **20 productos** del catálogo JSON público de Shopify, comprobando permisos robots.txt y rechazando IP o dominios locales. Si la tienda bloquea el acceso, detiene el análisis.
- Detecta posibles descripciones cortas/vacías, títulos repetidos, pocas imágenes, ausencia de alt y guía de tallas. Son **señales editoriales**, no métricas de ventas ni una auditoría SEO completa.
- El informe se genera como artefacto temporal de GitHub Actions para revisión humana. **No accede a clientes, no envía propuestas, no cambia tiendas ni publica datos privados.** Las pruebas locales en entorno aislado comprobaron el tipo de análisis; el éxito de la nueva ejecución en la nube debe revisarse en Actions.


## Seguimiento automatizado de pagos de 149 € (clave restringida configurada)

- Código: [scripts/harvey_verificar_pagos.py](scripts/harvey_verificar_pagos.py)
- Pruebas ficticias: [tests/test_harvey_verificar_pagos.py](tests/test_harvey_verificar_pagos.py)
- Workflow programado: [Harvey - Revisar pagos reales de 149 EUR](.github/workflows/harvey-pagos-verificados.yml), cada 2 horas.
- [Guía iPhone de activación](docs/ACTIVAR_MONITOR_STRIPE_DESDE_IPHONE.md): requiere **solo** el secreto `STRIPE_RESTRICTED_KEY` en GitHub, con permiso Stripe Checkout Sessions de **solo lectura**.
- **Última consulta real verificada (01/11/2026 a las 17:32 UTC):** el monitor autenticó con Stripe, leyó una página y confirmó **0 pagos reales** del enlace. La alerta de autenticación anterior se cerró automáticamente. [Evidencia en GitHub Actions](https://github.com/infolevanemaison/harvey-commerce-ai-web/actions/runs/41331212512). Se ejecuta por programación, pero cada futura ejecución requiere comprobar sus registros antes de afirmar que está funcionando.
- La configuración guarda una clave restringida solo en GitHub Actions Secrets; **no** publicar ni pegar claves en código, chats o incidencias.
- No se crean cargos, reembolsos ni facturas desde GitHub. Una sesión de Checkout abierta no es una venta.
- Avisos anónimos mediante Issues; al ser público este repositorio, la existencia de un aviso de compra sería pública. No registrar PII.

## Sitio anterior (archivo histórico, no desplegado por este repositorio)

Landing anterior y no publicada, preservada para referencia técnica. **La web real es el sitio de Higgsfield enlazado al principio.**

## Estado
- Sitio preparado en GitHub; **no desplegar ni promocionar públicamente** antes de completar identificaciones y obligaciones legales.
- Contiene `noindex,nofollow`, aviso legal pendiente y llamadas a solicitar **información**, no a pagar.
- Sin formularios, scripts de analítica, cookies, checkout ni procesamiento de pagos.
- El canal provisional de consultas usa un alias de correo. Antes de escalar, es recomendable dedicar a la agencia un buzón independiente.
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
Clientes reales: 0. Facturación cobrada: 0 €. Gasto nuevo previsto: 0 €. Ni estas cifras ni oportunidades investigadas deben confundirse con ventas. La publicación de herramientas tampoco demuestra visitas o solicitudes.
