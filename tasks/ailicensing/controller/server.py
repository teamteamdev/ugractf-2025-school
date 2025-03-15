from kyzylborda_lib.sandbox import start_oneshot
from kyzylborda_lib.secrets import validate_token, get_flag
from kyzylborda_lib.server import tcp


@tcp.listen
async def handle(conn: tcp.Connection):
    await conn.writeall(b"Enter token: ")
    token = (await conn.readline()).decode(errors="ignore").strip()
    if not validate_token(token):
        await conn.writeall(b"Wrong token\n")
        return
    oneshot = await start_oneshot(token)

    with oneshot.open("/app/flag", "w") as f:
        print("-----BEGIN AI CHATBOT LICENSE-----", file=f)
        print(get_flag(token), file=f)
        print("-----END AI CHATBOT LICENSE-----", file=f)

    return oneshot
