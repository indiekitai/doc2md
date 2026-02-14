# Doc2MD

[![PyPI](https://img.shields.io/pypi/v/indiekit-doc2md?color=blue)](https://pypi.org/project/indiekit-doc2md/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

文档转 Markdown 服务。专为 AI Agent 设计，提供 REST API 和 MCP 两种接入方式。

## 支持格式

| 输入 | 输出 |
|------|------|
| PDF | Markdown |
| Word (.docx) | Markdown |
| HTML | Markdown |
| URL (网页) | Markdown |

## 特点

- **Agent 友好**：纯 API，无 GUI，专为程序调用设计
- **支持 Cloudflare Markdown for Agents**：抓取网页时优先获取 Markdown 格式
- **双接入**：REST API + MCP Server，灵活接入
- **自动清洗**：HTML 转换时自动移除脚本、导航等无关内容

## 安装

```bash
pip install indiekit-doc2md
```

## REST API 使用

启动服务：

```bash
doc2md-server
# 默认端口 8087
```

### 转换网页

```bash
curl "http://localhost:8087/convert/url?url=https://example.com"
```

### 转换 PDF

```bash
curl -X POST http://localhost:8087/convert/pdf \
  -F "file=@document.pdf"
```

### 转换 Word

```bash
curl -X POST http://localhost:8087/convert/docx \
  -F "file=@document.docx"
```

### 转换 HTML

```bash
curl -X POST http://localhost:8087/convert/html \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Hello</h1><p>World</p>"}'
```

## MCP Server 使用

配置 Claude Desktop（`claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "doc2md": {
      "command": "doc2md-mcp"
    }
  }
}
```

然后对 Claude 说：
- "把这个网页转成 Markdown：https://..."
- "帮我把这个 PDF 转成文本"

## API 文档

启动服务后访问：`http://localhost:8087/docs`

## 作为库使用

```python
from doc2md import convert_url, convert_pdf, convert_html

# 转换网页
markdown = await convert_url("https://example.com")

# 转换 PDF
with open("doc.pdf", "rb") as f:
    markdown = convert_pdf(f.read())

# 转换 HTML
markdown = convert_html("<h1>Hello</h1>")
```

## License

MIT
