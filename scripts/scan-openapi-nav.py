#!/usr/bin/env python3
"""
scan-openapi-nav.py — 巡检 openapi-nav.yml 与 docs/openapi/ 的一致性

【这是什么 / 为什么需要它】
本仓库（DaoCloud/daocloud-api-docs）有两样东西会流向主仓库 DaoCloud-docs 的文档站：

    1. docs/openapi/     —— 全部 OpenAPI 页面（CI 里被 `cp dao-openapi/docs/openapi docs/zh/docs/` 拷走）
    2. openapi-nav.yml   —— 站点导航树（被主仓库 scripts/merged_nav.py 读进 navigation.yml）

这两边必须对得上：nav 里指向的 md 必须真实存在，仓库里的 md 想被访问到就得挂进 nav。
本脚本就是把两边对一遍，报告三类问题。属于**人工巡检工具**，CI 不会执行它。

【用法】
    cd <仓库根目录>          # 必须！脚本用相对路径 openapi-nav.yml / docs/openapi 读文件，跑到别的目录会报 2
    python3 scripts/scan-openapi-nav.py
无第三方依赖，只用标准库（re / os / sys / collections）。

【检查项与输出】
    1. Duplicates in nav  —— 同一个 md 在 nav 里被引用了多次（多为复制粘贴导致的重复挂载）
    2. Broken references  —— nav 里指向的 openapi/xxx.md 在 docs/ 下不存在（会造成 404、本地 build 报断链）
    3. 未挂载的 md        —— docs/openapi/ 下有、但 nav 里没有的页面

【退出码】
    0 = 全部正常
    1 = 存在「有 md 但没挂进 nav」（**提示级**，不一定是错误）
    2 = 仓库根目录下找不到 openapi-nav.yml（通常是 cwd 不对）
    3 = 存在重复引用或断链（需要修）

【实现方式与注意】
    - 找引用靠的是对 nav 文件做**文本正则**扫描（`openapi/....md`），并不解析 YAML。
      所以只有 `openapi/xxx.md` 这种裸相对路径写法能被识别（当前 nav 就是这么写的）；
      一旦有人改成别的写法（带引号、省略 openapi/ 前缀等），这里会静默漏掉。
    - 「未挂载」只作提示。有些页面是**故意不挂**的，例如 openapi/api-doc-flow.md，
      以及 baize / leopard / skoala / zestu 下个别尚未整理进导航的版本，不要一看到就无脑补挂。
    - 统计「已挂载」用的是 paths 全量（含重复），「唯一路径数」才是去重后的数字。
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

# nav 里的引用一律写成 openapi/后面加路径.md 的裸相对路径，直接正则抓出来
paths = re.findall(r'openapi/[\w\-/.]+\.md', nav_text)
count = Counter(paths)
# 出现次数 > 1 = 同一个页面在导航树里被挂了多次
duplicates = [p for p, c in count.items() if c > 1]

# 断链：nav 写的是 openapi/xxx.md，落盘位置是 docs/openapi/xxx.md，所以要补上 docs/ 前缀
broken_refs = [p for p in paths if not os.path.exists(os.path.join('docs', p))]

# 反向收集：把 docs/openapi 下真实存在的 md 全部找出来，转成和 nav 同一种「相对仓库根」的写法
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
