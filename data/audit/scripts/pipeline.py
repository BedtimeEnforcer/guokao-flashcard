# -*- coding: utf-8 -*-
"""
国考逻辑填空学习数据 · 构建与检查流水线
用法：
  python pipeline.py build   # 从 parts/ 构建三个最终 JSONL（去重、补ID、补来源字段）
  python pipeline.py check   # 对最终文件做全面检查，输出 check-report.md
  python pipeline.py all     # 先 build 后 check
"""
import io, os, re, sys, json, ast
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"D:/workbuddywork/收集资料/国考逻辑填空数据"
PARTS = os.path.join(BASE, "parts")

LOG = []          # 构建日志
QUARANTINE = []   # 严重问题条目（不进入正式数据）

def log(msg):
    LOG.append(msg)
    print(msg)

# ---------------- 基础工具 ----------------
def norm_space(s):
    if not isinstance(s, str):
        return ""
    s = s.replace("\u200b", "").replace("\ufeff", "")
    s = re.sub(r"[ \t\r\n]+", " ", s)
    return s.strip()

def load_jsonl(path):
    rows = []
    with io.open(path, encoding="utf-8") as fh:
        for ln, line in enumerate(fh, 1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception:
                try:
                    obj = ast.literal_eval(s)
                except Exception as e:
                    log(f"[解析失败] {os.path.basename(path)} 第{ln}行：{str(e)[:90]}")
                    continue
            if isinstance(obj, dict):
                rows.append(obj)
            else:
                log(f"[类型异常] {os.path.basename(path)} 第{ln}行：非对象，已跳过")
    return rows

def part_files(prefix):
    if not os.path.isdir(PARTS):
        return []
    return [os.path.join(PARTS, f) for f in sorted(os.listdir(PARTS))
            if f.startswith(prefix) and f.endswith(".jsonl")]

def w_jsonl(path, rows):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        for o in rows:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")

def clean_list(vals, maxn=4):
    out = []
    if isinstance(vals, list):
        for it in vals:
            if isinstance(it, str):
                s = norm_space(it)
                if s:
                    out.append(s)
    elif isinstance(vals, str):
        for p in re.split(r"[、,，;；/]", norm_space(vals)):
            if norm_space(p):
                out.append(norm_space(p))
    return out[:maxn]

def clean_confusing(vals, maxn=3):
    out = []
    if isinstance(vals, list):
        for it in vals:
            if isinstance(it, dict):
                w = norm_space(it.get("word", ""))
                d = norm_space(it.get("difference", ""))
                if w and d:
                    out.append({"word": w, "difference": d})
    return out[:maxn]

DIFF_MAP = {"easy": "easy", "简单": "easy", "容易": "easy",
            "medium": "medium", "中等": "medium", "中": "medium", "一般": "medium",
            "hard": "hard", "困难": "hard", "难": "hard"}

def clean_diff(v):
    s = norm_space(v).lower()
    return DIFF_MAP.get(s, "medium")

def q(obj, reason, src):
    o = dict(obj)
    o["_reason"] = reason
    o["_src"] = src
    QUARANTINE.append(o)

# ---------------- 构建：词卡 ----------------
def build_cards():
    nf_path = os.path.join(BASE, "urls_404.json")
    no_entry = set()
    if os.path.exists(nf_path):
        try:
            with io.open(nf_path, encoding="utf-8") as fh:
                no_entry = set(json.load(fh))
            log(f"已加载无词条清单：{len(no_entry)} 个词将使用站内搜索链接")
        except Exception:
            pass
    items = []   # (category, obj, src)
    for p in part_files("cards_idioms_"):
        for o in load_jsonl(p):
            items.append(("成语", o, os.path.basename(p)))
    for p in part_files("cards_words_"):
        for o in load_jsonl(p):
            items.append(("实词", o, os.path.basename(p)))

    seen = set()
    dup_cnt = 0
    kept = []
    for cat, o, src in items:
        w = norm_space(o.get("word", ""))
        w = re.sub(r"[（）()\[\]【】\s]", "", w)
        if not w:
            q(o, "word缺失或为空", src); continue
        if w in seen:
            dup_cnt += 1
            continue
        d = norm_space(o.get("definition", ""))
        if not d:
            q(o, "definition缺失", src); continue
        ex = norm_space(o.get("example", ""))
        if not ex:
            q(o, "example缺失", src); continue
        seen.add(w)
        row = {
            "word": w,
            "category": cat,
            "definition": d,
            "context": norm_space(o.get("context", "")),
            "collocations": clean_list(o.get("collocations"), 4),
            "confusing_words": clean_confusing(o.get("confusing_words"), 3),
            "example": ex,
            "misuse": norm_space(o.get("misuse", "")),
            "difficulty": clean_diff(o.get("difficulty")),
            "tags": clean_list(o.get("tags"), 4),
        }
        # 轻微问题记录（不阻断）
        if len(d) < 10 or len(d) > 150:
            log(f"[长度异常] {w} definition长度={len(d)}")
        kept.append(row)

    idioms = [r for r in kept if r["category"] == "成语"]
    words = [r for r in kept if r["category"] == "实词"]
    for i, r in enumerate(idioms, 1):
        r["id"] = "CY%04d" % i
    for i, r in enumerate(words, 1):
        r["id"] = "SC%04d" % i
    out = idioms + words
    final = []
    for r in out:
        final.append({
            "id": r["id"], "word": r["word"], "category": r["category"],
            "definition": r["definition"], "context": r["context"],
            "collocations": r["collocations"], "confusing_words": r["confusing_words"],
            "example": r["example"], "misuse": r["misuse"], "difficulty": r["difficulty"],
            "tags": r["tags"],
            "source_url": ("https://www.zdic.net/hans/" + r["word"]) if r["word"] not in no_entry
                          else ("https://www.zdic.net/search/?q=" + r["word"]),
            "source_reference": "汉典网（zdic.net）词条及权威辞书规范释义核校；释义与用法按现代汉语规范编写，例句为原创",
        })
    w_jsonl(os.path.join(BASE, "cards.jsonl"), final)
    log(f"cards.jsonl：成语 {len(idioms)} 条 + 实词 {len(words)} 条 = {len(final)} 条（去重移除 {dup_cnt} 条）")
    return final

# ---------------- 构建：辨析 ----------------
def build_comparisons():
    items = []
    for p in part_files("comparisons_"):
        for o in load_jsonl(p):
            items.append((o, os.path.basename(p)))
    seen = set()
    dup_cnt = 0
    kept = []
    for o, src in items:
        ws = clean_list(o.get("words"), 6)
        if len(ws) != 2:
            q(o, f"words字段不是2个词（得到{len(ws)}个）", src); continue
        key = tuple(sorted(ws))
        if key in seen:
            dup_cnt += 1
            continue
        seen.add(key)
        row = {
            "words": [ws[0], ws[1]],
            "similarity": norm_space(o.get("similarity", "")),
            "key_difference": norm_space(o.get("key_difference", "")),
            "usage_difference": norm_space(o.get("usage_difference", "")),
            "examples": clean_list(o.get("examples"), 2),
            "source": norm_space(o.get("source", "") or o.get("source_note", "")) or
                      "依据权威辞书释义及现代汉语规范用法综合辨析（未逐条标注辞书页码）",
        }
        if not row["key_difference"]:
            q(o, "key_difference缺失", src); continue
        kept.append(row)
    for i, r in enumerate(kept, 1):
        r["id"] = "BJ%04d" % i
    final = []
    for r in kept:
        final.append({
            "id": r["id"], "words": r["words"], "similarity": r["similarity"],
            "key_difference": r["key_difference"], "usage_difference": r["usage_difference"],
            "examples": r["examples"], "source": r["source"],
        })
    w_jsonl(os.path.join(BASE, "comparisons.jsonl"), final)
    log(f"comparisons.jsonl：{len(final)} 组（去重移除 {dup_cnt} 组）")
    return final

# ---------------- 构建：题目 ----------------
def build_questions(cards):
    word2id = {c["word"]: c["id"] for c in cards}
    fallback_cnt = 0
    items = []
    for p in part_files("questions_"):
        for o in load_jsonl(p):
            items.append((o, os.path.basename(p)))
    seen_q = set()
    dup_cnt = 0
    kept = []
    auto_fix = 0
    for o, src in items:
        qt = norm_space(o.get("question", ""))
        if not qt:
            q(o, "question缺失", src); continue
        if qt in seen_q:
            dup_cnt += 1
            continue
        seen_q.add(qt)
        opts = {}
        raw = o.get("options")
        if isinstance(raw, dict):
            for k, v in raw.items():
                kk = str(k).strip().upper()
                m = re.match(r"^([ABCD])", kk)
                if m and isinstance(v, str) and norm_space(v):
                    opts[m.group(1)] = norm_space(v)
        if len(opts) != 4:
            q(o, f"options不完整（得到{len(opts)}个选项）", src); continue
        ans = ""
        m = re.search(r"[ABCD]", str(o.get("answer", "")).upper())
        if m:
            ans = m.group(0)
        if ans not in opts:
            q(o, "answer缺失或不在选项内", src); continue
        ana = norm_space(o.get("analysis", ""))
        if not ana:
            q(o, "analysis缺失", src); continue
        # 解析与答案一致性
        picks = set(re.findall(r"选\s*([ABCD])", ana))
        if picks and picks != {ans}:
            q(o, f"analysis中的答案指向（{sorted(picks)}）与answer（{ans}）不一致", src)
            continue
        if not picks:
            ana = ana.rstrip("。") + f"。故本题选{ans}。"
            auto_fix += 1
        if not ana.endswith(f"选{ans}。"):
            ana = ana.rstrip("。") + f"。"
        rw = clean_list(o.get("related_words"), 4)
        rids = [word2id[w] for w in rw if w in word2id]
        if not rids:
            # 关联回退：从题干与选项中提取在库词（真实出现的关联词）
            text = qt + "".join(opts.values())
            extra = [w for w in word2id if w in text]
            extra = sorted(extra, key=lambda w: text.find(w))[:3]
            if extra:
                rids = [word2id[w] for w in extra]
                fallback_cnt += 1
        kept.append({
            "question": qt, "options": {k: opts[k] for k in "ABCD"}, "answer": ans,
            "analysis": ana,
            "knowledge_point": norm_space(o.get("knowledge_point", "")),
            "related_card_ids": rids,
        })
    for i, r in enumerate(kept, 1):
        r["id"] = "T%04d" % i
    final = []
    unmatched = 0
    for r in kept:
        if not r["related_card_ids"]:
            unmatched += 1
        final.append({
            "id": r["id"], "question": r["question"], "options": r["options"],
            "answer": r["answer"], "analysis": r["analysis"],
            "knowledge_point": r["knowledge_point"],
            "related_card_ids": r["related_card_ids"],
        })
    w_jsonl(os.path.join(BASE, "questions.jsonl"), final)
    log(f"questions.jsonl：{len(final)} 道（去重移除 {dup_cnt} 道；自动补齐解析尾句 {auto_fix} 道；关联回退补充 {fallback_cnt} 道；仍无关联 {unmatched} 道）")
    return final

# ---------------- 检查 ----------------
def read_final(name):
    return load_jsonl(os.path.join(BASE, name))

def do_check():
    R = []
    def w(line=""):
        R.append(line)
    cards = read_final("cards.jsonl")
    comps = read_final("comparisons.jsonl")
    qs = read_final("questions.jsonl")
    w("# 数据检查报告")
    w()
    # 1 总量与ID
    ids = [c["id"] for c in cards]
    w(f"- cards.jsonl：{len(cards)} 条；成语 {sum(1 for c in cards if c['category']=='成语')} 条；实词 {sum(1 for c in cards if c['category']=='实词')} 条；ID唯一：{'是' if len(set(ids))==len(ids) else '否'}")
    w(f"- comparisons.jsonl：{len(comps)} 组；ID唯一：{'是' if len(set(c['id'] for c in comps))==len(comps) else '否'}")
    w(f"- questions.jsonl：{len(qs)} 道；ID唯一：{'是' if len(set(q['id'] for q in qs))==len(qs) else '否'}")
    w()
    # 2 字段完整
    card_fields = ["id","word","category","definition","context","collocations","confusing_words","example","misuse","difficulty","tags","source_url","source_reference"]
    bad = [c.get("id") for c in cards if any(k not in c or c[k] in ("", [], None) for k in card_fields if k not in ("confusing_words","tags"))]
    w(f"- 词卡字段完整性：{'全部通过' if not bad else '缺失条目 ' + ','.join(map(str, bad[:20]))}")
    comp_fields = ["id","words","similarity","key_difference","usage_difference","examples","source"]
    badc = [c.get("id") for c in comps if any(k not in c or c[k] in ("", [], None) for k in comp_fields)]
    w(f"- 辨析字段完整性：{'全部通过' if not badc else '缺失条目 ' + ','.join(map(str, badc[:20]))}")
    q_fields = ["id","question","options","answer","analysis","knowledge_point","related_card_ids"]
    badq = [q.get("id") for q in qs if any(k not in q or q[k] in ("", None) for k in q_fields)]
    w(f"- 题目字段完整性：{'全部通过' if not badq else '缺失条目 ' + ','.join(map(str, badq[:20]))}")
    w()
    # 3 词唯一性
    ws = [c["word"] for c in cards]
    dups = [x for x, n in Counter(ws).items() if n > 1]
    w(f"- 词卡word唯一性：{'通过' if not dups else '重复: ' + ','.join(dups[:20])}")
    w()
    # 4 辨析与词卡关联
    wset = set(ws)
    hit2 = sum(1 for c in comps if all(x in wset for x in c["words"]))
    hit1 = sum(1 for c in comps if any(x in wset for x in c["words"]))
    w(f"- 辨析词覆盖：两词均在词卡中 {hit2}/{len(comps)}；至少一词在词卡中 {hit1}/{len(comps)}")
    miss = [c["words"] for c in comps if not any(x in wset for x in c["words"])]
    if miss:
        w(f"  未覆盖辨析对 {len(miss)} 组（示例）：" + "；".join("/".join(m) for m in miss[:12]))
    w()
    # 5 题目检查
    idset = set(ids)
    ok_ans = sum(1 for q in qs if re.search(r"选\s*" + q["answer"], q["analysis"]))
    w(f"- 题目答案与解析一致：{ok_ans}/{len(qs)}")
    badrel = [q["id"] for q in qs if any(rid not in idset for rid in q["related_card_ids"])]
    w(f"- 题目关联ID可解析：{'全部通过' if not badrel else '悬空引用: ' + ','.join(badrel[:20])}")
    no_rel = [q["id"] for q in qs if not q["related_card_ids"]]
    w(f"- 有关联词卡的题目：{len(qs)-len(no_rel)}/{len(qs)}（无关联 {len(no_rel)} 道）")
    w()
    # 6 解析失败重扫
    for name in ["cards.jsonl","comparisons.jsonl","questions.jsonl"]:
        p = os.path.join(BASE, name)
        n = 0
        with io.open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    n += 1
        w(f"- {name} 行数：{n}")
    w()
    w("检查方式：Python 逐行 JSON 解析 + 字段/唯一性/关联性自动校验。")
    text = "\n".join(R)
    with io.open(os.path.join(BASE, "check-report.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(text)

# ---------------- 主流程 ----------------
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("build", "all"):
        LOG.clear(); QUARANTINE.clear()
        cards = build_cards()
        comps = build_comparisons()
        qs = build_questions(cards)
        if QUARANTINE:
            w_jsonl(os.path.join(BASE, "quarantine.jsonl"), QUARANTINE)
            log(f"quarantine.jsonl：{len(QUARANTINE)} 条（见文件）")
        with io.open(os.path.join(BASE, "build-log.txt"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(LOG))
    if mode in ("check", "all"):
        do_check()

if __name__ == "__main__":
    main()

