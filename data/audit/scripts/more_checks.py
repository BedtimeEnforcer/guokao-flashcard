# -*- coding: utf-8 -*-
"""内容质量深度抽查：对最终三个文件输出可疑条目清单到 more-checks.md"""
import io, os, sys, json

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"D:/workbuddywork/收集资料/国考逻辑填空数据"

def load(name):
    rows = []
    p = os.path.join(BASE, name)
    if not os.path.exists(p):
        return rows
    with io.open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def main():
    out = []
    def w(s=""): out.append(s)

    cards = load("cards.jsonl")
    comps = load("comparisons.jsonl")
    qs = load("questions.jsonl")

    w("# 深度抽查清单（交付前内容巡检）")
    w()

    # ---- 词卡 ----
    w("## 一、词卡：内容偏薄或字段空缺")
    w()
    thin = []
    for c in cards:
        issues = []
        if len(c["definition"]) < 15: issues.append(f"释义仅{len(c['definition'])}字")
        if len(c["context"]) < 8: issues.append("语境说明短")
        if len(c["example"]) < 12: issues.append(f"例句仅{len(c['example'])}字")
        if len(c.get("misuse", "")) < 8: issues.append("误用提示短")
        if not c.get("confusing_words"): issues.append("无易混词")
        if not c.get("tags"): issues.append("无标签")
        if not c.get("collocations"): issues.append("无搭配")
        if issues:
            thin.append((c["id"], c["word"], "；".join(issues)))
    w(f"合计 {len(thin)} 条（占 {len(cards)} 条词卡的 {len(thin)*100//max(len(cards),1)}%）")
    for r in thin[:100]:
        w(f"- {r[0]} {r[1]}：{r[2]}")
    w()

    # ---- 辨析 ----
    w("## 二、辨析：内容偏薄")
    w()
    thin2 = []
    for c in comps:
        issues = []
        if len(c["usage_difference"]) < 60: issues.append(f"用法辨析仅{len(c['usage_difference'])}字")
        if len(c["key_difference"]) < 20: issues.append("核心区别短")
        if len(c.get("examples", [])) < 2: issues.append("例句不足2句")
        if issues:
            thin2.append((c["id"], "/".join(c["words"]), "；".join(issues)))
    w(f"合计 {len(thin2)} 组（占 {len(comps)} 组的 {len(thin2)*100//max(len(comps),1)}%）")
    for r in thin2[:60]:
        w(f"- {r[0]} {r[1]}：{r[2]}")
    w()

    # ---- 题目 ----
    w("## 三、题目：解析偏薄或字段空缺")
    w()
    thin3 = []
    for q in qs:
        issues = []
        if len(q["analysis"]) < 100: issues.append(f"解析仅{len(q['analysis'])}字")
        if not q.get("knowledge_point"): issues.append("无考点标注")
        if not q.get("related_card_ids"): issues.append("无关联词卡")
        for opt, val in q["options"].items():
            if len(val) == 0: issues.append(f"选项{opt}为空")
        if issues:
            thin3.append((q["id"], "；".join(issues)))
    w(f"合计 {len(thin3)} 道（占 {len(qs)} 道的 {len(thin3)*100//max(len(qs),1)}%）")
    for r in thin3[:80]:
        w(f"- {r[0]}：{r[1]}")
    w()

    with io.open(os.path.join(BASE, "more-checks.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    print("\n".join(out[:60]))
    print(f"\n...完整清单已写入 more-checks.md（共 {len(out)} 行）")

if __name__ == "__main__":
    main()

