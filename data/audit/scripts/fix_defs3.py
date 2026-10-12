# -*- coding: utf-8 -*-
"""最后3条轻微偏薄条目修订"""
import io, os, json

BASE = r"D:/workbuddywork/收集资料/国考逻辑填空数据/parts"

UPD = {
    "初露锋芒": {"definition": "比喻刚开始显露出力量或才干，多指年轻新秀。"},
    "多此一举": {"definition": "指做了多余的、不必要的事，多含不以为然之意。"},
    "无师自通": {"confusing_words": [
        {"word": "自学成才", "difference": "无师自通强调不经老师传授就能通晓掌握，多指知识、技艺；自学成才强调依靠自学成长为人才，侧重人的成长与成就。"}
    ]},
}

for f in sorted(os.listdir(BASE)):
    if not (f.startswith("cards_idioms") and f.endswith(".jsonl")):
        continue
    p = os.path.join(BASE, f)
    rows = []
    changed = 0
    with io.open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                o = json.loads(line)
                w = o.get("word", "")
                if w in UPD:
                    o.update(UPD[w])
                    changed += 1
                rows.append(o)
    if changed:
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            for o in rows:
                fh.write(json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "\n")
        print(f"{f}: 修订 {changed} 条")
print("完成")

