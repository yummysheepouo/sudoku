import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

def load_settings():
    defaults = {"bg_volume": 1.0, "sfx_volume": 1.0}
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
                bg = float(data.get("bg_volume", defaults["bg_volume"]))
                sfx = float(data.get("sfx_volume", defaults["sfx_volume"]))
                return {"bg_volume": max(0.0, min(1.0, bg)), "sfx_volume": max(0.0, min(1.0, sfx))}
    except Exception as e:
        print("Failed to load settings:", e)
    return defaults

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print("Failed to save settings:", e)