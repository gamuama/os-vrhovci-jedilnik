import base64, json, urllib.parse, urllib.request
from datetime import date, timedelta
from pathlib import Path

DAYS = {0:"ponedeljek",1:"torek",2:"sreda",3:"cetrtek",4:"petek"}

def next_school_date(today):
    d = today + timedelta(days=1)
    while d.weekday() >= 5: d += timedelta(days=1)
    return d

def day_data(menu, wanted):
    value = menu.get("days", {}).get(DAYS.get(wanted.weekday(), ""))
    return value if isinstance(value, dict) and value.get("date") == wanted.isoformat() else None

def format_day(day, display, unavailable):
    if not day: return unavailable
    sep = display.get("separator", "\n")
    return sep.join((
        f"{display.get('dop_malica','Dop. malica')}: {day.get('dop_malica','').strip()}",
        f"{display.get('kosilo','Kosilo')}: {day.get('kosilo','').strip()}",
        f"{display.get('pop_malica','Pop. malica')}: {day.get('pop_malica','').strip()}",
    ))

def update_sensor(cfg, idx, text):
    params = urllib.parse.urlencode({"type":"command","param":"udevice","idx":idx,"nvalue":0,"svalue":text})
    req = urllib.request.Request(f"{cfg['url']}/json.htm?{params}", headers={"User-Agent":"os-vrhovci-jedilnik/0.3.0"})
    if cfg.get("username"):
        token = base64.b64encode(f"{cfg['username']}:{cfg.get('password','')}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
    with urllib.request.urlopen(req, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))
    if str(result.get("status", "")).upper() != "OK":
        raise RuntimeError(f"Domoticz IDX {idx} ni bil posodobljen: {result}")

def publish_menu(path: Path, config, today=None, verbose=False):
    today = today or date.today()
    menu = json.loads(path.read_text(encoding="utf-8"))
    cfg, display = config["domoticz"], config.get("display", {})
    today_value = day_data(menu, today) if today.weekday() < 5 else None
    next_date = next_school_date(today)
    next_value = day_data(menu, next_date)
    text_today = format_day(today_value, display, display.get("ni_pouka", "Danes ni pouka."))
    text_next = format_day(next_value, display, display.get("ni_podatkov_jutri", "Jedilnik za naslednji šolski dan še ni objavljen."))
    update_sensor(cfg, cfg["idx_danes"], text_today)
    update_sensor(cfg, cfg["idx_jutri"], text_next)
    if verbose:
        print(f"Domoticz IDX {cfg['idx_danes']} posodobljen za danes.")
        print(f"Domoticz IDX {cfg['idx_jutri']} posodobljen za {next_date.isoformat()}.")
