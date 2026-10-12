# -*- coding: utf-8 -*-
"""第二步：实词领域分类映射（SC编号 -> 领域类号），校验完整性后输出中间文件"""
import io, os, json

DST = r"C:/Users/Ethan/Desktop/codex/考研助手/data"

# 实词领域分类（类号）
# 1=政策治理与公共管理  2=经济活动与市场运行  3=文化建设与精神传承  4=社会民生与社会风貌
# 5=思维判断与言语表达  6=状态变化与程度评价  7=心理性格与处事态度  8=程度时间与语气副词
# 区间表达："起-止:类号" 或 "单号:类号"
RANGES = [
    "1-5:1", "6-7:5", "8-13:1", "14:5", "15:1", "16:6", "17-19:5", "20-30:1",
    "31-38:5", "39-42:1", "43:3", "44:1", "45:2", "46:5", "47-49:1", "50-55:3",
    "56:1", "57-62:3", "63:6", "64:2", "65-67:6", "68-69:1", "70:7", "71-75:1",
    "76-78:2", "79:6", "80-81:2", "82-85:1", "86:7", "87:1", "88-90:6", "91-93:3",
    "94-95:6", "96:5", "97-103:1", "104:7", "105-106:6", "107-118:5", "119-123:1",
    "124:2", "125-126:1", "127-128:7", "129-136:1", "137-139:5", "140:1",
    "141-152:6", "153-155:4", "156-158:6", "159:8", "160-166:6", "167-171:7",
    "172-174:6", "175:4", "176-190:7", "191:5", "192:3", "193:6", "194-195:1",
    "196-197:3", "198-203:7", "204-206:4", "207-223:6", "224:5", "225-227:1",
    "228-239:6", "240-279:8", "280:7", "281:6", "282:5", "283-284:6", "285-292:5",
    "293:6", "294-297:7", "298-303:6", "304-305:4", "306:7", "307-318:6",
    "319-331:7", "332-339:5", "340:6", "341-342:5", "343-344:6", "345:4",
    "346-348:3", "349-353:1", "354:6", "355:1", "356:7", "357:3", "358-359:6",
    "360-362:1", "363-369:6", "370-371:3", "372:7", "373-375:3", "376-377:2",
    "378-380:1", "381:6", "382:1", "383:7", "384:5", "385:1", "386-387:1",
    "388:6", "389:7", "390-419:8",
]

# 解析区间
num2cat = {}
for seg in RANGES:
    rng, cat = seg.split(":")
    cat = int(cat)
    if "-" in rng:
        a, b = rng.split("-")
        for n in range(int(a), int(b) + 1):
            assert n not in num2cat, f"编号 {n} 重复映射"
            num2cat[n] = cat
    else:
        n = int(rng)
        assert n not in num2cat, f"编号 {n} 重复映射"
        num2cat[n] = cat

# 读取实词卡核对完整性
cards = [json.loads(l) for l in io.open(os.path.join(DST, "cards.jsonl"), encoding="utf-8") if l.strip()]
words = [c for c in cards if c["category"] == "实词"]
nums = {}
for c in words:
    n = int(c["id"][2:])  # SC0001 -> 1
    nums[n] = c["word"]

missing = [n for n in nums if n not in num2cat]
extra = [n for n in num2cat if n not in nums]
print(f"实词总数：{len(words)}；映射覆盖：{len(set(num2cat) & set(nums))}")
print("未映射编号：", missing if missing else "无")
print("多余映射：", extra if extra else "无")

if not missing and not extra:
    out = {f"SC{n:04d}": num2cat[n] for n in sorted(nums)}
    with io.open(os.path.join(DST, "audit", "km_words_cat.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=1))
    from collections import Counter
    cnt = Counter(num2cat.values())
    names = {1: "政策治理与公共管理", 2: "经济活动与市场运行", 3: "文化建设与精神传承",
             4: "社会民生与社会风貌", 5: "思维判断与言语表达", 6: "状态变化与程度评价",
             7: "心理性格与处事态度", 8: "程度时间与语气副词"}
    print("\n各类分布：")
    for k in sorted(cnt):
        print(f"  类{k} {names[k]}：{cnt[k]} 个")
    print("\n已输出 audit/km_words_cat.json")
else:
    print("！校验未通过，请修正映射")

