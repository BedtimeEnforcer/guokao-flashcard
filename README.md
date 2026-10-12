# 知序 · 国考逻辑填空

适合电脑和手机的免费学习网站，提供主动回忆词卡、间隔复习、近义辨析、原创语境选择题、进度统计，以及本机进度备份与恢复。访客无需注册。

## 内容与审核

目前收录 **1169 张词卡**（750 条成语、419 条实词）、**220 组辨析**、**410 道自编题**，覆盖 14 个主题。原始内容位于 `data/`，`scripts/build_site.py` 将其转换为网站使用的统一格式。构建过程检查 JSONL、字段、唯一 ID、答案索引和关联关系，并把题目正确选项均衡分布到 A/B/C/D；选项解析同步重排，原始内容保持不变。

内容提供方记录了全量程序检查及 100 张词卡、50 组辨析、50 道题的抽样审读，**尚未逐条完成独立的语义和辞书核对**。部分来源链接通往词典搜索页，不能视为对应词条已核实。详情见 [审核记录](data/review-notes.md)。发现词义或答案问题，欢迎在 [Issues](https://github.com/BedtimeEnforcer/guokao-flashcard/issues) 中指出条目和问题。

## 本地构建与测试

```powershell
py -3 scripts/validate_content.py
py -3 scripts/build_site.py
py -3 scripts/smoke_test.py
```

`dist/` 是可发布的静态站点目录。可用任意静态文件服务器打开它，无需 Node、数据库或付费服务。测试脚本需要 Python Playwright 和可用的 Chromium/Edge 浏览器。

学习进度保存在当前浏览器的 `localStorage`。换浏览器或设备时，先在设置中导出备份，再在另一设备导入。站内导入内容仅用于本机预览，刷新后恢复公开内容。

## 发布

仓库中的 GitHub Actions 工作流在推送到 `main` 后校验、构建并发布 `dist/`。仓库需在 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。公开地址：[https://bedtimeenforcer.github.io/guokao-flashcard/](https://bedtimeenforcer.github.io/guokao-flashcard/)。

## 内容原则

- [公务员考试大纲](https://www.forestry.gov.cn/c/www/gsgg/645383.jhtml)用于确认言语理解与表达的考查方向。
- “收录于本站”不表示“国考高频”或“考试必考”。
- 训练题和例句由内容提供方编写，均非真题原文。
- 原始条目 ID 在修订时应保持稳定，以免影响已有学习记录。

内容制作目标和统一格式见 [CONTENT_SPEC.md](CONTENT_SPEC.md)；现有数据包使用另一套字段，由构建脚本兼容转换。

