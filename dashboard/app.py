import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template_string
import psycopg2
import json

app = Flask(__name__)

DB_CONFIG = {
    "host": "192.168.0.70",
    "dbname": "satpipeline",
    "user": "satuser",
    "password": os.getenv("DB_PASSWORD"),
    "port": 5432,
}

PROCESADOR_URL = "http://192.168.0.69:5000"

TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ground Station // Sat-Pipeline</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0d13;
    --panel: #10141d;
    --panel-2: #151b26;
    --border: #232c3d;
    --text: #e8e6df;
    --muted: #7c869b;
    --amber: #ffb400;
    --teal: #55d6c2;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif;
    line-height: 1.5;
  }
  .mono { font-family: 'IBM Plex Mono', monospace; }
  a { color: var(--teal); }
  .ticker-wrap {
    background: #000;
    border-bottom: 1px solid var(--border);
    overflow: hidden;
    white-space: nowrap;
    padding: 6px 0;
  }
  .ticker {
    display: inline-block;
    padding-left: 100%;
    animation: ticker-scroll 28s linear infinite;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.08em;
    color: var(--amber);
  }
  @keyframes ticker-scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-100%); }
  }
  @media (prefers-reduced-motion: reduce) {
    .ticker { animation: none; padding-left: 20px; }
  }
  header.hero {
    padding: 56px 24px 40px;
    max-width: 1180px;
    margin: 0 auto;
    border-bottom: 1px solid var(--border);
  }
  .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--teal);
    font-size: 13px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin: 0 0 14px;
  }
  h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: clamp(32px, 5vw, 54px);
    font-weight: 600;
    margin: 0 0 10px;
    letter-spacing: -0.01em;
  }
  .lead {
    color: var(--muted);
    font-size: 17px;
    max-width: 640px;
    margin: 0 0 36px;
  }
  .readout-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
  }
  .readout {
    background: var(--panel);
    padding: 20px;
  }
  .readout .label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 0 0 8px;
  }
  .readout .value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: var(--amber);
  }
  .readout .value.teal { color: var(--teal); }
  section { max-width: 1180px; margin: 0 auto; padding: 48px 24px; }
  .section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 0 24px;
  }
  .section-label::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border);
  }
  #map {
    height: 420px;
    width: 100%;
    border: 1px solid var(--border);
    filter: saturate(0.9);
  }
  .pass {
    border: 1px solid var(--border);
    background: var(--panel);
    margin-bottom: 28px;
  }
  .pass-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    background: var(--panel-2);
  }
  .pass-id {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 60%;
  }
  .pass-date {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--muted);
    white-space: nowrap;
  }
  .pass-body {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
  }
  .pass-img-wrap { position: relative; border-right: 1px solid var(--border); }
  .pass-img-wrap:last-child { border-right: none; }
  .pass-img-wrap img { display: block; width: 100%; height: 260px; object-fit: cover; }
  .pass-img-tag {
    position: absolute; top: 10px; left: 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; letter-spacing: 0.1em;
    background: rgba(0,0,0,0.6);
    color: var(--amber);
    padding: 3px 8px;
    text-transform: uppercase;
  }
  .pass-stats {
    display: flex;
    gap: 0;
    border-top: 1px solid var(--border);
  }
  .pass-stat {
    flex: 1;
    padding: 16px 20px;
    border-right: 1px solid var(--border);
  }
  .pass-stat:last-child { border-right: none; }
  .pass-stat .label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 8px;
  }
  .gauge {
    height: 6px;
    background: #232c3d;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 8px;
  }
  .gauge-fill { height: 100%; background: var(--teal); }
  .pass-stat .num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 18px;
    color: var(--text);
  }
  .coords {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--muted);
    font-size: 13px;
  }
  footer {
    max-width: 1180px;
    margin: 0 auto;
    padding: 40px 24px 60px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 13px;
  }
  footer .arch {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--muted);
    margin-top: 10px;
  }
  @media (max-width: 760px) {
    .pass-body { grid-template-columns: 1fr; }
    .pass-img-wrap { border-right: none; border-bottom: 1px solid var(--border); }
    .pass-stats { flex-direction: column; }
    .pass-stat { border-right: none; border-bottom: 1px solid var(--border); }
  }
</style>
</head>
<body>

<div class="ticker-wrap">
  <div class="ticker mono">
    GROUND STATION ONLINE &nbsp;&bull;&nbsp; COPERNICUS / SENTINEL-2 &nbsp;&bull;&nbsp; {{ total_pasadas }} PASADAS REGISTRADAS &nbsp;&bull;&nbsp; NDVI MEDIO {{ "%.3f"|format(ndvi_global) }} &nbsp;&bull;&nbsp; ULTIMA CAPTURA {{ ultima_fecha }} &nbsp;&bull;&nbsp;
  </div>
