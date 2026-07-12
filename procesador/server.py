from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.expanduser("~/sat-pipeline/procesador/recibidos")
RESULTS_FOLDER = os.path.expanduser("~/sat-pipeline/procesador/resultados")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No se envio ningun archivo"}), 400
    file = request.files["file"]
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    print(f"Archivo recibido: {filename} ({os.path.getsize(filepath)} bytes)")
    return jsonify({"status": "ok", "filename": filename}), 200


@app.route("/images/<path:filename>")
def get_image(filename):
    return send_from_directory(RESULTS_FOLDER, filename)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "alive"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
