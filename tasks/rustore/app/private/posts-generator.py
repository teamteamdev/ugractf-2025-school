#!/usr/bin/env python3

import requests
import os
import json
import random
import traceback

random.seed(8381)
users = ["".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(16)) for i in range(8)]

print(users)

SYSTEM_PROMPT = """
    You are a Rust programmer. You are given a task to write a Rust program.
    Your program should be HARD to understand, debug, and read. You are actually a Fortran programmer in your heart, so your
        code must be valid Rust, but variable names and general vibe should remind of how Fortran programmers write code.
"""

USER_PROMPTS = [
    """
    Your nonce value is XXX.
    Pick a random topic in programming, science, or technology, such as Fibonacci number calculation, quick sort of an array, or a simple web server,
    (don’t stick to these examples, make something else),
    and write a Rust program somewhere between 10 and 100 lines of code.
    Only output the program, do not include any other text. The program should be a complete program, not a fragment.
    The program should be a simple program that can be run directly using `cargo run`.
    The program should not have any comments.
    If nonce value is odd, make program something that does I/O and system calls.
    If nonce value is not divisible by 3, make whitespace very ugly and illogical.
    """
]

def make_post():
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "openai/gpt-4o",
                            "messages": [
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": random.choice(USER_PROMPTS).replace("XXX", str(random.randint(1, 10000)))}
                            ]
                        }).json()
        return resp["choices"][0]["message"]["content"].replace("```rust", "").replace("```", "")
    except Exception as e:
        print(resp)
        traceback.print_exc()

posts = [
    {
        "username": random.choice(users),
        "content": make_post()
    }
    for i in range(26)
]

posts = [p for p in posts if p["content"] is not None]

for p in posts:
    print(f'======= {p["username"]}\n{p["content"]}\n')

json.dump(posts, open("posts.json", "w"))
