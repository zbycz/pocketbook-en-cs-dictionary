# PocketBook EN→CS slovník

<h1 align="center">⬇️&nbsp;<a href="https://github.com/zbycz/pocketbook-en-cs-dictionary/raw/main/en-cs2.dic">STÁHNOUT SLOVNÍK (en-cs2.dic)</a>&nbsp;⬇️</h1>

Stačí zkopírovat do `/system/dictionaries/` ve čtečce.

## Build

Potřeba: `python3`, `java` 17+, `git`, `curl`.

```sh
./build.sh        # -> en-cs2.dic
```

## Soubory

| | |
|---|---|
| `en-cs2.dic` | **hotový slovník** (88 792 hesel) |
| `build.sh` | stáhne zdroj i nástroje a postaví `.dic` |
| `convert_en_cs.py` | `en-cs.txt` → XDXF (POS, dělení hesel typu `bbq = barbeque`) |
| `additions.txt` | +176 ručních hesel (`EN`⇥`CS`⇥`POS`) |

## Poznámky

- Jméno ve čtečce: `Anglicko-cesky slovnik2`, 88 792 hesel.
- Hledání ignoruje velikost písmen, diakritiku, interpunkci, pomlčky i apostrofy
  (takže `pen-holder` = `penholder`, `don’t` = `dont`).
- Ohebné tvary řeší morphemy ze `cs/morphems.txt`: `poising → poise`, `flitted → flit`.
- Zdroj: <https://dl.cihar.com/slovnik/stardict-english-czech-latest-source.tar.gz>
- Nástroje: [joao-a-cardoso/pb-dic-converter](https://github.com/joao-a-cardoso/pb-dic-converter),
  [Markismus/LanguageFilesPocketbookConverter](https://github.com/Markismus/LanguageFilesPocketbookConverter)
