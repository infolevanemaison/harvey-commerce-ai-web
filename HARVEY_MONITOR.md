# Harvey Commerce AI — buscador autónomo de oportunidades

## Estado al 31/10/2026
- Programación configurada: **cada 4 horas, minuto 23 UTC** (6 veces al día), en el repositorio público de la agencia. Las ejecuciones pueden retrasarse o fallar, y **todavía no se ha acreditado una ejecución correcta**.
- Origen: entradas RSS públicas indexadas por Bing; no se accede a cuentas privadas ni se extrae contenido detrás de autenticación.
- Guarda como máximo 3 oportunidades por ejecución, con tope de 20 pendientes. Trata los anuncios indexados como **no verificados**, aunque las entradas lleven título y URL.
- Para reducir duplicados se calcula un identificador a partir de la URL original y se compara con los issues ya guardados.
- Cada oportunidad contiene un texto orientativo. **El sistema NO envía solicitudes, propuestas, emails, DMs, mensajes, pagos ni contratos**.
- Los resultados van a [Issues de esta agencia](https://github.com/infolevanemaison/harvey-commerce-ai-web/issues) y el proceso se consulta en [GitHub Actions](https://github.com/infolevanemaison/harvey-commerce-ai-web/actions/workflows/harvey-oportunidades.yml).
- No se emplean API de pago ni suscripciones adicionales; los límites gratuitos de GitHub dependen del repositorio y la cuenta.

## Comprobación de funcionamiento desde iPhone
1. Abre el enlace de **Actions** anterior.
2. Comprueba si existe alguna ejecución en verde de «Harvey — detectar oportunidades públicas».
3. Si no hay ninguna, puede estar deshabilitado; abre el workflow y busca «Enable workflow» si aparece.
4. Puedes ejecutar «Run workflow» una vez para comprobarlo manualmente. Si falla, revisa el log del paso de Python; no asumas que funciona por tener el fichero.

## Pendientes antes de trabajar para clientes
1. **Cuenta Workana:** perfil aún en revisión; no admite propuestas, ni se permite eludir la plataforma con correos externos.
2. **Ejército:** debe existir resolución de compatibilidad por escrito antes de ejercer actividad privada.
3. **Calidad:** comprobar datos y entregables; no inventar precios, resultados ni testimonios.
4. **Tesorería:** cuota RETA e impuestos se deben verificar con documentación real. El sistema no factura ni cobra.

## Métricas al momento de configurar
- Propuestas enviadas desde la agencia: **0** (sin evidencia de envíos).
- Clientes pagados: **0**.
- Ingresos comprobados de la agencia: **0 €**.
- Oportunidades sin revisar: consultar Issues; su existencia no equivale a leads interesados.

El objetivo es minimizar las tareas del fundador, pero el trabajo pagado y los compromisos con terceros requieren autorización legal, supervisión y acceso seguro.
