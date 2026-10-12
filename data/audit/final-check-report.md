# 最终数据检查报告（自动生成）

## 一、文件检查（UTF-8 / JSON 格式 / 每行一个对象）
- cards.jsonl：1169 行，解析错误 0
- comparisons.jsonl：220 行，解析错误 0
- questions.jsonl：410 行，解析错误 0
- knowledge-map.json：解析成功（14 个分类）

## 二、数据检查（ID 唯一 / 字段完整 / 无重复）
- 卡片 ID 唯一：通过（1169 个）
- 辨析 ID 唯一：通过
- 题目 ID 唯一：通过
- 卡片字段完整：通过
- 辨析字段完整：通过
- 题目字段完整：通过
- 词条无重复：通过
- 题目无重复：通过
- 辨析对无重复：通过

## 三、关联检查（引用存在性）
- 题目关联 card_id 全部存在：通过
- 有关联的题目：344/410
- knowledge-map 分类内 card_id 全部存在：通过
- knowledge-map 卡片无重复归类：通过
- knowledge-map 覆盖全部卡片（1169/1169）：通过
- knowledge-map 反查表完整且指向有效分类：通过

## 四、数量统计
- cards.jsonl：1169 条（成语 750 + 实词 419）
- comparisons.jsonl：220 组
- questions.jsonl：410 道
- knowledge-map.json：14 个分类，标签索引 11 种

生成时间：2026-10-13（自动检查）
