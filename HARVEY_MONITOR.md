# Harvey Commerce AI — buscador autónomo de oportunidades

## Estado al 31/10/2026
- Programación configurada: **cada 4 horas, minuto 23 UTC** (6 veces al día), en el repositorio público de la agencia. Las ejecuciones pueden retrasarse o fallar. Se han **verificado ejecuciones correctas de GitHub Actions**, pero cada futura ejecución y la captación de clientes no están garantizadas.
- Origen: RSS públicos de Freelancer y resultados RSS de Bing con anuncios de Workana; no se accede a cuentas privadas ni a contenido detrás de autenticación. El buscador RSS puede omitir oportunidades reales, devolver datos caducados o fallar temporalmente.
- Guarda como máximo **5 oportunidades por ejecución**, con tope de **30 pendientes**. Clasifica anuncios por afinidad a fichas de producto, contenido SEO y Shopify; intenta excluir prohibiciones de IA, condiciones idiomáticas inadecuadas y proyectos amplios de desarrollo. Las coincidencias y puntuaciones **no son clientes ni anuncios verificados**, y requieren evaluación humana.
- Para reducir duplicados se calcula un identificador a partir de la URL original y se compara con los issues ya guardados.
- Cada oportunidad contiene un borrador genérico que debe personalizarse y revisarse. Los anuncios encontrados manualmente cuentan con propuestas específicas en el repositorio privado.  **El sistema NO envía solicitudes, propuestas, emails, DMs, mensajes, pagos ni contratos**.
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

## Última comprobación técnica (31/10/2026)
- Ejecución anterior correcta del flujo: https://github.com/infolevanemaison/harvey-commerce-ai-web/actions/runs/41243210423. El filtro y la puntuación se han modificado el 01/11/2026 y deben contrastarse con un nuevo registro de Actions.
- Importante: registros en Issues contienen anuncios **no contactados**; los cerrados son descartados por falta de encaje. No son visitas ni solicitudes recibidas en la agencia.
- Trabajo comercial y obligaciones legales siguen bloqueados antes de autorización y validación.


## Auditoría y recuperación del monitor — 04/11/2026

