from kyzylborda_lib.secrets import get_flag, get_token
import secrets
import requests


def generate():
    # flag was: ugra_some_words_here
    # flag will be: ugra_{some_{words_{here}}}

    flag = get_flag()
    flag = flag.replace("_", "_{")
    flag = flag + "}" * flag.count("{")

    res = requests.post(
        f"https://radikal.s.2025.ugractf.ru/{get_token()}/api/formulas",
        json={
            "name": "⛳️ Флаговая формула ♾️",
            "description": "В данной научной статье представлен способ вывода формулы для универсального кодирования флагов.",
            "password": secrets.token_urlsafe(32),
            "latex": flag
        }
    )
    if res.status_code != 201:
        raise ValueError(f"Failed to generate: status {res.status_code}, error {res.text}")
