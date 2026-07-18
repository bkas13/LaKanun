"""PDF and HTML text extraction for legal documents."""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

import pdfplumber
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)


@dataclass
class ExtractedChunk:
    """A chunk of extracted text with metadata."""

    text: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]


@dataclass
class ParsedDocument:
    """Result of parsing a document."""

    file_path: str
    country: str
    category: str
    title: str
    full_text: str
    language: str
    chunks: List[ExtractedChunk]
    metadata: Dict[str, Any]
    article_number: Optional[str] = None
    subcategory: Optional[str] = None


class TextChunker:
    """Split text into overlapping chunks for embeddings."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[ExtractedChunk]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        chunk_index = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)

            # Try to break at sentence boundary
            if end < text_len:
                # Look for sentence end within last 100 chars
                search_start = max(start + self.chunk_size - 100, start)
                sentence_end = self._find_sentence_boundary(text, search_start, end)
                if sentence_end > start:
                    end = sentence_end

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(ExtractedChunk(
                    text=chunk_text,
                    chunk_index=chunk_index,
                    start_char=start,
                    end_char=end,
                    metadata={}
                ))
                chunk_index += 1

            # Move start with overlap
            start = max(start + 1, end - self.chunk_overlap)

        return chunks

    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """Find the last sentence boundary in range."""
        # Look for sentence endings
        for i in range(end - 1, start - 1, -1):
            if text[i] in ".!?।" and (i + 1 == len(text) or text[i + 1].isspace()):
                return i + 1
        return end


class HTMLParser:
    """Parse HTML legal documents."""

    # Tags to remove
    REMOVE_TAGS = ["script", "style", "nav", "header", "footer", "aside", "form", "button"]

    # Selectors for main content
    CONTENT_SELECTORS = [
        "main",
        "article",
        ".content",
        "#content",
        ".main-content",
        ".post-content",
        ".entry-content",
        ".document-content",
        ".law-content",
        ".act-content",
    ]

    def __init__(self):
        self.chunker = TextChunker()

    def parse(self, file_path: Path, country: str, category: str) -> ParsedDocument:
        """Parse an HTML file."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        soup = BeautifulSoup(html, "lxml")

        # Remove unwanted tags
        for tag in soup(self.REMOVE_TAGS):
            tag.decompose()

        # Try to find main content
        content = self._extract_main_content(soup)

        # Extract title
        title = self._extract_title(soup)

        # Clean text
        full_text = self._clean_text(content.get_text(separator="\n", strip=True))

        # Detect language
        language = self._detect_language(full_text)

        # Chunk
        chunks = self.chunker.chunk_text(full_text)

        # Extract metadata
        metadata = self._extract_metadata(soup, full_text)

        return ParsedDocument(
            file_path=str(file_path),
            country=country,
            category=category,
            title=title,
            full_text=full_text,
            language=language,
            chunks=chunks,
            metadata=metadata,
        )

    def _extract_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Find the main content area."""
        for selector in self.CONTENT_SELECTORS:
            elements = soup.select(selector)
            if elements:
                return elements[0]

        # Fallback: body or whole document
        return soup.body or soup

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract document title."""
        # Try multiple sources
        if soup.title and soup.title.string:
            return soup.title.string.strip()

        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        # Try meta tags
        for meta in soup.find_all("meta"):
            if meta.get("property") == "og:title" or meta.get("name") == "title":
                return meta.get("content", "").strip()

        return "Untitled Document"

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove page numbers, headers/footers
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
        return text.strip()

    def _detect_language(self, text: str) -> str:
        """Detect document language."""
        # Sample text for detection
        sample = text[:1000]
        try:
            lang = detect(sample)
            # Map to our codes
            lang_map = {
                "ne": "ne",  # Nepali
                "hi": "hi",  # Hindi
                "en": "en",  # English
            }
            return lang_map.get(lang, "en")
        except LangDetectException:
            # Default to English
            return "en"

    def _extract_metadata(self, soup: BeautifulSoup, text: str) -> Dict[str, Any]:
        """Extract metadata from HTML."""
        meta = {}

        # Meta tags
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property")
            content = tag.get("content")
            if name and content:
                meta[name] = content

        # Extract dates
        date_patterns = [
            r"(\d{4}[-/]\d{2}[-/]\d{2})",
            r"(\d{2}[-/]\d{2}[-/]\d{4})",
            r"([A-Za-z]+ \d{1,2}, \d{4})",
        ]
        for pattern in date_patterns:
            matches = re.findall(pattern, text[:2000])
            if matches:
                meta["extracted_dates"] = matches[:5]
                break

        return meta


