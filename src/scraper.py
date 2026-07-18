"""Document scraper for Nepal and India legal sources."""

import asyncio
import hashlib
import json
import logging
import random
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config import (
    INDIA_SOURCES,
    NEPAL_SOURCES,
    settings,
)

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class DocumentMetadata:
    """Metadata for a scraped document."""

    id: str
    country: str
    category: str
    source_url: str
    title: str
    date_published: Optional[str] = None
    date_scraped: str = ""
    file_path: str = ""
    content_hash: str = ""
    language: str = "en"
    subcategory: Optional[str] = None
    article_number: Optional[str] = None
    extra: Dict[str, Any] = None

    def __post_init__(self):
        if self.date_scraped == "":
            self.date_scraped = datetime.utcnow().isoformat()
        if self.extra is None:
            self.extra = {}


class RateLimiter:
    """Token bucket rate limiter for respecting rate limits."""

    def __init__(self, rate: float):
        self.rate = rate
        self.tokens = rate
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class UserAgentRotator:
    """Rotates user agents to avoid blocking."""

    def __init__(self, agents: List[str]):
        self.agents = agents
        self.index = 0

    def get(self) -> str:
        agent = self.agents[self.index]
        self.index = (self.index + 1) % len(self.agents)
        return agent


class DocumentScraper:
    """Async document scraper with rate limiting, retries, and resume capability."""

    def __init__(
        self,
        country: str,
        category: str,
        rate_limit: float = 2.0,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.country = country.lower()
        self.category = category.lower()
        self.rate_limiter = RateLimiter(rate_limit)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.ua_rotator = UserAgentRotator(settings.scraper_user_agents)
        self.session: Optional[aiohttp.ClientSession] = None
        self.metadata: List[DocumentMetadata] = []
        self.seen_hashes: Set[str] = set()

        # Load existing metadata to enable resume
        self._load_existing_metadata()

    def _load_existing_metadata(self):
        """Load existing documents.json to skip already downloaded files."""
        if settings.documents_file.exists():
            try:
                with open(settings.documents_file, "r") as f:
                    data = json.load(f)
                for item in data:
                    if item.get("country") == self.country and item.get("category") == self.category:
                        self.seen_hashes.add(item.get("content_hash", ""))
                logger.info(f"Loaded {len(self.seen_hashes)} existing document hashes for resume")
            except Exception as e:
                logger.warning(f"Could not load existing metadata: {e}")

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            connector=connector,
            headers={"User-Agent": self.ua_rotator.get()},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _get_save_dir(self) -> Path:
        """Get the directory to save raw files."""
        return settings.raw_data_dir / self.country / self.category

    def _get_file_path(self, url: str, content_type: str) -> Path:
        """Generate a file path for the downloaded content."""
        save_dir = self._get_save_dir()
        save_dir.mkdir(parents=True, exist_ok=True)

        # Create a filename from URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        parsed = urlparse(url)
        path_part = parsed.path.strip("/").replace("/", "_")[:50] or "index"

        if "pdf" in content_type:
            ext = ".pdf"
        elif "html" in content_type:
            ext = ".html"
        else:
            ext = ".bin"

        return save_dir / f"{path_part}_{url_hash}{ext}"

    def _compute_hash(self, content: bytes) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content).hexdigest()

    @retry(
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3),
    )
    async def _fetch(self, url: str) -> tuple[bytes, str]:
        """Fetch a URL with retries and rate limiting."""
        await self.rate_limiter.acquire()

        headers = {"User-Agent": self.ua_rotator.get()}
        async with self.session.get(url, headers=headers, allow_redirects=True) as response:
            response.raise_for_status()
            content = await response.read()
            content_type = response.headers.get("Content-Type", "").lower()
            return content, content_type

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract relevant links from HTML."""
        soup = BeautifulSoup(html, "lxml")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)

            # Filter for relevant legal documents
            parsed = urlparse(full_url)
            if parsed.scheme not in ("http", "https"):
                continue

            # Skip non-document links
            skip_patterns = [
                r"\.(jpg|jpeg|png|gif|css|js|ico|svg|woff|ttf)($|\?)",
                r"(facebook|twitter|linkedin|youtube|instagram)\.com",
                r"(mailto:|tel:|javascript:)",
            ]
            if any(re.search(p, full_url, re.I) for p in skip_patterns):
                continue

            links.append(full_url)

        return list(set(links))  # Deduplicate

    def _extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML."""
        soup = BeautifulSoup(html, "lxml")

        title = ""
        if soup.title:
            title = soup.title.string.strip() if soup.title.string else ""
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        # Try to find date
        date_patterns = [
            r"(\d{4}[-/]\d{2}[-/]\d{2})",
            r"(\d{2}[-/]\d{2}[-/]\d{4})",
            r"([A-Za-z]+ \d{1,2}, \d{4})",
        ]
        date_published = None
        text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_published = match.group(1)
                break

        return {"title": title, "date_published": date_published}

    async def _save_file(self, path: Path, content: bytes):
        """Save content to file asynchronously."""
        async with aiofiles.open(path, "wb") as f:
            await f.write(content)

    async def _process_document(self, url: str, content: bytes, content_type: str):
        """Process a single document."""
        content_hash = self._compute_hash(content)

        # Skip if already seen
        if content_hash in self.seen_hashes:
            logger.debug(f"Skipping already downloaded: {url}")
            return

        self.seen_hashes.add(content_hash)

        # Save file
        file_path = self._get_file_path(url, content_type)
        await self._save_file(file_path, content)

        # Extract metadata
        metadata = DocumentMetadata(
            id=f"{self.country}_{self.category}_{content_hash[:12]}",
            country=self.country,
            category=self.category,
            source_url=url,
            title="",
            file_path=str(file_path.relative_to(settings.project_root)),
            content_hash=content_hash,
        )

        if "html" in content_type:
            html = content.decode("utf-8", errors="ignore")
            meta = self._extract_metadata(html, url)
            metadata.title = meta["title"]
            metadata.date_published = meta["date_published"]

        self.metadata.append(metadata)
        logger.info(f"Downloaded: {metadata.title or url} -> {file_path.name}")

    async def scrape_source(self, source_url: str, max_depth: int = 2):
        """Scrape a source URL and follow links up to max_depth."""
        visited: Set[str] = set()
        to_visit: List[tuple[str, int]] = [(source_url, 0)]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Scraping {source_url}", total=None)

            while to_visit:
                url, depth = to_visit.pop(0)

                if url in visited or depth > max_depth:
                    continue

                visited.add(url)
                progress.update(task, description=f"Scraping {url[:80]}...")

                try:
                    content, content_type = await self._fetch(url)
                    await self._process_document(url, content, content_type)

                    # Follow links if HTML and not too deep
                    if depth < max_depth and "html" in content_type:
                        html = content.decode("utf-8", errors="ignore")
                        links = self._extract_links(html, url)
                        for link in links:
                            if link not in visited:
                                to_visit.append((link, depth + 1))

                    progress.advance(task)
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    progress.advance(task)

    def save_metadata(self):
        """Save metadata to documents.json."""
        # Load existing
        all_docs = []
        if settings.documents_file.exists():
            try:
                with open(settings.documents_file, "r") as f:
                    all_docs = json.load(f)
            except Exception:
                pass

        # Remove old entries for this country/category
        all_docs = [
            d for d in all_docs
            if not (d.get("country") == self.country and d.get("category") == self.category)
        ]

        # Add new entries
        for meta in self.metadata:
            all_docs.append(asdict(meta))

        # Save
        settings.documents_file.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.documents_file, "w") as f:
            json.dump(all_docs, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.metadata)} document metadata entries")


async def run_scraper(
    country: str,
    category: str,
    max_depth: int = 2,
    rate_limit: float = 2.0,
):
    """Run the scraper for a specific country and category."""
    sources = NEPAL_SOURCES if country.lower() == "nepal" else INDIA_SOURCES

    if category not in sources:
        raise ValueError(f"Unknown category: {category}. Available: {list(sources.keys())}")

    urls = sources[category]

    async with DocumentScraper(country, category, rate_limit=rate_limit) as scraper:
        for url in urls:
            logger.info(f"Starting scrape of {url}")
            await scraper.scrape_source(url, max_depth=max_depth)

        scraper.save_metadata()
        logger.info(f"Scraping complete. Downloaded {len(scraper.metadata)} documents.")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Scrape legal documents for Nepal/India")
    parser.add_argument("--country", choices=["nepal", "india"], required=True)
    parser.add_argument("--category", choices=["constitution", "legislation", "case_law", "regulations"], required=True)
    parser.add_argument("--max-depth", type=int, default=2, help="Max link depth to follow")
    parser.add_argument("--rate-limit", type=float, default=2.0, help="Requests per second")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    asyncio.run(run_scraper(args.country, args.category, args.max_depth, args.rate_limit))


if __name__ == "__main__":
    main()