</div>
<header class="hero">
  <p class="eyebrow">// sat-pipeline ground station</p>
  <h1>Monitor de vegetacion<br>via observacion terrestre</h1>
  <p class="lead">Pipeline propio de ingesta, procesado y almacenamiento de imagenes Sentinel-2 (ESA / Copernicus). Cada pasada se descompone en bandas espectrales, se calcula el indice de vegetacion NDVI y se archiva junto a su huella geografica.</p>

  <div class="readout-grid">
    <div class="readout">
      <p class="label">Pasadas procesadas</p>
      <p class="value">{{ total_pasadas }}</p>
    </div>
    <div class="readout">
      <p class="label">NDVI medio</p>
      <p class="value teal">{{ "%.3f"|format(ndvi_global) }}</p>
    </div>
    <div class="readout">
      <p class="label">Satelite</p>
      <p class="value" style="font-size:20px;">Sentinel-2</p>
    </div>
    <div class="readout">
      <p class="label">Ultima captura</p>
      <p class="value" style="font-size:18px;">{{ ultima_fecha }}</p>
    </div>
  </div>
</header>

<section>
  <p class="section-label">Geolocalizacion de pasadas</p>
  <div id="map"></div>
</section>

<section>
  <p class="section-label">Registro de pasadas</p>

  {% for img in imagenes %}
  <div class="pass">
    <div class="pass-head">
      <span class="pass-id mono" title="{{ img.nombre_producto }}">{{ img.nombre_producto }}</span>
      <span class="pass-date">{{ img.fecha_captura }}</span>
    </div>
    <div class="pass-body">
      <div class="pass-img-wrap">
        <span class="pass-img-tag">RGB / color real</span>
        <img src="{{ procesador_url }}/images/{{ img.ruta_color_real.split('/')[-1] }}" alt="Color real" loading="lazy">
      </div>
      <div class="pass-img-wrap">
        <span class="pass-img-tag">NDVI</span>
        <img src="{{ procesador_url }}/images/{{ img.ruta_ndvi.split('/')[-1] }}" alt="NDVI" loading="lazy">
      </div>
    </div>
    <div class="pass-stats">
      <div class="pass-stat">
        <p class="label">Coordenadas</p>
        <p class="coords">{{ "%.4f"|format(img.latitud) }}, {{ "%.4f"|format(img.longitud) }}</p>
      </div>
      <div class="pass-stat">
        <p class="label">NDVI promedio</p>
        <div class="gauge"><div class="gauge-fill" style="width: {{ ((img.ndvi_promedio + 1) / 2 * 100)|round(1) }}%;"></div></div>
        <p class="num">{{ "%.3f"|format(img.ndvi_promedio) }}</p>
      </div>
      <div class="pass-stat">
        <p class="label">Rango NDVI</p>
        <p class="num">{{ "%.2f"|format(img.ndvi_minimo) }} &ndash; {{ "%.2f"|format(img.ndvi_maximo) }}</p>
      </div>
    </div>
  </div>
  {% endfor %}
</section>

<footer>
  <p>Sat-Pipeline &mdash; estacion de procesamiento de imagenes satelitales autohospedada sobre Proxmox.</p>
  <p class="arch">ingestor &rarr; procesador &rarr; postgres/postgis &rarr; dashboard</p>
</footer>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  var map = L.map('map', { scrollWheelZoom: false }).setView([{{ centro_lat }}, {{ centro_lon }}], 11);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: 'CARTO / OpenStreetMap',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map);

  var puntos = {{ puntos_json|safe }};
  puntos.forEach(function(p) {
    L.circleMarker([p.lat, p.lon], {
      radius: 8, color: '#ffb400', fillColor: '#ffb400', fillOpacity: 0.6, weight: 1
    }).addTo(map).bindPopup('<b>' + p.nombre + '</b><br>NDVI: ' + p.ndvi.toFixed(3));
  });
</script>
</body>
</html>
"""


def obtener_imagenes():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT nombre_producto, fecha_captura, latitud, longitud,
               ndvi_promedio, ndvi_maximo, ndvi_minimo,
               ruta_color_real, ruta_ndvi
        FROM imagenes_procesadas
        ORDER BY fecha_captura DESC
    """)
    columnas = [desc[0] for desc in cur.description]
    filas = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(zip(columnas, fila)) for fila in filas]


@app.route("/")
def index():
    imagenes = obtener_imagenes()

    if imagenes:
        centro_lat = imagenes[0]["latitud"]
        centro_lon = imagenes[0]["longitud"]
        ndvi_global = sum(i["ndvi_promedio"] for i in imagenes) / len(imagenes)
        ultima_fecha = str(imagenes[0]["fecha_captura"])
    else:
        centro_lat, centro_lon = 38.2669, -0.6987
        ndvi_global = 0.0
        ultima_fecha = "N/A"

    puntos = [
        {"lat": img["latitud"], "lon": img["longitud"],
         "nombre": img["nombre_producto"], "ndvi": img["ndvi_promedio"]}
        for img in imagenes
    ]

    return render_template_string(
        TEMPLATE,
        imagenes=imagenes,
        procesador_url=PROCESADOR_URL,
        centro_lat=centro_lat,
        centro_lon=centro_lon,
        puntos_json=json.dumps(puntos),
        total_pasadas=len(imagenes),
        ndvi_global=ndvi_global,
        ultima_fecha=ultima_fecha,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
