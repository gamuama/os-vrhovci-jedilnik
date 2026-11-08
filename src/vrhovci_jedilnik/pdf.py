from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def pdf_to_text(pdf_path: Path) -> str:
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF ne obstaja: {pdf_path}")
    executable = shutil.which("pdftotext")
    if not executable:
        raise RuntimeError("Ukaz pdftotext ni nameščen. Namesti paket poppler-utils.")

    process = subprocess.run(
        [executable, "-layout", "-enc", "UTF-8", str(pdf_path), "-"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if process.returncode != 0:
        error = process.stderr.strip() or "neznana napaka"
        raise RuntimeError(f"pdftotext ni uspel: {error}")
    if not process.stdout.strip():
        raise RuntimeError("PDF ni vrnil besedila. Dokument je morda skeniran in zahteva OCR.")
    return process.stdout
