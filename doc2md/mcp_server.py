"""
Doc2MD MCP Server
Let AI agents convert documents to Markdown
"""

import asyncio
import base64

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .converter import convert_pdf, convert_docx, convert_html, convert_url

server = Server("doc2md")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available document conversion tools."""
    return [
        Tool(
            name="convert_url_to_markdown",
            description="抓取网页并转换为 Markdown 格式。支持 Cloudflare Markdown for Agents 协议，会优先获取 Markdown 格式。",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要转换的网页 URL"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="convert_html_to_markdown",
            description="将 HTML 内容转换为 Markdown 格式。自动清理脚本、样式等无关内容。",
            inputSchema={
                "type": "object",
                "properties": {
                    "html": {
                        "type": "string",
                        "description": "要转换的 HTML 内容"
                    }
                },
                "required": ["html"]
            }
        ),
        Tool(
            name="convert_pdf_to_markdown",
            description="将 PDF 文件转换为 Markdown 格式。输入 base64 编码的 PDF 内容。",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_base64": {
                        "type": "string",
                        "description": "Base64 编码的 PDF 文件内容"
                    }
                },
                "required": ["pdf_base64"]
            }
        ),
        Tool(
            name="convert_docx_to_markdown",
            description="将 Word 文档转换为 Markdown 格式。输入 base64 编码的 DOCX 内容。",
            inputSchema={
                "type": "object",
                "properties": {
                    "docx_base64": {
                        "type": "string",
                        "description": "Base64 编码的 DOCX 文件内容"
                    }
                },
                "required": ["docx_base64"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a document conversion tool."""
    
    try:
        if name == "convert_url_to_markdown":
            url = arguments.get("url", "")
            if not url:
                return [TextContent(type="text", text="错误：需要提供 URL")]
            
            markdown = await convert_url(url)
            
            # Truncate if too long
            if len(markdown) > 100000:
                markdown = markdown[:100000] + "\n\n...[内容过长，已截断]..."
            
            return [TextContent(type="text", text=markdown)]
        
        elif name == "convert_html_to_markdown":
            html = arguments.get("html", "")
            if not html:
                return [TextContent(type="text", text="错误：需要提供 HTML 内容")]
            
            markdown = convert_html(html)
            return [TextContent(type="text", text=markdown)]
        
        elif name == "convert_pdf_to_markdown":
            pdf_b64 = arguments.get("pdf_base64", "")
            if not pdf_b64:
                return [TextContent(type="text", text="错误：需要提供 base64 编码的 PDF")]
            
            try:
                pdf_bytes = base64.b64decode(pdf_b64)
            except Exception:
                return [TextContent(type="text", text="错误：无效的 base64 编码")]
            
            markdown = convert_pdf(pdf_bytes)
            return [TextContent(type="text", text=markdown)]
        
        elif name == "convert_docx_to_markdown":
            docx_b64 = arguments.get("docx_base64", "")
            if not docx_b64:
                return [TextContent(type="text", text="错误：需要提供 base64 编码的 DOCX")]
            
            try:
                docx_bytes = base64.b64decode(docx_b64)
            except Exception:
                return [TextContent(type="text", text="错误：无效的 base64 编码")]
            
            markdown = convert_docx(docx_bytes)
            return [TextContent(type="text", text=markdown)]
        
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
            
    except Exception as e:
        return [TextContent(type="text", text=f"转换失败: {str(e)}")]


def main():
    """Run the MCP server."""
    asyncio.run(stdio_server(server))


if __name__ == "__main__":
    main()
