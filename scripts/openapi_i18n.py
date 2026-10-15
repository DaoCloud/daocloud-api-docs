#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
openapi_i18n.py —— OpenAPI 文档英文版生成工具（JSON 字段级翻译）

【为什么需要它】
docs/openapi/ 下的 600+ 个 Swagger JSON 由各产品仓的 proto 注释生成，注释是中文，
于是 info.title / summary / description 里全是中文，英文站无法直接复用这些 JSON。

【核心约束】
只翻译「人类可读」字段，绝不触碰结构性内容。
经全量统计，承载中文的字段只有 3 个：title / description / summary。
paths、operationId、参数名、$ref、type、enum、definitions 的键名一律原样保留，
因此产出的英文 JSON 与源 JSON 结构完全一致，可被 Swagger UI 正常渲染。

【为什么用词表而不是机器翻译】
全仓 12.8 万次中文串出现，去重后只有约 2,900 个唯一串；前 1,124 个就覆盖 80% 的出现量。
用词表「一次翻译、处处复用」比逐文件机翻更一致、成本更低，也便于人工校对。

【镜像树布局】
产物放在 docs/openapi-en/，目录结构与文件名与 docs/openapi/ 完全一致。
好处：.md wrapper（内容为 `# <swagger-ui src=vX.Y.Z.json>`）与语言无关，可原样复制，
无需修改任何引用路径。

【子命令】
    scan    抽取所有待翻译串，按频次输出词表底稿
    apply   按词表生成英文树
    verify  校验英文树与中文树结构一致（防止翻译破坏 schema）
    nav     生成英文导航 openapi-nav-en.yml

