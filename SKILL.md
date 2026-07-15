---
name: arxiv-detect
description: Search arXiv for the latest daily papers on a user-specified topic and summarize them. Use this skill whenever the user asks to find, discover, or summarize the newest arXiv papers on a specific research topic (e.g., "latest papers on LLMs", "new arXiv papers about diffusion models", "what's new on arXiv about protein design", "today's hot papers on multi-agent systems"). Generates a structured, readable summary in Chinese.
---

# arXiv Daily Paper Detector

## Workflow

1. 从用户输入中提取研究主题（topic）
2. 运行 `scripts/search_arxiv.py` 脚本查询 arXiv API
3. 解析 JSON 输出，为每篇论文生成结构化摘要
4. 如果用户要求下载 PDF，使用 `--download` 运行脚本，下载完成后告知用户本地路径
5. 返回给用户一篇易读的中文总结

## Running the search script

```bash
python scripts/search_arxiv.py --topic "large language model" --max-results 10
```

参数说明：
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--topic` | 必填 | 搜索主题，支持空格分隔的关键词，内部自动转为 AND 查询 |
| `--max-results` | 10 | 返回的最大论文数（推荐 5-15） |
| `--download` | 不下载 | 添加此标志后下载 PDF 到本地文件夹 |
| `--output-dir` | `./arxiv_papers` | PDF 下载目录（仅在 `--download` 时生效） |

输出为 JSON 格式，包含每篇论文的：title, authors, summary（摘要全文）, published, updated, link, categories, comment（如有）。使用 `--download` 时还会额外输出 arxiv_id 和 download_path（本地 PDF 路径）。

## arXiv 分类名映射表

展示论文时，将分类代号转换为中文与英文全称。以下为常见分类映射：

| 代号 | 中文 | English |
|------|------|---------|
| `cs.AI` | 人工智能 | Artificial Intelligence |
| `cs.CL` | 计算语言学 | Computation and Language |
| `cs.CV` | 计算机视觉 | Computer Vision and Pattern Recognition |
| `cs.LG` | 机器学习 | Machine Learning |
| `cs.IR` | 信息检索 | Information Retrieval |
| `cs.NE` | 神经与进化计算 | Neural and Evolutionary Computing |
| `cs.MA` | 多智能体系统 | Multiagent Systems |
| `cs.RO` | 机器人学 | Robotics |
| `cs.SE` | 软件工程 | Software Engineering |
| `cs.CR` | 密码学与安全 | Cryptography and Security |
| `cs.DB` | 数据库 | Databases |
| `cs.DC` | 分布式并行计算 | Distributed, Parallel, and Cluster Computing |
| `cs.HC` | 人机交互 | Human-Computer Interaction |
| `cs.SI` | 社会信息学 | Social and Information Networks |
| `cs.GT` | 博弈论 | Computer Science and Game Theory |
| `cs.MM` | 多媒体 | Multimedia |
| `cs.SD` | 声音 | Sound |
| `cs.SY` | 系统与控制 | Systems and Control |
| `stat.ML` | 机器学习（统计） | Machine Learning (Statistics) |
| `stat.ME` | 方法论 | Methodology |
| `stat.CO` | 计算 | Computation |
| `math.OC` | 优化与控制 | Optimization and Control |
| `math.PR` | 概率论 | Probability |
| `math.ST` | 统计理论 | Statistics Theory |
| `q-bio.BM` | 生物分子 | Biomolecules |
| `q-bio.GN` | 基因组学 | Genomics |
| `q-bio.QM` | 定量方法 | Quantitative Methods |
| `eess.AS` | 音频与语音处理 | Audio and Speech Processing |
| `eess.IV` | 图像与视频处理 | Image and Video Processing |
| `physics.data-an` | 数据分析与统计物理 | Data Analysis, Statistics and Probability |
| `q-fin.ST` | 统计金融 | Statistical Finance |

注意：遇到未收录的分类代号时，保留原代号并尝试将前缀译为合理中文。

## PDF 下载

默认不下载 PDF。当用户要求下载时：

```bash
python scripts/search_arxiv.py --topic "large language model" --max-results 10 --download
```

- PDF 默认保存到运行目录下的 `arxiv_papers/` 文件夹
- 可通过 `--output-dir` 指定其他目录
- 每篇论文保存为 `{arxiv_id}.pdf`（如 `2401.12345.pdf`）
- 如果文件已存在则跳过，不会重复下载
- 下载失败时不中断流程，对应的 `download_path` 为 `null`
- 下载后的路径会显示在 JSON 输出的 `download_path` 字段中，最终回复时告知用户本地文件位置

## Output format

阅读 JSON 输出后，每篇论文均按以下完整结构详细推荐。如论文数量较多（≥ 9 篇），在标题下方添加快速导航，按主题或方法分组。

### 今日 arXiv 更新：`{topic}`
> 共检索到 {N} 篇论文（{earliest_date} ~ {latest_date}）

**快速导航**（≥ 9 篇时使用）
1. {方向名称}（{N} 篇）：#1, #3, #7
2. {方向名称}（{N} 篇）：#2, #4, #5

**1. {论文标题}**
- **作者**：{第一作者或课题组}, 等 {N} 人
- **分类**：{中文名称} · {English}
- **链接**：[摘要](https://arxiv.org/abs/{ID}) · [PDF](https://arxiv.org/pdf/{ID}) · ID: `{arxiv_id}`
- **本地文件**：如有下载，显示 `{download_path}`
- **提交**：{published_date}（{当日新提交 / 更新于 YYYY-MM-DD}）
- **核心内容**：
  - **研究问题**：论文试图解决什么问题？现有方法有什么不足？
  - **方法/思路**：提出了什么方法或框架？核心创新点在哪里？
  - **关键结果**：在哪些基准上做了实验？主要定量/定性结论是什么？
  - **方法优势**：相比基线方法，在什么指标上取得了提升？提升幅度如何？
  - **局限与展望**（如有）：方法的局限性或可改进的方向

**2. {论文标题}**
- **作者**：{第一作者或课题组}, 等 {N} 人
- **分类**：{中文名称} · {English}
- **链接**：[摘要](https://arxiv.org/abs/{ID}) · [PDF](https://arxiv.org/pdf/{ID}) · ID: `{arxiv_id}`
- **本地文件**：如有下载，显示 `{download_path}`
- **提交**：{published_date}（{当日新提交 / 更新于 YYYY-MM-DD}）
- **核心内容**：
  - **研究问题**：论文试图解决什么问题？现有方法有什么不足？
  - **方法/思路**：提出了什么方法或框架？核心创新点在哪里？
  - **关键结果**：在哪些基准上做了实验？主要定量/定性结论是什么？
  - **方法优势**：相比基线方法，在什么指标上取得了提升？提升幅度如何？
  - **局限与展望**（如有）：方法的局限性或可改进的方向

### 今日看点

**趋势**：本周/今日该方向最活跃的研究主题或方法论走向
**值得跟进**：引用具体某篇论文的结果，说明为什么值得后续关注
**可能错过**：如有不那么显眼但有长期潜力的论文，提一句

注意：
- 优先关注当天/近两天提交的论文（published 字段）
- 如多篇论文主题相近，可以分组概述
- 摘要要凝练、准确，突出"新"在哪里
- 最终回复使用中文
- 每条 summary 可能较长（arXiv 摘要是全文），只需提炼核心信息即可
- 如果脚本返回 error 字段，提示用户重试并说明原因
- 作者超过 5 人时只列出第一作者（或末位通讯作者），后加"等 {N} 人"
- 展示分类时查阅上方映射表，输出 `{中文（English）}` 格式，如 `计算语言学（Computation and Language）`

## Scripts

- `scripts/search_arxiv.py` — 传入 `--topic` 和可选 `--max-results`，返回该主题最新论文的 JSON。加 `--download` 可下载 PDF 到本地。
