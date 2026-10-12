# -*- coding: utf-8 -*-
"""第一步：建立 词->来源批次 映射，输出分类设计素材"""
import io, os, json
from collections import defaultdict

SRC = r"D:/workbuddywork/收集资料/国考逻辑填空数据/parts"
DST = r"C:/Users/Ethan/Desktop/codex/考研助手/data"

cards = [json.loads(l) for l in io.open(os.path.join(DST, "cards.jsonl"), encoding="utf-8") if l.strip()]
wset = set(c["word"] for c in cards)

# 与构建一致：按文件名字典序遍历，首现优先
word2src = {}
for f in sorted(os.listdir(SRC)):
    if f.startswith("cards_") and f.endswith(".jsonl"):
        for l in io.open(os.path.join(SRC, f), encoding="utf-8"):
            if l.strip():
                w = json.loads(l)["word"]
                if w in wset and w not in word2src:
                    word2src[w] = f

by = defaultdict(list)
for w, f in word2src.items():
    by[f].append(w)

# 输出1：批次统计 + 各批次词表
lines = []
for f in sorted(by):
    words = sorted(by[f])
    lines.append(f"### {f}（{len(words)} 个）")
    lines.append("、".join(words))
    lines.append("")
with io.open(os.path.join(DST, "audit", "km_batches.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines))

# 输出2：实词词表（word + 释义摘要），供领域分类
wlines = []
for c in cards:
    if c["category"] == "实词":
        wlines.append(f'{c["id"]}|{c["word"]}|{c["definition"][:40]}')
with io.open(os.path.join(DST, "audit", "km_words_list.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(wlines))

# 输出3：成语词表（word + 释义摘要），供分类复核
ilines = []
for c in cards:
    if c["category"] == "成语":
        ilines.append(f'{c["id"]}|{c["word"]}|{c["definition"][:36]}')
with io.open(os.path.join(DST, "audit", "km_idioms_list.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(ilines))

print("批次统计：")
for f in sorted(by):
    print(f"  {f}: {len(by[f])} 个")
print(f"覆盖词数：{len(word2src)} / 总词数 {len(wset)}")
missing = [w for w in wset if w not in word2src]
print("未映射词：", missing if missing else "无")
print()
print("已输出：audit/km_batches.txt、audit/km_words_list.txt、audit/km_idioms_list.txt")

