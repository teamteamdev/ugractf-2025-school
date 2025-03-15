import csv
import os


DICTIONARY: dict[str, str] = {}
with open("dictionary.csv", "r", newline='') as f:
    reader = csv.reader(f, delimiter=' ', quotechar="'", quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    for row in reader:
        char, _code, *values = row
        for value in values:
            DICTIONARY[value] = char


with open(os.environ["FILE"]) as f:
    for line in f:
        print(DICTIONARY[line.rstrip('\n')], end='')
print()
