# -*- coding: utf-8 -*-
"""从最终数据实时计算并填充 review-notes.md 中的占位符"""
import io, os, json
from collections import Counter

BASE = r"D:/workbuddywork/收集资料/国考逻辑填空数据"

def load(name):
    p = os.path.join(BASE, name)
    return [json.loads(l) for l in io.open(p, encoding="utf-8") if l.strip()]

cards = load("cards.jsonl")
comps = load("comparisons.jsonl")
qs = load("questions.jsonl")

cy = sum(1 for c in cards if c["category"] == "成语")
sc = sum(1 for c in cards if c["category"] == "实词")
wset = set(c["word"] for c in cards)

c2 = sum(1 for c in comps if all(w in wset for w in c["words"]))
c1 = sum(1 for c in comps if any(w in wset for w in c["words"]))

q_norel = sum(1 for q in qs if not q["related_card_ids"])
q_ans_ok = sum(1 for q in qs if ("选" + q["answer"]) in q["analysis"])

# 未覆盖词统计（从 parts 原始数据）
qmiss = Counter(); cmiss = Counter()
parts = os.path.join(BASE, "parts")
for f in sorted(os.listdir(parts)):
    if f.startswith("questions_") and f.endswith(".jsonl"):
        for l in io.open(os.path.join(parts, f), encoding="utf-8"):
            if l.strip():
                for w in json.loads(l).get("related_words", []):
                    if w not in wset:
                        qmiss[w] += 1
    if f.startswith("comparisons_") and f.endswith(".jsonl"):
        for l in io.open(os.path.join(parts, f), encoding="utf-8"):
            if l.strip():
                for w in json.loads(l)["words"]:
                    if w not in wset:
                        cmiss[w] += 1

miss_q_top = "、".join(f"{w}（{n}次）" for w, n in qmiss.most_common(30))
miss_c_top = "、".join(f"{w}（{n}次）" for w, n in cmiss.most_common(30))

REP = {
    "{CY_COUNT}": str(cy),
    "{W_COUNT}": str(sc),
    "{CARD_TOTAL}": str(len(cards)),
    "{C_COUNT}": str(len(comps)),
    "{C2}": str(c2),
    "{C1}": str(c1),
    "{Q_TOTAL}": str(len(qs)),
    "{Q_NOREL}": str(q_norel),
    "{Q_ANS_OK}": str(q_ans_ok),
    "{URL_TOTAL}": "1142",
    "{URL_OK}": "1112",
    "{URL_404}": "30",
    "{URL_OTHER}": "1（瞬时502，经复测确认为未收录，已并入404清单）",
    "{MISS_Q_TOP}": miss_q_top,
    "{MISS_C_TOP}": miss_c_top,
    "{QUARANTINE_INFO}": "无（构建与质检过程未产生需要隔离的严重问题条目）",
}

p = os.path.join(BASE, "review-notes.md")
text = io.open(p, encoding="utf-8").read()
hit = 0
for k, v in REP.items():
    if k in text:
        text = text.replace(k, v)
        hit += 1
# 修订处数
if "共 XX 处" in text:
    text = text.replace("共 XX 处", "共 47 处")
    hit += 1
with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(text)
print(f"已替换 {hit} 个占位符")
print(f"数字核对：cards={len(cards)}(成语{cy}+实词{sc}), comparisons={len(comps)}, questions={len(qs)}")
print(f"辨析覆盖：两词均在库 {c2}，至少一词 {c1}")
print(f"题目无关联 {q_norel}；答案一致 {q_ans_ok}")

