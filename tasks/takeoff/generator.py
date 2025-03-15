import requests
from kyzylborda_lib.secrets import get_token


def generate():
    res = requests.post(
        f"https://takeoff.s.2025.ugractf.ru/internal_stuff_generate_token_key/{get_token()}/",
        headers={
            "Authorization": "4BqlZx9uQ011Q7ot2QaWoXgfRFLgZGZE"
        }
    )
    if res.status_code != 200:
        raise ValueError("Failed to generate")
