# Guía de lanzamiento – Grupo Urbanísima

Objetivo: publicar la web nueva en el dominio del cliente (SiteGround), dejar el formulario enviando correos y rehacer las campañas de Google Ads con medición de conversiones correcta.

**Orden recomendado (no lo alteres):** 0 Accesos → 1 Copias de seguridad → 2 Pruebas en subdominio → 3 Publicar → 4 Conversiones → 5 Auditoría de campañas → 6 Campañas nuevas → 7 Seguimiento.

> **Por qué este orden:** la medición (paso 4) debe funcionar *antes* de tocar las campañas. Si no, no sabrás si los cambios mejoran o empeoran.

---

## 0. Accesos y seguridad (10 min)

- **No compartas contraseñas por chat ni por correo.** Pídele al cliente que te *invite* con tu propio correo:
  - **Google Ads:** Administración → Acceso y seguridad → Usuarios → invitar con rol **Administrador** (o vincular tu cuenta de administrador/MCC).
  - **SiteGround:** Área de cliente → Compartir acceso (colaboradores) o, si no está disponible, crear un usuario propio.
  - **WordPress:** Usuarios → Añadir nuevo → rol Administrador con tu correo.
- Activa la verificación en dos pasos en tu cuenta de Google.
- Cuando termines el proyecto, el cliente revoca tus accesos o los mantiene a propósito.

## 1. Antes de tocar nada: copias y datos (30 min)

1. **Copia completa de SiteGround:** Site Tools → Seguridad → Copias de seguridad → *Crear copia de seguridad*. Descárgala también.
2. **WordPress:** Herramientas → Exportar → *Todo el contenido*. Guarda además la carpeta `wp-content/uploads`.
3. **Google Search Console** (si el dominio está verificado): Rendimiento → Páginas y Consultas → exporta 12 meses. Sirve para saber qué URLs traen visitas.
4. **Google Ads:** haz capturas del panel de cada campaña (últimos 12 meses) y descarga estos informes en CSV, que usarás en el paso 5:
   términos de búsqueda, palabras clave, anuncios, ubicaciones, dispositivos, día y hora, y conversiones.

### Lo que ya encontramos en la web actual (importante)
- Tiene **unas 47 páginas indexadas** (servicios por zona, chimeneas en Alicante y Castellón, aire acondicionado…). La web nueva es de una sola página: por eso incluimos **43 redirecciones 301** (`.htaccess`) que llevan cada URL antigua al servicio correspondiente. Así no se pierde el posicionamiento ni se rompen los anuncios.
- **No tiene ninguna etiqueta de Google** (ni Google Ads, ni Analytics, ni Tag Manager). Es probable que las conversiones no se estén midiendo, o se midan desde otro sitio. Revísalo en el paso 4.
- Existe una página `/gracias/` (la web nueva mantiene esa URL).

### Decisiones que debe tomar el cliente
| Tema | Pregunta |
|---|---|
| **Aire acondicionado** | La web antigua tiene 4 páginas (recarga, reparación, montaje). No está en los 14 servicios. ¿Lo siguen ofreciendo? Si sí, hay que añadirlo como servicio 15. Ahora esas URLs redirigen a la portada. |
| **Chimeneas en Alicante y Castellón** | La web nueva dice "provincia de Valencia". ¿Atienden también esas provincias? |
| **Textos legales** | Se han reescrito (ver `docs/CUMPLIMIENTO-LEGAL.md`). Faltan el **CIF y el Registro Mercantil**, y hay que confirmar el **código postal** (45007 no es de Valencia). Que los revise su gestoría o abogado. |
| **Correo de recepción** | ¿Todo a `info@`? En la web antigua también aparece `admin@`. Se cambia en `contact.php` (línea `$TO`). |
| **Quién edita la web a partir de ahora** | La web nueva es estática (rápida y sin plugins que se rompan), pero **ya no se edita desde WordPress**. Los cambios se hacen sobre los archivos. |

