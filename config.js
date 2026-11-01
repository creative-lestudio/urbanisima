/*
 * CONFIGURACIÓN DE LA WEB. Es el único archivo que hay que editar al publicar.
 *
 * GOOGLE_TAG_ID  → ID de la etiqueta de Google del Google Ads de la cuenta (formato AW-1234567890).
 *                  Google Ads > Objetivos > Conversiones > Resumen > "Etiqueta de Google".
 *                  Mientras esté vacío no se carga ningún script de Google ni se muestra el banner de cookies.
 * CONVERSIONS    → valor "send_to" de cada acción de conversión (formato AW-1234567890/AbCdEfGhIjK).
 *                  Google Ads > Objetivos > Conversiones > (acción) > Configuración de la etiqueta > "Fragmento de evento".
 */
window.URBANISIMA_CONFIG = {
  GOOGLE_TAG_ID: '',
  CONVERSIONS: {
    lead: '',            // solicitud enviada (correo o WhatsApp). Se dispara en /gracias/
    click_call: '',      // clic en un teléfono
    click_whatsapp: ''   // clic directo en los botones de WhatsApp (flotante, barra móvil, contacto)
  },
  ENDPOINT: 'contact.php',               // script PHP que envía el correo (ver contact.php)
  WHATSAPP: '34722115251',
  EMAIL: 'info@grupo-urbanisima.com'     // solo para el plan B (se abre el correo del usuario si falla el envío)
};
