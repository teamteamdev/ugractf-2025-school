import requests
import os

# Платформы, которые были переименованы из "километровых" названий и не ищутся в ЕСР
DICTIONARY: dict[str, str] = {
    'Беливо': chr(95),
    'Смолёво': chr(73),
    'Платовская': chr(109),
    'Новое Перепечино': chr(113), # 112.9; нет статьи, рядом с Петушками -- смотреть в маршрутную карту Горьковского направления
}

def decode(name):
    res = DICTIONARY.get(name)
    if res is not None:
        return res

    content = requests.get(f"https://osm.sbin.ru/esr/search:{name}").content
    if 'Название (unla.webservis.ru):'.encode() not in content:
        assert b'<li>' in content, (name, content)
        content = content[content.find(b'<li>'):content.find(b'</ol>')].replace(b'</li>', b'\n').split(b'\n')

        choice = next(
            (line for line in content if 'Моск'.encode() in line),
            next(
                (line for line in content if f': {name}<'.encode() in line),
                None
            )
        )
        if not choice:
            print(b'\n'.join(content).decode())
            assert choice
        choice = choice[choice.find(b'esr:'):]
        choice = choice[:choice.find(b'>')]
        choice = choice.decode()
        content = requests.get(f"https://osm.sbin.ru/esr/{choice}").content

    line = next(
        line
        for line
        in content.split(b'\n')
        if 'Название (unla.webservis.ru):'.encode() in line
    )

    assert line.endswith(b'</td></tr>'), line
    line = line[:-10].rstrip()
    assert line.endswith('км'.encode()), line
    line = line[:-4].rstrip()
    line = line[line.rindex(b' ') + 1:].replace(b',', b'.')

    DICTIONARY[name] = chr(round(float(line)))
    return DICTIONARY[name]


with open(os.environ["FILE"]) as f:
    for line in f:
        print(decode(line.rstrip('\n')), end='')
print()

__import__("pprint").pp(DICTIONARY)
