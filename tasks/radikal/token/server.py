from kyzylborda_lib.secrets import validate_token
from kyzylborda_lib.server import http


@http.listen
async def handle(req: http.Request):
    token = req.path[1:]
    if validate_token(token):
        return http.respond(200, b"")
    else:
        return http.respond(403, b"")
