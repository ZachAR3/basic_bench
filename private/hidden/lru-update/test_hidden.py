import unittest
from collections import OrderedDict
from random import Random
from lru import LRUCache


class HiddenLruTests(unittest.TestCase):
    def test_update_at_capacity_does_not_evict(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("b", 20)
        self.assertEqual(cache.get("a"), 1)
        self.assertEqual(cache.get("b"), 20)

    def test_update_changes_recency(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("b", 3)
        cache.put("c", 4)
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), 3)

    def test_capacity_one_repeated_updates(self):
        cache = LRUCache(1)
        for value in range(20):
            cache.put("same", value)
            self.assertEqual(cache.get("same"), value)

    def test_randomized_against_ordered_dict(self):
        random = Random(90210)
        capacity = 4
        cache = LRUCache(capacity)
        reference = OrderedDict()
        for _ in range(300):
            key = random.choice("abcdef")
            if random.random() < 0.62:
                value = random.randrange(-20, 20)
                if key in reference:
                    del reference[key]
                reference[key] = value
                while len(reference) > capacity:
                    reference.popitem(last=False)
                cache.put(key, value)
            else:
                expected = reference.get(key)
                if key in reference:
                    reference.move_to_end(key)
                self.assertEqual(cache.get(key), expected)
            self.assertLessEqual(len(cache.items), capacity)
            self.assertEqual(set(cache.items), set(reference))

    def test_updates_do_not_duplicate_linked_list_nodes(self):
        cache = LRUCache(3)
        for key in "abc":
            cache.put(key, key)
        for index in range(100):
            cache.put("b", index)
        keys = []
        node = cache.head.next
        while node is not cache.tail:
            keys.append(node.key)
            node = node.next
        self.assertEqual(len(keys), 3)
        self.assertEqual(set(keys), {"a", "b", "c"})
        self.assertEqual(keys[-1], "b")
