class _StackItem:
    __slots__ = ("value", "below")

    def __init__(self, value, below):
        self.value = value
        self.below = below


class Stack:
    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, value):
        self._top = _StackItem(value, self._top)
        self._size += 1

    def pop(self):
        if self._top is None:
            raise IndexError("pop from empty stack")
        item = self._top
        self._top = item.below
        self._size -= 1
        return item.value

    def peek(self):
        if self._top is None:
            raise IndexError("peek from empty stack")
        return self._top.value

    def clear(self):
        self._top = None
        self._size = 0

    def is_empty(self):
        return self._size == 0

    def __len__(self):
        return self._size

    def __iter__(self):
        cur = self._top
        while cur is not None:
            yield cur.value
            cur = cur.below
