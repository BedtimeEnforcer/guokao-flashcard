# -*- coding: utf-8 -*-
"""全量验证词卡来源URL：低并发 + 限流重试；输出 404 清单（urls_404.json）与验证报告"""
import io, os, sys, json, time, urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE = r"D:/workbuddywork/收集资料/国考逻辑填空数据"
PARTS = os.path.join(BASE, "parts")

def collect_words():
    ws = []
    seen = set()
    for f in sorted(os.listdir(PARTS)):
        if f.startswith("cards_") and f.endswith(".jsonl"):
            with io.open(os.path.join(PARTS, f), encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        o = json.loads(line)
                        w = (o.get("word") or "").strip()
                        if w and w not in seen:
                            seen.add(w)
                            ws.append(w)
    return ws

def check_word(w):
    url = "https://www.zdic.net/hans/" + w
    safe = urllib.parse.quote(url, safe=":/")
    req = urllib.request.Request(safe, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    for attempt, wait in enumerate((0, 2, 4)):
        if wait:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return w, 200
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                continue
            return w, e.code
        except Exception as e:
            if attempt < 2:
                continue
            return w, str(e)[:50]

def main():
    words = collect_words()
    print(f"待验证词数：{len(words)}")
    results = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = []
        for i, w in enumerate(words):
            futs.append(ex.submit(check_word, w))
            time.sleep(0.25)
        for fu in futs:
            results.append(fu.result())
    ok = [w for w, s in results if s == 200]
    nf = [w for w, s in results if s == 404]
    other = [(w, s) for w, s in results if s not in (200, 404)]
    print(f"验证完成：可达 {len(ok)}，无词条(404) {len(nf)}，其他异常 {len(other)}，耗时 {int(time.time()-t0)}s")
    with io.open(os.path.join(BASE, "urls_404.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(nf, ensure_ascii=False, indent=1))
    with io.open(os.path.join(BASE, "verify-urls-report.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"词卡来源URL验证（全量）\n总数：{len(words)}\n可达(200)：{len(ok)}\n无词条(404)：{len(nf)}\n其他异常：{len(other)}\n\n无词条清单：\n" + "\n".join(nf))
        if other:
            fh.write("\n\n其他异常：\n" + "\n".join(f"{w} -> {s}" for w, s in other))
    print("404清单已写入 urls_404.json；报告 verify-urls-report.txt")
    if other:
        print("其他异常：", other[:10])
    print("无词条示例：", nf[:20])

if __name__ == "__main__":
    main()

