import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "notification_mode": "cli",
    "cpu_threshold_percent": 85.0,
    "ram_threshold_percent": 85.0,
    "disk_threshold_percent": 90.0,
    "top_process_count": 5,
    "telegram_chat_id": "",
    "telegram_token": ""
}

def validate_config(config_data):
    validated = DEFAULT_CONFIG.copy()
    errors = []

    def parse_percent(key, default_val):
        try:
            val = float(config_data.get(key, default_val))
            if val < 0.0 or val > 100.0:
                clamped_val = max(0.0, min(100.0, val))
                errors.append(f"Nilai {key} ({val}) di luar batas 0-100. Dikoreksi menjadi: {clamped_val}")
                return clamped_val
            return val
        except (ValueError, TypeError):
            errors.append(f"Invalid format untuk {key}. Menggunakan default: {default_val}")
            return default_val

    validated["cpu_threshold_percent"] = parse_percent("cpu_threshold_percent", 85.0)
    validated["ram_threshold_percent"] = parse_percent("ram_threshold_percent", 85.0)
    validated["disk_threshold_percent"] = parse_percent("disk_threshold_percent", 90.0)

    try:
        validated["top_process_count"] = max(1, int(config_data.get("top_process_count", 5)))
    except (ValueError, TypeError):
        errors.append("Invalid format untuk top_process_count. Menggunakan default: 5")
        validated["top_process_count"] = 5

    mode = str(config_data.get("notification_mode", "")).lower()
    if mode in ["cli", "telegram", "both"]:
        validated["notification_mode"] = mode
    else:
        errors.append(f"Notification mode '{mode}' tidak valid. Fallback ke 'cli'.")
        validated["notification_mode"] = "cli"

    validated["telegram_chat_id"] = str(config_data.get("telegram_chat_id", ""))
    validated["telegram_token"] = str(config_data.get("telegram_token", ""))

    return validated, errors

def load_config(config_path=None):
    config = DEFAULT_CONFIG.copy()
    load_errors = []

    if not config_path:
        # Resolve path to project_root/config/config.json
        base_dir = Path(__file__).resolve().parent.parent
        path = base_dir / "config" / "config.json"
    else:
        path = Path(config_path)

    if path.exists():
        try:
            with open(path, 'r') as file:
                external_config = json.load(file)
                config.update(external_config)
        except json.JSONDecodeError as e:
            load_errors.append(f"Format JSON tidak valid di {path}: {e}. Fallback ke default.")
        except Exception as e:
            load_errors.append(f"Gagal membaca {path}: {e}. Fallback ke default.")
    else:
        load_errors.append(f"File konfigurasi {path} tidak ditemukan. Fallback ke default.")

    config["telegram_token"] = os.getenv("TELEGRAM_TOKEN", config["telegram_token"])

    final_config, val_errors = validate_config(config)
    load_errors.extend(val_errors)

    return final_config, load_errors

