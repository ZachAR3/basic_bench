import unittest

from webdav import parse_endpoint


class HiddenEndpointTests(unittest.TestCase):
    def test_bracketed_ipv6_and_port(self):
        endpoint = parse_endpoint("https://[2001:db8::1]:8443/dav")
        self.assertEqual(endpoint.host, "2001:db8::1")
        self.assertEqual(endpoint.port, 8443)
        self.assertEqual(endpoint.authority, "[2001:db8::1]:8443")

    def test_percent_decoded_credentials(self):
        endpoint = parse_endpoint("https://user%40corp:p%3Ass@example.com/dav")
        self.assertEqual(endpoint.username, "user@corp")
        self.assertEqual(endpoint.password, "p:ss")

    def test_encoded_path_octets_are_preserved(self):
        endpoint = parse_endpoint("https://example.com/team%2Farchive/a%20b/")
        self.assertEqual(endpoint.base_path, "/team%2Farchive/a%20b")

    def test_encoded_parent_traversal_is_rejected(self):
        for value in (
            "https://example.com/dav/%2e%2e/secrets",
            "https://example.com/dav/../secrets",
            "https://example.com/./dav",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_endpoint(value)

    def test_query_and_fragment_are_rejected(self):
        for value in (
            "https://example.com/dav?token=x",
            "https://example.com/dav#section",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_endpoint(value)

    def test_unicode_host_is_idna_normalized(self):
        endpoint = parse_endpoint("https://BÜCHER.example/dav")
        self.assertEqual(endpoint.host, "xn--bcher-kva.example")

    def test_password_without_username_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_endpoint("https://:secret@example.com/dav")

    def test_empty_path_becomes_root(self):
        self.assertEqual(parse_endpoint("https://example.com").base_path, "/")

    def test_malformed_port_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_endpoint("https://example.com:notaport/dav")
