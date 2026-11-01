# Cumplimiento legal – Grupo Urbanísima (España, noviembre 2026)

> **Importante:** esto es un trabajo técnico hecho de buena fe sobre la normativa vigente (RGPD, LOPDGDD, LSSI-CE, TRLGDCU y la Guía de cookies de la AEPD). **No sustituye el asesoramiento de un abogado o de la gestoría de la empresa.** Los textos legales deben ser revisados y validados por ellos antes de publicar, y revisarse una vez al año o cuando cambie la ley.

## Qué incluye la web

| Obligación | Cómo está resuelta |
|---|---|
| **Aviso legal** (LSSI-CE, art. 10) | `/aviso-legal/`: titular, domicilio, correo, inscripción registral, condiciones de uso, propiedad intelectual, responsabilidad, consumidores, ley aplicable. |
| **Política de privacidad** (RGPD art. 13; LOPDGDD) | `/ley-proteccion-datos/`: responsable, datos, finalidades y bases jurídicas, destinatarios (SiteGround, correo, WhatsApp/Meta, Google), transferencias internacionales, plazos, derechos, AEPD, menores, seguridad. Sustituye la antigua (ARCO, "Nombre de la empresa…"). |
| **Información por capas** | Resumen visible junto a **los dos formularios** («Información básica sobre protección de datos»). |
| **Consentimiento en formularios** | Casilla obligatoria «He leído y acepto la política de privacidad», sin premarcar, en los dos formularios. El servidor la exige. |
| **Prueba del consentimiento** (art. 7.1 RGPD) | Cada correo de solicitud incluye la aceptación, la fecha y la versión de la política. |
| **Minimización de datos** | El correo ya no incluye la IP. La atribución publicitaria (`gclid`, UTM) solo se guarda y envía si aceptas la publicidad. |
| **Política de cookies** (LSSI-CE art. 22.2) | `/aviso-ley-cookies/`: tabla de cookies (titular, finalidad, duración, tipo), cómo gestionarlas, retirar el consentimiento. |
| **Banner de cookies** (Guía AEPD) | «Rechazar todo» y «Aceptar todo» idénticos en aspecto y clics, «Configurar» con categorías sin marcar, **no se carga nada de Google antes de decidir**, enlace permanente «Configurar cookies» en el pie, la decisión caduca a los 24 meses y retirar publicidad borra las cookies. Sin etiqueta de Google configurada no hay cookies de terceros ni banner. |
| **Tipografías sin Google** | Alojadas en el propio servidor: no se envía la IP del visitante a Google por cargar fuentes. |
| **Condiciones de presupuesto y contratación** (TRLGDCU) | `/condiciones/`: presupuesto gratuito y no vinculante, aceptación, ejecución, garantía, **desistimiento de 14 días** (contratos fuera del establecimiento) con modelo de formulario y excepciones, reclamaciones, jurisdicción. |
| **Seguridad** | HTTPS forzado, HSTS, cabeceras de seguridad, antibots sin servicios de terceros, límite de envíos. |
| **Comunicaciones comerciales** (LSSI-CE art. 21) | La web no envía publicidad no solicitada y así lo indica. |

## Pendiente por parte de la empresa (antes de publicar)

1. **CIF y datos del Registro Mercantil.** Son obligatorios en el Aviso legal (art. 10 LSSI-CE) y no aparecían en los textos anteriores. Complétalos en `config.js` (`LEGAL.CIF` y `LEGAL.REGISTRO_MERCANTIL`). Mientras estén vacíos, las páginas muestran «[… pendiente de completar]».
   - Comprueba que no falta nada con: `npm run check:legal` (si devuelve error, no publiques).
2. **Código postal.** Los textos y la web dicen **45007**, pero los códigos postales de Valencia empiezan por **46** (el 45 es Toledo). Confirma el correcto, corrígelo en `config.js` (`LEGAL.CODIGO_POSTAL`) y en `index.html` (contacto, pie y datos estructurados `postalCode`).
3. **Proveedor de correo.** La política anterior citaba Raiola Networks, pero los buzones de la empresa (`info@`, `admin@`, `gerencia@`) están en SiteGround, y así consta ahora en la política. Si queda algún buzón antiguo en otro proveedor, hay que añadirlo.
4. **Contratos de encargado del tratamiento (art. 28 RGPD).** Acepta/archiva los de SiteGround, el proveedor de correo y, en Google Ads, las *Condiciones de tratamiento de datos* (Administración → Configuración de la cuenta).
5. **Procedimientos internos** (la política lo promete):
   - **Eliminar las solicitudes que no se contraten a los 30 días** del último contacto (correo, WhatsApp, hojas de cálculo). Si prefieres otro plazo, cámbialo en la política y en `contact.php`.
   - **Atender los derechos de los usuarios en un mes** (acceso, supresión, etc.) escribiendo a `info@`.
   - **Registro de actividades de tratamiento** (art. 30 RGPD): documento interno, no público.
   - Protocolo de **brechas de seguridad** (aviso a la AEPD en 72 h cuando proceda).
6. **Revisión jurídica de las condiciones** (garantía, desistimiento, validez del presupuesto, plazos) y de la política de privacidad.
7. **Hojas de reclamaciones.** La normativa autonómica de consumo las exige en establecimientos abiertos al público; confirma si les aplica con la gestoría. El texto indica que están disponibles.

## Si cambia algo en el futuro

- Activar **Google Analytics**, remarketing, chat, mapas incrustados, vídeos o redes sociales: hay que actualizar la tabla de cookies y, si procede, pedir consentimiento.
- Añadir una **tienda online o pagos**: se necesitan condiciones de venta específicas, información precontractual y política de devoluciones.
- Enviar **newsletters o promociones**: se necesita consentimiento expreso y casilla propia.
- Cambiar a otro hosting o correo: actualizar destinatarios y transferencias en la política.
- Revisar la web ante cambios normativos de cookies o privacidad en la UE.

## Efecto en Google Ads

Como Google no se carga hasta que el usuario acepta, **solo se miden las conversiones de quienes aceptan la publicidad**. Es la opción más prudente en España y es normal que haya menos conversiones registradas que solicitudes reales (los correos siguen llegando todos). Para compararlo, lleva la cuenta de las solicitudes recibidas por correo y no solo las de Google Ads.