仅依赖标准库。
"""

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone

# 承载人类可读文本的字段白名单。除此之外的一切内容都不翻译。
TRANSLATABLE_KEYS = ("title", "description", "summary")

# 中日韩统一表意文字，用来判断一个串是否需要翻译
CJK_RE = re.compile(r"[\u4e00-\u9fff]")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = os.path.join(REPO_ROOT, "docs", "openapi")
DEFAULT_DST = os.path.join(REPO_ROOT, "docs", "openapi-en")
DEFAULT_GLOSSARY = os.path.join(REPO_ROOT, "glossary", "openapi-glossary.json")
DEFAULT_NAV = os.path.join(REPO_ROOT, "openapi-nav.yml")
DEFAULT_NAV_EN = os.path.join(REPO_ROOT, "openapi-nav-en.yml")
DEFAULT_NAV_LABELS = os.path.join(REPO_ROOT, "glossary", "nav-labels.json")


def has_cjk(text):
    """串里是否含中文。"""
    return bool(CJK_RE.search(text))


def iter_json_files(src):
    """遍历源树下所有 Swagger JSON，返回仓库内相对路径（用 / 分隔，跨平台一致）。"""
    for root, _dirs, files in os.walk(src):
        for fn in sorted(files):
            if fn.endswith(".json"):
                full = os.path.join(root, fn)
                yield full, os.path.relpath(full, src).replace(os.sep, "/")


def iter_md_files(src):
    """遍历源树下所有 Markdown。"""
    for root, _dirs, files in os.walk(src):
        for fn in sorted(files):
            if fn.endswith(".md"):
                full = os.path.join(root, fn)
                yield full, os.path.relpath(full, src).replace(os.sep, "/")


def map_strings(node, on_string):
    """
    递归复制 node，并把所有 dict 的字符串值交给 on_string(key, value) 处理。

    只对「字典的值」调用，字典的键、list 元素的位置都保持原样，
    这样结构性字段（paths、$ref、参数名等）天然不会被碰到。
    """
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if isinstance(value, str):
                out[key] = on_string(key, value)
            else:
                out[key] = map_strings(value, on_string)
        return out
    if isinstance(node, list):
        return [map_strings(item, on_string) for item in node]
    return node


# --------------------------------------------------------------------------
# scan：抽取待翻译串，产出词表底稿
# --------------------------------------------------------------------------
def cmd_scan(args):
    counter = Counter()
    key_of = {}
    samples = {}
    files_scanned = 0

    for _full, rel in iter_json_files(args.src):
        files_scanned += 1
        with open(_full, encoding="utf-8") as f:
            data = json.load(f)

        def collect(key, value):
            if key in TRANSLATABLE_KEYS and has_cjk(value):
                text = value.strip()
                counter[text] += 1
                key_of.setdefault(text, set()).add(key)
                samples.setdefault(text, set()).add(rel)
            return value

        map_strings(data, collect)

    total_occ = sum(counter.values())
    entries = []
    for text, count in counter.most_common():
        entries.append({
            "zh": text,
            "count": count,
            "keys": sorted(key_of[text]),
            "samples": sorted(samples[text])[:3],
        })

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_dir": os.path.relpath(args.src, REPO_ROOT),
        "translatable_keys": list(TRANSLATABLE_KEYS),
        "files_scanned": files_scanned,
        "total_occurrences": total_occ,
        "unique_strings": len(entries),
        "strings": entries,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("SCAN 完成")
    print(f"  扫描 JSON      : {files_scanned}")
    print(f"  中文串出现次数 : {total_occ}")
    print(f"  唯一串数量     : {len(entries)}")
    if total_occ:
        print(f"  去重压缩比     : {100 * len(entries) / total_occ:.1f}%")
    print(f"  词表底稿已写入 : {os.path.relpath(args.out, REPO_ROOT)}")

    # 提示覆盖率：前多少个唯一串能覆盖 80% 的出现次数
    if total_occ:
        cum = 0
        for idx, entry in enumerate(entries, 1):
            cum += entry["count"]
            if cum >= 0.8 * total_occ:
                print(f"  前 {idx} 个唯一串即覆盖 80% 的出现次数")
                break

    print()
    print("  高频串 Top 10：")
    for entry in entries[:10]:
        print(f"    {entry['count']:6d}  {entry['zh'][:60]}")
    return 0


# --------------------------------------------------------------------------
# apply：按词表生成英文树
# --------------------------------------------------------------------------
def cmd_apply(args):
    if not os.path.exists(args.glossary):
        print(f"ERROR: 词表不存在：{args.glossary}", file=sys.stderr)
        return 2

    with open(args.glossary, encoding="utf-8") as f:
        glossary = json.load(f)
    # 允许词表用注释键说明用途，形如 _comment
    glossary = {k: v for k, v in glossary.items() if not k.startswith("_")}

    stats = {
        "files_total": 0,
        "files_translated": 0,
        "strings_translated": 0,
        "strings_missing": 0,
        "md_copied": 0,
        "md_needs_translation": [],
    }
    missing = Counter()
    missing_where = {}

    for full, rel in iter_json_files(args.src):
        if args.module and not rel.startswith(args.module + "/"):
            continue
        stats["files_total"] += 1
        with open(full, encoding="utf-8") as f:
            data = json.load(f)

        def translate(key, value):
            if key not in TRANSLATABLE_KEYS or not has_cjk(value):
                return value
            text = value.strip()
            if text in glossary:
                stats["strings_translated"] += 1
                return glossary[text]
            stats["strings_missing"] += 1
            missing[text] += 1
            missing_where.setdefault(text, rel)
            return value

        translated = map_strings(data, translate)

        out_path = os.path.join(args.dst, rel)
        if not args.dry_run:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(translated, f, ensure_ascii=False, indent=2)
                f.write("\n")

        if translated != data:
            stats["files_translated"] += 1

    # .md wrapper 与语言无关，原样复制；含正文的页单独标出来，需要人工/机翻
    for full, rel in iter_md_files(args.src):
        if args.module and not rel.startswith(args.module + "/"):
            continue
        with open(full, encoding="utf-8") as f:
            content = f.read()
        out_path = os.path.join(args.dst, rel)
        if not args.dry_run:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            shutil.copy2(full, out_path)
        stats["md_copied"] += 1
        if has_cjk(content):
            stats["md_needs_translation"].append(rel)

    total = stats["strings_translated"] + stats["strings_missing"]
    coverage = 100 * stats["strings_translated"] / total if total else 100.0

    print("APPLY 完成" + ("（dry-run，未落盘）" if args.dry_run else ""))
    print(f"  JSON 文件      : {stats['files_total']}（内容有变化 {stats['files_translated']}）")
    print(f"  翻译串命中     : {stats['strings_translated']}")
    print(f"  未命中(保留中文): {stats['strings_missing']}")
    print(f"  词表覆盖率     : {coverage:.1f}%")
    print(f"  Markdown 复制  : {stats['md_copied']}（其中含中文需翻译 {len(stats['md_needs_translation'])}）")
    if not args.dry_run:
        print(f"  英文树         : {os.path.relpath(args.dst, REPO_ROOT)}")

    if missing:
        report_path = os.path.join(os.path.dirname(args.glossary), "missing-strings.json")
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "unique_missing": len(missing),
            "occurrences": sum(missing.values()),
            "strings": [
                {"zh": text, "count": count, "first_seen_in": missing_where[text]}
                for text, count in missing.most_common()
            ],
        }
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"  未命中明细     : {os.path.relpath(report_path, REPO_ROOT)}")

    if stats["md_needs_translation"]:
        print()
        print("  以下 Markdown 含中文，需单独翻译（wrapper 之外的正文页）：")
        for rel in sorted(stats["md_needs_translation"]):
            print(f"    - {rel}")

    return 0


# --------------------------------------------------------------------------
# verify：校验英文树与中文树结构一致
# --------------------------------------------------------------------------
def diff_structure(src_node, dst_node, path, problems):
    """递归比较两个 JSON 的结构；只有「本来就该变」的中文串允许不同。"""
    if isinstance(src_node, dict):
        if not isinstance(dst_node, dict):
            problems.append(f"{path}: 类型不一致，源为 object，产物为 {type(dst_node).__name__}")
            return
        only_src = set(src_node) - set(dst_node)
        only_dst = set(dst_node) - set(src_node)
        if only_src:
            problems.append(f"{path}: 产物缺少键 {sorted(only_src)[:5]}")
        if only_dst:
            problems.append(f"{path}: 产物多出键 {sorted(only_dst)[:5]}")
        for key in sorted(set(src_node) & set(dst_node)):
            diff_structure(src_node[key], dst_node[key], f"{path}/{key}", problems)
        return

    if isinstance(src_node, list):
        if not isinstance(dst_node, list):
            problems.append(f"{path}: 类型不一致，源为 array，产物为 {type(dst_node).__name__}")
            return
        if len(src_node) != len(dst_node):
            problems.append(f"{path}: 数组长度不一致 {len(src_node)} -> {len(dst_node)}")
            return
        for i, (a, b) in enumerate(zip(src_node, dst_node)):
            diff_structure(a, b, f"{path}[{i}]", problems)
        return

    if isinstance(src_node, str):
        if not isinstance(dst_node, str):
            problems.append(f"{path}: 类型不一致，源为 string，产物为 {type(dst_node).__name__}")
            return
        # 源串不含中文，产物却变了 —— 说明误改了不该动的内容
        if not has_cjk(src_node) and src_node != dst_node:
            problems.append(f"{path}: 非中文串被改动 {src_node[:40]!r} -> {dst_node[:40]!r}")
        return

    if src_node != dst_node:
        problems.append(f"{path}: 原始值被改动 {src_node!r} -> {dst_node!r}")


def cmd_verify(args):
    if not os.path.isdir(args.dst):
        print(f"ERROR: 英文树不存在：{args.dst}（先跑 apply）", file=sys.stderr)
        return 2

    checked = 0
    problems = []
    for full, rel in iter_json_files(args.src):
        if args.module and not rel.startswith(args.module + "/"):
            continue
        out_path = os.path.join(args.dst, rel)
        if not os.path.exists(out_path):
            problems.append(f"{rel}: 英文树中缺少对应文件")
            continue
        checked += 1
        with open(full, encoding="utf-8") as f:
            src_data = json.load(f)
        with open(out_path, encoding="utf-8") as f:
            dst_data = json.load(f)
        before = len(problems)
        diff_structure(src_data, dst_data, rel, problems)
        if len(problems) == before:
            # 关键元信息必须完全一致
            if src_data.get("swagger") != dst_data.get("swagger"):
                problems.append(f"{rel}: swagger 版本被改动")
            if (src_data.get("info") or {}).get("version") != (dst_data.get("info") or {}).get("version"):
                problems.append(f"{rel}: info.version 被改动")

    print("VERIFY 结果")
    print(f"  比对 JSON 文件 : {checked}")
    if problems:
        print(f"  结构问题       : {len(problems)}")
        for item in problems[:30]:
            print(f"    - {item}")
        if len(problems) > 30:
            print(f"    ... 另有 {len(problems) - 30} 条")
        return 3
    print("  结构问题       : 0  —— 英文树与中文树结构一致，可安全渲染")
    return 0


# --------------------------------------------------------------------------
# nav：生成英文导航
# --------------------------------------------------------------------------
def cmd_nav(args):
    """把中文导航里的标签翻成英文，页面路径保持原样。

    注意：导航里 leaf 是 `openapi/xxx.md` 这样的页面路径，必须原样保留；
    只有非路径的标签（如「早期版本」「容器管理 OpenAPI」）才翻译。
    """
    if not os.path.exists(args.src):
        print(f"ERROR: 导航文件不存在：{args.src}", file=sys.stderr)
        return 2

    labels = {}
    if os.path.exists(args.labels):
        with open(args.labels, encoding="utf-8") as f:
            labels = json.load(f)

    try:
        import yaml
    except ImportError:
        print("ERROR: 需要 PyYAML（uv run python 或 pip install pyyaml）", file=sys.stderr)
        return 2

    with open(args.src, encoding="utf-8") as f:
        nav = yaml.safe_load(f)

    missing = set()

    def translate_label(text):
        # 页面路径不翻译
        if text.endswith(".md") or text.startswith("openapi/") or text.endswith(".yml"):
            return text
        if not has_cjk(text):
            return text
        if text in labels:
            return labels[text]
        missing.add(text)
        return text

    def walk(node):
        if isinstance(node, dict):
            return {translate_label(str(k)): walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(item) for item in node]
        if isinstance(node, str):
            return translate_label(node)
        return node

    translated = walk(nav)

    with open(args.out, "w", encoding="utf-8") as f:
        yaml.dump(translated, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=4096)

    print("NAV 完成")
    print(f"  英文导航       : {os.path.relpath(args.out, REPO_ROOT)}")
    if missing:
        print(f"  未翻译标签     : {len(missing)} 种，需补进 {os.path.relpath(args.labels, REPO_ROOT)}")
        for text in sorted(missing)[:40]:
            print(f"    - {text}")
        return 1
    print("  未翻译标签     : 0")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="OpenAPI 文档英文版生成工具（字段级 JSON 翻译 + 导航生成）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="抽取待翻译串，产出词表底稿")
    p_scan.add_argument("--src", default=DEFAULT_SRC, help="中文树目录")
    p_scan.add_argument("--out", default=os.path.join(REPO_ROOT, "glossary", "zh-strings.json"),
                        help="词表底稿输出路径")
    p_scan.set_defaults(func=cmd_scan)

    p_apply = sub.add_parser("apply", help="按词表生成英文树")
    p_apply.add_argument("--src", default=DEFAULT_SRC, help="中文树目录")
    p_apply.add_argument("--dst", default=DEFAULT_DST, help="英文树输出目录")
    p_apply.add_argument("--glossary", default=DEFAULT_GLOSSARY, help="词表文件")
    p_apply.add_argument("--module", default=None, help="只处理指定模块，如 skoala")
    p_apply.add_argument("--dry-run", action="store_true", help="只统计，不落盘")
    p_apply.set_defaults(func=cmd_apply)

    p_verify = sub.add_parser("verify", help="校验英文树与中文树结构一致")
    p_verify.add_argument("--src", default=DEFAULT_SRC, help="中文树目录")
    p_verify.add_argument("--dst", default=DEFAULT_DST, help="英文树目录")
    p_verify.add_argument("--module", default=None, help="只校验指定模块")
    p_verify.set_defaults(func=cmd_verify)

    p_nav = sub.add_parser("nav", help="生成英文导航")
    p_nav.add_argument("--src", default=DEFAULT_NAV, help="中文导航文件")
    p_nav.add_argument("--out", default=DEFAULT_NAV_EN, help="英文导航输出路径")
    p_nav.add_argument("--labels", default=DEFAULT_NAV_LABELS, help="导航标签词表")
    p_nav.set_defaults(func=cmd_nav)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
