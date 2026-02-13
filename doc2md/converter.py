"""
Document conversion functions
"""

import io
import re
from typing import Optional

import fitz  # pymupdf
from docx import Document
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import httpx


def convert_pdf(content: bytes, extract_images: bool = False) -> str:
    """
    Convert PDF to Markdown.
    
    Args:
        content: PDF file bytes
        extract_images: Whether to extract and embed images (base64)
    
    Returns:
        Markdown text
    """
    doc = fitz.open(stream=content, filetype="pdf")
    markdown_parts = []
    
    for page_num, page in enumerate(doc, 1):
        # Extract text blocks
        text = page.get_text("text")
        
        if text.strip():
            # Add page separator for multi-page docs
            if page_num > 1:
                markdown_parts.append(f"\n---\n*Page {page_num}*\n")
            
            # Clean up text
            text = clean_text(text)
            markdown_parts.append(text)
    
    doc.close()
    
    result = "\n\n".join(markdown_parts)
    return post_process_markdown(result)


def convert_docx(content: bytes) -> str:
    """
    Convert Word document to Markdown.
    
    Args:
        content: DOCX file bytes
    
    Returns:
        Markdown text
    """
    doc = Document(io.BytesIO(content))
    markdown_parts = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        
        style_name = para.style.name.lower() if para.style else ""
        
        # Handle headings
        if "heading 1" in style_name:
            markdown_parts.append(f"# {text}")
        elif "heading 2" in style_name:
            markdown_parts.append(f"## {text}")
        elif "heading 3" in style_name:
            markdown_parts.append(f"### {text}")
        elif "heading 4" in style_name:
            markdown_parts.append(f"#### {text}")
        elif "title" in style_name:
            markdown_parts.append(f"# {text}")
        elif "list" in style_name:
            markdown_parts.append(f"- {text}")
        else:
            # Check for bold/italic runs
            formatted_text = format_runs(para.runs)
            markdown_parts.append(formatted_text)
    
    # Handle tables
    for table in doc.tables:
        table_md = convert_table(table)
        markdown_parts.append(table_md)
    
    result = "\n\n".join(markdown_parts)
    return post_process_markdown(result)


def format_runs(runs) -> str:
    """Format Word runs with bold/italic."""
    parts = []
    for run in runs:
        text = run.text
        if not text:
            continue
        if run.bold and run.italic:
            text = f"***{text}***"
        elif run.bold:
            text = f"**{text}**"
        elif run.italic:
            text = f"*{text}*"
        parts.append(text)
    return "".join(parts)


def convert_table(table) -> str:
    """Convert Word table to Markdown table."""
    rows = []
    for i, row in enumerate(table.rows):
        cells = [cell.text.strip().replace("|", "\\|") for cell in row.cells]
        rows.append("| " + " | ".join(cells) + " |")
        if i == 0:
            # Add header separator
            rows.append("|" + "|".join(["---"] * len(cells)) + "|")
    return "\n".join(rows)


def convert_html(content: str, base_url: Optional[str] = None) -> str:
    """
    Convert HTML to Markdown.
    
    Args:
        content: HTML string
        base_url: Base URL for resolving relative links
    
    Returns:
        Markdown text
    """
    # Parse and clean HTML
    soup = BeautifulSoup(content, "html.parser")
    
    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()
    
    # Try to find main content
    main_content = (
        soup.find("main") or 
        soup.find("article") or 
        soup.find(class_=re.compile(r"content|article|post|entry")) or
        soup.find("body") or
        soup
    )
    
    # Convert to markdown
    markdown = md(
        str(main_content),
        heading_style="atx",
        bullets="-",
        code_language="",
    )
    
    return post_process_markdown(markdown)


async def convert_url(url: str, timeout: float = 30.0) -> str:
    """
    Fetch URL and convert to Markdown.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
    
    Returns:
        Markdown text
    """
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        # Try to get markdown directly (Cloudflare Markdown for Agents)
        # Disable compression to avoid encoding issues
        headers = {"Accept": "text/markdown, text/html", "Accept-Encoding": "identity"}
        resp = await client.get(url, headers=headers)
        
        content_type = resp.headers.get("content-type", "")
        
        if "text/markdown" in content_type:
            # Server returned markdown directly!
            return resp.text
        elif "application/pdf" in content_type:
            return convert_pdf(resp.content)
        else:
            # HTML - convert to markdown
            return convert_html(resp.text, base_url=url)


def clean_text(text: str) -> str:
    """Clean up extracted text."""
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    # Remove excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def post_process_markdown(text: str) -> str:
    """Post-process markdown for cleanup."""
    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Clean up list formatting
    text = re.sub(r"\n\s*-\s+", "\n- ", text)
    # Remove trailing whitespace
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text.strip()
