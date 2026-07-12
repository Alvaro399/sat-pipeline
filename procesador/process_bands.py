import os
from dotenv import load_dotenv
load_dotenv()
import rasterio
import numpy as np
from PIL import Image
import gc
import psycopg2
from datetime import datetime

RECIBIDOS = os.path.expanduser("~/sat-pipeline/procesador/recibidos")
RESULTADOS = os.path.expanduser("~/sat-pipeline/procesador/resultados")
os.makedirs(RESULTADOS, exist_ok=True)

DB_CONFIG = {
    "host": "192.168.0.70",
    "dbname": "satpipeline",
    "user": "satuser",
    "password": os.getenv("DB_PASSWORD"),
    "port": 5432,
}

NOMBRE_PRODUCTO = "S2C_MSIL2A_20260708T104621_N0512_R051_T30SXH_20260708T141014"
FECHA_CAPTURA = datetime(2026, 7, 8, 10, 46, 21)
LATITUD = 38.2669
LONGITUD = -0.6987


def leer_banda_normalizada(nombre):
    path = os.path.join(RECIBIDOS, f"{nombre}.jp2")
    with rasterio.open(path) as src:
        banda = src.read(
            1,
            out_shape=(src.height // 2, src.width // 2),
            resampling=rasterio.enums.Resampling.average
        ).astype(np.float32)
    minimo, maximo = np.percentile(banda, (2, 98))
    banda = np.clip((banda - minimo) / (maximo - minimo + 1e-6) * 255, 0, 255).astype(np.uint8)
    gc.collect()
    return banda


def leer_banda_raw(nombre):
    path = os.path.join(RECIBIDOS, f"{nombre}.jp2")
    with rasterio.open(path) as src:
        banda = src.read(
            1,
            out_shape=(src.height // 2, src.width // 2),
            resampling=rasterio.enums.Resampling.average
        ).astype(np.float32)
    return banda


def generar_color_real():
    print("Generando imagen de color real (RGB)...")
    r = leer_banda_normalizada("B04")
    g = leer_banda_normalizada("B03")
    b = leer_banda_normalizada("B02")
    rgb = np.dstack((r, g, b))
    del r, g, b
    gc.collect()
    img = Image.fromarray(rgb, mode="RGB")
    out_path = os.path.join(RESULTADOS, "color_real.png")
    img.save(out_path)
    print(f"Guardado: {out_path}")
    del rgb, img
    gc.collect()
    return out_path


def generar_ndvi():
    print("Calculando NDVI...")
    red = leer_banda_raw("B04")
    nir = leer_banda_raw("B08")
    ndvi = (nir - red) / (nir + red + 1e-6)
    ndvi = np.clip(ndvi, -1, 1)
    del red, nir
    gc.collect()
    ndvi_norm = ((ndvi + 1) / 2 * 255).astype(np.uint8)
    try:
        import matplotlib.cm as cm
        colored = (cm.RdYlGn(ndvi_norm / 255.0)[:, :, :3] * 255).astype(np.uint8)
        img = Image.fromarray(colored, mode="RGB")
    except ImportError:
        img = Image.fromarray(ndvi_norm, mode="L")
    out_path = os.path.join(RESULTADOS, "ndvi.png")
    img.save(out_path)
    stats = {
        "promedio": float(ndvi.mean()),
        "maximo": float(ndvi.max()),
        "minimo": float(ndvi.min()),
    }
    print(f"Guardado: {out_path}")
    print(f"NDVI promedio: {stats['promedio']:.3f}")
    return out_path, stats


def guardar_en_db(ruta_color, ruta_ndvi, stats):
    print("Guardando metadatos en la base de datos...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO imagenes_procesadas
        (nombre_producto, fecha_captura, latitud, longitud,
         ndvi_promedio, ndvi_maximo, ndvi_minimo,
         ruta_color_real, ruta_ndvi, geom)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326))
    """, (
        NOMBRE_PRODUCTO, FECHA_CAPTURA, LATITUD, LONGITUD,
        stats["promedio"], stats["maximo"], stats["minimo"],
        ruta_color, ruta_ndvi, LONGITUD, LATITUD
    ))
    conn.commit()
    cur.close()
    conn.close()
    print("Guardado correctamente en la base de datos.")


if __name__ == "__main__":
    ruta_color = generar_color_real()
    gc.collect()
    ruta_ndvi, stats = generar_ndvi()
    guardar_en_db(ruta_color, ruta_ndvi, stats)
    print("\nProcesamiento completado.")
