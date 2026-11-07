#!/usr/bin/env sh
# StarDict EN-CS -> PocketBook .dic
set -eu
cd "$(dirname "$0")"

SRC=https://dl.cihar.com/slovnik/stardict-english-czech-latest-source.tar.gz
B=.build
OUT=en-cs2.dic
NAME="Anglicko-cesky slovnik2"

mkdir -p "$B"

if [ ! -f "$B/en-cs.txt" ]; then
  curl -fsSL "$SRC" | tar -xz -C "$B"
  mv "$B"/stardict-english-czech-*-source/en-cs.txt "$B/en-cs.txt"
fi

[ -d "$B/pb-dic-converter" ] || git clone -q --depth 1 https://github.com/joao-a-cardoso/pb-dic-converter "$B/pb-dic-converter"
[ -d "$B/lang" ] || git clone -q --depth 1 https://github.com/Markismus/LanguageFilesPocketbookConverter "$B/lang"

python3 convert_en_cs.py -i "$B/en-cs.txt" -o "$B/en-cs.xdxf" -a additions.txt

"$B/pb-dic-converter/linux/xdxf-2-pbdic" -i "$B/en-cs.xdxf" -o "$OUT" \
  -l cs -d "$B/lang/cs" -n "$NAME" -m EXACT

echo "OK: $OUT"
