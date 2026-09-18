#!/usr/bin/env python3
"""
midware-tools.py — 维护 docs/openapi/midware.md 里各中间件卡片的「版本链接列表」

【这是什么 / 为什么需要它】
docs/openapi/midware.md 是「中间件 OpenAPI 文档」索引页，用 material 的 grid cards 排版：
每个中间件一张卡片，卡内**最多 4 行、每行最多 4 个版本链接**，例如：

    -   :simple-elasticsearch:{ .lg .middle } __Elasticsearch OpenAPI__
                                    <- 空行
        ---                         <- 卡片分隔线，脚本以此为定位锚点
                                    <- 空行
        - [v0.29.0](mcamel/elasticsearch/elasticsearch-v0.29.0.md), [v0.28.x](...), ...
        ... 另外 3 行

版本数据来源是 docs/openapi/mcamel/<组件>/*.md（如 mcamel/elasticsearch/elasticsearch-v0.29.0.md）。
每发一版中间件，就往对应目录加一对 vX.Y.Z.md + vX.Y.Z.json，然后跑本脚本把卡片刷新成最新的 16 个版本。
仓库现在的中间件组件：elasticsearch / kafka / minio / mongodb / mysql / postgresql / rabbitmq /
redis / rocketmq / seaweedfs。属于**人工运行的工具**，CI 不会执行它。

【用法】
    cd <仓库根目录>          # 必须！脚本用相对路径 docs/openapi/... 读写文件
    python3 scripts/midware-tools.py scan                      # 只读预览，不改文件
    python3 scripts/midware-tools.py format [组件...] [--dry-run]   # 改写 midware.md
    python3 scripts/midware-tools.py validate [组件...]        # 校验卡片格式
无第三方依赖，只用标准库（sys / pathlib / re / argparse）。

【三个子命令】
    scan      只读。列出每个组件「扫描到的版本数 → 去重/折叠后剩余数」，并打印前 16 个标签。
              上线新版后先跑它看一眼，确认选取结果符合预期。
    format    真正改写 midware.md。不带组件名 = 处理 mcamel/ 下所有组件（**注意会批量改**）；
              带 --dry-run 只打印将写入的 4 行、不落盘。
    validate  校验每张卡片：是否恰好 4 行、每行是否 1~4 个链接、链接指向的文件是否存在。
              退出码 0 = 全过，1 = 有不合格。

【版本选取规则（scan 与 format 共用同一套逻辑）】
    1. 读 mcamel/<组件>/ 下所有 .md，从文件名里抠出版本号
    2. 按版本从新到旧排序
    3. **丢掉最旧的 1 个**（保留数 = 总数 - 1），避免页面尾部堆积远古版本
    4. 按 major.minor 折叠：同一个 vX.Y 下有多个 patch 时合并成一条 vX.Y.x，
       链接指向该系列**最新的 patch** 文件；只有单个 patch 时保留 vX.Y.Z 原样
    5. 取前 16 条，每行 4 条、最多 4 行；条数不足就只输出实际用到的行数（不用空行去凑）

【写入的保守性】
format 只在卡片分隔线之后、下一张卡片（`-   :`）之前，替换以 `- [` 开头的版本链接行（最多 4 行），
图标、`__标题__`、说明文字等其它内容原样保留；一行 `- [` 都没匹配到就不写。分隔线后面的空行、
以及最后一张卡片块尾的换行都会保住，所以「这一项不需要改」时输出与输入逐字节一致。

────────────────────────────────────────────────────────────────────────────
【修复记录 —— 2026-09-18】
这版修掉了 4 个 bug。修之前这个工具的输出是不能用的，别拿旧版本的结果去改 midware.md：
    1. 链接路径缺组件目录名。build_lines() 写死 `mcamel/{fn}`，正确应为 `mcamel/<组件>/{fn}`；
       原样跑会把链接写成 `mcamel/elasticsearch-v0.29.0.md`，而真实路径是
       `mcamel/elasticsearch/elasticsearch-v0.29.0.md` → 全站 404。
    2. 标签多带 `.md`。parse_versions() 原用字符类 `[0-9A-Za-z.\-x]+`，字符类里的 `.` 把文件名的
       扩展名也吞了进去，「只有单个 patch」的条目会渲染成 `[v0.29.0.md]`（应为 `[v0.29.0]`）。
       现改为锚定的 VER_RE。
    3. validate 必然失败。原过滤条件 `startswith('-')` 会把卡片分隔线 `---`（strip 后同样以 `-` 开头）
       也算成版本行，导致普遍报 "expected 4 lines, found 5"；rocketmq 因刚好凑够 4 行，
       改报 "line has no version links: ---"。现改为 `startswith('- [')`。
    4. format 与 validate 自相矛盾。原 build_lines() 用空的 `-` 行把结果补齐到 4 行，而 validate 又要求
       每行都必须有链接 —— 于是只要某组件不足 16 个版本，format 的产物必然过不了自家 validate。
       现在不再补齐，validate 也相应放宽为 1~4 行（与 midware.md 真实写法一致）。
    另外：删掉了从未被调用的 sort_versions_desc()；把 major.minor 的推导抽成 base_of()，消除原先
    两处重复实现（其中一处在版本串解析不出数字时会 IndexError）。

【跑 format 前仍需人工确认的一点：vX.Y.x 该指向哪个 patch】
工具的规则是「vX.Y.x 指向该系列**最新**的 patch」。但现网 midware.md 里 26 个 vX.Y.x 标签中，
22 个指向该系列的 **.0**、只有 4 个（postgresql v0.18.x / v0.5.x、redis v0.27.x、rocketmq v0.15.x）
指向更新的 patch —— 两种写法并存，说明这个文件一直是**手工维护**的，并没有在跑本工具。
所以直接跑 format 会改写那 22 条。这个语义变化请先 `format --dry-run` 逐项确认再决定是否落盘。
────────────────────────────────────────────────────────────────────────────
"""

