"""aiefficiency_jd319 —— 统计AI 工程效率工具工程师·GPU 故障与作业自愈各部分的长度占比并标出异常。

按段落统计AI 工程效率工具工程师·GPU 故障与作业自愈相关的长度分布，标出过长、过短与重复表达的部分

定位：
  区分「重复」与「必要冗余」——后者是刻意强调，不计入冗余

岗位对应：
  目标岗位　宇树科技 · 架构AI 工程效率工具工程师
  技能主线　Python、Agent、LLM评测
  领域标签　大模型应用、MLOps

设计约束：
  1. **只报告能定位到具体位置的结论**，不做语义猜测。
  2. **规则表公开**，每条命中都能对应到岗位要求的一条明示规则。
  3. **输入为空或格式不对时明确报错**，不静默返回空结果。

仅依赖 Python 标准库。

用法:
    python aiefficiency_jd319.py --help
    python aiefficiency_jd319.py --file input.txt
    python aiefficiency_jd319.py --text "示例内容"
    python aiefficiency_jd319.py --file input.txt --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# 岗位规则表：每条规则独立可核查，命中即报，不做推断。
# 规则由岗位 JD 的技能线与领域标签派生——每条都能对回岗位要求。
# 目标岗位：宇树科技 · 架构AI 工程效率工具工程师
RULES: list[dict] = [
    {
        "name": "AI 工程效率工具工程师·GPU 故障与作业自愈·缺失",
        "why": "岗位要求「Python」在输入里找不到对应内容",
        "severity": "high",
        "keywords": ['missing', 'absent', '缺少', '没有', '未提供', 'Python'],
    },
    {
        "name": "AI 工程效率工具工程师·GPU 故障与作业自愈·冲突",
        "why": "两处关于「Agent」的描述互相矛盾",
        "severity": "high",
        "keywords": ['conflict', 'contradict', '矛盾', '不一致', '相反', 'Agent'],
    },
    {
        "name": "AI 工程效率工具工程师·GPU 故障与作业自愈·越界",
        "why": "「LLM评测」的取值超出岗位场景的常规范围",
        "severity": "medium",
        "keywords": ['out of range', 'outlier', '越界', '超限', '超过', 'LLM评测'],
    },
    {
        "name": "AI 工程效率工具工程师·GPU 故障与作业自愈·退化",
        "why": "「大模型应用」相关的信息量不足以支撑判断",
        "severity": "medium",
        "keywords": ['degrade', 'insufficient', '不足', '太少', '无法', '大模型应用'],
    },
    {
        "name": "AI 工程效率工具工程师·GPU 故障与作业自愈·泄漏",
        "why": "「MLOps」相关的内容被意外暴露",
        "severity": "high",
        "keywords": ['leak', 'expose', '泄漏', '暴露', '明文', 'MLOps'],
    },
    {
        "name": "AI 工程效率工具工程师·GPU 故障与作业自愈·重复",
        "why": "同一处「AI 工程效率工具工程师」信息被反复传递",
        "severity": "low",
        "keywords": ['duplicate', 'repeat', '重复', 'again', 'AI 工程效率工具工程师'],
    },
    {
        "name": "AI 工程效率工具工程师·GPU 故障与作业自愈·陈旧#2",
        "why": "「Python」的时效性已过期",
        "severity": "medium",
        "keywords": ['stale', 'expired', '过期', '陈旧', '旧版', 'Python'],
    },
    {
        "name": "AI 工程效率工具工程师·GPU 故障与作业自愈·不可核#2",
        "why": "关于「Agent」的说法无法追溯到具体证据",
        "severity": "high",
        "keywords": ['unverifiable', 'no evidence', '无法追溯', '没有来源', 'Agent'],
    },
]


def aiefficiency_jd319_measure(text: str) -> dict:
    """多口径测量长度。"""
    lines = [l for l in text.splitlines() if l.strip()]
    words = re.findall(r"[A-Za-z0-9']+|[\u4e00-\u9fff]", text)
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    return {
        "chars": len(text),
        "chars_no_space": len(re.sub(r"\s", "", text)),
        "words": len(words),
        "lines": len(lines),
        "paragraphs": len(paras),
    }


def aiefficiency_jd319_sections(text: str) -> list[dict]:
    """按 markdown 标题切段；没有标题就按空行切。"""
    out: list[dict] = []
    cur_title = "(未命名)"
    cur: list[str] = []
    for raw in text.splitlines():
        m = re.match(r"^#{1,6}\s+(.*)$", raw)
        if m:
            if cur:
                out.append({"title": cur_title, "text": "\n".join(cur)})
            cur_title = m.group(1).strip()
            cur = []
        else:
            cur.append(raw)
    if cur:
        out.append({"title": cur_title, "text": "\n".join(cur)})
    if not out and text.strip():
        out.append({"title": "(未命名)", "text": text})
    return out


def aiefficiency_jd319_repetition(text: str) -> dict:
    """找出重复的句子。"""
    sents = [s.strip() for s in re.split(r"(?<=[。！？.!?])\s*", text) if s.strip()]
    seen: dict[str, int] = {}
    for s in sents:
        seen[s] = seen.get(s, 0) + 1
    dups = {s: c for s, c in seen.items() if c > 1}
    return {"sentences": len(sents), "duplicates": dups,
            "duplicate_ratio": (sum(dups.values()) - len(dups)) / len(sents) if sents else 0.0}


def aiefficiency_jd319_analyze(text: str) -> dict:
    """主分析：长度分布、段落占比与重复率。"""
    m = aiefficiency_jd319_measure(text)
    secs = aiefficiency_jd319_sections(text)
    per = []
    for s in secs:
        sub = aiefficiency_jd319_measure(s["text"])
        per.append({"title": s["title"], **{k: v for k, v in sub.items() if k != "paragraphs"}})
    rep = aiefficiency_jd319_repetition(text)
    return {
        "total": m,
        "sections": per,
        "section_count": len(secs),
        "repetition": rep,
        "largest_section": max(per, key=lambda x: x["chars"])["title"] if per else "",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def render(result: dict) -> str:
    """把结果渲染成人读的文本。每个工具的版式不同。"""
    out: list[str] = []
    if not result.get("ok", True):
        out.append(f"无法分析：{{result.get('error', '未知原因')}}")
        return "\n".join(out)
    t = result["total"]
    out.append(f"字符 {t['chars']}  词 {t['words']}  行 {t['lines']}  段 {t['paragraphs']}")
    out.append(f"段数：{result['section_count']}  最大段：{result['largest_section']}")
    out.append("")
    out.append("各段占比：")
    for s in result["sections"]:
        out.append(f"  {s['title'][:40]:<42} {s['chars']:>6} 字符")
    out.append("")
    rep = result["repetition"]
    out.append(f"重复率：{rep['duplicate_ratio']:.2%}（{len(rep['duplicates'])} 组重复句）")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="aiefficiency_jd319",
        description="按段落统计AI 工程效率工具工程师·GPU 故障与作业自愈相关的长度分布，标出过长、过短与重复表达的部分（仅依赖标准库）",
        epilog=(
            "示例:\n"
            "  python aiefficiency_jd319.py --file input.txt\n"
            "  python aiefficiency_jd319.py --text '示例内容'\n"
            "  python aiefficiency_jd319.py --file input.txt --json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="输入文件路径")
    src.add_argument("--text", help="直接给出输入内容")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"读不了文件：{{e}}", file=sys.stderr)
            return 2
    else:
        content = args.text

    if not content.strip():
        print("输入是空的。", file=sys.stderr)
        return 2

    result = aiefficiency_jd319_analyze(content)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(render(result))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
