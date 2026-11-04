# Harvey Commerce AI — sistema operativo de agencia (01/11/2026)

## Objetivo
Maximizar trabajo autónomo manteniendo acceso, cobros, compromisos y gastos controlados. **Autorización general del titular NO sustituye las condiciones contractuales de cada tercero ni da acceso a sus cuentas.** No se deben inventar clientes ni ingresos.

## Estado real verificado
1. **Búsqueda de oportunidades:** GitHub Actions, cada 4 horas. Ejecución programada correcta 01/11/2026, comprobada en registros. Redacción de borradores para revisar; **no envía solicitudes**.
2. **Producción estructurada:** nuevo flujo [harvey-generar-piloto.yml](.github/workflows/harvey-generar-piloto.yml) probado en GitHub Actions. Genera un paquete de 5 fichas + SEO + FAQs + hooks y lista QA desde un brief JSON de DEMOSTRACIÓN.
3. **Redacción IA generativa:** no conectada en GitHub. El generador actual es determinista y no usa APIs ni consume créditos.
4. **Workana:** API de envío no disponible; términos prohíben acceder a sus recursos por medios automáticos no autorizados; no bots ni compartir datos/contactos o cobrar fuera de plataforma. Preparar propuestas y entregar usando sus herramientas cuando estén autorizadas.
5. **Captación directa:** candidaturas individualizadas enviadas desde Gmail a invitaciones públicas (2 confirmadas). No hay un buzón específico de la agencia ni automatización externa del correo de ese buzón.
6. **Cobros directos (actualizado 04/11/2026):** Stripe dispone de un monitor de solo lectura con clave restringida; el 04/11 a las 13:46 UTC se consultó correctamente 1 página: 0 sesiones completadas y 0 pagos reales de 149 €. El enlace de pago LIVE histórico está desactivado y no debe reactivarse mientras la contratación esté suspendida. El funcionamiento del monitor no equivale a poder cobrar nuevos encargos.
7. **Contratos, facturas, entregas:** sin contratos reales ni cobros confirmados. No hay pipeline seguro activo para clientes reales.
8. **Privacidad:** el repositorio actual es público; **NUNCA subir briefs reales con datos de clientes, datos personales, fotografías no autorizadas, credenciales, secretos o contratos**. El motor de producción público admite solo entradas `demo-`. Para clientes reales hará falta un repositorio privado y un sistema de acceso seguro separado de Levanemaison.

## Política de autonomía para tareas continuas
- **PERMITIDO automáticamente:** investigar ofertas públicas de modo respetuoso; deduplicar; puntuar pertinencia; crear borradores; construir muestras con datos públicos y verificados; validar la forma de los briefs; ejecutar test de contenidos; preparar índices, checklists y archivos; registrar métricas reales.
- **SOLO con aceptación previa de la persona correspondiente y canales compatibles:** responder solicitudes entrantes genuinas; solicitar brief; enviar presupuesto fijo si su alcance y precio están inequívocamente definidos; procesar trabajo tras confirmación del pago del proveedor. Evitar campañas indiscriminadas, usar baja/consentimiento donde corresponda.
- **REQUIERE DECISIÓN O CONFIRMACIÓN ESPECÍFICA:** asumir contratos que cambien alcance/condiciones, usar cuentas de clientes, publicar contenidos a sus nombres, divulgar información, hacer devoluciones o descuentos no acordados, modificar pagos, suscripciones, identidad fiscal, compras o gastos.
- **PROHIBIDO:** enviar postulaciones de Workana con robots; suplantar clientes; aceptar contraseñas en texto plano; retirar pagos de Workana; enviar datos de clientes a repositorios públicos; tratar un anuncio como un cliente confirmado; inventar ventas o reseñas.
- **Presupuesto por defecto:** 0 € de nuevos gastos/suscripciones. Stripe, si se conecta, cobraría comisiones por pagos realmente procesados.

## Producto piloto estándar — preparación
- Precio propuesto: **149 € por 5 fichas**, pendiente de cerrar condiciones fiscales y comisiones según canal; no modificar automáticamente el precio con clientes.
- Incluye borrador de títulos, descripción basada en atributos del cliente, SEO, preguntas frecuentes y 5 ideas de contenido.
- No incluye gestión de redes, desarrollo integral, anuncios, producción de video, integración de sistemas, acceso a Shopify, cambios en checkout ni resultados garantizados.
- Se entrega en documentos para aprobación; una ronda razonable de correcciones, definida antes de contratar.
- Si no llegan datos de tallas, materiales, disponibilidad, fotografías y políticas, marcar como pendientes; no rellenar por adivinación.

## Requisitos para automatización de extremo a extremo CON clientes directos
1. Correo propio de Harvey con autorización de acceso automatizado **separado de Levanemaison**.
2. Identidad/aviso legal, condiciones del servicio, privacidad y contrato estándar confirmados.
3. Medio de cobro conectado (p. ej. Stripe) y notificaciones de pago confiables. Nunca aceptar un pantallazo como comprobación de cobro.
4. Formulario o canal de briefing con consentimiento, acceso privado y medidas de seguridad.
5. Generación de contenido mediante un proveedor IA con autorización, presupuesto y política de datos; calidad revisada y ninguna afirmación no verificada.
6. Entrega segura, confirmación de recepción, gestión de cambios y facturación conforme a los datos fiscales aplicables.
7. Reintentos, registros y alertas de excepción, además de política de reembolso.

## Flujo deseado
`Lead público → filtro → borrador de propuesta → canal de postulación permitido → consulta/brief consentido → oferta aceptada y cobro confirmado → producción privada → QA → entrega privada → revisión → cierre/facturación.`

**Situación real:** Automatizados el primer filtro y el generador DEMO. No afirmar que cobros, contratos ni entregas reales ya sean autónomos.

## Seguimiento Workana y PeoplePerHour — 04/11/2026

Consultar `docs/plan-workana-pph-20261104.md`: incluye fuentes oficiales, tres oportunidades públicas verificadas como abiertas en noviembre (antiguas, con competencia), borradores NO enviados, perfil profesional sin resultados ficticios y restricción legal. El estado exacto de Workana NO se ha comprobado dentro de la cuenta: en Gmail no aparece aprobación, no asumirla. Freelancer sigue excluido. PeoplePerHour sin cuenta autorizada. No crear cronjobs ni enviar pujas, contratos, emails o pagos con esta actualización.
