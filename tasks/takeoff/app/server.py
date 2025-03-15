import os
import sqlite3

from cryptography.hazmat.primitives import _serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from flask import Flask, render_template, request, abort, Response
from kyzylborda_lib.secrets import get_flag, validate_token

STATE_DIR = os.environ.get("STATE_DIR") or "/state"
SECRET_KEY = "4BqlZx9uQ011Q7ot2QaWoXgfRFLgZGZE"
SSH_KEY_SEED = "lC47v79kWbFkyNSx"

db = sqlite3.connect(os.path.join(STATE_DIR, "takeoff.db"), autocommit=True)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS keys(token TEXT, pubkey TEXT, prkey TEXT)")
cur.execute("CREATE INDEX IF NOT EXISTS keys_token ON keys(token)")
cur.execute("CREATE INDEX IF NOT EXISTS keys_key ON keys(pubkey)")
app = Flask(__name__)

@app.route("/<token>/")
def root(token):
    if not validate_token(token):
        return "Invalid token.", 401
    return render_template("index.html")

@app.route("/<token>/keys/public.pgp")
def pgp_pub(token):
    if not validate_token(token):
        return "Invalid token.", 401
    with open("static/public.pgp", "r") as file:
        return Response(file.read(), mimetype="text/plain")

@app.route("/<token>/keys/private.pgp")
def pgp_private(token):
    if not validate_token(token):
        return "Invalid token.", 401
    with open("static/private.pgp", "r") as file:
        return Response(file.read(), mimetype="text/plain")

@app.route("/<token>/keys/id_ed25519.pub")
def ssh_pub(token):
    pub = cur.execute("SELECT pubkey FROM keys WHERE token = ?", (token,)).fetchone()
    if pub is None:
        return "Invalid token.", 401
    return Response(pub[0] + " ph4nt0m@cyb3ri4n.ru", mimetype="text/plain")

@app.route("/<token>/keys/id_ed25519")
def ssh_private(token):
    pr = cur.execute("SELECT prkey FROM keys WHERE token = ?", (token,)).fetchone()
    if pr is None:
        return "Invalid token.", 401
    return Response(pr[0], mimetype="text/plain")

@app.post("/internal_stuff_generate_token_key/<token>/")
def generate_key(token):
    if 'Authorization' not in request.headers or request.headers['Authorization'] != SECRET_KEY:
        return abort(404)
    if len(token) != 16:
        return "Token must be 16 characters long"
    private_key = Ed25519PrivateKey.from_private_bytes((token + SSH_KEY_SEED).encode('utf-8'))
    public_key = private_key.public_key()

    pub_str = public_key.public_bytes(_serialization.Encoding.OpenSSH, _serialization.PublicFormat.OpenSSH).decode('utf-8')
    pr_str = private_key.private_bytes(_serialization.Encoding.PEM, _serialization.PrivateFormat.OpenSSH, _serialization.NoEncryption()).decode('utf-8')
    cur.execute("INSERT INTO keys(token, pubkey, prkey) VALUES(?, ?, ?)", (token, pub_str, pr_str))
    return "OK"

@app.post("/internal_stuff_verify_key/")
def verify_key():
    if 'Authorization' not in request.headers or request.headers['Authorization'] != SECRET_KEY:
        return abort(404)
    token = cur.execute("SELECT token FROM keys WHERE pubkey = ?", (request.data.decode('utf-8'),)).fetchone()
    if token is None:
        return "Invalid key.", 401
    return {'token': token[0], 'flag': get_flag(token[0])}