import unittest
from random import Random
from toposort import stable_toposort


class HiddenTopoTests(unittest.TestCase):
    def test_stable_input_order(self):
        graph = {"b": [], "a": [], "d": ["b"], "c": ["a"]}
        self.assertEqual(stable_toposort(graph), ["b", "a", "d", "c"])

    def test_duplicate_dependencies(self):
        self.assertEqual(stable_toposort({"a": ["b", "b"], "b": []}), ["b", "a"])

    def test_cycle(self):
        with self.assertRaises(ValueError):
            stable_toposort({"a": ["b"], "b": ["a"]})

    def test_self_cycle(self):
        with self.assertRaises(ValueError):
            stable_toposort({"a": ["a"]})

    def test_dependency_only_nodes_follow_first_appearance(self):
        graph = {"build": ["parse", "fetch"], "ship": ["build", "sign"]}
        order = stable_toposort(graph)
        self.assertEqual(order[:3], ["parse", "fetch", "sign"])
        self.assertLess(order.index("build"), order.index("ship"))

    def test_random_dags_are_valid_and_deterministic(self):
        random = Random(1337)
        for size in range(2, 15):
            nodes = [f"n{i}" for i in range(size)]
            graph = {}
            for index, node in enumerate(nodes):
                candidates = nodes[:index]
                graph[node] = [
                    candidate
                    for candidate in candidates
                    if random.random() < 0.28
                ]
            first = stable_toposort(graph)
            second = stable_toposort(graph)
            self.assertEqual(first, second)
            self.assertEqual(set(first), set(nodes))
            positions = {node: index for index, node in enumerate(first)}
            for node, dependencies in graph.items():
                for dependency in dependencies:
                    self.assertLess(positions[dependency], positions[node])

    def test_duplicate_dependencies_do_not_create_false_cycle(self):
        graph = {"deploy": ["build", "build", "test"], "build": [], "test": ["build"]}
        self.assertEqual(stable_toposort(graph), ["build", "test", "deploy"])
