#!/usr/bin/env python3

import aiohttp.web
import aiohttp_jinja2 as jinja2
import asyncio
import datetime
from jinja2 import FileSystemLoader
import json
import jwt
import mimetypes
import os
import random
import shutil
import sqlite3
import sys
import time
import traceback

with open("/flag.txt") as f:
    flag = f.read()
os.unlink("/flag.txt")


BASE_DIR = os.path.dirname(__file__)
PRIVATE_DIR = os.path.join(BASE_DIR, "private")
DEFAULT_POSTS = json.load(open(os.path.join(PRIVATE_DIR, "posts.json")))

STATE_DIR = os.environ.get("STATE_DIR") or "/state"

JWT_SECRET = "392841394333333333333919393993939393"


# default ones are deprecated
# https://docs.python.org/3/library/sqlite3.html#default-adapters-and-converters-deprecated
sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat())
sqlite3.register_converter("timestamp", lambda val: datetime.datetime.fromisoformat(val.decode()))

db = sqlite3.connect(os.path.join(STATE_DIR, "rustore.db"),
                     detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
                     autocommit=True)
cur = db.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS posts
               (token TEXT, date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                username TEXT, content TEXT)""")


app = aiohttp.web.Application()
routes = aiohttp.web.RouteTableDef()


async def run_antivirus():
    while True:
        try:
            open(os.path.join(STATE_DIR, ".antivirus-state"), "w").write(str(time.time()))
            for token in os.listdir(STATE_DIR):
                if not os.path.isdir(os.path.join(STATE_DIR, token)):
                    continue

                if not os.path.exists(av_temp_path := os.path.join(STATE_DIR, token, "avatars-temp")):
                    continue

                for avatar_file in os.listdir(av_temp_path):
                    full_path = os.path.join(av_temp_path, avatar_file)
                    target_path = os.path.join(STATE_DIR, token, "avatars", avatar_file)

                    content = open(full_path).read()

                    if "{" in content or "}" in content:
                        os.remove(full_path)
                        shutil.copy(os.path.join(PRIVATE_DIR, "avatar-denied.svg"), target_path)
                    else:
                        os.rename(full_path, target_path)  # assuming Unix atomic semantics
        except Exception as e:
            traceback.print_exc()
        finally:
            await asyncio.sleep(12)


def initialize_user(token):
    for post in DEFAULT_POSTS:
        cur.execute("INSERT INTO posts(token, date_time, username, content) VALUES(?, ?, ?, ?)",
                    (token, datetime.datetime.fromtimestamp(time.time() - 86400 - random.random() * 1000000), post["username"], post["content"]))
    shutil.copytree(os.path.join(BASE_DIR, "private", "user"), os.path.join(STATE_DIR, token))
    shutil.copy(os.path.join(BASE_DIR, "private", "avatar.svg"),
                    os.path.join(STATE_DIR, token, "avatars", f"{token}.svg"))


@routes.get("/{token}")
async def slashless(request):
    return aiohttp.web.HTTPMovedPermanently(f"/{request.match_info['token']}/")


@routes.get("/{token}/")
async def main(request):
    token = request.match_info["token"]

    if request.query_string:
        file_path = os.path.join(STATE_DIR, token, request.query_string)
        if not os.path.exists(file_path):
            raise aiohttp.web.HTTPNotFound()

        if not os.path.realpath(file_path).startswith(os.path.realpath(os.path.join(STATE_DIR, token))):
            raise aiohttp.web.HTTPForbidden()

        if os.path.isdir(file_path):
            files = os.listdir(file_path)
            html = "<html><body><ul>"
            for f in files:
                html += f'<li><a href="#">{f}</a></li>'
            html += "</ul></body></html>"
            return aiohttp.web.Response(text=html, content_type='text/html')

        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = "application/octet-stream"

        return aiohttp.web.FileResponse(file_path, headers={"Content-Type": content_type})

    cur.execute("""SELECT date_time, username, content FROM posts
                   WHERE token = ? ORDER BY date_time DESC""",
                (token,))
    posts = cur.fetchall()
    if not posts:
        initialize_user(token)
        return aiohttp.web.HTTPFound(f"/{token}/")

    try:
        theme = jwt.decode(request.cookies.get("settings"), JWT_SECRET, algorithms=["HS256"])["theme"]
    except Exception:
        theme = "default.html"

    try:
        jinja2.setup(app, loader=FileSystemLoader(os.path.join(STATE_DIR, token)))
        return jinja2.render_template(
            os.path.normpath(os.path.join("themes", theme)),
            request, {"theme": theme, "flag": flag, "posts": posts}
        )
    except Exception:
        return aiohttp.web.HTTPInternalServerError(reason="Internal server error. Try clearing cookies.")


@routes.post("/{token}/settings")
async def settings(request):
    token = request.match_info["token"]

    reader = await request.multipart()
    theme = None

    async for field in reader:
        if field.name == "theme":
            theme = await field.text()
        elif field.name == "avatar":
            if not field.filename:
                continue

            avatar_dir = os.path.join(STATE_DIR, token, "avatars-temp")
            os.makedirs(avatar_dir, exist_ok=True)
            avatar_path = os.path.join(avatar_dir, f"{token}.svg")
            shutil.copy(
                os.path.join(PRIVATE_DIR, "avatar-progress.svg"),
                os.path.join(STATE_DIR, token, "avatars", f"{token}.svg")
            )
            with open(avatar_path, "wb") as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)

    if theme is None:
        raise aiohttp.web.HTTPBadRequest()

    jwt_token = jwt.encode({"theme": theme}, JWT_SECRET, algorithm="HS256")
    response = aiohttp.web.HTTPFound(f"/{token}/")
    response.set_cookie(name="settings", value=jwt_token, httponly=True, secure=True, samesite="Strict")
    return response


@routes.post("/{token}/post")
async def post(request):
    token = request.match_info["token"]

    data = await request.post()
    try:
        content = data["content"]
    except KeyError:
        raise aiohttp.web.HTTPBadRequest()

    cur.execute("INSERT INTO posts(token, username, content) VALUES(?, ?, ?)",
                (token, token, content))

    return aiohttp.web.HTTPFound(f"/{token}/")


async def start_background_tasks(app):
    app["antivirus_task"] = asyncio.create_task(run_antivirus())


async def cleanup_background_tasks(app):
    app["antivirus_task"].cancel()
    try:
        await app["antivirus_task"]
    except asyncio.CancelledError:
        pass


app.add_routes(routes)
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)


if __name__ == "__main__":
    if os.environ.get("DEBUG") == "F":
        aiohttp.web.run_app(app, host="0.0.0.0", port=31337)
    else:
        aiohttp.web.run_app(app, path=sys.argv[1])
