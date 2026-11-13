import os, tempfile
from browser_history import BrowserHistory

def step(title):
    print(f"\n--- {title} ---")

b = BrowserHistory("https://home.example", capacity=5)

step("1. Visit pages")
for u in ["https://a.com", "https://b.com", "https://c.com"]:
    b.visit(u)
b.display_history()

step("2. back(2) then forward(1)")
print("back(2)    ->", b.back(2))
print("forward(1) ->", b.forward(1))
b.display_history()

step("3. Boundary: back(100) and forward(100)")
print("back(100)    ->", b.back(100), "(stops at oldest)")
print("forward(100) ->", b.forward(100), "(stops at newest)")

step("4. Branching: go back 2, visit a new page (forward history is cleared)")
b.back(2)
b.visit("https://branch.com")
b.display_history()

step("5. current_page() - does not change state")
print(b.current_page())

step("6. Capacity = 5: visiting more pages prunes the oldest")
b.visit("https://x.com"); b.visit("https://y.com"); b.visit("https://z.com")
b.display_history()

step("7. Delete a URL, then restore it")
print("deleted:", b.delete_url("https://branch.com"))
b.display_history()
print("restored:", b.restore())
b.display_history()

step("8. Export / import")
path = os.path.join(tempfile.gettempdir(), "history_demo.txt")
b.export_history(path)
print(open(path).read())
other = BrowserHistory("https://placeholder.example", capacity=5)
other.import_history(path)
print("Imported into a new browser:")
other.display_history()

step("9. delete_history()")
b.delete_history()
b.display_history()
print("back() on empty history ->", b.back())
b.visit("https://fresh-start.com")
b.display_history()
