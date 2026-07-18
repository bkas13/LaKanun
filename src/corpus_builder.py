"""Build structured legal corpus from parsed documents."""

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Set

from tqdm import tqdm

from .parser import parse_directory, ParsedDocument

logger = logging.getLogger(__name__)


# Nepal Constitution article mapping
NEPAL_CONSTITUTION_ARTICLES = {
    # Part 3: Fundamental Rights and Duties (Articles 16-46)
    "16": {"title": "Right to Live with Dignity", "category": "fundamental_rights", "subcategory": "life_dignity"},
    "17": {"title": "Right to Freedom", "category": "fundamental_rights", "subcategory": "freedom"},
    "18": {"title": "Right to Equality", "category": "fundamental_rights", "subcategory": "equality"},
    "19": {"title": "Right to Communication", "category": "fundamental_rights", "subcategory": "communication"},
    "20": {"title": "Right to Justice", "category": "fundamental_rights", "subcategory": "justice"},
    "21": {"title": "Right of Victim of Crime", "category": "fundamental_rights", "subcategory": "victim_rights"},
    "22": {"title": "Right against Torture", "category": "fundamental_rights", "subcategory": "torture"},
    "23": {"title": "Right against Preventive Detention", "category": "fundamental_rights", "subcategory": "detention"},
    "24": {"title": "Right against Untouchability and Discrimination", "category": "fundamental_rights", "subcategory": "discrimination"},
    "25": {"title": "Right to Property", "category": "fundamental_rights", "subcategory": "property"},
    "26": {"title": "Right to Religious Freedom", "category": "fundamental_rights", "subcategory": "religion"},
    "27": {"title": "Right to Information", "category": "fundamental_rights", "subcategory": "information"},
    "28": {"title": "Right to Privacy", "category": "fundamental_rights", "subcategory": "privacy"},
    "29": {"title": "Right against Exploitation", "category": "fundamental_rights", "subcategory": "exploitation"},
    "30": {"title": "Right to Clean Environment", "category": "fundamental_rights", "subcategory": "environment"},
    "31": {"title": "Right to Education", "category": "fundamental_rights", "subcategory": "education"},
    "32": {"title": "Right to Language and Culture", "category": "fundamental_rights", "subcategory": "culture"},
    "33": {"title": "Right to Employment", "category": "fundamental_rights", "subcategory": "employment"},
    "34": {"title": "Right to Labour", "category": "fundamental_rights", "subcategory": "labour"},
    "35": {"title": "Right to Health", "category": "fundamental_rights", "subcategory": "health"},
    "36": {"title": "Right to Food", "category": "fundamental_rights", "subcategory": "food"},
    "37": {"title": "Right to Housing", "category": "fundamental_rights", "subcategory": "housing"},
    "38": {"title": "Rights of Women", "category": "fundamental_rights", "subcategory": "women"},
    "39": {"title": "Rights of Children", "category": "fundamental_rights", "subcategory": "children"},
    "40": {"title": "Rights of Dalit", "category": "fundamental_rights", "subcategory": "dalit"},
    "41": {"title": "Rights of Senior Citizens", "category": "fundamental_rights", "subcategory": "senior_citizens"},
    "42": {"title": "Rights of Consumer", "category": "fundamental_rights", "subcategory": "consumer"},
    "43": {"title": "Rights against Exile", "category": "fundamental_rights", "subcategory": "exile"},
    "44": {"title": "Right to Constitutional Remedies", "category": "fundamental_rights", "subcategory": "remedies"},
    "45": {"title": "Duties of Citizens", "category": "fundamental_rights", "subcategory": "duties"},
    "46": {"title": "Provisions relating to Fundamental Rights", "category": "fundamental_rights", "subcategory": "provisions"},

    # Part 4: Directive Principles (Articles 47-51)
    "47": {"title": "Directive Principles", "category": "directive_principles", "subcategory": "general"},
    "48": {"title": "Policies of the State", "category": "directive_principles", "subcategory": "policies"},
    "49": {"title": "Policies relating to Social Justice and Inclusion", "category": "directive_principles", "subcategory": "social_justice"},
    "50": {"title": "Policies relating to National Economy", "category": "directive_principles", "subcategory": "economy"},
    "51": {"title": "Policies relating to National Security", "category": "directive_principles", "subcategory": "security"},

    # Other key articles
    "56": {"title": "President", "category": "executive", "subcategory": "president"},
    "75": {"title": "Federal Parliament", "category": "legislature", "subcategory": "parliament"},
    "137": {"title": "Supreme Court", "category": "judiciary", "subcategory": "supreme_court"},
    "232": {"title": "Commission for Investigation of Abuse of Authority", "category": "constitutional_bodies", "subcategory": "ciaa"},
    "281": {"title": "Amendment of Constitution", "category": "constitutional", "subcategory": "amendment"},
}