---

## 2. Pruebas en un subdominio (45 min)

Prueba todo en un sitio paralelo antes de reemplazar la web real.

1. SiteGround → Site Tools → **Dominio → Subdominios** → crear `nueva.grupo-urbanisima.com`.
2. **Protégelo con contraseña** para que Google no lo indexe: Seguridad → *URLs protegidas*.
3. **Crea el buzón que enviará los correos:** Correo → Cuentas → `web@grupo-urbanisima.com`. (Debe existir; si no, los correos pueden caer en spam.)
4. **Sube los archivos** de este repositorio a la carpeta del subdominio: Site Tools → Sitio → *Administrador de archivos* (o SFTP). Sube todo salvo `docs/`, `README.md` y `package.json`.
   - Imprescindibles: `index.html`, `styles.css`, `main.js`, `config.js`, `tracking.js`, `contact.php`, `.htaccess`, `robots.txt`, `sitemap.xml`, y las carpetas `assets/`, `gracias/`, `aviso-legal/`, `ley-proteccion-datos/`, `aviso-ley-cookies/`.
   - Para ver el archivo `.htaccess` activa "Mostrar archivos ocultos" en el administrador.
5. **Prueba el formulario de contacto** (los dos botones):
   - *Enviar por correo*: debe llevarte a `/gracias/` y llegar un correo a `info@`.
   - *Enviar por WhatsApp*: se abre WhatsApp con el mensaje, la página va a `/gracias/` y **también llega una copia por correo**.
   - Prueba también el formulario de arriba (hero) y desde el móvil.
   - Si el correo no llega: mira la carpeta spam; confirma que `web@` existe; en SiteGround activa SPF y DKIM (Site Tools → Correo → Autenticación).
6. En el móvil, comprueba que todo se ve bien y los botones Llamar y WhatsApp funcionan.

## 3. Publicar en el dominio real (30 min, mejor fuera del horario de atención)

> **Antes de publicar:** rellena los datos legales en `config.js` (CIF, Registro Mercantil, código postal) y ejecuta `npm run check:legal`. Sin ellos el Aviso legal está incompleto. Ver `docs/CUMPLIMIENTO-LEGAL.md`.

1. Haz **otra copia de seguridad** justo antes (paso 1.1).
2. En el Administrador de archivos, mueve los archivos de WordPress de `public_html` a una carpeta `public_html/_wp_old/` y **protégela con contraseña** (URLs protegidas). Mantenla 30 días por si hay que recuperar algo; luego elimínala.
3. Sube los archivos de la web nueva a la raíz de `public_html` (incluido `.htaccess`, que sustituye al de WordPress).
4. Comprueba, con el navegador en una ventana privada:
   - `https://grupo-urbanisima.com/` carga la web nueva y `http://` y `www.` redirigen a `https://grupo-urbanisima.com`.
   - Cinco URLs antiguas redirigen bien, por ejemplo `/servicios-grupo-urbanisima/servicios-de-reparacion-de-tejados/` debe llevar a `/?servicio=tejados`.
   - Los formularios, igual que en el paso 2.
5. **Search Console:** Sitemaps → añadir `https://grupo-urbanisima.com/sitemap.xml`. Revisa "Páginas" a las 2 semanas: si aparecen 404 de URLs que antes traían visitas, añade su redirección en `.htaccess`.
6. Si el sitio no cargara o hubiera un error 500: renombra `.htaccess` a `.htaccess.bak`; la web debería abrir. Si no, restaura la copia del paso 1.

---

## 4. Medición de conversiones (la base de todo) – 1 h

Sin esto, Google Ads no sabe qué anuncios traen clientes y la puja automática no puede optimizar.

### 4.1 Revisa lo que hay
Google Ads → **Objetivos → Conversiones → Resumen**. Anota las acciones existentes y su estado. Si ves "Sin actividad reciente" o "Etiqueta inactiva", confirma que no se estaba midiendo.

