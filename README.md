# OŠ Vrhovci jedilnik

Majhen Python projekt, ki iz tedenskega PDF jedilnika OŠ Vrhovci izdela strukturiran JSON.

## Kaj naredi

- prebere lokalni PDF,
- za pretvorbo uporabi `pdftotext -layout`,
- prepozna obdobje tedna in dneve od ponedeljka do petka,
- za vsak dan izloči dopoldansko malico, kosilo in popoldansko malico,
- rezultat varno zapiše v JSON prek začasne datoteke in atomskega `os.replace`,
- ob napaki ne prepiše zadnjega veljavnega JSON-a.

## Zahteve

- Python 3.9 ali novejši
- paket `poppler-utils`, ki vsebuje `pdftotext`

Raspberry Pi OS / Debian:

```bash
sudo apt update
sudo apt install -y python3 poppler-utils
```

## Namestitev

```bash
git clone git@github.com:TVOJ_GITHUB_USERNAME/os-vrhovci-jedilnik.git
cd os-vrhovci-jedilnik
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Uporaba

PDF kopiraj v projekt, nato zaženi:

```bash
vrhovci-jedilnik ./2.tedenOBJAVA.pdf --output ./data/jedilnik.json
```

Ali brez namestitve paketa:

```bash
PYTHONPATH=src python3 -m vrhovci_jedilnik ./2.tedenOBJAVA.pdf --output ./data/jedilnik.json
```

Za diagnostični izpis pretvorjenega besedila:

```bash
vrhovci-jedilnik ./2.tedenOBJAVA.pdf \
  --output ./data/jedilnik.json \
  --text-output ./data/jedilnik.txt \
  --verbose
```

## Preverjanje JSON-a

```bash
python3 -m json.tool data/jedilnik.json
```

## Testi

```bash
python3 -m unittest discover -s tests -v
```

## Predlagana lokacija na Pi

```text
/home/pi/domoticz/plugins/os-vrhovci-jedilnik/
```

## Primer cron opravila

Primer vsak dan ob 06:15. Pot do PDF-ja je za prvo verzijo lokalna in jo pozneje lahko zamenjamo z avtomatskim prenosom aktualnega PDF-ja.

```cron
15 6 * * * cd /home/pi/domoticz/plugins/os-vrhovci-jedilnik && /usr/bin/python3 -m vrhovci_jedilnik ./2.tedenOBJAVA.pdf --output ./data/jedilnik.json >> ./data/update.log 2>&1
```

## Naslednja faza

- odkrivanje aktualnega PDF-ja na strani OŠ Vrhovci,
- varen prenos samo ob spremembi,
- opcijsko posodabljanje Domoticz Text senzorjev za danes in jutri.
