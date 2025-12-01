#!/usr/bin/env python3
"""
scan-openapi-nav.py

Usage: python3 scripts/scan-openapi-nav.py

Scans repository openapi-nav.yml vs docs/openapi/ and reports:
 - duplicates referenced in nav
 - broken references (nav references that don't exist)
 - openapi files present under docs/openapi but missing from nav
"""
import re
import os
import sys
from collections import Counter

NAV_FILE = 'openapi-nav.yml'
DOCS_DIR = 'docs/openapi'

if not os.path.exists(NAV_FILE):
    print(f"ERROR: {NAV_FILE} not found in repo root")
    sys.exit(2)

with open(NAV_FILE, 'r', encoding='utf-8') as f:
    nav_text = f.read()

# find paths that look like openapi/... .md
paths = re.findall(r'openapi/[\w\-/.]+\.md', nav_text)
count = Counter(paths)
duplicates = [p for p, c in count.items() if c > 1]

# Find missing references (nav refers to file but docs/<path> doesn't exist)
broken_refs = [p for p in paths if not os.path.exists(os.path.join('docs', p))]

# Walk the docs/openapi tree and collect all markdown files
actual = set()
for root, dirs, files in os.walk(DOCS_DIR):
    for fn in files:
        if fn.endswith('.md'):
            rel = os.path.join(root, fn)
            actual.add(rel.replace('docs/', ''))

# Which files exist but are not referenced by nav
missing_in_nav = sorted(list(actual - set(paths)))

print("SCAN RESULTS")
print("============")
print(f"Total referenced openapi paths in {NAV_FILE}: {len(paths)}")
print(f"Unique referenced paths: {len(count)}")
print()
if duplicates:
    print("Duplicates in nav (referenced more than once):")
    for p in duplicates:
        print(f"  - {p}  (count={count[p]})")
else:
    print("No duplicates found in nav.")

print()
if broken_refs:
    print("Broken references (nav -> file not present under docs/):")
    for p in sorted(set(broken_refs)):
        print(f"  - {p}")
else:
    print("No broken references — all referenced files exist under docs/.")

print()
print(f"Total md files under {DOCS_DIR}: {len(actual)}")
print(f"Files present under {DOCS_DIR} but NOT referenced in nav: {len(missing_in_nav)}")
for p in missing_in_nav:
    print(f"  - {p}")

if missing_in_nav:
    print('\nRun the script regularly to discover new docs to add to openapi-nav.yml.')

# Exit codes: 0 = OK, 1 = missing files found, 3 = duplicates or broken refs
if duplicates or broken_refs:
    sys.exit(3)
if missing_in_nav:
    sys.exit(1)
sys.exit(0)