### 4.2 Crea las acciones de conversión
Objetivos → Conversiones → **Nueva acción de conversión → Sitio web**:

| Acción | Categoría | ¿Principal? | Conteo | Ventana |
|---|---|---|---|---|
| **Solicitud por correo** (`lead_email`) | Enviar formulario de clientes potenciales | **Sí** | Uno | 30 días |
| **Solicitud por WhatsApp** (`lead_whatsapp`) | Enviar formulario de clientes potenciales | No al principio (secundaria); principal cuando haya datos | Uno | 30 días |
| **Clic en teléfono** | Contacto | No (secundaria) | Uno | 30 días |
| **Clic en WhatsApp** | Contacto | No (secundaria) | Uno | 30 días |
| **Llamadas desde anuncios** (más de 30 s) | Llamada | **Sí** | Uno | 30 días |

Para la última: al crear los anuncios añade el *asset de llamada* y activa "Contar llamadas como conversiones".

### 4.3 Conecta la web
1. En Google Ads → Objetivos → Conversiones → Resumen, copia el **ID de la etiqueta de Google** (formato `AW-1234567890`).
2. En cada acción, abre "Configuración de la etiqueta → Usar Google Tag → Fragmento de evento" y copia el `send_to` (`AW-1234567890/AbCdEf...`).
3. Pega los valores en **`config.js`**:
   ```js
   GOOGLE_TAG_ID: 'AW-1234567890',
   CONVERSIONS: {
     lead_email:     'AW-1234567890/AbCdEf...',   // Solicitud por correo
     lead_whatsapp:  'AW-1234567890/XyZaBc...',   // Solicitud por WhatsApp
     click_call:     'AW-1234567890/GhIjKl...',   // Clic en teléfono
     click_whatsapp: 'AW-1234567890/MnOpQr...'    // Clic en WhatsApp
   },
   ```
4. Sube `config.js` otra vez (al subdominio primero, luego a la raíz). Al configurar el ID, la web muestra el **banner de cookies** y **solo carga Google cuando el visitante acepta** (cumple la LSSI-CE y la guía de la AEPD). Es normal que Google Ads registre menos conversiones que las solicitudes reales recibidas por correo: lleva también esa cuenta.
5. **Verifica:** abre https://tagassistant.google.com, conecta tu web, acepta cookies, envía un formulario de prueba y confirma que se dispara la conversión en `/gracias/`. El estado en Google Ads puede tardar 24-48 h en pasar a "Registrando conversiones".

### 4.4 Qué se mide
- **`lead_email` / `lead_whatsapp`:** se disparan una vez por sesión al cargar `/gracias/`. Con WhatsApp cuenta cuando abren el chat, no cuando lo envían; es una limitación normal de WhatsApp.
- Cada correo de solicitud incluye el **gclid y los UTM** de la visita, así sabes qué anuncio y qué palabra clave trajo cada cliente. Pide al cliente que anote cuáles se convierten en trabajo y, en 4-6 semanas, impórtalo como conversión offline.

### 4.5 Opcional recomendado
- Vincular **Google Analytics 4** y Search Console.
- Activar **conversiones mejoradas para clientes potenciales** (Objetivos → Configuración).

---

## 5. Auditoría de las campañas actuales (1-2 h)

Todavía no se ha visto nada de la cuenta; este paso es para hacerlo con datos reales. Si me pasas los CSV del paso 1.4 (sin contraseñas), preparo el diagnóstico.

Revisa, en este orden, en un rango de 90 días y otro de 12 meses:

