"""
Doc2MD REST API
"""

import os
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import uvicorn

from .converter import convert_pdf, convert_docx, convert_html, convert_url

app = FastAPI(
    title="Doc2MD",
    description="Document to Markdown converter API. Supports PDF, Word, HTML, and URLs.",
    version="0.2.0",
)


class UrlRequest(BaseModel):
    url: str
    timeout: float = 30.0
    use_fallback: bool = True
    prefer_markdown_new: bool = False


class HtmlRequest(BaseModel):
    html: str
    base_url: Optional[str] = None


class ConversionResponse(BaseModel):
    markdown: str
    source_type: str
    char_count: int


@app.get("/")
async def root():
    return {
        "name": "Doc2MD",
        "description": "Document to Markdown converter",
        "version": "0.2.0",
        "endpoints": {
            "/convert/pdf": "POST - Convert PDF file",
            "/convert/docx": "POST - Convert Word document",
            "/convert/html": "POST - Convert HTML string",
            "/convert/url": "GET/POST - Fetch URL and convert",
            "/{url:path}": "GET - URL prefix mode (e.g., /https://example.com)",
        },
        "features": {
            "cloudflare_markdown": "Supports Accept: text/markdown",
            "markdown_new_fallback": "Falls back to markdown.new on failure",
            "url_prefix_mode": "Prepend d.indiekit.ai/ to any URL",
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


# ============== URL Prefix Mode ==============
# Matches: /https://example.com, /http://example.com
# This must be defined carefully to not conflict with other routes

@app.get("/https/{path:path}", response_class=PlainTextResponse)
async def url_prefix_https(
    path: str,
    fallback: bool = Query(True, description="Use markdown.new as fallback"),
    prefer_new: bool = Query(False, description="Prefer markdown.new as primary")
):
    """
    URL prefix mode for HTTPS URLs.
    Usage: d.indiekit.ai/https://example.com
    """
    url = f"https://{path}"
    try:
        markdown = await convert_url(url, use_fallback=fallback, prefer_markdown_new=prefer_new)
        return markdown
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")


@app.get("/http/{path:path}", response_class=PlainTextResponse)
async def url_prefix_http(
    path: str,
    fallback: bool = Query(True, description="Use markdown.new as fallback"),
    prefer_new: bool = Query(False, description="Prefer markdown.new as primary")
):
    """
    URL prefix mode for HTTP URLs.
    Usage: d.indiekit.ai/http://example.com
    """
    url = f"http://{path}"
    try:
        markdown = await convert_url(url, use_fallback=fallback, prefer_markdown_new=prefer_new)
        return markdown
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")


# ============== Standard API Endpoints ==============

@app.post("/convert/pdf", response_model=ConversionResponse)
async def api_convert_pdf(file: UploadFile = File(...)):
    """Convert PDF to Markdown."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "File must be a PDF")
    
    content = await file.read()
    
    try:
        markdown = convert_pdf(content)
        return ConversionResponse(
            markdown=markdown,
            source_type="pdf",
            char_count=len(markdown)
        )
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")


@app.post("/convert/docx", response_model=ConversionResponse)
async def api_convert_docx(file: UploadFile = File(...)):
    """Convert Word document to Markdown."""
    if not file.filename or not file.filename.lower().endswith((".docx", ".doc")):
        raise HTTPException(400, "File must be a Word document (.docx)")
    
    content = await file.read()
    
    try:
        markdown = convert_docx(content)
        return ConversionResponse(
            markdown=markdown,
            source_type="docx",
            char_count=len(markdown)
        )
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")


@app.post("/convert/html", response_model=ConversionResponse)
async def api_convert_html(request: HtmlRequest):
    """Convert HTML to Markdown."""
    try:
        markdown = convert_html(request.html, base_url=request.base_url)
        return ConversionResponse(
            markdown=markdown,
            source_type="html",
            char_count=len(markdown)
        )
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")


@app.post("/convert/url", response_model=ConversionResponse)
async def api_convert_url(request: UrlRequest):
    """Fetch URL and convert to Markdown."""
    try:
        markdown = await convert_url(
            request.url, 
            timeout=request.timeout,
            use_fallback=request.use_fallback,
            prefer_markdown_new=request.prefer_markdown_new
        )
        return ConversionResponse(
            markdown=markdown,
            source_type="url",
            char_count=len(markdown)
        )
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")


@app.get("/convert/url", response_class=PlainTextResponse)
async def api_convert_url_get(
    url: str = Query(..., description="URL to convert"),
    fallback: bool = Query(True, description="Use markdown.new as fallback"),
    prefer_new: bool = Query(False, description="Prefer markdown.new as primary")
):
    """Fetch URL and convert to Markdown (GET endpoint for easy testing)."""
    try:
        markdown = await convert_url(url, use_fallback=fallback, prefer_markdown_new=prefer_new)
        return markdown
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")


def main():
    """Run the API server."""
    port = int(os.environ.get("PORT", 8087))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
