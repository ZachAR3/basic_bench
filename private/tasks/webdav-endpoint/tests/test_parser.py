import unittest

from webdav import parse_endpoint


class EndpointTests(unittest.TestCase):
    def test_basic_https_endpoint(self):
        endpoint = parse_endpoint("https://dav.example.com/webdav/")
        self.assertEqual(endpoint.scheme, "https")
        self.assertEqual(endpoint.host, "dav.example.com")
        self.assertEqual(endpoint.base_path, "/webdav")
        self.assertIsNone(endpoint.port)

    def test_explicit_port(self):
        endpoint = parse_endpoint("http://localhost:8080/dav")
        self.assertEqual(endpoint.authority, "localhost:8080")

    def test_rejects_unsupported_scheme(self):
        with self.assertRaises(ValueError):
            parse_endpoint("ftp://example.com/files")


if __name__ == "__main__":
    unittest.main()
