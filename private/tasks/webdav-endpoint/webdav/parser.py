from urllib.parse import unquote, urlsplit

from .model import Endpoint


def parse_endpoint(value):
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("WebDAV endpoints must use http or https")
    if not parsed.netloc:
        raise ValueError("host is required")

    authority = parsed.netloc.rsplit("@", 1)[-1]
    host = authority.split(":", 1)[0].lower()
    if not host:
        raise ValueError("host is required")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid port") from exc

    base_path = unquote(parsed.path or "/").rstrip("/") or "/"
    if ".." in base_path.split("/"):
        raise ValueError("parent traversal is not allowed")
    return Endpoint(
        scheme=parsed.scheme,
        host=host,
        port=port,
        base_path=base_path,
        username=parsed.username,
        password=parsed.password,
    )
