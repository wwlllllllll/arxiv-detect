# arXiv Daily Paper Detector

## 简介

这是一个 Codex Agent 技能，用于每天自动搜索 arXiv 上特定主题的最新论文，生成结构化、易读的中文摘要。支持关键词搜索、分类过滤、PDF 批量下载等功能，帮助科研人员高效追踪前沿进展。

## 功能特性

- **论文检索** — 通过 arXiv API 搜索指定主题的最新论文，支持关键词组合查询
- **中文摘要** — 为每篇论文生成结构化中文简介，包含研究问题、方法、结果和局限性
- **PDF 下载** — 可选批量下载论文 PDF 到本地，自动跳过已存在的文件
- **分类映射** — 内置 arXiv 分类代号与中文/英文全称的映射表
- **每日汇总** — 支持快速导航、按主题分组、今日看点等输出格式

## 快速开始

```bash
# 搜索指定主题的最新论文
python scripts/search_arxiv.py --topic "large language model" --max-results 10

# 搜索并下载 PDF
python scripts/search_arxiv.py --topic "diffusion model" --max-results 10 --download

# 指定 PDF 下载目录
python scripts/search_arxiv.py --topic "protein design" --max-results 15 --download --output-dir ./papers
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--topic` | 必填 | 搜索主题，支持空格分隔的关键词，内部自动转为 AND 查询 |
| `--max-results` | 10 | 返回的最大论文数（推荐 5-15） |
| `--download` | 不下载 | 添加此标志后下载 PDF 到本地文件夹 |
| `--output-dir` | `./arxiv_papers` | PDF 下载目录（仅在 `--download` 时生效） |

## 输出格式

脚本以 JSON 格式输出，包含每篇论文的：

- **title** — 论文标题
- **authors** — 作者列表
- **summary** — 摘要全文
- **published** / **updated** — 提交/更新日期
- **link** — arXiv 页面链接
- **categories** — 分类代号
- **comment** — 作者备注（如有）

使用 `--download` 时额外包含 `arxiv_id` 和 `download_path`（本地 PDF 路径）。

## 目录结构

```
arxiv-detect/
├── SKILL.md                   # Codex Agent 技能描述
├── README.md                  # 本文件
├── .gitignore                 # Git 忽略规则
├── agents/
│   └── openai.yaml            # Agent 配置文件
└── scripts/
    └── search_arxiv.py        # arXiv 论文搜索脚本
```

## 使用场景

- 每天早上快速浏览自己研究领域的最新 arXiv 投稿
- 为组会准备文献综述材料
- 追踪特定技术方向（如大语言模型、扩散模型、蛋白质设计等）的进展
- 批量下载感兴趣领域的论文 PDF 供离线阅读

## 许可证

MIT