# Indian legal acts mapping
INDIAN_ACTS = {
    "ipc": {
        "name": "Indian Penal Code",
        "category": "criminal",
        "sections": list(range(1, 512)),
    },
    "crpc": {
        "name": "Code of Criminal Procedure",
        "category": "criminal",
        "sections": list(range(1, 485)),
    },
    "cpc": {
        "name": "Code of Civil Procedure",
        "category": "civil",
        "sections": list(range(1, 159)),
    },
    "contract_act": {
        "name": "Indian Contract Act",
        "category": "civil",
        "sections": list(range(1, 267)),
    },
    "minimum_wages": {
        "name": "Minimum Wages Act",
        "category": "labor",
        "sections": list(range(1, 32)),
    },
}


@dataclass
class CorpusArticle:
    """Structured legal article for the corpus."""

    id: str
    country: str
    source: str
    category: str
    subcategory: str
    article_number: str
    title: str
    full_text: str
    chunks: List[str]
    language: str
    amendments: List[str] = field(default_factory=list)
    related_articles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CorpusBuilder:
    """Build structured legal corpus from parsed documents."""

    def __init__(
        self,
        raw_data_dir: Path,
        output_file: Path,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ):
        self.raw_data_dir = raw_data_dir
        self.output_file = output_file
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.articles: List[CorpusArticle] = []
        self.article_index: Dict[str, CorpusArticle] = {}
        self.relationship_graph: Dict[str, Set[str]] = {}

    def build(self) -> List[CorpusArticle]:
        """Build the complete corpus."""
        logger.info("Starting corpus build...")

        # Process Nepal documents
        nepal_dir = self.raw_data_dir / "nepal"
        if nepal_dir.exists():
            self._process_country("nepal", nepal_dir)

        # Process India documents
        india_dir = self.raw_data_dir / "india"
        if india_dir.exists():
            self._process_country("india", india_dir)

        # Build relationship graph
        self._build_relationships()

        # Save corpus
        self._save_corpus()

        logger.info(f"Corpus built with {len(self.articles)} articles")
        return self.articles

    def _process_country(self, country: str, country_dir: Path):
        """Process all documents for a country."""
        categories = ["constitution", "legislation", "case_law", "regulations"]

        for category in categories:
            cat_dir = country_dir / category
            if not cat_dir.exists():
                continue

            logger.info(f"Processing {country}/{category}...")

            for doc in parse_directory(cat_dir, country, category):
                articles = self._extract_articles(doc, country, category)
                for article in articles:
                    self.articles.append(article)
                    self.article_index[article.id] = article

    def _extract_articles(self, doc: ParsedDocument, country: str, category: str) -> List[CorpusArticle]:
        """Extract articles from a parsed document."""
        articles = []

        if country == "nepal" and category == "constitution":
            articles.extend(self._extract_nepal_constitution_articles(doc))
        elif country == "india":
            articles.extend(self._extract_indian_articles(doc, category))
        else:
            # Generic extraction for other documents
            articles.append(self._create_generic_article(doc, country, category))

        return articles

    def _extract_nepal_constitution_articles(self, doc: ParsedDocument) -> List[CorpusArticle]:
        """Extract individual articles from Nepal Constitution."""
        articles = []
        text = doc.full_text

        # Pattern to find articles: "Article 16." or "Article 16 -"
        article_pattern = re.compile(
            r"(?:Article|अनुच्छाद)\s+(\d{1,3})[A-Z]?\s*[.\-:]\s*(.+?)(?=(?:Article|अनुच्छाद)\s+\d{1,3}[A-Z]?\s*[.\-:]|\Z)",
            re.DOTALL | re.IGNORECASE,
        )

        matches = list(article_pattern.finditer(text))

        for i, match in enumerate(matches):
            article_num = match.group(1)
            article_text = match.group(2).strip()

            if len(article_text) < 50:
                continue

            # Get article info
            info = NEPAL_CONSTITUTION_ARTICLES.get(article_num, {})
            title = info.get("title", f"Article {article_num}")
            cat = info.get("category", "constitutional")
            subcat = info.get("subcategory", "general")

            # Create chunks
            chunks = self._create_chunks(article_text)

            article = CorpusArticle(
                id=f"nepal_constitution_art_{article_num}",
                country="nepal",
                source="constitution_of_nepal_2015",
                category=cat,
                subcategory=subcat,
                article_number=article_num,
                title=title,
                full_text=article_text,
                chunks=chunks,
                language=doc.language,
                metadata={
                    "source_file": doc.file_path,
                    "part": self._get_constitution_part(article_num),
                },
            )
            articles.append(article)

        # If no articles found, create one from full doc
        if not articles and len(doc.full_text) > 500:
            articles.append(self._create_generic_article(doc, "nepal", "constitution"))

        return articles

    def _get_constitution_part(self, article_num: str) -> str:
        """Get constitution part for article number."""
        num = int(article_num)
        if 1 <= num <= 4:
            return "Preliminary"
        elif 5 <= num <= 15:
            return "Citizenship"
        elif 16 <= num <= 46:
            return "Fundamental Rights and Duties"
        elif 47 <= num <= 51:
            return "Directive Principles"
        elif 52 <= num <= 66:
            return "Executive"
        elif 67 <= num <= 90:
            return "Legislature"
        elif 91 <= num <= 106:
            return "Legislative Procedures"
        elif 107 <= num <= 136:
            return "Judiciary"
        elif 137 <= num <= 154:
            return "Constitutional Bodies"
        elif 155 <= num <= 172:
            return "Local Government"
        elif 173 <= num <= 192:
            return "Federal Finance"
        elif 193 <= num <= 204:
            return "Intergovernmental Relations"
        elif 205 <= num <= 228:
            return "Civil Service and Other Services"
        elif 229 <= num <= 240:
            return "Election Commission"
        elif 241 <= num <= 254:
            return "Audit and Finance"
        elif 255 <= num <= 270:
            return "Commissions"
        elif 271 <= num <= 280:
            return "Political Parties"
        elif 281 <= num <= 288:
            return "Emergency Powers"
        elif 289 <= num <= 308:
            return "Amendment and Miscellaneous"
        return "Unknown"

    def _extract_indian_articles(self, doc: ParsedDocument, category: str) -> List[CorpusArticle]:
        """Extract articles/sections from Indian legal documents."""
        articles = []
        text = doc.full_text

        # Try to find sections/articles
        section_pattern = re.compile(
            r"(?:Section|Article|अनुच्छाद|धारा)\s+(\d{1,3}[A-Z]?)\s*[.\-:]\s*(.+?)(?=(?:Section|Article|अनुच्छाद|धारा)\s+\d{1,3}[A-Z]?\s*[.\-:]|\Z)",
            re.DOTALL | re.IGNORECASE,
        )

        matches = list(section_pattern.finditer(text))

        if matches:
            for match in matches:
                sec_num = match.group(1)
                sec_text = match.group(2).strip()

                if len(sec_text) < 50:
                    continue

                chunks = self._create_chunks(sec_text)

                article = CorpusArticle(
                    id=f"india_{category}_sec_{sec_num}",
                    country="india",
                    source=doc.title.lower().replace(" ", "_")[:50],
                    category=category,
                    subcategory=category,
                    article_number=sec_num,
                    title=f"Section {sec_num}",
                    full_text=sec_text,
                    chunks=chunks,
                    language=doc.language,
                    metadata={"source_file": doc.file_path},
                )
                articles.append(article)
        else:
            # Generic fallback
            articles.append(self._create_generic_article(doc, "india", category))

        return articles

    def _create_generic_article(self, doc: ParsedDocument, country: str, category: str) -> CorpusArticle:
        """Create a generic article from document."""
        chunks = self._create_chunks(doc.full_text)

        # Generate ID from file path
        file_id = Path(doc.file_path).stem.lower().replace(" ", "_")[:50]

        return CorpusArticle(
            id=f"{country}_{category}_{file_id}",
            country=country,
            source=doc.title.lower().replace(" ", "_")[:50],
            category=category,
            subcategory=category,
            article_number="full",
            title=doc.title,
            full_text=doc.full_text,
            chunks=chunks,
            language=doc.language,
            metadata={"source_file": doc.file_path},
        )

    def _create_chunks(self, text: str) -> List[str]:
        """Create overlapping chunks from text."""
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)

            # Try to break at sentence boundary
            if end < text_len:
                search_start = max(start + self.chunk_size - 100, start)
                for i in range(end - 1, search_start - 1, -1):
                    if text[i] in ".!?।" and (i + 1 == text_len or text[i + 1].isspace()):
                        end = i + 1
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(chunk_text)

            start = max(start + 1, end - self.chunk_overlap)

        return chunks

    def _build_relationships(self):
        """Build relationship graph between articles."""
        # By country and category
        by_category: Dict[str, List[CorpusArticle]] = {}
        for article in self.articles:
            key = f"{article.country}_{article.category}"
            if key not in by_category:
                by_category[key] = []
            by_category[key].append(article)

        # Link sequential articles
        for key, articles in by_category.items():
            articles.sort(key=lambda a: self._sort_key(a.article_number))
            for i, article in enumerate(articles):
                related = []
                if i > 0:
                    related.append(articles[i - 1].id)
                if i < len(articles) - 1:
                    related.append(articles[i + 1].id)

                # Add constitutional cross-references for Nepal
                if article.country == "nepal" and article.category == "fundamental_rights":
                    num = article.article_number
                    if num.isdigit():
                        n = int(num)
                        if n > 16:
                            related.append(f"nepal_constitution_art_{n - 1}")
                        if n < 46:
                            related.append(f"nepal_constitution_art_{n + 1}")

                article.related_articles = related[:5]  # Limit to 5
                self.relationship_graph[article.id] = set(related)

    def _sort_key(self, article_num: str) -> tuple:
        """Sort key for article numbers."""
        match = re.match(r"(\d+)([A-Z]?)", article_num)
        if match:
            return (int(match.group(1)), match.group(2))
        return (999, article_num)

    def _save_corpus(self):
        """Save corpus to JSON file."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        data = [asdict(article) for article in self.articles]

        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved corpus to {self.output_file} ({len(data)} articles)")

        # Also save relationship graph
        graph_file = self.output_file.parent / "relationship_graph.json"
        graph_data = {k: list(v) for k, v in self.relationship_graph.items()}
        with open(graph_file, "w") as f:
            json.dump(graph_data, f, indent=2)


def build_corpus(
    raw_data_dir: Path,
    output_file: Path,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> List[CorpusArticle]:
    """Build the legal corpus."""
    builder = CorpusBuilder(raw_data_dir, output_file, chunk_size, chunk_overlap)
    return builder.build()


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    raw_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/corpus.json")

    build_corpus(raw_dir, output)