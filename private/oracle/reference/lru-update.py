class _Node:
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.items = {}
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append(self, node):
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def get(self, key, default=None):
        node = self.items.get(key)
        if node is None:
            return default
        self._remove(node)
        self._append(node)
        return node.value

    def put(self, key, value):
        node = self.items.get(key)
        if node is not None:
            self._remove(node)
            node.value = value
            self._append(node)
            return
        if len(self.items) >= self.capacity:
            oldest = self.head.next
            self._remove(oldest)
            del self.items[oldest.key]
        node = _Node(key, value)
        self.items[key] = node
        self._append(node)
