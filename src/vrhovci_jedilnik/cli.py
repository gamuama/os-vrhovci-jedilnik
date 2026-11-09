import argparse, sys
from pathlib import Path
from .config import load_config
from .domoticz import publish_menu
from .io import atomic_write_json
from .parser import parse_menu
from .pdf import pdf_to_text
from .updater import update_from_web

def build_parser():
    p=argparse.ArgumentParser(description="PDF jedilnik OŠ Vrhovci v JSON in Domoticz")
    p.add_argument("pdf",nargs="?",type=Path)
    p.add_argument("--output","-o",type=Path,default=Path("data/jedilnik.json"))
    p.add_argument("--pdf-output",type=Path,default=Path("data/jedilnik.pdf"))
    p.add_argument("--text-output",type=Path)
    p.add_argument("--config",type=Path,default=Path("config.json"))
    p.add_argument("--force",action="store_true")
    p.add_argument("--no-domoticz",action="store_true")
    p.add_argument("--verbose","-v",action="store_true")
    return p

def main(argv=None):
    a=build_parser().parse_args(argv)
    try:
        if a.pdf is None:
            update_from_web(a.output,a.pdf_output,a.text_output,a.force,verbose=a.verbose)
        else:
            text=pdf_to_text(a.pdf)
            if a.text_output:
                a.text_output.parent.mkdir(parents=True,exist_ok=True); a.text_output.write_text(text,encoding="utf-8")
            result=parse_menu(text); result["source_file"]=a.pdf.name; atomic_write_json(result,a.output)
            print(f"OK: {a.output}")
        if not a.no_domoticz: publish_menu(a.output,load_config(a.config),verbose=a.verbose)
        return 0
    except Exception as exc:
        print(f"NAPAKA: {exc}",file=sys.stderr); return 1