class PDFParser:
    """Parse PDF legal documents."""

    def __init__(self):
        self.chunker = TextChunker()

    def parse(self, file_path: Path, country: str, category: str) -> ParsedDocument:
        """Parse a PDF file."""
        full_text = ""
        pages_text = []

        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages_text.append(text)
                full_text += f"\n--- PAGE {i + 1} ---\n{text}"

        # Clean text
        full_text = self._clean_pdf_text(full_text)

        # Detect language
        language = self._detect_language(full_text)

        # Extract title from first page
        title = self._extract_pdf_title(pages_text[0] if pages_text else "")

        # Chunk
        chunks = self.chunker.chunk_text(full_text)

        # Extract metadata
        metadata = self._extract_pdf_metadata(full_text, len(pages_text))

        return ParsedDocument(
            file_path=str(file_path),
            country=country,
            category=category,
            title=title,
            full_text=full_text,
            language=language,
            chunks=chunks,
            metadata=metadata,
        )

    def _clean_pdf_text(self, text: str) -> str:
        """Clean PDF-extracted text."""
        # Remove page markers
        text = re.sub(r"--- PAGE \d+ ---", "", text)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove headers/footers (repeating lines)
        lines = text.split("\n")
        line_counts = {}
        for line in lines:
            line = line.strip()
            if len(line) > 10:
                line_counts[line] = line_counts.get(line, 0) + 1

        # Remove lines that appear on many pages (likely headers/footers)
        threshold = len(lines) * 0.3
        filtered_lines = [
            line for line in lines
            if line_counts.get(line.strip(), 0) < threshold or len(line.strip()) <= 10
        ]
        return "\n".join(filtered_lines).strip()

    def _extract_pdf_title(self, first_page: str) -> str:
        """Extract title from first page."""
        lines = first_page.split("\n")
        # First non-empty substantial line
        for line in lines:
            line = line.strip()
            if len(line) > 20 and not line.isdigit():
                return line[:200]
        return "Untitled PDF"

    def _detect_language(self, text: str) -> str:
        """Detect document language."""
        sample = text[:1000]
        try:
            lang = detect(sample)
            return {"ne": "ne", "hi": "hi", "en": "en"}.get(lang, "en")
        except LangDetectException:
            return "en"

    def _extract_pdf_metadata(self, text: str, page_count: int) -> Dict[str, Any]:
        """Extract metadata from PDF text."""
        meta = {"page_count": page_count}

        # Look for document numbers, dates
        patterns = {
            "act_number": r"(Act\s+No\.?\s*\d+)",
            "year": r"(20\d{2}|19\d{2})",
            "section": r"(Section\s+\d+[A-Z]?)",
            "article": r"(Article\s+\d+[A-Z]?)",
        }

        for key, pattern in patterns.items():
            matches = re.findall(pattern, text[:5000], re.IGNORECASE)
            if matches:
                meta[key] = matches[:10]

        return meta


def parse_document(file_path: Path, country: str, category: str) -> ParsedDocument:
    """Parse a document based on file extension."""
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        parser = PDFParser()
    elif suffix in (".html", ".htm"):
        parser = HTMLParser()
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return parser.parse(file_path, country, category)


def parse_directory(
    directory: Path,
    country: str,
    category: str,
) -> Generator[ParsedDocument, None, None]:
    """Parse all supported files in a directory."""
    extensions = {".pdf", ".html", ".htm"}

    for file_path in directory.rglob("*"):
        if file_path.suffix.lower() in extensions:
            try:
                yield parse_document(file_path, country, category)
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}")


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 4:
        print("Usage: python -m src.parser <directory> <country> <category>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    country = sys.argv[2]
    category = sys.argv[3]

    for doc in parse_directory(directory, country, category):
        print(f"Parsed: {doc.title} ({len(doc.chunks)} chunks, lang={doc.language})")