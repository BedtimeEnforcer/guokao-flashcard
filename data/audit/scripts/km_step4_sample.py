# -*- coding: utf-8 -*-
"""第四步：随机抽样（100卡/50辨析/50题），输出为可审读格式"""
import io, os, json, random

DST = r"C:/Users/Ethan/Desktop/codex/考研助手/data"
print = print

cards = [json.loads(l) for l in io.open(os.path.join(DST, "cards.jsonl"), encoding="utf-8") if l.strip()]
comps = [json.loads(l) for l in io.open(os.path.join(DST, "comparisons.jsonl"), encoding="utf-8") if l.strip()]
qs = [json.loads(l) for l in io.open(os.path.join(DST, "questions.jsonl"), encoding="utf-8") if l.strip()]

random.seed(20261013)

# 100张词卡（成实词按比例：约64成语+36实词）
idioms = [c for c in cards if c["category"] == "成语"]
words = [c for c in cards if c["category"] == "实词"]
s100 = random.sample(idioms, 64) + random.sample(words, 36)
random.shuffle(s100)

lines = []
for c in s100:
    lines.append(f'[{c["id"]}] {c["word"]}（{c["category"]}）')
    lines.append(f'  释义：{c["definition"]}')
    for cw in c.get("confusing_words", []):
        lines.append(f'  易混：{cw["word"]} —— {cw["difference"]}')
    lines.append(f'  例句：{c["example"]}')
    lines.append("")
with io.open(os.path.join(DST, "audit", "sample_100_cards.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines))

# 50组辨析
s50c = random.sample(comps, 50)
lines = []
for c in s50c:
    lines.append(f'[{c["id"]}] {" / ".join(c["words"])}')
    lines.append(f'  共：{c["similarity"]}')
    lines.append(f'  别：{c["key_difference"]}')
    lines.append(f'  析：{c["usage_difference"]}')
    lines.append("")
with io.open(os.path.join(DST, "audit", "sample_50_comparisons.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines))

# 50道题
s50q = random.sample(qs, 50)
lines = []
for q in s50q:
    lines.append(f'[{q["id"]}] {q["question"]}')
    for k in "ABCD":
        lines.append(f'  {k}. {q["options"][k]}')
    lines.append(f'  答案：{q["answer"]}')
    lines.append(f'  解析：{q["analysis"]}')
    lines.append("")
with io.open(os.path.join(DST, "audit", "sample_50_questions.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines))

print(f"抽样完成：100卡（成语64+实词36）、50组辨析、50道题")
print("输出：audit/sample_100_cards.txt、audit/sample_50_comparisons.txt、audit/sample_50_questions.txt")
for f in ["sample_100_cards.txt", "sample_50_comparisons.txt", "sample_50_questions.txt"]:
    p = os.path.join(DST, "audit", f)
    print(f"  {f}: {os.path.getsize(p)} 字节")

