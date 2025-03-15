#!/bin/sh
[[ -z $SOLVE ]] && { echo "SOLVE=/path/to/file.torrent ./solve.sh"; exit 1; }

./extract-hashes.rs >hashes.txt
if [[ -z $NO_CRACK ]]; then
    hashcat -w 3 -O -a 3 -m 100 hashes.txt "?a?a?a?a?a"
fi
hashcat -w 3 -O -a 3 -m 100 hashes.txt "?a?a?a?a?a" --show >hashes.cracked
sed <hashes.cracked -e 's/:/\\]:/' -e 's/^/s:\\[/' -e 's/$/:/' -e 's/\$HEX//' >hashes.sed
sed -e 's/^/[/' -e 's/$/]/' hashes.txt | sed -f hashes.sed | tr -d '\n'
