# OŠ Vrhovci jedilnik

Python parser in samodejni updater tedenskega jedilnika OŠ Vrhovci.

## v0.2.0

Privzeti spletni način:

```bash
PYTHONPATH=src python3 -m vrhovci_jedilnik --verbose
```

Obnašanje:

- ponedeljek-petek: išče PDF za trenutni teden,
- sobota-nedelja: išče PDF za naslednji teden,
- če `data/jedilnik.json` že vsebuje vseh 5 dni ciljnega tedna, izpiše `SKIP` in ne prenaša ničesar,
- `--force` ta pregled obide in prisilno ponovno prenese ter obdela PDF.

Prisilna osvežitev:

```bash
PYTHONPATH=src python3 -m vrhovci_jedilnik --force --verbose
```

Diagnostika:

```bash
PYTHONPATH=src python3 -m vrhovci_jedilnik \
  --text-output ./data/jedilnik.txt \
  --verbose
```

Lokalni PDF način iz v0.1.x je še vedno podprt:

```bash
PYTHONPATH=src python3 -m vrhovci_jedilnik ./2.tedenOBJAVA.pdf \
  --output ./data/jedilnik.json \
  --verbose
```

## Zahteve

- Python 3.9+
- `pdftotext` iz paketa `poppler-utils`

## Cron

Vsak dan ob 06:15:

```cron
15 6 * * * cd /home/pi/domoticz/plugins/os-vrhovci-jedilnik && /usr/bin/env PYTHONPATH=src /usr/bin/python3 -m vrhovci_jedilnik >> data/update.log 2>&1
```

Cron lahko teče vsak dan. Če JSON že vsebuje ciljni teden, updater konča brez spremembe.

## Testi

```bash
python3 -m unittest discover -s tests -v
```

## v0.3.0 Domoticz
```bash
cp config.example.json config.json
nano config.json
PYTHONPATH=src python3 -m vrhovci_jedilnik --force --verbose
```
Za test brez objave uporabi `--no-domoticz`.
