# Migración al dominio principal y Google Ads

## 1. Migración a grupo-urbanisima.com (SiteGround)
Antes de empezar: copia de seguridad completa (SiteGround > Copias de seguridad) y ya tener el ZIP final.

1. **Guardar WordPress**: en el Administrador de archivos, dentro de `public_html`, crea la carpeta `_wp_old` y mueve ahí **todo** lo que hay (WordPress). No borres nada.
2. **Proteger la carpeta antigua**: Site Tools > Seguridad > URL protegidas > `_wp_old` con usuario y contraseña.
3. **Subir la web nueva**: sube `web-grupo-urbanisima.zip` a `public_html` y extráelo ahí (archivos directamente en `public_html`, no en una subcarpeta). Activa "Mostrar archivos ocultos" para comprobar que está `.htaccess`.
4. **Vaciar cachés**: Site Tools > Speed > Caching > Dynamic Cache > Flush. Recarga con Ctrl+F5.
5. **HTTPS y dominio**: Site Tools > Seguridad > HTTPS Enforce activado; el `.htaccess` redirige a `https://grupo-urbanisima.com` (sin www).
6. **Pruebas (todas deben pasar)**:
   - `https://grupo-urbanisima.com/` carga la web nueva.
   - `https://grupo-urbanisima.com/reparacion-de-tejados-en-valencia/?gclid=PRUEBA123` redirige (301) a la página de servicio **conservando** `?gclid=PRUEBA123`.
   - Enviar el formulario con correo y con WhatsApp: llegan a `info@grupo-urbanisima.com` y a la copia, y WhatsApp abre el +34 722 115 251.
   - `/gracias/`, `/aviso-legal/`, `/ley-proteccion-datos/`, `/aviso-ley-cookies/` y `/condiciones/` cargan.
7. **Search Console**: añade/comprueba la propiedad y envía `https://grupo-urbanisima.com/sitemap.xml`.
8. **Entorno de pruebas**: deja `nueva.grupo-urbanisima.com` con contraseña (o bórralo) para que no compita en Google.
9. **Medición**: con Tag Assistant, acepta cookies y envía una solicitud: deben verse `lead_email` o `lead_whatsapp` en `/gracias/`.

**Antes de publicar (obligatorio por ley):** rellenar `LEGAL.CIF` y `LEGAL.REGISTRO_MERCANTIL` y confirmar el código postal en `config.js` (45007 parece incorrecto). Comprobar con `npm run check:legal`.
**Privacidad:** las copias a `creative.lestudio@gmail.com` hacen que Le Studio reciba datos personales de los clientes. Hay que reflejarlo en la política de privacidad (destinatarios/encargado del tratamiento) y firmar un contrato de encargo de tratamiento con la empresa.

## 2. Google Ads: estructura recomendada
Cuenta con seguimiento automático (gclid) activado. Plantilla de seguimiento a nivel de cuenta:
`{lpurl}?utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_term={keyword}`

**Conversiones** (Objetivos > Conversiones): solo estas dos como *principales*: `lead_email` y `lead_whatsapp` (se disparan en `/gracias/`). Las conversiones antiguas "Retiradas" se dejan así. No marcar como principal ningún clic en teléfono o WhatsApp.

**Campañas de Búsqueda (4 + marca)**, una por grupo de servicios, ubicación: **provincia de Valencia** (presencia, no "interés"), idioma español:
- Tejados y cubiertas · Humedades e impermeabilización · Reformas interiores · Fachadas y mantenimiento · Marca (palabra exacta "grupo urbanisima", presupuesto mínimo, URL: portada).

**Pujas**: empezar con *Maximizar conversiones*; al tener 30 conversiones en 30 días, pasar a *CPA objetivo*. Presupuesto repartido según prioridad del negocio (goteras/impermeabilización y tejados primero).
**Palabras clave**: frase y exacta por servicio (p. ej. "reparar goteras valencia", "impermeabilizar terraza valencia"). Sin concordancia amplia hasta tener datos.
**Negativas** (lista compartida): gratis, empleo, trabajo, curso, tutorial, "hazlo tú mismo", precio de materiales, leroy, bricomart, segunda mano, wikipedia.
**Anuncios**: 2 anuncios adaptables por grupo de anuncios, con titulares de servicio y "Visita gratuita", "Presupuesto sin compromiso", "Valencia y provincia". No prometer plazos ni garantías que no estén confirmadas.
**Extensiones**: enlaces de sitio (Servicios, Goteras, Tejados, Pedir presupuesto), destacados (Visita gratuita · Sin compromiso · Valencia y provincia), llamada (+34 722 115 251, L–V 9–19).

### Página final de cada grupo de anuncios
| Campaña | Grupo de anuncios | URL final |
|---|---|---|
| Tejados y cubiertas | Rehabilitación y reparación de tejados antiguos | `https://grupo-urbanisima.com/servicios/rehabilitacion-reparacion-tejados-valencia/` |
| Tejados y cubiertas | Construcción de tejados nuevos | `https://grupo-urbanisima.com/servicios/construccion-tejados-nuevos-valencia/` |
| Tejados y cubiertas | Cubiertas y cerramientos de panel sandwich | `https://grupo-urbanisima.com/servicios/cubiertas-cerramientos-panel-sandwich-valencia/` |
| Humedades e impermeabilización | Reparación de goteras | `https://grupo-urbanisima.com/servicios/reparacion-goteras-valencia/` |
| Humedades e impermeabilización | Impermeabilización de cubiertas, canalones y terrazas | `https://grupo-urbanisima.com/servicios/impermeabilizacion-cubiertas-canalones-terrazas-valencia/` |
| Humedades e impermeabilización | Rehabilitación y construcción de terrazas | `https://grupo-urbanisima.com/servicios/rehabilitacion-construccion-terrazas-valencia/` |
| Reformas interiores | Reforma integral | `https://grupo-urbanisima.com/servicios/reforma-integral-valencia/` |
| Reformas interiores | Reforma de baños | `https://grupo-urbanisima.com/servicios/reforma-banos-valencia/` |
| Reformas interiores | Trabajos en pladur | `https://grupo-urbanisima.com/servicios/trabajos-pladur-valencia/` |
| Reformas interiores | Pintura interior | `https://grupo-urbanisima.com/servicios/pintura-interior-valencia/` |
| Fachadas y mantenimiento | Pintura de fachadas | `https://grupo-urbanisima.com/servicios/pintura-fachadas-valencia/` |
| Fachadas y mantenimiento | Limpieza y mantenimiento de chimeneas | `https://grupo-urbanisima.com/servicios/limpieza-mantenimiento-chimeneas-valencia/` |
| Fachadas y mantenimiento | Desatasco de chimeneas y salidas de humo | `https://grupo-urbanisima.com/servicios/desatasco-chimeneas-salidas-humo-valencia/` |
| Fachadas y mantenimiento | Limpieza de canalones | `https://grupo-urbanisima.com/servicios/limpieza-canalones-valencia/` |
| Marca | grupo urbanisima | `https://grupo-urbanisima.com/` |

Los enlaces ya precargan el servicio en el formulario. Para anuncios por tipo de cliente se puede añadir `?perfil=particulares|comunidades|empresas` a la URL.

## 3. Lo que necesito para configurarlo contigo
Capturas de: la lista de campañas (con estrategia de puja y presupuesto), el motivo del rechazo de los anuncios, el informe de términos de búsqueda y las conversiones. Con eso concreto palabras clave, negativas y reparto de presupuesto.
