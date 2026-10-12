# -*- coding: utf-8 -*-
"""抽样验证 cards.jsonl 中 source_url 的可达性（汉典词条页）"""
import io, os, sys, json, random, urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE = r"D:/workbuddywork/收集资料/国考逻辑填空数据"

def check(url):
    safe = urllib.parse.quote(url, safe=":/")
    req = urllib.request.Request(safe, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return url, r.status
    except urllib.error.HTTPError as e:
        return url, e.code
    except Exception as e:
        return url, str(e)[:70]

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    cards = []
    p = os.path.join(BASE, "cards.jsonl")
    with io.open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                cards.append(json.loads(line))
    random.seed(20261013)
    sample = random.sample(cards, min(n, len(cards)))
    ok = 0
    fails = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for url, st in ex.map(check, [c["source_url"] for c in sample]):
            if st == 200:
                ok += 1
            else:
                fails.append((url, st))
    print(f"URL抽样验证：共 {len(sample)} 个，可达 {ok} 个，异常 {len(fails)} 个")
    for u, st in fails[:15]:
        print("  异常：", u, "->", st)

if __name__ == "__main__":
    main()

