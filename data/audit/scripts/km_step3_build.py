# -*- coding: utf-8 -*-
"""第三步：生成 knowledge-map.json（知识地图：分类索引 + 标签索引 + 反查表）"""
import io, os, json
from collections import defaultdict, Counter

DST = r"C:/Users/Ethan/Desktop/codex/考研助手/data"
PARTS = r"D:/workbuddywork/收集资料/国考逻辑填空数据/parts"

cards = [json.loads(l) for l in io.open(os.path.join(DST, "cards.jsonl"), encoding="utf-8") if l.strip()]
by_id = {c["id"]: c for c in cards}
wset = set(c["word"] for c in cards)

# ---------- 成语：来源批次 -> 分类 ----------
word2src = {}
for f in sorted(os.listdir(PARTS)):
    if f.startswith("cards_idioms_") and f.endswith(".jsonl"):
        for l in io.open(os.path.join(PARTS, f), encoding="utf-8"):
            if l.strip():
                w = json.loads(l)["word"]
                if w in wset and w not in word2src:
                    word2src[w] = f

def idiom_cat_of(word):
    f = word2src.get(word, "")
    if f.startswith("cards_idioms_1"):
        return "idiom_01"
    if f.startswith("cards_idioms_2"):
        return "idiom_02"
    if f.startswith("cards_idioms_3"):
        return "idiom_03"
    if f.startswith("cards_idioms_4"):
        return "idiom_04"
    if f.startswith("cards_idioms_5"):
        return "idiom_05"
    if f.startswith(("cards_idioms_6", "cards_idioms_7")):
        return "idiom_06"
    return None

# ---------- 实词：领域分类 ----------
words_cat = json.load(io.open(os.path.join(DST, "audit", "km_words_cat.json"), encoding="utf-8"))
WORD_CAT_MAP = {
    1: ("word_01", "政策治理与公共管理"),
    2: ("word_02", "经济活动与市场运行"),
    3: ("word_03", "文化建设与精神传承"),
    4: ("word_04", "社会民生与社会风貌"),
    5: ("word_05", "思维判断与言语表达"),
    6: ("word_06", "状态变化与程度评价"),
    7: ("word_07", "心理性格与处事态度"),
    8: ("word_08", "程度时间与语气副词"),
}
IDIOM_CAT_MAP = {
    "idiom_01": "人物品质与为人处世",
    "idiom_02": "才智学识与认知判断",
    "idiom_03": "言谈表达与文辞运用",
    "idiom_04": "发展变化与形势态势",
    "idiom_05": "数量范围与比较差异",
    "idiom_06": "做事处事与成效结果",
}

# ---------- 组装分类 ----------
cat_cards = defaultdict(list)
card_index = {}
problems = []

for c in cards:
    if c["category"] == "成语":
        cat = idiom_cat_of(c["word"])
    else:
        cat = WORD_CAT_MAP[words_cat[c["id"]]][0]
    if cat is None:
        problems.append(c["id"])
        continue
    cat_cards[cat].append(c["id"])
    card_index[c["id"]] = cat

# ---------- 标签索引 ----------
tags_index = defaultdict(list)
for c in cards:
    for t in c.get("tags", []):
        tags_index[t].append(c["id"])
tags_index = {k: v for k, v in sorted(tags_index.items(), key=lambda kv: -len(kv[1]))}

# ---------- 主题引导（对任务示例主题的映射与代表词） ----------
demo_words = ["方兴未艾", "如火如荼", "日新月异", "江河日下", "每况愈下",
              "高风亮节", "表里如一", "光明磊落", "寥寥无几", "不胜枚举",
              "凤毛麟角", "标本兼治", "釜底抽薪", "扬汤止沸"]
demo_words = [w for w in demo_words if w in wset]
demo_ids = {w: next(c["id"] for c in cards if c["word"] == w) for w in demo_words}

# ---------- 输出 ----------
cats_out = []
for cid in ["idiom_01", "idiom_02", "idiom_03", "idiom_04", "idiom_05", "idiom_06"]:
    cats_out.append({
        "id": cid, "type": "成语", "name": IDIOM_CAT_MAP[cid],
        "count": len(cat_cards[cid]), "card_ids": sorted(cat_cards[cid]),
    })
for k in sorted(WORD_CAT_MAP):
    cid, name = WORD_CAT_MAP[k]
    cats_out.append({
        "id": cid, "type": "实词", "name": name,
        "count": len(cat_cards[cid]), "card_ids": sorted(cat_cards[cid]),
    })

km = {
    "version": "1.0",
    "generated_at": "2026-10-13",
    "description": "国考逻辑填空知识地图：词语分类索引，供分类学习、按标签筛选与关联调用。",
    "stats": {
        "total_cards": len(cards),
        "idiom_count": sum(1 for c in cards if c["category"] == "成语"),
        "word_count": sum(1 for c in cards if c["category"] == "实词"),
        "category_count": len(cats_out),
    },
    "categories": cats_out,
    "card_index": dict(sorted(card_index.items())),
    "tags_index": tags_index,
    "theme_guide": {
        "note": "以下为任务示例主题与实际分类的对应关系（示例词为各主题的代表词，非完整列表）。",
        "描写发展变化": {"category": "idiom_04", "examples": [{"word": w, "card_id": demo_ids[w]} for w in demo_words if w in ("方兴未艾", "如火如荼", "日新月异", "江河日下", "每况愈下")]},
        "描写人物品质": {"category": "idiom_01", "examples": [{"word": w, "card_id": demo_ids[w]} for w in demo_words if w in ("高风亮节", "表里如一", "光明磊落")]},
        "描写数量变化": {"category": "idiom_05", "examples": [{"word": w, "card_id": demo_ids[w]} for w in demo_words if w in ("寥寥无几", "不胜枚举", "凤毛麟角")]},
        "描写社会治理": {"category": "idiom_06", "examples": [{"word": w, "card_id": demo_ids[w]} for w in demo_words if w in ("标本兼治", "釜底抽薪", "扬汤止沸")]},
        "描写心理状态": {"category": None, "examples": [], "hint": "当前词库未单列此主题，可结合 idiom_01（人物品质与为人处世）与 word_07（心理性格与处事态度）中的相关条目筛选"},
        "描写环境状态": {"category": None, "examples": [], "hint": "当前词库覆盖较少，建议后续扩充"},
    },
}

if problems:
    print("！存在无法分类的卡片：", problems[:20])

out_path = os.path.join(DST, "knowledge-map.json")
with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(km, ensure_ascii=False, indent=1))

# 校验
total_in_cats = sum(c["count"] for c in cats_out)
print(f"总卡片：{len(cards)}；分类内卡片合计：{total_in_cats}；反查表条目：{len(card_index)}")
print(f"分类数：{len(cats_out)}（成语 6 + 实词 8）")
for c in cats_out:
    print(f"  {c['id']} {c['name']}：{c['count']}")
print(f"标签索引：{len(tags_index)} 种标签")
for k, v in list(tags_index.items())[:12]:
    print(f"  {k}: {len(v)}")
print(f"\n已输出：{out_path}")

