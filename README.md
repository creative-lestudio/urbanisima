# Grupo Urbanísima – Web

Landing estática (HTML + CSS + JS, sin dependencias ni build) orientada a conversión.

## Estructura

```
index.html   Contenido y estructura
styles.css   Estilos (colores en :root: --blue #01477f, --yellow #fec200)
main.js      Menú móvil, formularios → WhatsApp, contadores
assets/      Logo e imágenes
```

## Previsualizar en local

Necesitas Python 3 o Node.js. Desde la carpeta del proyecto:

```bash
npm start
```

o, sin Node:

```bash
python3 -m http.server 8080
```

Abre http://localhost:8080. Guarda cambios y recarga la página (Ctrl/Cmd+Shift+R).

Para ver la versión móvil: DevTools del navegador (F12) → icono de dispositivo móvil.
Para verla en tu teléfono real: con el ordenador y el móvil en la misma wifi, abre
`http://IP-DE-TU-ORDENADOR:8080`.

## Previsualizar online (GitHub Pages)

El workflow `.github/workflows/pages.yml` publica la web en cada push a la rama
`claude/intelligent-knuth-ugklb3` o `main`.

Activación (una sola vez): repositorio → Settings → Pages → Source: **GitHub Actions**.
La URL será `https://creative-lestudio.github.io/urbanisima/`.

## Publicación y Google Ads

Ver **[docs/GUIA-LANZAMIENTO.md](docs/GUIA-LANZAMIENTO.md)**: despliegue en SiteGround, formulario por correo, conversiones y rediseño de campañas.

## Pendiente de configurar

- Los formularios abren WhatsApp o envían correo mediante `contact.php` (requiere PHP: funciona en SiteGround; en la vista previa de GitHub Pages no hay PHP y se abre el programa de correo como plan B).
- IDs de Google Ads en `config.js` (ver la guía).
