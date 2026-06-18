import unittest
from migration import migrate_settings


class HiddenMigrationTests(unittest.TestCase):
    def test_v1_runs_all_migrations_without_mutating(self):
        original = {"version": 1, "theme": "dark", "plugin": {"x": 1}}
        result = migrate_settings(original)
        self.assertEqual(original, {"version": 1, "theme": "dark", "plugin": {"x": 1}})
        self.assertEqual(result["version"], 3)
        self.assertEqual(result["display"]["color_scheme"], "dark")
        self.assertEqual(result["plugin"], {"x": 1})

    def test_nested_values_are_not_shared(self):
        original = {"version": 3, "extra": {"items": []}}
        result = migrate_settings(original)
        result["extra"]["items"].append(1)
        self.assertEqual(original["extra"]["items"], [])

    def test_future_version_rejected(self):
        with self.assertRaises(ValueError):
            migrate_settings({"version": 4})

    def test_v1_without_theme_uses_system_and_reaches_v3(self):
        result = migrate_settings({"version": 1, "other": 9})
        self.assertEqual(
            result,
            {"version": 3, "other": 9, "display": {"color_scheme": "system"}},
        )

    def test_v2_preserves_other_display_keys(self):
        source = {
            "version": 2,
            "display": {"theme": "dark", "font_scale": 1.25},
            "extensions": ["a", "b"],
        }
        result = migrate_settings(source)
        self.assertEqual(
            result["display"],
            {"color_scheme": "dark", "font_scale": 1.25},
        )
        self.assertEqual(result["extensions"], ["a", "b"])
        self.assertEqual(source["display"]["theme"], "dark")

    def test_idempotence(self):
        once = migrate_settings({"version": 1, "theme": "light"})
        twice = migrate_settings(once)
        self.assertEqual(twice, once)
        self.assertIsNot(twice, once)

    def test_invalid_old_version_rejected(self):
        with self.assertRaises(ValueError):
            migrate_settings({"version": 0})
