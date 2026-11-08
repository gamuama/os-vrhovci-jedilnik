from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .io import atomic_write_json
from .parser import parse_menu
from .pdf import pdf_to_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pretvori PDF jedilnik OŠ Vrhovci v JSON."
    )
    parser.add_argument("pdf", type=Path, help="Pot do tedenskega PDF-ja")
    parser.add_argument(
        "--output", "-o", type=Path, default=Path("data/jedilnik.json"),
        help="Izhodni JSON (privzeto: data/jedilnik.json)",
    )
    parser.add_argument(
        "--text-output", type=Path,
        help="Opcijsko shrani tudi besedilo, pridobljeno s pdftotext",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = pdf_to_text(args.pdf)
        if args.text_output:
            args.text_output.parent.mkdir(parents=True, exist_ok=True)
            args.text_output.write_text(text, encoding="utf-8")
        result = parse_menu(text)
        result["source_file"] = args.pdf.name
        atomic_write_json(result, args.output)
        if args.verbose:
            print(f"Teden: {result['week_from']} do {result['week_to']}")
            print(f"Prebranih dni: {len(result['days'])}")
        print(f"OK: {args.output}")
        return 0
    except Exception as exc:
        print(f"NAPAKA: {exc}", file=sys.stderr)
        return 1
