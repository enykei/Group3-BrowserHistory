from node import Node


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def __iter__(self):
        cur = self.head
        while cur is not None:
            nxt = cur.next
            yield cur
            cur = nxt

    # insertion
    def append_tail(self, node):
        node.prev = self.tail
        node.next = None
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        node.in_list = True
        self._size += 1
        return node

    def insert_after(self, anchor, node):
        if anchor is self.tail:
            return self.append_tail(node)
        node.prev = anchor
        node.next = anchor.next
        anchor.next.prev = node
        anchor.next = node
        node.in_list = True
        self._size += 1
        return node

    def insert_before(self, anchor, node):
        if anchor is self.head:
            node.prev = None
            node.next = anchor
            anchor.prev = node
            self.head = node
            node.in_list = True
            self._size += 1
            return node
        return self.insert_after(anchor.prev, node)

    # removal
    def remove(self, node):
        if not node.in_list:
            raise ValueError("node is not part of this list")
        if node.prev is None:
            self.head = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self.tail = node.prev
        else:
            node.next.prev = node.prev
        node.prev = None
        node.next = None
        node.in_list = False
        self._size -= 1
        return node

    def remove_head(self):
        if self.head is None:
            raise IndexError("remove from empty list")
        return self.remove(self.head)

    def truncate_after(self, node):
        removed = 0
        cur = node.next
        node.next = None
        self.tail = node
        while cur is not None:
            nxt = cur.next
            cur.prev = None
            cur.next = None
            cur.in_list = False
            cur = nxt
            removed += 1
        self._size -= removed
        return removed

    def clear(self):
        cur = self.head
        while cur is not None:
            nxt = cur.next
            cur.prev = cur.next = None
            cur.in_list = False
            cur = nxt
        self.head = self.tail = None
        self._size = 0

    # queries
    def find_all(self, url):
        return [n for n in self if n.url == url]

    def to_list(self):
        return [n.url for n in self]

    def check_integrity(self):
        if self._size == 0:
            assert self.head is None and self.tail is None, "empty list must have no head/tail"
            return True
        assert self.head is not None and self.tail is not None
        assert self.head.prev is None, "head.prev must be None"
        assert self.tail.next is None, "tail.next must be None"
        count, cur, prev = 0, self.head, None
        while cur is not None:
            assert cur.prev is prev, "prev pointer does not mirror next pointer"
            assert cur.in_list, "linked node must be flagged in_list"
            prev, cur = cur, cur.next
            count += 1
            assert count <= self._size, "cycle or size mismatch"
        assert prev is self.tail, "tail not reachable from head"
        assert count == self._size, "size counter out of sync"
        return True