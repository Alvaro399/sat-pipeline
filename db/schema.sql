-- Esquema de base de datos para Sat-Pipeline
-- Requiere PostgreSQL con la extension PostGIS activada

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE imagenes_procesadas (
    id SERIAL PRIMARY KEY,
    nombre_producto TEXT NOT NULL,
    fecha_captura TIMESTAMP NOT NULL,
    latitud DOUBLE PRECISION NOT NULL,
    longitud DOUBLE PRECISION NOT NULL,
    ndvi_promedio DOUBLE PRECISION,
    ndvi_maximo DOUBLE PRECISION,
    ndvi_minimo DOUBLE PRECISION,
    ruta_color_real TEXT,
    ruta_ndvi TEXT,
    fecha_procesado TIMESTAMP DEFAULT NOW(),
    geom GEOMETRY(Point, 4326)
);