| Qué mirar | Dónde | Señal de problema |
|---|---|---|
| Conversiones reales | Objetivos | Cero o muy pocas conversiones con muchos clics: falla la medición o la web. |
| **Términos de búsqueda** | Palabras clave → Términos de búsqueda | Búsquedas sin relación (empleo, "gratis", "cómo hacer", otras ciudades, aire acondicionado si ya no se ofrece). Añádelas como negativas. |
| Concordancia de palabras clave | Palabras clave | Mucha *amplia* sin negativas gasta en búsquedas irrelevantes. |
| Nivel de calidad | Palabras clave → columna Nivel de calidad | Menos de 6: anuncio y página no coinciden con la búsqueda. |
| **Redes** | Configuración | Desactiva **Display** y **socios de búsqueda** si están activos en campañas de búsqueda. |
| **Ubicación** | Configuración → Ubicaciones | Debe ser "**Presencia**: personas en tus ubicaciones", no "Presencia o interés". Provincia de Valencia. |
| Dispositivos y horas | Informes | Gasto en horas/días sin conversiones (por ejemplo, madrugada). |
| Cuota de impresiones perdida | Columnas | "Por presupuesto" alta: sube presupuesto o reduce alcance. "Por ranking" alta: mejora anuncios y calidad. |
| Anuncios | Anuncios | Anuncios de texto expandido antiguos (ya no se pueden crear), pocos titulares, sin variantes. |
| Assets | Assets | Sin sitelinks, llamada, ubicación o textos destacados. |
| Estrategia de puja | Configuración | CPC manual abandonado o presupuestos muy bajos para la puja automática. |
| **Landing** | Anuncios | Todos apuntan a la portada antigua o a páginas que ahora redirigen. Cámbialos en el paso 6. |

**Anota:** CPC medio, CTR, coste por conversión, nº de conversiones/mes y qué servicio genera más. Son tu punto de partida para comparar.

---

## 6. Campañas nuevas (2-3 h)

**Regla:** no borres las campañas viejas. Crea las nuevas en paralelo, déjalas 2 semanas y luego **pausa** las viejas si rinden peor.

### 6.1 Estructura propuesta
Todas: **Red de Búsqueda**, ubicación *Provincia de Valencia* (presencia), idioma español, sin Display ni socios.

| Campaña | Grupos de anuncios (ejemplos) | URL final |
|---|---|---|
| **1. Goteras e impermeabilización** (la de mayor intención) | goteras en techo · impermeabilización de terrazas · impermeabilización de cubiertas · humedades en tejado | `https://grupo-urbanisima.com/?servicio=impermeabilizacion` |
| **2. Reparación de tejados** | reparación de tejados · cambio de tejas · rehabilitación de tejados · tejados urgente | `…/?servicio=tejados` |
| **3. Comunidades de vecinos** | rehabilitación de fachadas · impermeabilización de edificios · pintura de patios · pintado de garajes | `…/?perfil=comunidades&servicio=fachadas` |
| **4. Empresas y naves** | cubiertas de naves industriales · panel sandwich · pavimento epoxi · reformas de locales | `…/?perfil=empresas&servicio=tejados` |
| **5. Otros servicios** (poco presupuesto) | canalones · deshollinado de chimeneas · jardinería | `…/?servicio=canalones` etc. |
| **6. Marca** (opcional, barata) | "grupo urbanisima" | `https://grupo-urbanisima.com/` |

**Cómo funcionan las URL:** la web lee `?perfil=` y `?servicio=`. La página llega ya con el servicio buscado **el primero**, marcado "Lo que buscas", seleccionado en el formulario, y con el formulario del hero abierto en el paso 2 con los servicios del perfil. Valores de `servicio`: `tejados`, `impermeabilizacion`, `canalones`, `fachadas`, `verticales`, `garajes`, `panel`, `epoxi`, `chimeneas`, `jardines`, `piscinas`, `locales`, `cocinas`, `reformas`. Valores de `perfil`: `particulares`, `comunidades`, `empresas`.

**Seguimiento de URL (cuenta → Configuración → Plantilla de seguimiento):**
`{lpurl}&utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_term={keyword}`
(funciona porque todas las URLs finales ya llevan `?`). Deja **etiquetado automático (gclid)** activado.

