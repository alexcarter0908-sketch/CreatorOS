from pathlib import Path

path = Path(r"C:\Users\hp\Downloads\CreatorOS\CreatorOS-main\backend\app\services\agents\search_gate.py")
text = path.read_text(encoding="utf-8")

idx = text.find("multi-source research")
if idx == -1:
    print("Could not even find 'multi-source research' anywhere in the file.")
else:
    snippet = text[idx:idx+120]
    print("EXACT bytes/repr of that section:")
    print(repr(snippet))

print()
print("---")
print()

idx2 = text.find("deep_search = bool")
if idx2 == -1:
    print("Could not find 'deep_search = bool' anywhere in the file.")
else:
    snippet2 = text[idx2:idx2+100]
    print("EXACT bytes/repr of that section:")
    print(repr(snippet2))

print()
print("---")
print()
print("This script only READS the file. It has not changed anything.")
