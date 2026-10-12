# -*- coding: utf-8 -*-
"""批量修复偏短释义（扩充到规范长度，保持原意）"""
import io, os, json

BASE = r"D:/workbuddywork/收集资料/国考逻辑填空数据/parts"

FIXES = {
    "cards_idioms_6b.jsonl": {
        "持之以恒": "指长久地坚持下去，不半途而废；形容有恒心、能持久。",
    },
    "cards_words_2e.jsonl": {
        "境地": "所处的境况、处境；多指陷入的某种特定状况。",
        "职责": "职务上应尽的责任；指岗位或职务范围内应承担的事务。",
    },
    "cards_words_2f.jsonl": {
        "恰巧": "凑巧，正好碰上；强调偶然、正巧遇上某种情况。",
        "无须": "不需要，用不着；用于说明没有必要做某事。",
        "依然": "跟原来一样，照旧；表示情况或状态没有发生变化。",
        "略微": "稍微，程度很轻；表示数量或程度只有轻微变化。",
    },
}

for fn, fmap in FIXES.items():
    p = os.path.join(BASE, fn)
    rows = []
    hit = 0
    with io.open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                o = json.loads(line)
                if o.get("word") in fmap:
                    o["definition"] = fmap[o["word"]]
                    hit += 1
                rows.append(o)
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        for o in rows:
            fh.write(json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"{fn}: 修复 {hit}/{len(fmap)} 条，共 {len(rows)} 行")
print("完成")

