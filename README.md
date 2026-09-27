# ROLE FIGZ · Circuiti in Scala

Tienda de maquetas a escala de los 23 circuitos del calendario 2026 de Fórmula 1.

Sitio estático (HTML, CSS y JavaScript en `index.html`), publicado con GitHub Pages.

## Pedidos

Los pedidos se envían por email a través de [FormSubmit](https://formsubmit.co). El primer pedido dispara un email de activación a la dirección de destino, y hay que confirmarlo una vez para que empiecen a llegar.

## Fotos de producto

La ficha de cada circuito muestra `circuiti/<circuito>.webp` si existe; si no, muestra el trazado animado.

1. Guarda la foto con fondo verde croma como `circuiti/<circuito>.jpeg` (por ejemplo `circuiti/silverstone.jpeg`).
2. Ejecuta `python herramientas/recortar_fondo.py` (requiere `pip install pillow numpy`). El script recorta el fondo, genera el `.webp` y actualiza la lista `PHOTOS` de `index.html`.
3. Haz commit y push.

Nombres válidos: melbourne, shanghai, suzuka, sakhir, jeddah, miami, montreal, monaco, barcelona, spielberg, silverstone, spa, hungaroring, zandvoort, monza, madrid, baku, austin, mexico-city, interlagos, las-vegas, lusail, yas-marina.

## Créditos

Trazados de los circuitos basados en [julesr0y/f1-circuits-svg](https://github.com/julesr0y/f1-circuits-svg) (CC BY 4.0).

Maquetas de colección independientes, no afiliadas a Formula 1 ni a equipos oficiales.
