# Changelog

## 0.1.0 - 2026-11-08

- Prva različica lokalnega PDF parserja.
- Izvoz tedna, datumov in treh obrokov v JSON.
- Atomski zapis JSON-a in ohranitev starega rezultata ob napaki.
- Enotni testi na besedilu jedilnika za 9.-13. 11. 2026.

## 0.2.0 - 2026-11-09

- Samodejno iskanje aktualnega PDF-ja na strani OŠ Vrhovci.
- Od ponedeljka do petka išče jedilnik trenutnega tedna.
- V soboto in nedeljo išče jedilnik naslednjega tedna.
- Če veljaven JSON za ciljni teden že obstaja, ne naredi ničesar.
- Dodan `--force` za prisilno ponovno osvežitev.
- Spletni prenos in validacija, da preneseni PDF res pripada ciljnemu tednu.
- Ohranjen lokalni PDF način.
- Popravljeno rezanje bloka `ALERGENI V ŽIVILIH` iz petkove popoldanske malice.
