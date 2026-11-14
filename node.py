from datetime import datetime

class Node:
    #restricting the functionality of the "Node" class in order to have better performance and memory usage
    __slots__ = ("url", "title", "timestamp", "prev", "next", "in_list")

    def __init__(self, url, title=None, timestamp=None):
        self.url = url
        self.title = title if title else url
        self.timestamp = timestamp or datetime.now().isoformat(timespec="seconds")
        self.prev = None
        self.next = None
        self.in_list = False
    #while functioning __init__ set as True and when the code is terminated it automatically sets as False
    def metadata(self):
        return {"url": self.url, "title": self.title, "timestamp": self.timestamp}

    def __repr__(self):
        return f"Node({self.url!r})"