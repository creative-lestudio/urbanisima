# Captación de leads y automatización

## Qué registra cada solicitud
Cada envío del formulario genera un identificador único (`UR-AAMMDD-XXXXXX`) y queda con estado **Nuevo**. El correo a la empresa incluye:
identificador, fecha y hora, canal (correo/WhatsApp), formulario de origen (hero o contacto), origen de captación (Ads/orgánico/directo, si hubo consentimiento de cookies), página de entrada, servicio, tipo de cliente, localidad, urgencia, datos de contacto, comentarios y fotos adjuntas (hasta 3, JPG/PNG/WebP, ≤5 MB; el navegador las reduce a 1600 px).

Estados comerciales previstos (se gestionan en el CRM/hoja, no en la web):
`Nuevo → Contactado → Visita pendiente → Presupuesto enviado → Aceptado / Perdido`.

## Conectar con n8n, Make o un CRM (opcional)
En `contact.php` hay dos líneas al principio:
```php
$WEBHOOK_URL    = '';   // URL del webhook, p. ej. https://n8n.tudominio.com/webhook/urbanisima-leads
$WEBHOOK_SECRET = '';   // clave larga y aleatoria (solo vive en el servidor, nunca en la web)
```
Si se rellenan, cada solicitud se envía además como JSON (POST) con la cabecera
`X-Urbanisima-Signature: sha256=<HMAC-SHA256 del cuerpo con la clave>`. En n8n se verifica calculando el mismo HMAC con la misma clave.
Si el webhook falla, **la solicitud sigue llegando por correo** (el fallo se anota en el log de PHP).
Campos del JSON: `lead_id, fecha, estado, canal, formulario, origen_captacion, pagina_entrada, pagina_envio, servicio, tipo_cliente, localidad, urgencia, urgente, nombre, telefono, email, mensaje, fotos_adjuntas, utm{…}, politica_version`. Las fotos no se envían al webhook (solo van por correo).

**Falta para activarlo:** la URL del webhook y la clave (las crea quien monte n8n/CRM). Mientras estén vacías, está desactivado.

## Eventos de medición (GA4 vía la etiqueta de Google existente)
Solo se envían si el visitante aceptó las cookies de medición/publicidad.
| Evento | Cuándo |
|---|---|
| `click_whatsapp` / `click_phone` | clic en WhatsApp o teléfono (no son conversiones finales) |
| `click_quote_cta` | clic en un botón de pedir presupuesto (`ubicacion`: header, hero, servicio…) |
| `form_start` | primera interacción con el formulario del hero |
| `form_step_complete` | paso 1 y paso 2 completados (`step`) |
| `form_submit_success` y `lead_email` / `lead_whatsapp` | en /gracias/ tras enviar la solicitud. Las conversiones de Ads son `lead_*` |
| `service_view` | visita a una página de servicio (`servicio`) |
`project_view` queda pendiente hasta que existan páginas de proyectos.
KPIs como coste por lead, presupuestos enviados y aceptados se calculan en Google Ads/CRM, no en la web.
