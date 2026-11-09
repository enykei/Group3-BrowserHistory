from doubly_linked_list import DoublyLinkedList
from node import Node
from stack import Stack

DEFAULT_CAPACITY = 50
_EXPORT_HEADER = "#BROWSER_HISTORY v1"


class _DeletedRecord:
    __slots__ = ("node", "prev_anchor", "next_anchor",
                 "was_current", "fallback")

    def __init__(self, node, prev_anchor, next_anchor, was_current, fallback):
        self.node = node
        self.prev_anchor = prev_anchor
        self.next_anchor = next_anchor
        self.was_current = was_current
        self.fallback = fallback


class BrowserHistory:
    def __init__(self, homepage, capacity=DEFAULT_CAPACITY):
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
            raise ValueError("capacity must be an integer >= 1")
        self._check_url(homepage)
        self.capacity = capacity
        self._list = DoublyLinkedList()
        self._deleted = Stack()
        self.current = None
        self._list.append_tail(Node(homepage))
        self.current = self._list.head

    @staticmethod
    def _check_url(url):
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url must be a non-empty string")

    @staticmethod
    def _check_steps(steps):
        if not isinstance(steps, int) or isinstance(steps, bool):
            raise TypeError("steps must be an integer")
        if steps < 0:
            raise ValueError("steps must be >= 0")

    @staticmethod
    def _clean(text):
        return " ".join(str(text).split())

    def __len__(self):
        return len(self._list)

    def pages(self):
        return self._list.to_list()

    def deleted_count(self):
        return len(self._deleted)

    def _enforce_capacity(self):
        while len(self._list) > self.capacity:
            oldest = self._list.head
            if oldest is self.current:
                self.current = oldest.next
            self._list.remove_head()

    def visit(self, url, title=None):
        self._check_url(url)
        node = Node(url, title)
        if self.current is None:
            self._list.append_tail(node)
        else:
            self._list.truncate_after(self.current)
            self._list.append_tail(node)
        self.current = node
        self._enforce_capacity()
        return node.url

    def back(self, steps=1):
        self._check_steps(steps)
        if self.current is None:
            return None
        while steps > 0 and self.current.prev is not None:
            self.current = self.current.prev
            steps -= 1
        return self.current.url

    def forward(self, steps=1):
        self._check_steps(steps)
        if self.current is None:
            return None
        while steps > 0 and self.current.next is not None:
            self.current = self.current.next
            steps -= 1
        return self.current.url

    def current_page(self):
        if self.current is None:
            return None
        return self.current.metadata()

    def history_string(self):
        if len(self._list) == 0:
            return "(history is empty)"
        lines = [
            f"Browser history ({len(self._list)}/{self.capacity} pages, oldest -> newest)"]
        for i, node in enumerate(self._list, 1):
            marker = "  [<]" if node is self.current else ""
            lines.append(
                f"  {i:>2}. {node.url}{marker}   ({node.title}, {node.timestamp})")
        return "\n".join(lines)

    def display_history(self):
        print(self.history_string())
