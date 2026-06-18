import unittest
from toposort import stable_toposort


class TopoTests(unittest.TestCase):
    def test_dependencies_first(self):
        order = stable_toposort({"app": ["db"], "db": []})
        self.assertLess(order.index("db"), order.index("app"))

    def test_dependency_only_node(self):
        self.assertEqual(set(stable_toposort({"app": ["db"]})), {"app", "db"})


if __name__ == "__main__":
    unittest.main()
