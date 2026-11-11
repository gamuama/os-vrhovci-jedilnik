import json
from pathlib import Path

def load_config(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Konfiguracija ne obstaja: {path}. Kopiraj config.example.json v config.json.")
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg = data.get("domoticz", {})
    url = str(cfg.get("url", "")).strip().rstrip("/")
    if not url or "DOMOTICZ-IP" in url:
        raise ValueError("V config.json nastavi pravi domoticz.url.")
    for key in ("idx_danes", "idx_jutri", "idx_teden"):
        try: cfg[key] = int(cfg[key])
        except (KeyError, TypeError, ValueError): raise ValueError(f"Napačen domoticz.{key}.") from None
    cfg["url"] = url
    data["domoticz"] = cfg
    return data