### 6.2 Palabras clave
Empieza con **concordancia exacta y de frase** (sin amplia). Ejemplos para el grupo de goteras:
`[arreglar goteras en el techo]`, `[reparar goteras tejado]`, `"impermeabilización de terrazas valencia"`, `"impermeabilizar cubierta"`, `"reparación de tejados valencia"`. Añade variantes con las poblaciones más rentables.

**Negativas a nivel de cuenta (lista inicial):** `empleo`, `trabajo`, `curso`, `formación`, `tutorial`, `diy`, `cómo hacer`, `casero`, `pdf`, `segunda mano`, `fabricante`, `distribuidor`, `tienda`, `bricolaje`, `aire acondicionado` (si ya no se ofrece), `alicante`, `castellón`, `madrid`, `barcelona`, además de lo que encuentres en el informe de términos de búsqueda. **No pongas `gratis` como negativa**: el cliente ofrece presupuesto gratuito y esa gente sí interesa.

Revisa los términos de búsqueda **cada día la primera semana** y añade negativas.

### 6.3 Anuncios (Anuncio adaptable de búsqueda)
15 titulares (máx. 30 caracteres, ya comprobados) y 4 descripciones (máx. 90):

**Titulares**
1. Arreglo de Goteras en Valencia
2. Impermeabilización Terrazas
3. Reparación de Tejados
4. Presupuesto Gratis y Rápido
5. Más de 10 Años de Experiencia
6. Visita Gratis a Domicilio
7. Fin Definitivo a Humedades
8. Trabajos en Altura y Andamios
9. Toda la Provincia de Valencia
10. Llama al 722 115 251
11. Impermeabilizamos Cubiertas
12. ¿Goteras en el Techo? Llámanos
13. Mejores Materiales y Marcas
14. Garantía Profesional
15. Presupuesto Sin Compromiso

**Descripciones**
1. Acabamos con goteras y humedades de forma definitiva. Pide tu presupuesto gratis hoy.
2. Reparación e impermeabilización de tejados, terrazas y cubiertas en toda Valencia.
3. Vamos a tu domicilio sin coste. Presupuesto sin compromiso y trabajos con garantía.
4. Particulares, comunidades y empresas. Plan de trabajo y de seguridad. Pide presupuesto.

Adapta por campaña: en la de comunidades usa "Rehabilitación de Fachadas", "Comunidades de Vecinos" y "Trabajos Verticales"; en empresas, "Cubiertas de Naves", "Panel Sandwich" y "Pavimentos Epoxi". Pon la palabra clave principal en el titular 1. Tiene que haber al menos 2 anuncios por grupo.

### 6.4 Assets (extensiones)
- **Llamada:** +34 722 115 251. Programa solo **lunes a viernes 9:00–19:00** (el horario de atención telefónica de la web). Fuera de horario sigue funcionando el formulario y WhatsApp.
- **Sitelinks** (con URLs con parámetros): Particulares · Comunidades de vecinos · Empresas y naves · Pedir presupuesto (`#contacto`).
- **Textos destacados:** Presupuesto gratis · Sin compromiso · Visita a domicilio sin coste · +10 años de experiencia · Garantía profesional.
- **Ubicación:** vincula la ficha de **Google Business Profile** (Jacinto Labaila 8b, Valencia). Si no existe, créala: ayuda también al SEO local.
- **Fragmentos estructurados:** Servicios (los 14).

