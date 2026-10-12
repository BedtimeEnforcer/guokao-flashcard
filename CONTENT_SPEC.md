# 国考逻辑填空内容交付规范

网站从 `data/cards.jsonl`、`data/comparisons.jsonl`、`data/questions.jsonl` 读取正式内容。三个文件均为 UTF-8、每行一个 JSON 对象，不要包裹在数组或 Markdown 代码块中。可分批交付，但 ID 一经发布必须保持稳定，否则已有学习记录无法对应。

**当前状态：** 以下是最初的内容制作目标和统一格式建议。现有数据包由外部内容流程交付，采用另一套字段；`scripts/validate_content.py` 在构建时进行兼容转换。现有辨析中有些词不在词卡库，部分题目没有关联词卡，网站均可独立展示。实际数量与审核范围见 [README.md](README.md) 和 [data/review-notes.md](data/review-notes.md)。

目标：词语卡 1000 张（成语 750、实词 250）、近义辨析 200 组、语境选择题 300 道。这是内容制作目标，不是未经核验也必须凑齐的数字。网站按实际通过校验的数量展示。

## cards.jsonl

```json
{"id":"idiom-yuan-yuan-liu-chang","term":"源远流长","kind":"idiom","definition":"对词义的准确、简洁解释","usage":"适合什么语境及所强调的侧面","collocations":["搭配一","搭配二"],"confusable":["词语 ID 或词面"],"distinction":"与易混词的关键区别","example":"自己编写的恰当例句。","misuse":"自己编写的常见误用句。","misuse_reason":"为什么不恰当，以及怎样改。","difficulty":2,"tags":["文化传承"],"source":{"title":"辞书或公开资料名称","url":"https://...","locator":"具体词条或章节"}}
```

`kind` 只能为 `idiom` 或 `word`；`difficulty` 为 1、2、3。`definition`、`usage`、`example`、`source` 必填。所有正文是原创解释与原创例句，不复制辞书释义或商业题库原句。来源链接用于核验，不代表来源机构认可本站。

## comparisons.jsonl

```json
{"id":"cmp-yuan-yuan-lian-mian","terms":["源远流长","连绵不绝"],"shared":"二者的共同语义范围","difference":"最能决定选词的差异","examples":[{"term":"源远流长","sentence":"原创例句。"},{"term":"连绵不绝","sentence":"原创例句。"}],"tags":["文化传承"],"source":{"title":"核验来源名称","url":"https://...","locator":"具体词条或章节"}}
```

`terms` 至少两个，且每个词应能在词语卡中找到。`difference` 必须可用于判断真实语境，不能仅重复两条释义。

## questions.jsonl

```json
{"id":"q-cultural-001","stem":"依据上下文选择最恰当的词语：……____……","choices":["选项 A","选项 B","选项 C","选项 D"],"answer":0,"explanation":"说明上下文线索和为什么其余选项不合适。","choice_explanations":["A 项解析","B 项解析","C 项解析","D 项解析"],"tested_terms":["源远流长","连绵不绝"],"difficulty":2,"tags":["语境辨析"],"source":{"title":"核验来源名称或自编说明","url":"https://...","locator":"具体词条或章节"}}
```

`answer` 是从 0 开始的索引，范围 0–3。题目必须只有一个在给定语境中最恰当的答案；原创题干和解析。`tested_terms` 中的词需在词语卡中找到。

## 提交前检查

在项目目录执行 `py -3 scripts/validate_content.py`。检查通过后交付三份 JSONL 和 `review-notes.md`。不要把存疑内容放入正式文件；在审稿说明中列出待核验条目。

