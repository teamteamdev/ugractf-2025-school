import csv
from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag, get_secret
import random
import os


DICTIONARY: dict[str, list[str]] = {}
with open("dictionary.csv", "r", newline='') as f:
    reader = csv.reader(f, delimiter=' ', quotechar="'", quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    for row in reader:
        char, _code, *values = row
        DICTIONARY[char] = values


def encode_one(char) -> str:
    return random.choice(sum((DICTIONARY.get(key) for key in {char.lower(), char.upper()}), start=[]))


def generate():
    random.seed(get_secret("random_seed"))
    encoded = '\n'.join(encode_one(c) for c in get_flag())
    with open(get_attachments_dir() + "/Untitled.txt", "w+") as f:
        print(encoded, file=f)
