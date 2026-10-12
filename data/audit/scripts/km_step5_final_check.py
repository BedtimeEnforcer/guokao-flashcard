# -*- coding: utf-8 -*-
"""第五步：最终全量检查（文件/数据/关联/统计），输出 final-check-report.md"""
import io, os, json
from collections import Counter

DST = r"C:/Users/Ethan/Desktop/codex/考研助手/data"
R = []
def w(s=""):
    R.append(s)

def load_jsonl(name):
    rows, bad = [], []
    p = os.path.join(DST, name)
    with io.open(p, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            s = line.strip()
            if not s:
                continue
            try:
                rows.append(json.loads(s))
            except Exception as e:
                bad.append((i, str(e)[:60]))
    return rows, bad

cards, bad_c = load_jsonl("cards.jsonl")
comps, bad_m = load_jsonl("comparisons.jsonl")
qs, bad_q = load_jsonl("questions.jsonl")

w("# 最终数据检查报告（自动生成）")
w()
w("## 一、文件检查（UTF-8 / JSON 格式 / 每行一个对象）")
w(f"- cards.jsonl：{len(cards)} 行，解析错误 {len(bad_c)}")
w(f"- comparisons.jsonl：{len(comps)} 行，解析错误 {len(bad_m)}")
w(f"- questions.jsonl：{len(qs)} 行，解析错误 {len(bad_q)}")
if bad_c or bad_m or bad_q:
    for idx, e in (bad_c + bad_m + bad_q)[:20]:
        w(f"  ！解析错误行：{idx} {e}")
km = json.load(io.open(os.path.join(DST, "knowledge-map.json"), encoding="utf-8"))
w(f"- knowledge-map.json：解析成功（{len(km['categories'])} 个分类）")
w()

w("## 二、数据检查（ID 唯一 / 字段完整 / 无重复）")
cids = [c["id"] for c in cards]
cids_ok = len(set(cids)) == len(cids)
w(f"- 卡片 ID 唯一：{'通过' if cids_ok else '不通过'}（{len(cids)} 个）")
w(f"- 辨析 ID 唯一：{'通过' if len(set(c['id'] for c in comps)) == len(comps) else '不通过'}")
w(f"- 题目 ID 唯一：{'通过' if len(set(q['id'] for q in qs)) == len(qs) else '不通过'}")

card_fields = ["id", "word", "category", "definition", "context", "collocations", "confusing_words", "example", "misuse", "difficulty", "tags", "source_url", "source_reference"]
miss_f = [c["id"] for c in cards if any(k not in c for k in card_fields)]
w(f"- 卡片字段完整：{'通过' if not miss_f else '缺失 ' + ','.join(miss_f[:10])}")
comp_fields = ["id", "words", "similarity", "key_difference", "usage_difference", "examples", "source"]
miss_f2 = [c["id"] for c in comps if any(k not in c for k in comp_fields)]
w(f"- 辨析字段完整：{'通过' if not miss_f2 else '缺失 ' + ','.join(miss_f2[:10])}")
q_fields = ["id", "question", "options", "answer", "analysis", "knowledge_point", "related_card_ids"]
miss_f3 = [q["id"] for q in qs if any(k not in q for k in q_fields)]
w(f"- 题目字段完整：{'通过' if not miss_f3 else '缺失 ' + ','.join(miss_f3[:10])}")

dup_w = [x for x, n in Counter(c["word"] for c in cards).items() if n > 1]
w(f"- 词条无重复：{'通过' if not dup_w else '重复 ' + ','.join(dup_w[:10])}")
dup_q = [x for x, n in Counter(q["question"] for q in qs).items() if n > 1]
w(f"- 题目无重复：{'通过' if not dup_q else '重复 ' + str(len(dup_q))}")
dup_m = [x for x, n in Counter(tuple(sorted(c["words"])) for c in comps).items() if n > 1]
w(f"- 辨析对无重复：{'通过' if not dup_m else '重复 ' + str(len(dup_m))}")
w()

w("## 三、关联检查（引用存在性）")
idset = set(cids)
bad_rel = [q["id"] for q in qs if any(r not in idset for r in q["related_card_ids"])]
w(f"- 题目关联 card_id 全部存在：{'通过' if not bad_rel else '悬空 ' + ','.join(bad_rel[:10])}")
rel_cnt = sum(1 for q in qs if q["related_card_ids"])
w(f"- 有关联的题目：{rel_cnt}/{len(qs)}")

km_ids = [i for cat in km["categories"] for i in cat["card_ids"]]
km_bad = [i for i in km_ids if i not in idset]
km_dup = [x for x, n in Counter(km_ids).items() if n > 1]
w(f"- knowledge-map 分类内 card_id 全部存在：{'通过' if not km_bad else '悬空 ' + ','.join(km_bad[:10])}")
w(f"- knowledge-map 卡片无重复归类：{'通过' if not km_dup else '重复 ' + ','.join(km_dup[:10])}")
km_cover = len(set(km_ids)) == len(idset)
w(f"- knowledge-map 覆盖全部卡片（{len(set(km_ids))}/{len(idset)}）：{'通过' if km_cover else '不通过'}")
idx_ok = len(km["card_index"]) == len(idset) and all(km["card_index"].get(i) in [c["id"] for c in km["categories"]] for i in idset)
w(f"- knowledge-map 反查表完整且指向有效分类：{'通过' if idx_ok else '不通过'}")
w()

w("## 四、数量统计")
w(f"- cards.jsonl：{len(cards)} 条（成语 {sum(1 for c in cards if c['category'] == '成语')} + 实词 {sum(1 for c in cards if c['category'] == '实词')}）")
w(f"- comparisons.jsonl：{len(comps)} 组")
w(f"- questions.jsonl：{len(qs)} 道")
w(f"- knowledge-map.json：{len(km['categories'])} 个分类，标签索引 {len(km['tags_index'])} 种")
w()
w("生成时间：2026-10-13（自动检查）")

text = "\n".join(R)
with io.open(os.path.join(DST, "audit", "final-check-report.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(text)
print(text)

