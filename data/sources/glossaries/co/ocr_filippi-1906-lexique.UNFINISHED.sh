#!/bin/zsh
UA="vulgultra-research/0.1 (+noncommercial; lexical sourcing)"
cd "$(dirname "$0")/raw/filippi-1906-lexique-pages"   # needs fra+ita traineddata (tessdata_best) in ./tessdata
for n in $(seq 30 95); do
  f=n$n.jpg
  if [ ! -s $f ]; then curl -sS -L -m 120 -A "$UA" -o $f "https://archive.org/download/recueildesentenc00filiuoft/page/n$n.jpg"; sleep 3; fi
  [ -s n${n}_a.txt ] || tesseract $f n${n}_a --tessdata-dir tessdata -l fra+ita --psm 3 >/dev/null 2>&1
  if [ ! -s n${n}_b.txt ]; then magick $f -colorspace Gray -resize 140% -sharpen 0x1 tmp_b.png && tesseract tmp_b.png n${n}_b --tessdata-dir tessdata -l ita+fra --psm 3 >/dev/null 2>&1; fi
done
echo done
