#!/usr/bin/env python3
"""
midware-tools.py

Usage:
  python3 scripts/midware-tools.py format [component ...]   # format one or more midware components
  python3 scripts/midware-tools.py validate [component ...] # validate midware.md sections
  python3 scripts/midware-tools.py scan                        # show computed replacements for all components

Behavior (format):
  - Scans docs/openapi/mcamel/<component> for .md files and determines versions.
  - Orders versions newest-first, removes the oldest entry (so there are at most len-1 entries).
  - Collapses patch variants of the same major.minor into vX.Y.x and link that entry to the latest patch file.
  - Picks up to 16 entries (newest-first after removal/grouping) and writes them as 4 lines with up to 4 items per line.
  - Edits docs/openapi/midware.md replacing only the lines under the component's card area.

Notes:
  - This tool tries to be conservative and safe; it will not overwrite sections it cannot parse reliably.
  - You can run with --dry-run to preview changes.

"""

import sys
from pathlib import Path
import re
import argparse

ROOT = Path('.')
MIDWARE_FILE = ROOT / 'docs' / 'openapi' / 'midware.md'
MMC_ROOT = ROOT / 'docs' / 'openapi' / 'mcamel'

VER_RE = re.compile(r'v[0-9]+(?:\.[0-9]+)*(?:[.-]x|(?:\.[0-9]+)*)?')


def parse_versions(component_path: Path):
    files = [p.name for p in component_path.iterdir() if p.suffix == '.md']
    vers = []
    for fn in files:
        m = re.search(r'(v[0-9A-Za-z.\-x]+)', fn)
        if m:
            vers.append((m.group(1), fn))
    # dedupe preserving order
    seen = []
    ordered = []
    for v,fn in sorted(vers, reverse=True):
        if v not in seen:
            seen.append(v)
            ordered.append((v, fn))
    # fallback: if not found, return empty
    return ordered


def version_key(vstr: str):
    # convert 'v0.18.4' -> (0,18,4) ; 'v0.27.x' -> (0,27,9999) to put x after specific patches? we'll place 'x' as 9999 so it sorts highest
    v = vstr.lstrip('v')
    parts = re.split('[.-]', v)
    key = []
    for p in parts:
        if p.lower() == 'x':
            key.append(9999)
        else:
            try:
                key.append(int(p))
            except ValueError:
                # non-number fallback
                key.append(0)
    return tuple(key)


def sort_versions_desc(versions):
    # versions is a list of vstrings
    return sorted(versions, key=lambda s: version_key(s), reverse=True)


def group_patch_versions(versions_with_files):
    # versions_with_files: list of tuples (vstr, filename) newest-first
    # group by major.minor -> pick latest patch as the representative and label as vMAJOR.MINOR.x
    groups = {}
    for v, fn in versions_with_files:
        # extract major.minor
        nums = re.findall(r'\d+', v)
        if not nums:
            base = v
        else:
            if len(nums) >= 2:
                base = f'v{nums[0]}.{nums[1]}'
            else:
                base = f'v{nums[0]}.0'
        groups.setdefault(base, []).append((v, fn))

    # build collapsed list newest-first: for each base keep (label, filename)
    collapsed = []
    # preserve the input newest-first order: iterate over versions_with_files and add base entry when first seen
    seen_bases = set()
    for v, fn in versions_with_files:
        nums = re.findall(r'\d+', v)
        base = f'v{nums[0]}.{nums[1]}' if len(nums) >= 2 else f'v{nums[0]}.0'
        if base in seen_bases:
            continue
        seen_bases.add(base)
        group = groups[base]
        # group is list of (v,fn) newest-first if versions_with_files was newest-first
        # pick latest patch file (first entry) as target
        latest_v, latest_fn = group[0]
        if len(group) > 1:
            label = base + '.x'
        else:
            label = latest_v
        collapsed.append((label, latest_fn))

    return collapsed


def build_lines(labels_and_files, max_items=16):
    # take up to max_items newest-first
    items = labels_and_files[:max_items]
    lines = []
    for i in range(0, len(items), 4):
        chunk = items[i:i+4]
        # convert to markdown link syntax
        parts = [f'[{lbl}](mcamel/{fn})' for (lbl, fn) in chunk]
        lines.append('    - ' + ', '.join(parts))
    # ensure exactly 4 lines; if fewer, pad empty lines
    while len(lines) < 4:
        lines.append('    -')
    return lines[:4]


