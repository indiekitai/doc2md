"""
Doc2MD REST API
"""

import os
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import uvicorn

from .converter import convert_pdf, convert_docx, convert_html, convert_url

app = FastAPI(
    title="Doc2MD",
    description="Document to Markdown converter API. Supports PDF, Word, HTML, and URLs.",
    version="0.1.0",
)


class UrlRequest(BaseModel):
    url: str
    timeout: float = 30.0


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
        "endpoints": {
            "/convert/pdf": "POST - Convert PDF file",
            "/convert/docx": "POST - Convert Word document",
            "/convert/html": "POST - Convert HTML string",
            "/convert/url": "POST - Fetch URL and convert",
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


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
        markdown = await convert_url(request.url, timeout=request.timeout)
        return ConversionResponse(
            markdown=markdown,
            source_type="url",
            char_count=len(markdown)
        )
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")


@app.get("/convert/url", response_class=PlainTextResponse)
async def api_convert_url_get(url: str = Query(..., description="URL to convert")):
    """Fetch URL and convert to Markdown (GET endpoint for easy testing)."""
    try:
        markdown = await convert_url(url)
        return markdown
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")


def main():
    """Run the API server."""
    port = int(os.environ.get("PORT", 8087))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
