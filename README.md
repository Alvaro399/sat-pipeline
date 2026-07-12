# Sat-Pipeline

Pipeline propio de ingesta, procesamiento y visualizacion de imagenes satelitales Sentinel-2 (ESA / Copernicus), desplegado sobre una arquitectura de microservicios en contenedores LXC (Proxmox).

## Arquitectura

Copernicus (ESA)
  -> ingestor: descarga bandas espectrales selectivas (B02, B03, B04, B08)
  -> procesador: calcula NDVI y genera imagen en color real (via HTTP)
  -> sat-db: almacena metadatos + geometria en PostgreSQL/PostGIS
  -> dashboard: visualiza resultados en un mapa interactivo

Cada componente corre en su propio contenedor, se comunica por red interna, y tiene una unica responsabilidad.

## Componentes

- **ingestor**: se autentica contra la API de Copernicus Data Space, busca la imagen Sentinel-2 mas reciente para una zona dada, descarga solo las bandas necesarias (evitando bajar el producto .SAFE completo, de ~1.2GB) y las envia al procesador.
- **procesador**: recibe las bandas, calcula el indice de vegetacion NDVI y una imagen en color real, y guarda los metadatos en la base de datos.
- **db**: PostgreSQL + PostGIS, almacena metadatos geoespaciales de cada pasada procesada.
- **dashboard**: aplicacion Flask que muestra un mapa interactivo y el registro de pasadas procesadas con sus estadisticas NDVI.

## Stack

Python, Flask, rasterio, numpy, PostgreSQL/PostGIS, Leaflet.js, Proxmox (LXC).

## Instalacion

Cada carpeta tiene su propio requirements.txt y .env.example. Copia .env.example a .env en cada servicio y rellena tus credenciales antes de ejecutar.

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

El esquema de base de datos esta en db/schema.sql.

## Motivacion

Proyecto realizado para practicar arquitectura de microservicios aplicada a datos de observacion terrestre, combinando administracion de sistemas (Proxmox, LXC, redes internas) con procesamiento de datos geoespaciales reales.
