import os
import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

PROCESADOR_URL = "http://192.168.0.69:5000/upload"

BASE = (
    "https://download.dataspace.copernicus.eu/odata/v1/Products"
    "(4a1c4206-8577-49e2-be03-04c1cdf6ecee)"
    "/Nodes(S2C_MSIL2A_20260708T104621_N0512_R051_T30SXH_20260708T141014.SAFE)"
    "/Nodes(GRANULE)/Nodes(L2A_T30SXH_A009602_20260708T105954)"
    "/Nodes(IMG_DATA)/Nodes(R10m)"
)

BANDAS = {
    "B02": f"{BASE}/Nodes(T30SXH_20260708T104621_B02_10m.jp2)/$value",
    "B03": f"{BASE}/Nodes(T30SXH_20260708T104621_B03_10m.jp2)/$value",
    "B04": f"{BASE}/Nodes(T30SXH_20260708T104621_B04_10m.jp2)/$value",
    "B08": f"{BASE}/Nodes(T30SXH_20260708T104621_B08_10m.jp2)/$value",
}


def get_access_token():
    url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    data = {
        "client_id": "cdse-public",
        "username": os.getenv("COPERNICUS_USER"),
        "password": os.getenv("COPERNICUS_PASSWORD"),
        "grant_type": "password",
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def download_file(url, token, dest_path):
    headers = {"Authorization": f"Bearer {token}"}
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest_path, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, desc=os.path.basename(dest_path)
        ) as pbar:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                pbar.update(len(chunk))


def send_to_procesador(filepath, banda):
    print(f"Enviando banda {banda}...")
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f)}
        response = requests.post(PROCESADOR_URL, files=files)
    print(response.json())


if __name__ == "__main__":
    print("Autenticando...")
    token = get_access_token()

    dest_dir = os.path.expanduser("~/descargas_temp")
    os.makedirs(dest_dir, exist_ok=True)

    for banda, url in BANDAS.items():
        dest = os.path.join(dest_dir, f"{banda}.jp2")
        print(f"\n--- Banda {banda} ---")
        download_file(url, token, dest)
        send_to_procesador(dest, banda)
        os.remove(dest)
        print(f"{banda} enviada y eliminada localmente")

    print("\nProceso completado.")
