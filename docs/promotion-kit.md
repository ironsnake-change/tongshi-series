# 推广发布包

这个文件给仓库的使用者、维护者和转发者准备现成文案。公开发布前只需要替换链接、语气或平台标签，不需要重新解释产品。

## 一句话

把“每天写一篇”拆成研究、校验、备稿、投递四条可检查的流水线。

## 中文短帖

给那些想把 AI 内容做成长期系列的人：

Tongshi Series 是一个 research-first 的 Codex skill。它不靠“再来一篇”的提示词，而是把研究原文、编辑门禁、EPUB/PDF、库存和投递队列都落到磁盘上。

公开 beta，MIT，仓库在这里：
https://github.com/ironsnake-change/tongshi-series

## 朋友圈 / 即刻

最近把一个很朴素的念头做成了工程：让 AI 每天写一篇并不难，难的是每天都能稳定交付。

Tongshi Series 把这件事拆成四段：

- 先抓 research.md，再动笔
- 用脚本检查字数、章节和确定性说明
- 生成 EPUB/PDF
- 写作与投递分离，按队列发货

它不是一个“万能写作提示词”，更像一套编辑部的基础设施。公开 beta，欢迎拿走改成自己的主题系列。

https://github.com/ironsnake-change/tongshi-series

## 小红书

标题：我把“AI 每天写一篇”做成了流水线

正文：

一开始我以为难点是提示词。
后来发现，真正难的是：库存、来源、质量、成品、投递，每一环都可能掉链子。

所以我把通识长文的流程拆成了四个检查点：

01 研究
先把 Wikipedia 原文抓到 research.md，写不清的地方标不确定。

02 写作
按编辑规范写：具体场景、机制、转折、代价、争议，最后是三级确定性说明。

03 门禁
用 validator 检查字数、正文、章节、开头、术语表和延伸阅读。

04 投递
写作只补库存，投递按 queued_at 取稿；先备货，再发货。

我把这套流程整理成了公开的 Codex skill，MIT，有兴趣可以 fork 成自己的主题系列。

https://github.com/ironsnake-change/tongshi-series

标签：#AI写作 #内容创作 #知识管理 #开源项目 #效率工具

## V2EX / 论坛

标题：做了一个 research-first 的中文通识长文流水线，开源了

正文：

这不是一个“让模型写文章”的提示词合集，而是一个把编辑流程工程化的 skill。

核心设计：

- 研究先行：每篇先保存 research.md，写作时明确区分一手材料、后世转述和现代推断。
- 编辑门禁：validator 检查 4000–4500 汉字、10–15 节、开头长度、三级确定性说明、术语表和延伸阅读。
- 状态落盘：article.md、research.md、文章.epub、文章.pdf、.sent 都在同一目录。
- 写发分离：写作只补库存，投递按 meta.json 的 queued_at 排序，失败不跳稿。
- 可复用：MIT，公开仓库不包含邮箱、SMTP、推送 topic 或本地凭据。

目前是 v0.1.0 public beta。默认研究源是 Wikipedia，事实核查仍需人工；定时邮件实现属于私有环境配置，不随公开包提供。

仓库：
https://github.com/ironsnake-change/tongshi-series

如果你正在做邮件通讯、知识专栏或读书会材料，可以直接 fork 后替换 topics 和编辑规范。

## X / Twitter

Post 1:

Most “AI writing tools” stop at the prompt.

Tongshi Series starts where the prompt ends: a research dossier, an editorial gate, EPUB/PDF artifacts, and a queue that treats writing and delivery as separate systems.

Public beta, MIT:
https://github.com/ironsnake-change/tongshi-series

Post 2:

The pipeline is deliberately boring:

research.md → article.md → validator → EPUB/PDF → queued delivery

No hidden state in a chat window. Every article is a directory on disk. Every failure leaves a recoverable record.

Post 3:

It is also honest about its limits:

- Wikipedia is a starting source, not a final authority.
- The validator checks form, not historical truth.
- The public repo ships no SMTP credentials.
- The first release is a public beta, not an autonomous historian.

Build your own series with it.

## Show HN

Title: Show HN: A research-first Codex skill for a daily Chinese essay series

Body:

I kept running into the same failure mode: a model can draft one good essay, but a daily series needs research dossiers, editorial constraints, durable state, and a delivery queue.

Tongshi Series packages that workflow as a Codex skill and a small set of standard-library Python scripts:

- fetch and store research before drafting
- validate length, section rhythm, opening, certainty notes, glossary, and reading list
- build EPUB and PDF from the same Markdown
- keep a filesystem-backed queue with meta.json and .sent markers
- separate writing from delivery

It is a public beta. The validator checks structure, not truth; Wikipedia is only a starting source; mail credentials are intentionally not included.

Repo: https://github.com/ironsnake-change/tongshi-series

I would especially value feedback from people who run recurring newsletters or editorial series.

## 发布清单

- [ ] 在 GitHub 仓库 Settings 中把 social preview 设置为 assets/social-preview.png
- [ ] 检查 Pages 地址：https://ironsnake-change.github.io/tongshi-series/
- [ ] 确认 Release 已发布：https://github.com/ironsnake-change/tongshi-series/releases/tag/v0.1.0
- [ ] 发布时使用同一张横幅和同一句话，保持视觉与定位一致
- [ ] 不声称“完全自动”“事实无误”或“零成本”
- [ ] 在中文帖子中保留“public beta”与“Wikipedia 是起点”的边界
- [ ] 有人反馈安装问题时，优先让他们贴 quick_validate 和 validator 的实际输出

## 不建议的推广说法

- “全自动生成高质量文章”
- “不会出错的历史写作”
- “完全替代编辑”
- “接入一个 API 就永久免费”
- “一键发布，无需人工核查”

这些说法会让第一次试用的人把结构门禁误解成事实核查，也会把 public beta 误解成完成品。
