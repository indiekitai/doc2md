# Doc2MD

[![PyPI](https://img.shields.io/pypi/v/indiekit-doc2md?color=blue)](https://pypi.org/project/indiekit-doc2md/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

文档转 Markdown 服务。专为 AI Agent 设计，提供 REST API 和 MCP 两种接入方式。

**Live Demo**: https://d.indiekit.ai

## ✨ 特性

- **URL 前缀模式** - `d.indiekit.ai/https/example.com` 直接转换
- **三层转换管道** - Cloudflare → 本地转换 → markdown.new fallback
- **多格式支持** - PDF, Word, HTML, URL
- **MCP Server** - 让 Claude Desktop 直接调用
- **Agent 友好** - 纯 API，无 GUI

## 快速开始

### 方式一：URL 前缀（最简单）

```
https://d.indiekit.ai/https/example.com
https://d.indiekit.ai/https/github.com
https://d.indiekit.ai/https/news.ycombinator.com
```

在浏览器直接访问，或用 curl：

```bash
curl https://d.indiekit.ai/https/example.com
```

### 方式二：GET API

```bash
# 基础用法
curl "https://d.indiekit.ai/convert/url?url=https://example.com"

# 强制使用 markdown.new
curl "https://d.indiekit.ai/convert/url?url=https://example.com&prefer_new=true"
```

### 方式三：POST API

```bash
curl -X POST https://d.indiekit.ai/convert/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "prefer_markdown_new": true}'
```

## 转换管道

Doc2MD 使用三层 fallback 确保高可用：

```
1. Cloudflare Markdown for Agents
   ↓ (如果网站不支持)
2. 本地 HTML → Markdown 转换
   ↓ (如果转换失败或质量差)
3. markdown.new 服务
```

## 支持格式

| 格式 | 端点 | 方法 |
|------|------|------|
| URL | `/convert/url` | GET/POST |
| URL | `/https/{url}` | GET (前缀模式) |
| PDF | `/convert/pdf` | POST (file) |
| Word | `/convert/docx` | POST (file) |
| HTML | `/convert/html` | POST (json) |

## API 示例

### 转换 PDF

```bash
curl -X POST https://d.indiekit.ai/convert/pdf \
  -F "file=@document.pdf"
```

### 转换 Word

```bash
curl -X POST https://d.indiekit.ai/convert/docx \
  -F "file=@document.docx"
```

### 转换 HTML

```bash
curl -X POST https://d.indiekit.ai/convert/html \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Hello</h1><p>World</p>"}'
```

## MCP Server

安装后可在 Claude Desktop 中使用：

```bash
pip install indiekit-doc2md
```

配置 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "doc2md": {
      "command": "doc2md-mcp"
    }
  }
}
```

### MCP 工具列表

| 工具 | 描述 |
|------|------|
| `convert_url_to_markdown` | 转换 URL，支持 `prefer_markdown_new` 参数 |
| `fetch_via_markdown_new` | 直接通过 markdown.new 转换 |
| `convert_html_to_markdown` | 转换 HTML 字符串 |
| `convert_pdf_to_markdown` | 转换 base64 编码的 PDF |
| `convert_docx_to_markdown` | 转换 base64 编码的 Word |

### 使用示例

对 Claude 说：
- "把这个网页转成 Markdown：https://..."
- "用 markdown.new 抓取这个页面：https://..."
- "帮我把这个 PDF 转成文本"

## 作为 Python 库

```python
from doc2md import convert_url, convert_pdf, convert_html

# 转换 URL（自动 fallback）
markdown = await convert_url("https://example.com")

# 强制使用 markdown.new
markdown = await convert_url("https://example.com", prefer_markdown_new=True)

# 转换 PDF
with open("doc.pdf", "rb") as f:
    markdown = convert_pdf(f.read())

# 转换 HTML
markdown = convert_html("<h1>Hello</h1>")
```

## 自托管

```bash
git clone https://github.com/indiekitai/doc2md
cd doc2md
pip install -e .
doc2md-server  # 默认端口 8087
```

## 致谢

- [markdown.new](https://markdown.new) - 作为 fallback 服务
- [Cloudflare Markdown for Agents](https://blog.cloudflare.com/markdown-for-agents/) - 原生 Markdown 支持

## License

MIT
