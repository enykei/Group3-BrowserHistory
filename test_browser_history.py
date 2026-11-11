import contextlib, io, os, sys, tempfile, unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from browser_history import BrowserHistory            
from doubly_linked_list import DoublyLinkedList       
from node import Node                                 
from stack import Stack                               
#import main as cli      
#message being printed as a result of an error in the code is E402                            


def make(*urls,cap=50,home="home"):
        b = BrowserHistory(home, cap)
        for u in urls:
            b.visit(u)
        return b



class Base(unittest.TestCase):  # cursor must be active
        def tearDown(self):
            b = getattr(self,"b",None)
            if b is not None:
                b._list.check_integrity()
                if b.current is None:
                    self.assertEqual(len(b), 0)
                else:
                    self.assertTrue(b.current.in_list)  


class TestStructures(unittest.TestCase): #testing for each of the cases in the lists
        def test_list_insert_remove_truncate_clear(self):
            d = DoublyLinkedList()
            a, b, c = Node("a"),Node("b"),Node("c")
            d.append_tail(a);d.append_tail(c); d.insert_after(a,b)
            self.assertEqual(d.to_list(), ["a","b","c"]);d.check_integrity()
            d.remove(b);d.insert_before(a,Node("z"))
            self.assertEqual(d.to_list(),["z", "a", "c"]); d.check_integrity()
            nodes= [d.append_tail(Node(str(i))) for i in range(3)]
            self.assertEqual(d.truncate_after(a), 4)
            self.assertFalse(nodes[2].in_list);d.check_integrity()
            d.clear(); self.assertTrue(d.is_empty()); d.check_integrity()

        def test_list_errors(self):
            d =DoublyLinkedList()
            with self.assertRaises(IndexError):
                d.remove_head()
            with self.assertRaises(ValueError):
                d.remove(Node("never-added"))
        def test_stack_lifo_and_empty(self): #checking for the stack to be empty
            s =Stack()
            for i in range(3):
                s.push(i)
            self.assertEqual((s.peek(),s.pop(), s.pop(),s.pop()), (2, 2, 1, 0))
            with self.assertRaises(IndexError):
                s.pop()


class TestConstruction(Base):
        def test_homepage_is_current(self):
            self.b = BrowserHistory("home")
            self.assertEqual((self.b.current_page()["url"],len(self.b)),("home", 1))

        def test_invalid_arguments(self):
            for bad in ("", "   ", None, 5):
                with self.assertRaises(ValueError):
                    BrowserHistory(bad)
            for cap in (0, -3,"x",2.5, True):
                with self.assertRaises(ValueError):
                    BrowserHistory("home",cap)

class TestNavigation(Base):
    def setUp(self):
        self.b=make("a","b","c")                     

    def test_visit_back_forward(self):
        self.assertEqual(self.b.pages(),["home", "a", "b", "c"])
        self.assertEqual([self.b.back(1),self.b.back(2),self.b.forward(2), self.b.forward(1)],
                         ["b","home", "b","c"])
        self.assertEqual((self.b.back(0),self.b.forward(0)), ("c","c"))

    def test_boundaries(self):
        self.assertEqual(self.b.back(100),"home")
        self.assertEqual(self.b.forward(100),"c")
        self.assertEqual(self.b.forward(5),"c")          
        self.b = make(home="only")
        self.assertEqual((self.b.back(10), self.b.forward(10)), ("only","only"))

    def test_back_100_times_on_two_page_history(self):    # edge case
        self.b = make("two",home="one")
        for _ in range(100):
            self.assertEqual(self.b.back(1),"one")
        self.assertEqual((self.b.back(100),len(self.b)), ("one", 2))
        for _ in range(100):
            self.assertEqual(self.b.forward(1),"two")

    def test_branching_discards_forward_history(self):    # edge case
        old_c = self.b.current
        self.b.back(2); self.b.visit("new")
        self.assertEqual(self.b.pages(), ["home","a", "new"])
        self.assertEqual((self.b.forward(5),self.b.back(1)), ("new", "a"))
        self.assertFalse(old_c.in_list)
        self.assertIsNone(old_c.prev); self.assertIsNone(old_c.next)

    def test_branch_from_oldest_and_duplicate_url(self):
        self.b.back(100); self.b.visit("fresh")
        self.assertEqual(self.b.pages(), ["home","fresh"])
        self.b.visit("fresh")
        self.assertEqual(self.b.pages(), ["home","fresh", "fresh"])

    def test_invalid_input_changes_nothing(self):
        for steps, exc in ((-1, ValueError),(1.5, TypeError),("2", TypeError),(None, TypeError), (True, TypeError)):
            with self.assertRaises(exc):
                self.b.back(steps)
        with self.assertRaises(ValueError):
            self.b.forward(-1)
        with self.assertRaises(ValueError):
            self.b.visit("")
        self.assertEqual(len(self.b), 4)
    
    def test_current_page_is_read_only_and_has_metadata(self):
        self.b.back(2)
        before =(self.b.pages(),self.b.current)
        self.b.current_page(); self.b.current_page()
        self.assertEqual((self.b.pages(),self.b.current),before)
        self.b.visit("t", "My Title")
        page = self.b.current_page()
        self.assertEqual((page["url"],page["title"]),("t", "My Title"))
        self.assertTrue(page["timestamp"])


