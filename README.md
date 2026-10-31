# Harvey Commerce AI — sitio provisional

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
