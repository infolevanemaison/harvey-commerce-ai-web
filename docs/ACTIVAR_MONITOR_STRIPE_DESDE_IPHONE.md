# Harvey Commerce AI — Detector de pagos de 149 €

Actualizado: 1 de noviembre de 2026.

**Código publicado y controlable desde GitHub, pero NO opera sobre Stripe hasta completar un único secreto de lectura.** El workflow está preparado para programarse cada dos horas. No se debe contar una ejecución del workflow de pruebas como confirmación de monitorización real.

## Qué se ha confirmado sin esta automatización
- Cuenta Stripe real y separada: Harvey Commerce AI.
- Enlace de 149 € real y activo: https://buy.stripe.com/aFa8wO55ycPd0BA8qtfMA01
- ID utilizado en el código (no es secreto): plink_1UWy5mBWFeltZyxvmrvvaW77
- Consulta directa por la conexión Stripe: **una sesión abierta, sin pagar**, y cero pagos completados observados a la hora de esta revisión.
- Web actual desplegada: https://harvey-commerce-ai.higgsfield.app
- Pendiente: identificación legal completa del aviso legal y facturación adecuada para cada cliente; la automatización de pagos no resuelve esas obligaciones.

## Configuración desde el iPhone: solo UN secreto
1. Abre la **cuenta Stripe de Harvey Commerce AI** en https://dashboard.stripe.com/apikeys (comprueba que no estás en la cuenta de Levanemaison).
2. Crea una **clave restringida en modo real** llamada `harvey-github-pagos-lectura`. Deja todos los permisos en Ninguno salvo **Checkout Sessions → Lectura**. Si la organización requiere permisos adicionales para leer sesiones, concede solamente los mínimos necesarios, sin habilitar Escritura, reembolsos, cargos ni transferencias.
3. En GitHub, abre https://github.com/infolevanemaison/harvey-commerce-ai-web/settings/secrets/actions → **New repository secret**. Nombre exacto: `STRIPE_RESTRICTED_KEY`. Pega el valor completo de la clave restringida live (empieza por `rk_live_`) y guarda.
4. **No envíes esa clave por ChatGPT, Claude, correo ni como archivo**, ni la pegues en código o Issues.
5. Abre https://github.com/infolevanemaison/harvey-commerce-ai-web/actions/workflows/harvey-pagos-verificados.yml → **Run workflow**, selecciona main y ejecútalo. Sin acceso a esa página no se puede certificar el resultado del primer polling; comprueba las pestañas de ejecución y pruebas. Si aparece error HTTP 403, revisa permisos de **Lectura** de Checkout Sessions; si aparece HTTP 401, comprueba la clave restringida o sus restricciones.
6. GitHub Actions usa su propio `GITHUB_TOKEN` temporal para registrar avisos; no hace falta crear PAT ni el segundo secreto `STRIPE_PAYMENT_LINK_ID`, puesto que el identificador del enlace está fijado en el script.

## Funcionamiento previsto
- Workflow: [Harvey - Revisar pagos reales de 149 EUR](https://github.com/infolevanemaison/harvey-commerce-ai-web/actions/workflows/harvey-pagos-verificados.yml)
- Frecuencia programada: minuto 41 de cada 2 horas UTC. GitHub puede retrasar u omitir disparos programados; no hay garantía estricta de ejecución puntual.
- Valida únicamente Checkout Sessions **livemode, complete, paid, payment link específico, EUR, 14900 céntimos, mode=payment**. No marca como venta una sesión abierta o pendiente.
- Por pago validado, crea una incidencia en el repositorio público sin nombre, email, dirección, identificador de pago completo o información fiscal del comprador; solo un hash sin reversibilidad práctica para impedir avisos duplicados. Se asigna al propietario del repositorio, pero la entrega de notificaciones dependerá de sus ajustes de GitHub.
- **Aviso**: los Issues son públicos; por tanto terceros podrían inferir que existen compras. Si esto no es aceptable, dejar el secreto sin configurar y trasladar en el futuro las alertas a un backend privado autenticado.
- No emite facturas, no intenta reembolsos y no inicia entregas a partir de un pago de prueba.
- El registro de pago es un **indicador de transacción**, no de beneficio neto: revisar impuestos, comisiones y reembolsos en Stripe.
- **Sin el secreto, con una clave inválida (401/403) o si Stripe no responde, la ejecución termina en ROJO** y abre **una sola** alerta en Issues: «[Harvey][ALERTA] El monitor de pagos de Stripe no está operativo». No se abren alertas duplicadas, y la alerta se cierra sola en la primera ejecución que consulta Stripe correctamente.
- **Prueba de que ha consultado Stripe de verdad:** el registro y el resumen de la ejecución muestran «Stripe consultado: N página(s), M sesión(es) completadas del enlace, P pago(s) reales…». Un verde sin esa línea no demuestra vigilancia.

## Seguridad y mantenimiento
- El script rechaza claves generales `sk_live_`, utiliza `rk_live_` restringida.
- Nunca registrar ni copiar la clave a archivos, logs ni GitHub Issues.
- En caso de filtración, revocar la clave en Stripe, generar otra e introducirla en el mismo secreto.
- Desactivación: deshabilitar el workflow o quitar el secreto `STRIPE_RESTRICTED_KEY` de GitHub Actions. Esto NO afecta el enlace de pago ni la cuenta Stripe.
- La escritura en el repositorio está comprobada con el conector de GitHub de ChatGPT; que Claude no tenga instalación o permisos es independiente.
