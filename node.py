from datetime import datetime

class Node:

    __slots__ = ("url", "title", "timestamp", "prev", "next", "in_list")

    def __init__(self, url, title=None, timestamp=None):
        self.url = url
        self.title = title if title else url
        self.timestamp = timestamp or datetime.now().isoformat(timespec="seconds")
        self.prev = None
        self.next = None
        self.in_list = False

    def metadata(self):
        return {"url": self.url, "title": self.title, "timestamp": self.timestamp}

    def __repr__(self):
        return f"Node({self.url!r})"