import sys
from pathlib import Path
import re
import argparse

ROOT = Path('.')
MIDWARE_FILE = ROOT / 'docs' / 'openapi' / 'midware.md'
MMC_ROOT = ROOT / 'docs' / 'openapi' / 'mcamel'

# 从文件名里抠版本号：只认「v主.次[.补丁]」这种形态（如 elasticsearch-v0.29.0.md → v0.29.0）。
# 千万不要写成 [0-9A-Za-z.\-x]+ 之类的宽松字符类——字符类里的 `.` 会把文件名的 `.md`
# 一起吞进来，抠出 'v0.29.0.md' 这种脏值，最终渲染成 `[v0.29.0.md](...)`（2026-09-18 修掉的 bug）。
VER_RE = re.compile(r'(v\d+(?:\.\d+)+)')

# 卡片的 `---` 分隔线（卡片标题与链接区之间那一条）
DIVIDER = '---'
# 下一张卡片的起始标志（material grid cards 的写法）
NEXT_CARD = '\n\n-   :'


def parse_versions(component_path: Path):
    """从组件目录下所有 .md 的文件名里抠出版本号，返回 [(版本串, 文件名), ...]。

    只认 .md，同名的 .json 会被忽略（.json 是 swagger 源文件，不参与链接）。
    结果按版本串做过一次去重（排序保留第一个），调用方还会用 version_key 做一次数值排序。
    """
    files = [p.name for p in component_path.iterdir() if p.suffix == '.md']
    vers = []
    for fn in files:
        m = VER_RE.search(fn)
        if m:
            vers.append((m.group(1), fn))
    # 同目录下一个版本只会有一个文件；这里仍按版本去重，防止有人手动放进重复文件
    seen = set()
    ordered = []
    for v, fn in sorted(vers, reverse=True):
        if v not in seen:
            seen.add(v)
            ordered.append((v, fn))
    # 一个版本都没解析出来就是空列表，交由调用方报错
    return ordered


def version_key(vstr: str):
    """把版本串转成可比较的元组：'v0.18.4' -> (0,18,4)。

    版本串里若出现 'x'（如 'v0.27.x'），按 9999 处理，让它排在同系列任何具体 patch 之后。
    """
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
                # 非数字段按 0 处理（正常数据不会走到这里）
                key.append(0)
    return tuple(key)


def base_of(vstr: str) -> str:
    """取版本串的 major.minor，作为「同一系列」的分组键。'v0.29.0' / 'v0.29.1' -> 'v0.29'。"""
    nums = re.findall(r'\d+', vstr)
    if len(nums) >= 2:
        return f'v{nums[0]}.{nums[1]}'
    if len(nums) == 1:
        return f'v{nums[0]}.0'
    return vstr  # 兜底：解析不出数字就按原串分组，绝不抛异常


def group_patch_versions(versions_with_files):
    """按 major.minor 折叠版本，返回折叠后的 [(标签, 文件名), ...]（顺序与入参一致）。

    入参必须是**从新到旧**排序过的 [(版本串, 文件名), ...]（调用方已用 version_key 排好）。
    同一个 major.minor 下有多个 patch 时：
      - 标签合并成 vX.Y.x（表示「这一整个小版本系列」）
      - 链接指向该系列**最新**的那个 patch 文件
    只有一个 patch 时标签就是它自己的版本号。
    """
    # 先按 major.minor 归组，组内保持入参的从新到旧顺序
    groups = {}
    for v, fn in versions_with_files:
        groups.setdefault(base_of(v), []).append((v, fn))

    collapsed = []
    seen_bases = set()
    for v, fn in versions_with_files:
        base = base_of(v)
        if base in seen_bases:
            continue
        seen_bases.add(base)
        group = groups[base]              # 组内第一个 = 最新 patch
        latest_v, latest_fn = group[0]
        label = base + '.x' if len(group) > 1 else latest_v
        collapsed.append((label, latest_fn))

    return collapsed


