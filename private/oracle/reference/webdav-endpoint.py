import ipaddress
from urllib.parse import unquote, urlsplit

from .model import Endpoint


def parse_endpoint(value):
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("WebDAV endpoints must use http or https")
    if parsed.query or parsed.fragment:
        raise ValueError("query and fragment are not allowed")
    if parsed.hostname is None:
        raise ValueError("host is required")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid port") from exc

    host = parsed.hostname
    try:
        host = ipaddress.ip_address(host).compressed
    except ValueError:
        try:
            host = host.encode("idna").decode("ascii").lower()
        except UnicodeError as exc:
            raise ValueError("invalid host") from exc

    username = unquote(parsed.username) if parsed.username is not None else None
    password = unquote(parsed.password) if parsed.password is not None else None
    if password is not None and not username:
        raise ValueError("password requires a username")

    raw_path = parsed.path or "/"
    for segment in raw_path.split("/"):
        if unquote(segment) in {".", ".."}:
            raise ValueError("path traversal is not allowed")
    base_path = raw_path.rstrip("/") or "/"
    return Endpoint(
        scheme=parsed.scheme,
        host=host,
        port=port,
        base_path=base_path,
        username=username,
        password=password,
    )
