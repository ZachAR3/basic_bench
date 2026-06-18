import unittest
from config_loader import load_config


class HiddenConfigTests(unittest.TestCase):
    def test_complete_precedence(self):
        result = load_config(
            {"value": "default", "only_default": 1},
            {"value": "file", "only_file": 2},
            {"value": "env", "only_env": 3},
            {"value": "cli", "only_cli": 4},
        )
        self.assertEqual(result["value"], "cli")
        self.assertEqual(result["only_default"], 1)
        self.assertEqual(result["only_file"], 2)
        self.assertEqual(result["only_env"], 3)
        self.assertEqual(result["only_cli"], 4)

    def test_falsey_values_are_overrides(self):
        result = load_config(
            {"flag": True, "count": 5, "name": "x"},
            cli_values={"flag": False, "count": 0, "name": ""},
        )
        self.assertEqual(result, {"flag": False, "count": 0, "name": ""})

    def test_sources_are_not_mutated(self):
        sources = [
            {"x": "default"},
            {"x": "file"},
            {"x": "env"},
            {"x": "cli"},
        ]
        snapshots = [dict(source) for source in sources]
        load_config(*sources)
        self.assertEqual(sources, snapshots)

    def test_none_sources_and_disjoint_falsey_values(self):
        result = load_config(
            {"a": 1},
            None,
            {"b": None, "c": []},
            {"d": {}, "e": False},
        )
        self.assertEqual(
            result,
            {"a": 1, "b": None, "c": [], "d": {}, "e": False},
        )

    def test_every_pairwise_precedence_boundary(self):
        names = ("defaults", "file", "env", "cli")
        sources = [{"winner": name} for name in names]
        for highest in range(4):
            selected = [source if index <= highest else None for index, source in enumerate(sources)]
            self.assertEqual(load_config(*selected)["winner"], names[highest])
