# 国考逻辑填空词卡

自己备考时用的逻辑填空练习站，顺手放出来。就是个静态网站，不用注册，电脑手机都能打开：https://bedtimeenforcer.github.io/guokao-flashcard/

功能没什么花哨的：词卡翻着背、按间隔复习、近义辨析、自编的语境选择题、一个简单的进度统计。进度存在浏览器 localStorage 里，换设备前记得在设置里导出备份再导入，对面不认账。

内容现在有 1169 张词卡（750 条成语、419 条实词）、220 组辨析、410 道自编题，分了 14 个主题。原始数据在 `data/` 里，`scripts/build_site.py` 转成网站用的格式，构建时会顺带检查 JSONL 格式、字段、ID 是否重复、答案索引和关联关系，也会把正确选项尽量均摊到 A/B/C/D，解析跟着重排，原始内容不动。

丑话说前面：内容做过一遍全量程序检查，也抽读过 100 张词卡、50 组辨析、50 道题，但没有逐条做过独立的语义和辞书核对。有些来源链接只是指到词典搜索页，不代表那个词条已经被核实过。审核情况记在 `data/review-notes.md`。发现词义或答案有问题，去 Issues 里说一下是哪个条目就行，欢迎挑错。题和例句都是自己编的，不是真题，别当真题背。还有，「收录了」不等于「高频」更不等于「必考」，大纲只是用来对一下考查方向。

## 本地跑

```powershell
py -3 scripts/validate_content.py
py -3 scripts/build_site.py
py -3 scripts/smoke_test.py
```

构建出的 `dist/` 用任意静态服务器打开就行，不需要 Node 和数据库。测试脚本要 Python Playwright 和一个能用的 Chromium/Edge。

发布靠 GitHub Actions：推到 `main` 后自动校验、构建、发布 `dist/`。仓库设置里 Pages 的 Source 要选 GitHub Actions，不然发不出去。

内容格式和制作目标写在 `CONTENT_SPEC.md` 里。现有数据包用的是另一套字段，构建脚本做了兼容转换。改内容时条目 ID 尽量别动，会影响别人已有的学习记录。
