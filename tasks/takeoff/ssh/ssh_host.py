import asyncio
import socket
import threading

import paramiko
import requests
from paramiko.common import AUTH_FAILED, AUTH_SUCCESSFUL, OPEN_SUCCEEDED, OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

HOST_KEY = paramiko.Ed25519Key.from_private_key_file("server.key")
WEB_ENDPOINT = "https://takeoff.s.2025.ugractf.ru"
SECRET_KEY = "4BqlZx9uQ011Q7ot2QaWoXgfRFLgZGZE"

class SSHServerHandler (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.user_data = None

    def check_auth_publickey(self, username, key):
        try:
            check = requests.post(f'{WEB_ENDPOINT}/internal_stuff_verify_key/', data=f'ssh-ed25519 {key.get_base64()}', headers={
                'Authorization': SECRET_KEY
            })
            if check.status_code == 200:
                self.user_data = check.json()
                return AUTH_SUCCESSFUL
        except:
            return AUTH_FAILED
        return AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'publickey'

    def check_channel_request(self, kind, _):
        if kind == "session":
            return OPEN_SUCCEEDED
        return OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        return True

def connection(client):
    transport = paramiko.Transport(client)
    transport.add_server_key(HOST_KEY)
    transport.local_version = "SSH-2.0-OpenSSH_9.7p1 Ubuntu-7ubuntu4"

    server = SSHServerHandler()
    try:
        transport.start_server(server=server)
    except paramiko.SSHException as e:
        print("[!] SSHException", e)
        return

    channel = transport.accept(20)
    server.event.wait(10)
    if not server.event.is_set():
        print("[!] Client never asked for a shell.")
        return
    if server.user_data is None:
        print("[!] No user data available.")
        return
    fake_shell(server.user_data['flag'], channel)

def fake_shell(flag, channel):
    channel.sendall(f"Hello!\r\n\r\nThe server is unavailable.\r\nPlease contact the administrator.\r\nRequest id: {flag}\r\n\r\n")
    channel.close()

async def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", 40022))
    server_socket.setblocking(False)
    server_socket.listen(100)

    loop = asyncio.get_event_loop()

    while True:
        client_socket, client_addr = await loop.sock_accept(server_socket)
        thread = threading.Thread(target=connection, args=(client_socket,))
        thread.daemon = True
        thread.start()

asyncio.run(run_server())
