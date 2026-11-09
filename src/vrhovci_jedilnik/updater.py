from __future__ import annotations

import html
import json
import re
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urljoin

from .io import atomic_write_json
from .parser import parse_menu
from .pdf import pdf_to_text

MENU_PAGE = "https://www.os-vrhovci.si/jedilniki/"
PDF_LINK_RE = re.compile(r"href=[\"']([^\"']+\.pdf(?:\?[^\"']*)?)[\"']", re.I)
RANGE_RE = re.compile(r"(\d{1,2})\.\s*[-–]\s*(\d{1,2})\.")


def target_date(today: date) -> date:
    """Med tednom išči trenutni teden; v soboto/nedeljo naslednji teden."""
    if today.weekday() == 5:  # sobota -> ponedeljek +2
        return today + timedelta(days=2)
    if today.weekday() == 6:  # nedelja -> ponedeljek +1
        return today + timedelta(days=1)
    return today


def target_week_bounds(today: date) -> Tuple[date, date]:
    target = target_date(today)
    monday = target - timedelta(days=target.weekday())
    return monday, monday + timedelta(days=4)


def existing_json_has_target_week(path: Path, today: date) -> bool:
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        monday, friday = target_week_bounds(today)
        return (
            data.get("week_from") == monday.isoformat()
            and data.get("week_to") == friday.isoformat()
            and isinstance(data.get("days"), dict)
            and len(data["days"]) >= 5
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False


def fetch_text(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "os-vrhovci-jedilnik/0.2.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def download_file(url: str, destination: Path, timeout: int = 30) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(destination.suffix + ".tmp")
    request = urllib.request.Request(url, headers={"User-Agent": "os-vrhovci-jedilnik/0.2.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, temp.open("wb") as handle:
            handle.write(response.read())
        temp.replace(destination)
    finally:
        if temp.exists():
            temp.unlink()


def _strip_tags(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", value))


def find_pdf_for_target_week(page_html: str, page_url: str, today: date) -> str:
    """Poišče PDF link za ciljni ponedeljek-petek. Datum je lahko besedilo povezave."""
    monday, friday = target_week_bounds(today)
    for match in PDF_LINK_RE.finditer(page_html):
        href = html.unescape(match.group(1))
        # Najprej preglej besedilo same povezave, nato še omejeno okolico.
        close = page_html.find("</a>", match.end())
        own_html = page_html[match.end(): close if close != -1 else match.end() + 120]
        contexts = [_strip_tags(own_html), _strip_tags(page_html[max(0, match.start() - 120): match.end() + 180])]
        for context in contexts:
            for start_day, end_day in RANGE_RE.findall(context):
                if int(start_day) == monday.day and int(end_day) == friday.day:
                    return urljoin(page_url, href)
    raise RuntimeError(
        f"Na strani ni PDF-ja za ciljni teden {monday.isoformat()} do {friday.isoformat()}."
    )


def update_from_web(output: Path, pdf_path: Path, text_output: Optional[Path], force: bool = False,
                    today: Optional[date] = None, page_url: str = MENU_PAGE, verbose: bool = False) -> bool:
    today = today or date.today()
    monday, friday = target_week_bounds(today)

    if not force and existing_json_has_target_week(output, today):
        print(f"SKIP: {output} že vsebuje podatke za {monday.isoformat()} do {friday.isoformat()}.")
        return False

    page = fetch_text(page_url)
    pdf_url = find_pdf_for_target_week(page, page_url, today)
    if verbose:
        print(f"Ciljni teden: {monday.isoformat()} do {friday.isoformat()}")
        print(f"PDF: {pdf_url}")

    download_file(pdf_url, pdf_path)
    text = pdf_to_text(pdf_path)
    result = parse_menu(text)
    if result["week_from"] != monday.isoformat() or result["week_to"] != friday.isoformat():
        raise RuntimeError(
            f"Preneseni PDF vsebuje napačen teden: {result['week_from']} do {result['week_to']}."
        )

    if text_output:
        text_output.parent.mkdir(parents=True, exist_ok=True)
        text_output.write_text(text, encoding="utf-8")

    result["source_file"] = pdf_path.name
    result["source_url"] = pdf_url
    atomic_write_json(result, output)
    print(f"OK: {output}")
    return True
