from doubly_linked_list import DoublyLinkedList
from node import Node
from stack import Stack

DEFAULT_CAPACITY = 50
_EXPORT_HEADER = "#BROWSER_HISTORY v1"
#Remembers a deleted page and its old neighbours.
class _DeletedRecord:
    __slots__ = ("node", "prev_anchor", "next_anchor",
                 "was_current", "fallback")

    def __init__(self, node, prev_anchor, next_anchor, was_current, fallback):
        self.node = node
        self.prev_anchor = prev_anchor
        self.next_anchor = next_anchor
        self.was_current = was_current
        self.fallback = fallback

#browser history class manages the history of visited pages, allowing navigation, deletion, restoration, and import/export of history data.
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

    # delete & restore
    def delete_history(self):
        self._list.clear()
        self._deleted.clear()
        self.current = None

    Delete_histroy = delete_history

    def delete_url(self, url, all_matches=True):
        self._check_url(url)
        matches = self._list.find_all(url)
        if not all_matches:
            matches = matches[-1:]
        for node in matches:
            prev_a, next_a = node.prev, node.next
            was_current = node is self.current
            if was_current:
                self.current = prev_a if prev_a is not None else next_a
            self._list.remove(node)
            self._deleted.push(_DeletedRecord(node, prev_a, next_a, was_current, self.current))
        return len(matches)

    def restore(self):
        if self._deleted.is_empty():
            return None
        if len(self._list) >= self.capacity:
            return None 
        rec = self._deleted.pop()
        node = rec.node
        if rec.prev_anchor is not None and rec.prev_anchor.in_list:
            self._list.insert_after(rec.prev_anchor, node)
        elif rec.next_anchor is not None and rec.next_anchor.in_list:
            self._list.insert_before(rec.next_anchor, node)
        else:
            self._list.append_tail(node)
        if self.current is None or (rec.was_current and self.current is rec.fallback):
            self.current = node
        return node.url
    
    def export_history(self, path): 
           cur_idx= -1
           lines =[]
           for i, node in enumerate(self._list):
               if node is self.current:
                   cur_idx=i
               lines.append(f"{self._clean(node.url)}\t{self._clean(node.title)}\t{node.timestamp}")
           with open(path,"w", encoding="utf-8") as f:
               f.write(_EXPORT_HEADER +"\n")
               f.write(f"#current={cur_idx}\n")
               for line in lines:
                   f.write(line +"\n")
           return len(lines)
    def import_history(self,path):
            with open(path,"r",encoding="utf-8") as f:
                raw = [ln.rstrip("\n") for ln in f]
            if not raw or raw[0].strip() != _EXPORT_HEADER:
                raise ValueError("not a valid history file (missing header)")
            if len(raw) <2 or not raw[1].startswith("#current="):
                raise ValueError("invalid history file (missing #current line)")
            try:
                cur_idx =int(raw[1].split("=", 1)[1])
            except ValueError:
                raise ValueError("invalid #current value")
            entries =[]
            for n, line in enumerate(raw[2:], start=3):
                if not line.strip():
                    continue
                parts =line.split("\t")
                if len(parts) !=3 or not parts[0].strip():
                    raise ValueError(f"malformed entry on line {n}")
                entries.append(parts)
            valid = (0 <=cur_idx <len(entries)) if entries else (cur_idx ==-1)
            if not valid:
                raise ValueError("#current index is out of range")
            
            #application of the values
            drop = max(0, len(entries) - self.capacity)
            entries = entries[drop:]
            cur_idx = max(0, cur_idx - drop) if entries else -1
            self._list.clear()
            self._deleted.clear()
            self.current = None
            for i, (url, title, ts) in enumerate(entries):
                node = self._list.append_tail(Node(url, title, ts))
                if i == cur_idx:
                    self.current = node
            return len(entries)
                                    