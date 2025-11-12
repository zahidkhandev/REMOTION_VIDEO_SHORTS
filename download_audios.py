import os
import requests

# Mapping of sound_effect names to Mixkit direct downloadable WAV URLs
sound_effect_urls = {
    "soft_swoosh": "https://assets.mixkit.co/active_storage/sfx/1491/1491.wav",
    "quick_whoosh": "https://assets.mixkit.co/active_storage/sfx/39/39.wav",
    "slide_in": "https://assets.mixkit.co/active_storage/sfx/1530/1530.wav",
    "pop_in": "https://assets.mixkit.co/active_storage/sfx/2354/2354.wav",
    "gentle_transition": "https://assets.mixkit.co/active_storage/sfx/166/166.wav",
    # "tech_beep": "https://assets.mixkit.co/active_storage/sfx/1374/1374.wav",
    "digital_pulse": "https://assets.mixkit.co/active_storage/sfx/490/490.wav",
    "cyber_click": "https://assets.mixkit.co/active_storage/sfx/1133/1133.wav",
    "circuit_buzz": "https://assets.mixkit.co/active_storage/sfx/950/950.wav",
    "data_stream": "https://assets.mixkit.co/active_storage/sfx/1317/1317.wav",
    "success_chime": "https://assets.mixkit.co/active_storage/sfx/3109/3109.wav",
    "completion_bell": "https://assets.mixkit.co/active_storage/sfx/600/600.wav",
    "achievement_ding": "https://assets.mixkit.co/active_storage/sfx/560/560.wav",
    # "victory_tone": "https://assets.mixkit.co/active_storage/sfx/560/560.wav",
    # "attention_ping": "https://assets.mixkit.co/active_storage/sfx/2341/2341.wav",
    # "focus_tone": "https://assets.mixkit.co/active_storage/sfx/1757/1757.wav",
    # "alert_soft": "https://assets.mixkit.co/active_storage/sfx/458/458.wav",
    "notification_subtle": "https://assets.mixkit.co/active_storage/sfx/2870/2870.wav",
    # "soft_ambient": "https://assets.mixkit.co/active_storage/sfx/2277/2277.wav",
    # "gentle_hum": "https://assets.mixkit.co/active_storage/sfx/478/478.wav",
    # "quiet_atmosphere": "https://assets.mixkit.co/active_storage/sfx/1939/1939.wav",
    "spark_zap": "https://assets.mixkit.co/active_storage/sfx/866/866.wav",
    "bubble_pop": "https://assets.mixkit.co/active_storage/sfx/1317/1317.wav",
    # "discovery_twinkle": "https://assets.mixkit.co/active_storage/sfx/2104/2104.wav",
    # "science_pulse": "https://assets.mixkit.co/active_storage/sfx/2409/2409.wav",
}

DOWNLOAD_FOLDER = "sounds"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

for sound_name, url in sound_effect_urls.items():
    local_path = os.path.join(DOWNLOAD_FOLDER, f"{sound_name}.wav")
    print(f"Downloading '{sound_name}' from {url}...")
    try:
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Saved '{sound_name}' to {local_path}")
    except Exception as e:
        print(f"Failed to download '{sound_name}': {e}")

print("All downloads attempted.")
