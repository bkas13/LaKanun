"""Multilingual legal embeddings with ChromaDB vector store."""

import logging
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
import numpy as np

from src.config import settings

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class SearchResult:
    """Result from vector search."""

    id: str
    text: str
    score: float
    metadata: Dict[str, Any]


class EmbeddingManager:
    """Manage multilingual embeddings and vector search."""

    def __init__(
        self,
        model_name: str = None,
        persist_dir: Path = None,
        chunk_size: int = 512,
    ):
        self.model_name = model_name or settings.embedding_model
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        self.chunk_size = chunk_size

        self.model: Optional[SentenceTransformer] = None
        self.client: Optional[chromadb.Client] = None
        self.collections: Dict[str, Any] = {}

    def load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded. Dimension: {self.model.get_sentence_embedding_dimension()}")
        return self.model

    def init_chroma(self) -> chromadb.Client:
        """Initialize ChromaDB client."""
        if self.client is None:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=Settings(anonymized_telemetry=False),
            )
            logger.info(f"ChromaDB initialized at {self.persist_dir}")
        return self.client

    def get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection."""
        client = self.init_chroma()
        try:
            collection = client.get_collection(name)
            logger.info(f"Loaded existing collection: {name} ({collection.count()} items)")
        except Exception:
            collection = client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"Created new collection: {name}")
        self.collections[name] = collection
        return collection

    def get_country_collections(self, country: str) -> Dict[str, Any]:
        """Get all collections for a country."""
        collections = {}
        domains = ["general"] + settings.legal_domains

        for domain in domains:
            name = f"{settings.collection_prefix}_{country}_{domain}"
            collections[domain] = self.get_or_create_collection(name)

        return collections

    def index_corpus(self, corpus_file: Path, batch_size: int = 100):
        """Index the full corpus into ChromaDB."""
        logger.info(f"Loading corpus from {corpus_file}")

        with open(corpus_file, "r", encoding="utf-8") as f:
            corpus = json.load(f)

        logger.info(f"Loaded {len(corpus)} articles")

        self.load_model()
        self.init_chroma()

        # Group by country and domain
        by_country_domain: Dict[str, List[Dict]] = {}

        for article in corpus:
            country = article.get("country", "unknown")
            category = article.get("category", "general")
            key = f"{country}_{category}"
            if key not in by_country_domain:
                by_country_domain[key] = []
            by_country_domain[key].append(article)

        # Index each group
        for key, articles in by_country_domain.items():
            country, domain = key.split("_", 1)
            collection_name = f"{settings.collection_prefix}_{country}_{domain}"
            collection = self.get_or_create_collection(collection_name)

            logger.info(f"Indexing {len(articles)} articles for {collection_name}")

            self._index_articles(collection, articles, batch_size)

        logger.info("Indexing complete")

    def _index_articles(self, collection, articles: List[Dict], batch_size: int):
        """Index a batch of articles."""
        ids = []
        documents = []
        metadatas = []

        for article in articles:
            article_id = article.get("id", "")
            full_text = article.get("full_text", "")
            chunks = article.get("chunks", [])

            if not full_text and not chunks:
                continue

            # Use chunks if available, otherwise chunk the full text
            texts_to_index = chunks if chunks else [full_text]

            for i, chunk_text in enumerate(texts_to_index):
                chunk_id = f"{article_id}_chunk_{i}" if len(texts_to_index) > 1 else article_id

                ids.append(chunk_id)
                documents.append(chunk_text)

                metadata = {
                    "article_id": article_id,
                    "country": article.get("country", ""),
                    "category": article.get("category", ""),
                    "subcategory": article.get("subcategory", ""),
                    "article_number": article.get("article_number", ""),
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "language": article.get("language", "en"),
                    "chunk_index": i,
                    "total_chunks": len(texts_to_index),
                }
                metadatas.append(metadata)

                # Batch insert
                if len(ids) >= batch_size:
                    self._add_batch(collection, ids, documents, metadatas)
                    ids, documents, metadatas = [], [], []

        # Insert remaining
        if ids:
            self._add_batch(collection, ids, documents, metadatas)

    def _add_batch(self, collection, ids: List[str], documents: List[str], metadatas: List[Dict]):
        """Add a batch to ChromaDB with embeddings."""
        try:
            embeddings = self.model.encode(documents, show_progress_bar=False, batch_size=32).tolist()
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        except Exception as e:
            logger.error(f"Failed to add batch: {e}")
            # Try one by one
            for i in range(len(ids)):
                try:
                    emb = self.model.encode([documents[i]]).tolist()
                    collection.add(
                        ids=[ids[i]],
                        documents=[documents[i]],
                        embeddings=emb,
                        metadatas=[metadatas[i]],
                    )
                except Exception as e2:
                    logger.error(f"Failed to add {ids[i]}: {e2}")

    def search(
        self,
        query: str,
        country: str = None,
        category: str = None,
        top_k: int = 10,
        filter_metadata: Dict = None,
    ) -> List[SearchResult]:
        """Search for relevant legal articles."""
        self.load_model()

        # Build filter
        where = filter_metadata or {}
        if country:
            where["country"] = country
        if category:
            where["category"] = category

        # Determine which collections to search
        collections_to_search = []

        if country and category:
            name = f"{settings.collection_prefix}_{country}_{category}"
            if name in self.collections:
                collections_to_search.append(self.collections[name])
            else:
                collections_to_search.append(self.get_or_create_collection(name))
        elif country:
            # Search all domains for country
            for domain in ["general"] + settings.legal_domains:
                name = f"{settings.collection_prefix}_{country}_{domain}"
                try:
                    collections_to_search.append(self.get_or_create_collection(name))
                except Exception:
                    pass
        else:
            # Search all collections
            for name in self.collections:
                collections_to_search.append(self.collections[name])

        if not collections_to_search:
            logger.warning("No collections to search")
            return []

        # Encode query
        query_embedding = self.model.encode([query]).tolist()[0]

        # Search each collection
        all_results = []

        for collection in collections_to_search:
            try:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where if where else None,
                    include=["documents", "metadatas", "distances"],
                )

                if results["ids"] and results["ids"][0]:
                    for i, doc_id in enumerate(results["ids"][0]):
                        all_results.append(SearchResult(
                            id=doc_id,
                            text=results["documents"][0][i],
                            score=1 - results["distances"][0][i],  # Convert distance to similarity
                            metadata=results["metadatas"][0][i],
                        ))
            except Exception as e:
                logger.error(f"Search failed for {collection.name}: {e}")

        # Sort by score and deduplicate by article_id
        seen_articles = set()
        unique_results = []

        for result in sorted(all_results, key=lambda x: x.score, reverse=True):
            article_id = result.metadata.get("article_id", result.id)
            if article_id not in seen_articles:
                seen_articles.add(article_id)
                unique_results.append(result)

        return unique_results[:top_k]

    def find_related_articles(self, article_id: str, top_k: int = 5) -> List[SearchResult]:
        """Find articles related to a given article."""
        # Get the article's text from any collection
        for name, collection in self.collections.items():
            try:
                result = collection.get(ids=[article_id], include=["documents", "metadatas"])
                if result["ids"]:
                    text = result["documents"][0]
                    metadata = result["metadatas"][0]
                    country = metadata.get("country", "")
                    category = metadata.get("category", "")

                    # Search for similar
                    return self.search(text, country=country, category=category, top_k=top_k + 1)[1:]
            except Exception:
                continue

        return []

    def get_article(self, article_id: str) -> Optional[Dict]:
        """Get full article by ID."""
        for name, collection in self.collections.items():
            try:
                result = collection.get(ids=[article_id], include=["documents", "metadatas"])
                if result["ids"]:
                    return {
                        "id": article_id,
                        "text": result["documents"][0],
                        "metadata": result["metadatas"][0],
                    }
            except Exception:
                continue
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        stats = {"collections": {}, "total_documents": 0}

        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats["collections"][name] = count
                stats["total_documents"] += count
            except Exception:
                stats["collections"][name] = 0

        return stats

    def clear_all(self):
        """Clear all collections (use with caution)."""
        client = self.init_chroma()
        for name in client.list_collections():
            client.delete_collection(name)
        self.collections.clear()
        logger.info("All collections cleared")


# CLI
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Legal embeddings manager")
    parser.add_argument("--index", action="store_true", help="Index corpus")
    parser.add_argument("--query", type=str, help="Search query")
    parser.add_argument("--country", type=str, choices=["nepal", "india"], help="Filter by country")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--clear", action="store_true", help="Clear all collections")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    manager = EmbeddingManager()

    if args.clear:
        manager.clear_all()
        return

    if args.index:
        corpus_file = settings.corpus_file
        if corpus_file.exists():
            manager.index_corpus(corpus_file)
        else:
            logger.error(f"Corpus file not found: {corpus_file}")
        return

    if args.stats:
        stats = manager.get_stats()
        console.print_json(json.dumps(stats, indent=2))
        return

    if args.query:
        results = manager.search(
            args.query,
            country=args.country,
            category=args.category,
            top_k=args.top_k,
        )

        console.print(f"\n[bold]Found {len(results)} results for: {args.query}[/bold]\n")

        for i, result in enumerate(results, 1):
            meta = result.metadata
            console.print(f"[cyan]{i}. {meta.get('title', 'Unknown')}[/cyan]")
            console.print(f"   Article: {meta.get('article_id', 'N/A')}")
            console.print(f"   Country: {meta.get('country', 'N/A')} | Category: {meta.get('category', 'N/A')}")
            console.print(f"   Score: {result.score:.4f}")
            console.print(f"   Text: {result.text[:200]}...")
            console.print()

        return

    parser.print_help()


if __name__ == "__main__":
    main()