from __future__ import annotations

import re
import unicodedata
from datetime import date
from typing import Dict, Any, Tuple

DAY_NAMES = {
    "PONEDELJEK": "ponedeljek",
    "TOREK": "torek",
    "SREDA": "sreda",
    "CETRTEK": "cetrtek",
    "PETEK": "petek",
}

DAY_PATTERN = re.compile(
    r"\b(PONEDELJEK|TOREK|SREDA|ČETRTEK|CETRTEK|PETEK)\b\s+"
    r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})",
    re.IGNORECASE,
)

MEAL_PATTERN = re.compile(
    r"\b(MALICA|KOSILO|P\.?\s*MALICA)\b",
    re.IGNORECASE,
)

WEEK_PATTERN = re.compile(
    r"JEDILNIK\s+(\d{1,2})\.\s*[–-]\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})",
    re.IGNORECASE,
)


def ascii_upper(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(c for c in normalized if not unicodedata.combining(c)).upper()


def clean_text(value: str) -> str:
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\s*\n\s*", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" ,")


def iso_date(day: str, month: str, year: str) -> str:
    return date(int(year), int(month), int(day)).isoformat()


def parse_week(text: str) -> Tuple[str, str]:
    match = WEEK_PATTERN.search(text)
    if not match:
        raise ValueError("V PDF-ju ni mogoče prepoznati obdobja jedilnika.")
    start_day, end_day, month, year = match.groups()
    return iso_date(start_day, month, year), iso_date(end_day, month, year)


def meal_key(label: str) -> str:
    normalized = ascii_upper(re.sub(r"\s+", "", label).replace(".", ""))
    if normalized == "MALICA":
        return "dop_malica"
    if normalized == "KOSILO":
        return "kosilo"
    if normalized == "PMALICA":
        return "pop_malica"
    raise ValueError(f"Neznana oznaka obroka: {label}")


def parse_day_block(block: str) -> Dict[str, str]:
    matches = list(MEAL_PATTERN.finditer(block))
    result = {"dop_malica": "", "kosilo": "", "pop_malica": ""}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        result[meal_key(match.group(1))] = clean_text(block[start:end])
    missing = [key for key, value in result.items() if not value]
    if missing:
        raise ValueError("Manjkajo obroki: " + ", ".join(missing))
    return result


def parse_menu(text: str) -> Dict[str, Any]:
    week_from, week_to = parse_week(text)
    day_matches = list(DAY_PATTERN.finditer(text))
    if not day_matches:
        raise ValueError("V PDF-ju ni mogoče najti dnevov.")

    days: Dict[str, Dict[str, str]] = {}
    for index, match in enumerate(day_matches):
        raw_day, day, month, year = match.groups()
        normalized_day = DAY_NAMES[ascii_upper(raw_day)]
        block_start = match.end()
        block_end = day_matches[index + 1].start() if index + 1 < len(day_matches) else len(text)
        block = text[block_start:block_end]
        # Opombe in naslednje strani ne smejo postati del petkove popoldanske malice.
        block = re.split(r"\bOpombe\s*:", block, maxsplit=1, flags=re.IGNORECASE)[0]
        meals = parse_day_block(block)
        days[normalized_day] = {
            "date": iso_date(day, month, year),
            **meals,
        }

    expected = set(DAY_NAMES.values())
    missing_days = sorted(expected.difference(days))
    if missing_days:
        raise ValueError("Manjkajo dnevi: " + ", ".join(missing_days))

    return {
        "school": "OŠ Vrhovci",
        "week_from": week_from,
        "week_to": week_to,
        "days": days,
    }
