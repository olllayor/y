from flask import Flask, request, render_template, jsonify, send_file
from downloader import download_media
import requests
import os
import uuid

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    video_quality = request.form.get("video_quality", "1080")
    audio_format = request.form.get("audio_format", "mp3")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    result = download_media(url, video_quality, audio_format)
    if result["status"] == "success":
        return render_template(
            "player.html",
            download_url=result["download_url"],
            filename=result["filename"],
        )
    elif result["status"] == "picker":
        return jsonify({"picker": result["picker"]})
    else:
        return jsonify({"error": result["error"]}), 500


@app.route("/download_file/<filename>", methods=["GET"])
def download_file(filename):
    # get temporary file name
    temp_file = f"{str(uuid.uuid4())}.mp4"
    try:
        # Get the download url
        url = request.args.get("download_url")
        if not url:
            return jsonify({"error": "Download URL is missing"}), 400
        # download the file to the local server using request
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Ensure the request was successful
        with open(temp_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return send_file(
            temp_file,
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    app.run(debug=True)