def build_lines(component, labels_and_files, max_items=16):
    """把 (标签, 文件名) 列表渲染成卡片里的 markdown 链接行，每行最多 4 个、最多 4 行。

    链接必须是 `mcamel/<组件>/<文件名>`（相对 docs/openapi/ 的路径），
    所以组件名要传进来——早期版本写死了 `mcamel/{文件名}`，缺一截目录导致链接全部 404。
    条数不足 16 时**不补齐**：只输出实际需要的行数（与 midware.md 现有各卡片的写法一致，
    例如 rocketmq 3 行、seaweedfs 2 行）。
    """
    items = labels_and_files[:max_items]          # 只保留最新的 max_items 条
    lines = []
    for i in range(0, len(items), 4):
        chunk = items[i:i+4]
        parts = [f'[{lbl}](mcamel/{component}/{fn})' for (lbl, fn) in chunk]
        lines.append('    - ' + ', '.join(parts))
    return lines[:4]


def format_component_in_file(component: str, dry_run=False):
    """把 midware.md 里 component 这张卡片的版本链接行重写成按规则算出的 4 行。

    只替换卡片内以 `- [` 开头的前 4 行，卡片标题/图标/其它文字保持原样；
    一行都没匹配到（例如卡片格式被改过）就不写，宁可不改也不破坏。
    """
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

    # 丢掉最旧的那一条（选取规则第 3 步），避免卡片尾部一直堆远古版本
    if len(parsed_sorted) > 0:
        parsed_sorted = parsed_sorted[:-1]

    collapsed = group_patch_versions(parsed_sorted)
    lines = build_lines(component, collapsed, max_items=16)

    s = MIDWARE_FILE.read_text(encoding='utf-8')
    # 定位卡片块：从组件名之后的第一个分隔线，到下一张卡片（`-   :`）之前
    loc = s.lower().find(component.lower())
    if loc == -1:
        raise RuntimeError('component section not found in midware.md: ' + component)
    sep = s.find(DIVIDER, loc)
    if sep == -1:
        raise RuntimeError('divider not found after component: ' + component)
    rest = s[sep:]
    next_card = rest.find(NEXT_CARD)
    block_start_idx = sep
    block_end_idx = len(s) if next_card == -1 else sep + next_card

    pre = s[:block_start_idx]
    block_text = s[block_start_idx:block_end_idx]
    post = s[block_end_idx:]
    # 最后一张卡片（seaweedfs）的块尾带换行符，splitlines/join 会吃掉，这里单独保住
    trailing = '\n' if block_text.endswith('\n') else ''

    # 卡片内以 `- [` 开头的行就是版本链接行，其余（标题、图标、说明）一律原样保留
    out_lines = []
    replaced = 0
    for ln in block_text.splitlines():
        if ln.strip().startswith('- ['):
            if replaced < len(lines):
                out_lines.append(lines[replaced])
                replaced += 1
            else:
                # 新条目比旧行少（多个 patch 被折叠成一条 vX.Y.x）——多出来的旧行直接丢掉
                continue
        else:
            out_lines.append(ln)

    if replaced == 0:
        # 兜底：卡片里一行 `- [` 都没有（说明格式被改过）。把新内容插到分隔线之后、
        # 紧随其后的空行**下面**，以保持 material grid cards 需要的「分隔线 / 空行 / 列表」排版
        block_lines = block_text.splitlines()
        insert_at = 1
        while insert_at < len(block_lines) and block_lines[insert_at].strip() == '':
            insert_at += 1
        block_lines[insert_at:insert_at] = lines
        new_block = '\n'.join(block_lines)
    else:
        new_block = '\n'.join(out_lines)

    new_block += trailing

    new_text = pre + new_block + post
    if dry_run:
        print('-- DRY RUN: would update', component)
        print('\n'.join(lines))
        return True

    MIDWARE_FILE.write_text(new_text, encoding='utf-8')
    return True


def validate_component(component: str):
    """校验某组件卡片：1~4 行、每行 1~4 个 [标签](mcamel/...) 链接、且被链接的文件都存在。

    行数上限 4 是排版要求（卡片高度），下限 1 是因为版本少的组件本来就排不满
    （如 seaweedfs 只有 1 行），不会用空行去凑。

    :return: (是否通过, 说明文字)
    """
    s = MIDWARE_FILE.read_text(encoding='utf-8')
    loc = s.lower().find(component.lower())
    if loc == -1:
        return (False, 'section not found')
    # 定位卡片块：从组件名之后的第一个分隔线，到下一张卡片（`-   :`）之前
    sep = s.find(DIVIDER, loc)
    rest = s[sep:]
    next_card = rest.find(NEXT_CARD)
    block = rest[:next_card] if next_card != -1 else rest
    # 只认以 `- [` 开头的行才是版本链接行。注意别写成 startswith('-')——卡片分隔线 strip 后是
    # `---`，同样以 `-` 开头，会被误算成一行，导致行数永远多 1（2026-09-18 修掉的 bug）。
    lines = [ln.strip() for ln in block.splitlines() if ln.strip().startswith('- [')]
    if not (1 <= len(lines) <= 4):
        return (False, f'expected 1~4 lines, found {len(lines)}')
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
        # 不带组件名 = mcamel/ 下全部组件，会批量改写 midware.md。第一次跑请务必先加 --dry-run
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
