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