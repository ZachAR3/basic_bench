import unittest
from lru import LRUCache


class LruTests(unittest.TestCase):
    def test_eviction(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")
        cache.put("c", 3)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("a"), 1)

    def test_default(self):
        self.assertEqual(LRUCache(1).get("missing", 7), 7)


if __name__ == "__main__":
    unittest.main()
