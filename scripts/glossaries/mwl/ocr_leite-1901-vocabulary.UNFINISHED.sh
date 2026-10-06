#!/bin/zsh
UA="vulgultra-research/0.1 (+noncommercial; lexical sourcing)"
cd "$(dirname "$0")/raw/leite-1901-vol2-vocabulary-pages"   # needs por.traineddata (tessdata_best) in ./tessdata
for n in $(seq 158 236); do
  f=n$n.jpg
  if [ ! -s $f ]; then curl -sS -L -m 120 -A "$UA" -o $f "https://archive.org/download/estudosdephilolo02vascuoft/page/n$n.jpg"; sleep 2; fi
  [ -s n${n}_por.txt ] || tesseract $f n${n}_por --tessdata-dir tessdata -l por --psm 6 >/dev/null 2>&1
done
echo done