def format_component_in_file(component: str, dry_run=False):
    comp_path = MMC_ROOT / component
    if not comp_path.exists():
        raise FileNotFoundError(f"component folder not found: {comp_path}")
    parsed = parse_versions(comp_path)
    if not parsed:
        raise RuntimeError(f'no versions found for {component}')
    # parsed is newest-first sorted by filename order; ensure proper sort using version_key
    # create a unique newest-first list by sorting keys
    # map to list of tuples [(v,fn)]
    unique = []
    # parsed may have filenames and vstrings unsorted; sort by key
    parsed_sorted = sorted(parsed, key=lambda x: version_key(x[0]), reverse=True)

    # remove the oldest entry (the minimum)
    if len(parsed_sorted) > 0:
        parsed_sorted = parsed_sorted[:-1]

    collapsed = group_patch_versions(parsed_sorted)
    # build up to 16
    lines = build_lines(collapsed, max_items=16)

    # read file
    s = MIDWARE_FILE.read_text(encoding='utf-8')
    # find the component block start (the label line contains the component name)
    loc = s.lower().find(component.lower())
    if loc == -1:
        raise RuntimeError('component section not found in midware.md: ' + component)
    # find the '---' divider after label and then collect the following lines until next card or next '-   :' for another card
    sep = s.find('---', loc)
    if sep == -1:
        raise RuntimeError('divider not found after component: ' + component)
    # find next card start ('\n\n-   :')
    rest = s[sep:]
    next_card = rest.find('\n\n-   :')
    if next_card == -1:
        block = rest
        block_start_idx = sep
        block_end_idx = len(s)
    else:
        block = rest[:next_card]
        block_start_idx = sep
        block_end_idx = sep + next_card
    # within block, identify the existing lines that start with '    - [' — replace the first up to 4 such lines with our new lines
    pre = s[:block_start_idx]
    block_text = s[block_start_idx:block_end_idx]
    post = s[block_end_idx:]

    old_lines = block_text.splitlines()
    out_lines = []
    replaced = 0
    for ln in old_lines:
        if ln.strip().startswith('- ['):
            if replaced < 4:
                out_lines.append(lines[replaced])
                replaced += 1
            else:
                # skip other '- [' lines beyond the first 4
                continue
        else:
            out_lines.append(ln)
    # if we didn't replace any (maybe different formatting), append lines at the end of block_text
    if replaced == 0:
        # append the constructed lines right after the divider line
        block_lines = block_text.splitlines()
        # find position after the divider (first line is '---')
        block_lines.insert(1, '\n'.join(lines))
        new_block = '\n'.join(block_lines)
    else:
        new_block = '\n'.join(out_lines)

    new_text = pre + new_block + post
    if dry_run:
        print('-- DRY RUN: would update', component)
        print('\n'.join(lines))
        return True

    MIDWARE_FILE.write_text(new_text, encoding='utf-8')
    return True


def validate_component(component: str):
    # check there are exactly 4 lines with 4 items each and that linked files exist
    s = MIDWARE_FILE.read_text(encoding='utf-8')
    loc = s.lower().find(component.lower())
    if loc == -1:
        return (False, 'section not found')
    sep = s.find('---', loc)
    rest = s[sep:]
    next_card = rest.find('\n\n-   :')
    block = rest[:next_card] if next_card != -1 else rest
    lines = [ln.strip() for ln in block.splitlines() if ln.strip().startswith('-')]
    if len(lines) != 4:
        return (False, f'expected 4 lines, found {len(lines)}')
    # each expected to have up to 4 [link] items
    total = 0
    missing = []
    for ln in lines:
        links = re.findall(r'\[([^\]]+)\]\((mcamel/[^)]+)\)', ln)
        if len(links) > 4:
            return (False, f'line has >4 items: {ln}')
        if not links:
            return (False, f'line has no version links: {ln}')
        total += len(links)
        for label, path in links:
            if not (ROOT / 'docs' / 'openapi' / path).exists():
                missing.append(path)
    if missing:
        return (False, 'missing files: ' + ','.join(missing))
    return (True, f'lines OK, total links {total}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd')
    sub.add_parser('scan')
    pfmt = sub.add_parser('format')
    pfmt.add_argument('components', nargs='*')
    pfmt.add_argument('--dry-run', action='store_true')
    pval = sub.add_parser('validate')
    pval.add_argument('components', nargs='*')

    args = parser.parse_args()

    if args.cmd == 'scan':
        # report for all directories under mcamel
        for comp_dir in sorted((MMC_ROOT).iterdir()):
            if not comp_dir.is_dir():
                continue
            comp = comp_dir.name
            parsed = parse_versions(comp_dir)
            if not parsed:
                continue
            # sort and drop oldest
            parsed_sorted = sorted(parsed, key=lambda x: version_key(x[0]), reverse=True)
            if parsed_sorted:
                parsed_sorted = parsed_sorted[:-1]
            collapsed = group_patch_versions(parsed_sorted)
            print(f'[{comp}] total source={len(parsed)} after removal/grouping={len(collapsed)}')
            for i in range(0, min(16,len(collapsed)), 4):
                print('   ',' , '.join(lbl for lbl,fn in collapsed[i:i+4]))
            print()
        sys.exit(0)

    if args.cmd == 'format':
        comps = args.components or [d.name for d in MMC_ROOT.iterdir() if d.is_dir()]
        for c in comps:
            print('format', c)
            try:
                format_component_in_file(c, dry_run=args.dry_run)
            except Exception as e:
                print('  error:', e)
        print('done')
        sys.exit(0)

    if args.cmd == 'validate':
        comps = args.components or [d.name for d in MMC_ROOT.iterdir() if d.is_dir()]
        ok=True
        for c in comps:
            ok_, msg = validate_component(c)
            print(c, ok_, msg)
            if not ok_:
                ok=False
        sys.exit(0 if ok else 1)

    parser.print_help()