- **Desbloqueo realizado desde ChatGPT, sin reconectar GitHub:** el parche que Harvey Claude guardó en el repo privado bajo commit `5a68078` se ha aplicado a **este repositorio**. Commit `224462a395b093dfdbcfa21478ab91b564975556`: incorpora palabras clave en español al filtro y contador de rechazos. Se validaron las **52 pruebas**.
- **Limpieza completada:** se han cerrado como `not_planned` los ocho issues originales de Freelancer **#7, #9, #17, #18, #19, #24, #25, #26**, preservando sus historiales. Continúan abiertos solo los cinco Issues de Workana **#1, #20, #21, #22, #23**. No se envió ninguna candidatura.
- **Segundo diagnóstico real:** el run por push [41854190566](https://github.com/infolevanemaison/harvey-commerce-ai-web/actions/runs/41854190566) terminó `success`, pero **0 de 26 resultados RSS tenían enlace válido a Workana**. La búsqueda Bing RSS ha devuelto enlaces ajenos al dominio incluso usando `site:`. Por tanto el problema ACTUAL **ya no es exclusivamente el vocabulario del filtro**, sino que la fuente de búsqueda no proporciona resultados utilizables.
- **Monitorización segura de salud:** commit `d0aca1e95701db2d833ae43aab5669eaa4a888ab` añade estado `SIN_DATOS_RSS` / `SIN_ENLACES_WORKANA` / `ENLACES_WORKANA_PRESENTES` en el log y el resumen de GitHub Actions, sin entrar en Workana ni generar publicaciones falsas. **53 pruebas locales superadas.** Run [41855250808](https://github.com/infolevanemaison/harvey-commerce-ai-web/actions/runs/41855250808) completado con `success` y estado real: **30 elementos RSS, 0 enlaces válidos Workana, 0 oportunidades aceptadas**. El aviso ya no es silencioso aunque el flujo no falle.
- **Próximo camino permitido:** no usar bots, scraping, APIs no autorizadas ni accesos externos a Workana, según sus [términos](https://help.workana.com/hc/es/articles/360041499974-T%C3%89RMINOS-Y-CONDICIONES-DE-WORKANA). Mantener las cinco oportunidades en borrador; comprobar aprobación del perfil y aprovechar avisos nativos de la plataforma **solo cuando estén habilitados**. Ninguna oferta puede presentarse ni contratarse hasta resolver la habilitación y las autorizaciones profesionales necesarias. `docs/plan-workana-pph-20261104.md` contiene borradores personalizados.
- **Permisos por integración:** ChatGPT ha escrito en este repositorio y ha verificado lectura posterior. Eso **no demuestra** que la sesión temporal Claude Code ya tenga permisos de escritura; no solicitar al titular reconexión para volver a aplicar los cambios anteriores. Si Claude necesita escritura directamente en otra tarea, diagnosticar ese permiso separado antes de pedir intervención.
- **Cifras verificadas:** 0 propuestas nuevas enviadas, 0 clientes, 0 € de ingreso. La salud del sistema es distinta de conseguir oportunidades reales. No introducir nuevos gastos ni duplicar cronjobs.

## Validación de monitor y avisos nativos — 04/11/2026

- GitHub Actions `harvey-oportunidades.yml` ejecuta ahora las pruebas del filtro `test_monitor_oportunidades.py` **antes de consultar el RSS**; cambio mínimo confirmado en rama main. Ejecución real [41858337411](https://github.com/infolevanemaison/harvey-commerce-ai-web/actions/runs/41858337411): **4 pruebas específicas OK**, monitor finalizado, **26 ítems RSS, 0 enlaces de proyectos Workana y 0 oportunidades nuevas**. Esto indica problema de fuente y no ausencia demostrada de proyectos en Workana.
- Las notificaciones de proyectos de Workana pueden configurarse por el titular desde **foto de perfil → Mi cuenta → Notificaciones y alertas**. Fuente oficial: https://help.workana.com/hc/es/articles/360042101293--C%C3%B3mo-configurar-las-notificaciones-de-proyectos-que-recibes-por-correo
- Se amplió la automatización ChatGPT existente «Harvey responde mi correo» para clasificar **notificaciones nativas de nuevos proyectos Workana**, si llegan al Gmail autorizado, en su única comprobación diaria de Workana. No confirmar que las notificaciones estén activadas: no hay acceso a preferencias del perfil. No se ha creado otra tarea ni se accede al sitio con bots.
- **Siguiente condición:** recibir un aviso oficial legítimo o que el titular habilite alertas; hasta entonces no se espera que la rama de correo descubra nuevas oportunidades. No gastar, no postular ni contratar sin habilitación legal y perfil aprobado.

## Confirmación del titular: avisos de Workana activados — 04/11/2026

- El titular declara **«está todo activado en Workana»**. Considerar la configuración de avisos de proyectos activada **según confirmación del titular**; no repetir instrucciones para activarla.
- Verificación independiente del correo conectado `infolevanemaison@gmail.com` (Gmail, 04/11): búsquedas `workana -in:spam -in:trash` y `from:(workana.com) -in:spam -in:trash` devolvieron **0 mensajes**. Esto no demuestra un problema de Workana ni que las alertas estén desactivadas; no hay aviso recibido aún en este buzón.
- La tarea ya existente `Harvey responde mi correo` clasifica una vez al día avisos oficiales de moderación y nuevos proyectos; no añadir cron ni bots de Workana ni tratar un aviso como contrato.
- Aprobación del perfil: **no verificada por acceso al panel ni email**, incluso si el usuario confirma que tiene todo activado. Distinguir ajustes de notificaciones, aprobación del perfil y habilitación para contratar.
- Siguiente paso automático: cuando llegue una alerta real, confirmar remitente, fecha, enlace de proyecto y encaje con Shopify y fichas. Preparar propuesta en borrador y medir propuestas enviadas solo con evidencia en el canal autorizado. No realizar contrataciones remuneradas antes de resolver las autorizaciones profesionales y fiscales pendientes.
