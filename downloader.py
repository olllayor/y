import requests
from decouple import config

# Define the base URL of your Cobalt API instance
COBALT_API_URL = config("API")


# Function to download content using the Cobalt API
def download_media(url, video_quality="1080", audio_format="mp3"):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "url": url,
        "videoQuality": video_quality,
        "audioFormat": audio_format,
    }
    try:
        response = requests.post(COBALT_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("status") in ["tunnel", "redirect"]:
            return {
                "status": "success",
                "download_url": data["url"],
                "filename": data["filename"],
            }
        elif data.get("status") == "picker":
            return {"status": "picker", "picker": data["picker"]}
        else:
            return {"status": "error", "error": data.get("error")}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}
