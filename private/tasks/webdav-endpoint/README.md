# WebDAV endpoint parser

An endpoint consists of an HTTP(S) origin and an optional base path.

The parser must:

- accept DNS names, internationalized names, IPv4, and bracketed IPv6;
- normalize DNS names to lowercase ASCII IDNA;
- expose an explicit port when present;
- percent-decode user information but preserve encoded path octets;
- use `/` when no path is supplied and remove a trailing slash except at root;
- reject queries and fragments;
- reject decoded `.` and `..` path segments, including percent-encoded forms;
- reject malformed ports, missing hosts, unsupported schemes, and password-only credentials.

`Endpoint.authority` brackets IPv6 and includes an explicit port.
