# 七维内容引力模型

**Seven-Dimension Content Gravity** 是一套可复用的审稿与改稿框架。它把“抓住读者”拆成七个观察维度，但每篇文章只选择最适合的 **2–4 项**。

七个维度：情绪张力、读者收益、故事／案例、独特角度、作者声音、表达形式、具体细节。

它不是爆款公式，也不会用传播性覆盖事实。事实边界、中心判断、保密与版权边界始终优先。

## 仓库包含什么

- 可安装的 Agent Skill：`skill/seven-dimension-content-gravity/`
- 零运行时依赖的 Python CLI：`content-gravity`
- 可供其他项目导入的 Python API
- 可验证的编辑报告 JSON Schema：`schema/editorial-report.schema.json`
- 原始七点总结与完整框架文档
- 2026-10-18 AI 日报 A/B 实验记录

## 安装 CLI

```bash
uv tool install git+https://github.com/Jason-Kou/seven-dimension-content-gravity.git
```

开发安装：

```bash
git clone https://github.com/Jason-Kou/seven-dimension-content-gravity.git
cd seven-dimension-content-gravity
uv sync
```

## 常用命令

先做结构化检查：

```bash
content-gravity review article.md --profile deep-report
content-gravity review article.md --profile daily-briefing --format json
```

生成给任意模型或 Agent 使用的审稿／改稿指令：

```bash
content-gravity prompt article.md --profile deep-report --mode review
content-gravity prompt article.md --profile deep-report --mode revise > revision-prompt.md
content-gravity revise article.md --profile deep-report --output revision-prompt.md
```

生成可供 AMZCLI 或其他系统消费的 JSON 包：

```bash
content-gravity packet listing.md \
  --profile product-content \
  --mode revise \
  --output content-gravity-packet.json
```

支持 stdin/stdout：

```bash
cat article.md | content-gravity packet - --profile case-study --mode revise
```

## 接入 AMZCLI 或其他项目

CLI 采用稳定 JSON 输出，不绑定任何模型供应商。调用方可以把 `packet` 中的 `prompt` 交给自己已有的 Claude、Codex、Gemini、Ollama 或内部模型。

Python 调用：

```python
from content_gravity import analyze_document, build_prompt

text = open("listing.md", encoding="utf-8").read()
report = analyze_document(text, profile="product-content")
prompt = build_prompt(text, report, mode="revise")
```

建议的 AMZCLI 流程：

1. `content-gravity packet` 生成审改包。
2. AMZCLI 把 `prompt` 交给它已经配置的模型。
3. 模型返回修改稿与结构化审查报告。
4. 使用 `content-gravity validate-report` 核对源文件 SHA256 和主维度，防止旧审查误签新版本。

`revise` 命令生成完整的改稿指令，不会在没有模型的情况下假装自动完成主观改写。AMZCLI 或其他调用方把该指令交给自己已经配置的模型即可得到终稿。

## 为什么不让 CLI 自动“判断文章好坏”

关键词数量可以提示文章有没有数字、来源、案例或作者表达，却不能可靠判断一个观点是否真正独特、一段故事是否自然。CLI 因此只提供透明的结构信号、文章类型、主维度选择、哈希绑定和完整审改指令；最终判断由编辑或调用方的模型完成。

## 文章类型与默认主维度

- `daily-briefing`：独特角度、读者收益、作者声音、具体细节
- `deep-report`：独特角度、具体细节、读者收益、故事／案例
- `product-content`：读者收益、具体细节、表达形式
- `case-study`：故事／案例、具体细节、读者收益、作者声音
- `opinion`：独特角度、作者声音、情绪张力

使用 `--profile auto` 可让 CLI 根据结构信号推断文章类型。

## Skill 使用

`skill/seven-dimension-content-gravity/` 是标准 Skill 目录，可以复制或安装到支持 Agent Skills 的环境。加载后，可以直接说：

- “用七维引力审这篇深度稿。”
- “选择适合这篇产品文案的主维度并修改。”
- “不要七项全满足，只选最有效的 2–4 项。”

## 文档

- [原始七点总结](references/original-seven-points.md)
- [原始图文的完整文字整理版](references/original-article-full-text.md)
- [完整框架](references/framework.md)
- [AI 日报 A/B 实验](examples/ai-daily-ab/README.md)

## License

MIT

---

## English summary

Seven-Dimension Content Gravity is a model-agnostic editorial framework. It selects 2-4 article-fit dimensions from emotional tension, reader benefit, story/case, unique angle, author voice, format, and specificity. The repository ships an Agent Skill, a zero-dependency CLI, a Python API, and a hash-bound report contract for integration with other tools.
