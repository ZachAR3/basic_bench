import unittest
from config_loader import load_config


class ConfigTests(unittest.TestCase):
    def test_defaults_are_retained(self):
        result = load_config({"port": 80, "debug": False})
        self.assertEqual(result, {"port": 80, "debug": False})

    def test_distinct_keys_are_merged(self):
        result = load_config(
            {"default": 1},
            {"file": 2},
            {"environment": 3},
            {"cli": 4},
        )
        self.assertEqual(
            result,
            {"default": 1, "file": 2, "environment": 3, "cli": 4},
        )


if __name__ == "__main__":
    unittest.main()