class TestCapacity(Base):
    def test_prunes_oldest(self):
        self.b =make(*[f"p{i}" for i in range(1, 6)], cap=3, home="p0")
        self.assertEqual(self.b.pages(),["p3","p4","p5"])
        self.assertEqual((self.b.current_page()["url"], self.b.back(100)), ("p5", "p3"))

    def test_exact_capacity_and_capacity_one(self):
        self.b = make("p1", "p2", cap=3,home="p0")
        self.assertEqual(self.b.pages(),["p0", "p1","p2"])
        self.b = make("p1", "p2", cap=1,home="p0")
        self.assertEqual((self.b.pages(),self.b.back(5)), (["p2"], "p2"))

    def test_default_capacity_is_50(self):
        self.b = make(*[f"p{i}" for i in range(1, 120)],home="p0")
        self.assertEqual((len(self.b), self.b.pages()[0],self.b.pages()[-1]),(50, "p70","p119"))

    def test_prune_after_branching(self):
        self.b = make("p1","p2",cap=3,home="p0")
        self.b.back(1); self.b.visit("p3"); self.b.visit("p4")
        self.assertEqual(self.b.pages(),["p1","p3","p4"])


class TestDeleteRestore(Base):
    def setUp(self):
        self.b = make("a","b","c")

    def test_delete_relinks_and_missing_url(self):
        self.assertEqual(self.b.delete_url("a"), 1)
        self.assertEqual((self.b.pages(),self.b.back(1),self.b.back(1)), (["home","b", "c"], "b", "home"))
        self.assertEqual((self.b.delete_url("nope"),self.b.deleted_count()), (0,1))

    def test_restore_position_and_lifo(self):
        self.b.delete_url("b")
        self.assertEqual((self.b.restore(),self.b.pages()), ("b", ["home","a","b","c"]))
        self.b.delete_url("a"); self.b.delete_url("b")
        self.assertEqual((self.b.restore(),self.b.restore()), ("b", "a"))
        self.assertEqual(self.b.pages(),["home", "a", "b", "c"])
        self.assertIsNone(self.b.restore())               #checking if stack is empty

    def test_cursor_rules(self):
        self.b.delete_url("c")
        self.assertEqual(self.b.current_page()["url"],"b")         # moving back to it 
        self.b.restore()
        self.assertEqual(self.b.current_page()["url"],"c")         # returns to it
        self.b.delete_url("c"); self.b.back(1); self.b.restore()
        self.assertEqual(self.b.current_page()["url"],"a")         # user moving
        self.b.back(100); self.b.delete_url("home")
        self.assertEqual(self.b.current_page()["url"],"a")         # oldest deletion

    def test_duplicates_all_vs_latest(self):
        self.b.visit("a")
        self.assertEqual(self.b.delete_url("a", all_matches=False), 1)
        self.assertEqual(self.b.pages(), ["home","a", "b", "c"])
        self.assertEqual(self.b.delete_url("a"), 1)
        self.assertEqual(self.b.pages(), ["home","b", "c"])

    def test_delete_every_page_then_restore(self):
        for u in ("home", "a","b","c"):
            self.b.delete_url(u)
        self.assertEqual(len(self.b), 0)
        self.assertEqual((self.b.current_page(),self.b.back(3), self.b.forward(3)), (None, None, None))
        self.assertEqual((self.b.restore(),self.b.current_page()["url"]), ("c", "c"))

    def test_restore_when_neighbours_are_gone(self):
        self.b.delete_url("b"); self.b.back(1); self.b.visit("new")          # c dropped, a alive
        self.assertEqual((self.b.restore(), self.b.pages()), ("b", ["home", "a", "b", "new"]))
        self.b = make("a", "b", "c"); self.b.delete_url("b"); self.b.back(100); self.b.visit("new")
        self.assertEqual((self.b.restore(), self.b.pages()), ("b", ["home", "new", "b"]))  # both gone
        self.b = make("p1", "p2", cap=5, home="p0"); self.b.delete_url("p1")
        for u in ("p3", "p4", "p5", "p6"):
            self.b.visit(u)                               # p0 pruned
        self.b.back(100); self.b.visit("n")
        self.assertEqual((self.b.restore(), self.b.pages()), ("p1", ["p1", "p2", "n"]))  # before next anchor

    def test_restore_blocked_when_full(self):
        self.b = make("p1", "p2", cap=3, home="p0")
        self.b.delete_url("p1"); self.b.visit("p3")
        self.assertIsNone(self.b.restore())
        self.assertEqual(self.b.deleted_count(), 1)       # record kept
        self.b.delete_url("p3")
        self.assertEqual(self.b.restore(), "p3")

    def test_delete_history_and_alias(self):
        self.b.delete_url("a"); self.b.delete_history()
        self.assertEqual((len(self.b), self.b.deleted_count(), self.b.current_page()), (0, 0, None))
        self.assertEqual(self.b.history_string(), "(history is empty)")
        self.b.delete_history(); self.b.Delete_histroy()  # twice + spec spelling are safe
        self.b.visit("fresh")
        self.assertEqual((self.b.pages(), self.b.back(5)), (["fresh"], "fresh"))