### 6.5 Puja y presupuesto
- **Si hay menos de ~30 conversiones al mes:** empieza con *Maximizar clics* con CPC máximo, o *Maximizar conversiones* en cuanto la medición funcione (paso 4) y la campaña acumule unas 15-20 conversiones.
- **Con 30+ conversiones/30 días:** pasa a *Maximizar conversiones* con **CPA objetivo**.
- **Calcula el CPA máximo:** valor medio de un trabajo × margen × porcentaje de solicitudes que se cierran. Ejemplo: 900 € × 30 % × 25 % = 67 € por solicitud. (Pregunta los datos reales al cliente.)
- **Presupuesto diario ≈** (solicitudes deseadas al mes × coste por solicitud) ÷ 30,4. No lo repartas entre demasiadas campañas: concentra en 1 y 2, y deja las demás con poco.
- No cambies puja y anuncios el mismo día: en cada cambio, espera 7-14 días de "aprendizaje".

---

## 7. Seguimiento tras el lanzamiento

| Cuándo | Qué hacer |
|---|---|
| **Día 0** | Lanzar. Verificar que conversiones y llamadas se registran. |
| **Días 1-7** | Términos de búsqueda a diario → negativas. No cambiar puja. |
| **Día 7** | ¿Hay clics? ¿Hay solicitudes en los correos? Compara con el histórico del paso 5. |
| **Día 14** | Pausar anuncios y palabras clave con mucho gasto y cero conversiones. Ajustar presupuesto. |
| **Día 30** | Decidir: pausar campañas viejas, pasar a puja por CPA, ampliar lo que funciona. |
| **Mensual** | Informe: solicitudes, coste por solicitud, servicios más pedidos, horas y dispositivos, términos. Preguntar al cliente cuántas se convirtieron en trabajo. |

**Referencia, no objetivo:** compara siempre con *tu propio histórico del paso 5*; los resultados dependen del mercado, la competencia y la estacionalidad (picos con las lluvias).

---

## Checklist final

- [ ] Copia de seguridad hecha y descargada
- [ ] Buzón `web@` creado; SPF/DKIM activos
- [ ] Formularios probados en subdominio (correo, WhatsApp y hero) y en el dominio real
- [ ] 5 URLs antiguas redirigen bien
- [ ] `sitemap.xml` enviado en Search Console
- [ ] `config.js` con ID de Google y las 3 conversiones
- [ ] Tag Assistant confirma la conversión en `/gracias/`
- [ ] Banner de cookies visible y funcionando (probar Aceptar, Rechazar y «Configurar cookies» del pie)
- [ ] **`config.js` → `LEGAL`: CIF, Registro Mercantil y código postal correctos; `npm run check:legal` sin errores**
- [ ] Textos legales revisados por la gestoría o abogado (ver `docs/CUMPLIMIENTO-LEGAL.md`)
- [ ] Decisión sobre aire acondicionado y Alicante/Castellón
- [ ] Campañas nuevas con URLs con parámetros y plantilla de seguimiento
- [ ] Campañas viejas pausadas (no borradas) tras 2 semanas de comparación
- [ ] Ficha de Google Business Profile vinculada

## Mapa de archivos

| Archivo | Para qué sirve |
|---|---|
| `index.html`, `styles.css`, `main.js` | La web |
| `config.js` | **Único archivo que editas al publicar:** IDs de Google, correo, WhatsApp |
| `tracking.js` | Cookies, Consent Mode, gclid/UTM y conversiones |
| `contact.php` | Envía el correo de cada solicitud (líneas `$TO` y `$FROM` al principio) |
| `.htaccess` | HTTPS, redirecciones 301 de las URLs antiguas, caché |
| `gracias/` | Página de solicitud enviada (aquí se mide la conversión) |
| `aviso-legal/`, `ley-proteccion-datos/`, `aviso-ley-cookies/`, `condiciones/` | Textos legales actualizados (RGPD, LOPDGDD, LSSI-CE, TRLGDCU). Datos de la empresa en `config.js` |
| `assets/fonts/` | Tipografías alojadas en la web (sin llamadas a Google) |
| `legal.js` | Rellena CIF, domicilio, etc. en las páginas legales desde `config.js` |
| `scripts/check-legal.mjs` | `npm run check:legal`: avisa de datos legales que faltan |
| `robots.txt`, `sitemap.xml` | SEO |
