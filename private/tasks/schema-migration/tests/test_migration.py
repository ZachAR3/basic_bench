import unittest
from migration import migrate_settings


class MigrationTests(unittest.TestCase):
    def test_v2_to_v3(self):
        result = migrate_settings({"version": 2, "display": {"theme": "dark"}})
        self.assertEqual(result["version"], 3)
        self.assertEqual(result["display"]["color_scheme"], "dark")

    def test_v3_unchanged(self):
        doc = {"version": 3, "display": {"color_scheme": "light"}}
        self.assertEqual(migrate_settings(doc), doc)


if __name__ == "__main__":
    unittest.main()
