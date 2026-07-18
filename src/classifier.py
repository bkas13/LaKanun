"""Legal classification engine with RAG and LLM support."""

import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.config import settings
from src.embeddings import EmbeddingManager, SearchResult

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class ApplicableLaw:
    """A law applicable to the legal scenario."""

    id: str
    country: str
    title: str
    text: str
    relevance_score: float
    stance: str  # violates, supports, conditional, related, neutral
    explanation: str
    article_number: str = ""
    category: str = ""


@dataclass
class LegalAnalysis:
    """Complete legal analysis result."""

    query: str
    classification: str
    confidence: float
    applicable_laws: List[ApplicableLaw]
    reasoning: str
    legal_domains: List[str]
    jurisdiction: str
    severity: str
    recommended_action: str
    disclaimer: str = "This is AI-generated legal analysis, not professional legal advice. Consult a qualified attorney for legal matters."
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    query_id: str = ""


class LegalClassifier:
    """Core legal classification engine using RAG."""

    CLASSIFICATION_CATEGORIES = [
        "legal",
        "illegal",
        "illegal_with_conditions",
        "partially_legal",
        "requires_permits",
        "gray_area",
        "jurisdiction_specific",
    ]

    STANCE_TYPES = ["violates", "supports", "conditional", "related", "neutral"]

    SEVERITY_LEVELS = ["low", "medium", "high", "critical"]

    def __init__(
        self,
        embedding_manager: EmbeddingManager = None,
        anthropic_api_key: str = None,
        openai_api_key: str = None,
        use_llm: bool = True,
    ):
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.use_llm = use_llm
        self.anthropic_api_key = anthropic_api_key or settings.anthropic_api_key
        self.openai_api_key = openai_api_key or settings.openai_api_key

        # Load prompts
        from src.prompts import get_classification_prompt, get_reasoning_prompt
        self.classification_prompt_template = get_classification_prompt()
        self.reasoning_prompt_template = get_reasoning_prompt()

    def classify(
        self,
        query: str,
        country: str = "nepal",
        language: str = "en",
        top_k: int = 10,
    ) -> LegalAnalysis:
        """Classify a legal scenario."""
        query_id = hashlib.md5(f"{query}{country}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12]

        # Step 1: Retrieve relevant articles
        logger.info(f"Retrieving articles for query: {query[:100]}")
        search_results = self.embedding_manager.search(
            query=query,
            country=country,
            top_k=top_k,
        )

        if not search_results:
            return self._create_empty_analysis(query, query_id, country)

        # Step 2: Prepare context for LLM
        context_articles = self._prepare_context(search_results)

        # Step 3: Classify using LLM or fallback
        if self.use_llm and (self.anthropic_api_key or self.openai_api_key):
            analysis = self._classify_with_llm(query, context_articles, country, language)
        else:
            analysis = self._classify_with_similarity(query, search_results, country)

        analysis.query_id = query_id
        return analysis

    def _prepare_context(self, results: List[SearchResult]) -> List[Dict]:
        """Prepare retrieved articles as context."""
        context = []
        for i, result in enumerate(results):
            meta = result.metadata
            context.append({
                "rank": i + 1,
                "article_id": meta.get("article_id", result.id),
                "title": meta.get("title", "Unknown"),
                "country": meta.get("country", ""),
                "category": meta.get("category", ""),
                "article_number": meta.get("article_number", ""),
                "text": result.text,
                "relevance_score": result.score,
            })
        return context

    def _classify_with_llm(
        self,
        query: str,
        context_articles: List[Dict],
        country: str,
        language: str,
    ) -> LegalAnalysis:
        """Classify using LLM with RAG context."""
        try:
            if self.anthropic_api_key:
                return self._classify_with_anthropic(query, context_articles, country, language)
            elif self.openai_api_key:
                return self._classify_with_openai(query, context_articles, country, language)
        except Exception as e:
            logger.error(f"LLM classification failed: {e}, falling back to similarity")

        return self._classify_with_similarity(query, [], country, context_articles)

    def _classify_with_anthropic(
        self,
        query: str,
        context_articles: List[Dict],
        country: str,
        language: str,
    ) -> LegalAnalysis:
        """Classify using Anthropic Claude."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.anthropic_api_key)

        # Build context string
        context_str = "\n\n".join([
            f"[Article {i+1}] {art['title']} ({art['country']} - {art['category']} - Art. {art['article_number']})\n{art['text'][:1500]}"
            for i, art in enumerate(context_articles)
        ])

        prompt = self.classification_prompt_template.format(
            query=query,
            country=country.upper(),
            language=language,
            context=context_str,
            categories=", ".join(self.CLASSIFICATION_CATEGORIES),
            stances=", ".join(self.STANCE_TYPES),
        )

        response = client.messages.create(
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        return self._parse_llm_response(response.content[0].text, query, context_articles, country)

    def _classify_with_openai(
        self,
        query: str,
        context_articles: List[Dict],
        country: str,
        language: str,
    ) -> LegalAnalysis:
        """Classify using OpenAI GPT."""
        from openai import OpenAI

        client = OpenAI(api_key=self.openai_api_key)

        context_str = "\n\n".join([
            f"[Article {i+1}] {art['title']} ({art['country']} - {art['category']} - Art. {art['article_number']})\n{art['text'][:1500]}"
            for i, art in enumerate(context_articles)
        ])

        prompt = self.classification_prompt_template.format(
            query=query,
            country=country.upper(),
            language=language,
            context=context_str,
            categories=", ".join(self.CLASSIFICATION_CATEGORIES),
            stances=", ".join(self.STANCE_TYPES),
        )

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        return self._parse_llm_response(response.choices[0].message.content, query, context_articles, country)

    def _parse_llm_response(
        self,
        response_text: str,
        query: str,
        context_articles: List[Dict],
        country: str,
    ) -> LegalAnalysis:
        """Parse LLM response into structured analysis."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response_text)

            # Build applicable laws
            applicable_laws = []
            for law_data in data.get("applicable_laws", []):
                applicable_laws.append(ApplicableLaw(
                    id=law_data.get("id", ""),
                    country=law_data.get("country", country),
                    title=law_data.get("title", ""),
                    text=law_data.get("text", ""),
                    relevance_score=law_data.get("relevance_score", 0.0),
                    stance=law_data.get("stance", "related"),
                    explanation=law_data.get("explanation", ""),
                    article_number=law_data.get("article_number", ""),
                    category=law_data.get("category", ""),
                ))

            return LegalAnalysis(
                query=query,
                classification=data.get("classification", "gray_area"),
                confidence=data.get("confidence", 0.5),
                applicable_laws=applicable_laws,
                reasoning=data.get("reasoning", ""),
                legal_domains=data.get("legal_domains", []),
                jurisdiction=country,
                severity=data.get("severity", "medium"),
                recommended_action=data.get("recommended_action", "Consult a legal professional"),
            )

        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # Fallback
            return self._classify_with_similarity(query, [], country, context_articles)

    def _classify_with_similarity(
        self,
        query: str,
        search_results: List[SearchResult],
        country: str,
        context_articles: List[Dict] = None,
    ) -> LegalAnalysis:
        """Fallback classification using similarity scores only."""
        if not search_results and context_articles:
            # Convert context to search results
            search_results = [
                SearchResult(
                    id=a["article_id"],
                    text=a["text"],
                    score=a["relevance_score"],
                    metadata={
                        "article_id": a["article_id"],
                        "title": a["title"],
                        "country": a["country"],
                        "category": a["category"],
                        "article_number": a["article_number"],
                    },
                )
                for a in context_articles
            ]

        if not search_results:
            return self._create_empty_analysis(query, "", country)

        # Simple heuristic classification
        top_result = search_results[0]
        top_score = top_result.score

        # Determine classification based on top matches
        if top_score > 0.75:
            classification = "legal"
        elif top_score > 0.55:
            classification = "partially_legal"
        elif top_score > 0.4:
            classification = "gray_area"
        elif top_score > 0.3:
            classification = "illegal_with_conditions"
        else:
            classification = "illegal"

        # Build applicable laws from top results
        applicable_laws = []
        for i, result in enumerate(search_results[:5]):
            meta = result.metadata
            stance = "related"
            if result.score > 0.7:
                stance = "supports"
            elif result.score > 0.5:
                stance = "conditional"

            applicable_laws.append(ApplicableLaw(
                id=meta.get("article_id", result.id),
                country=meta.get("country", country),
                title=meta.get("title", "Unknown"),
                text=result.text[:500],
                relevance_score=result.score,
                stance=stance,
                explanation=f"Relevance score: {result.score:.2f}",
                article_number=meta.get("article_number", ""),
                category=meta.get("category", ""),
            ))

        # Simple reasoning
        reasoning = f"Based on similarity search, found {len(search_results)} relevant legal provisions. "
        reasoning += f"Top match: '{search_results[0].metadata.get('title', 'Unknown')}' with score {top_score:.2f}. "

        if classification in ["illegal", "illegal_with_conditions"]:
            reasoning += "The scenario appears to violate or conflict with existing legal provisions."
        elif classification in ["legal", "partially_legal"]:
            reasoning += "The scenario appears to be supported by or compliant with existing legal provisions."
        else:
            reasoning += "The legal status is unclear and requires professional legal consultation."

        return LegalAnalysis(
            query=query,
            classification=classification,
            confidence=min(top_score, 0.85),
            applicable_laws=applicable_laws,
            reasoning=reasoning,
            legal_domains=list(set(r.metadata.get("category", "") for r in search_results[:3] if r.metadata.get("category"))),
            jurisdiction=country,
            severity="high" if classification == "illegal" else "medium",
            recommended_action="Consult a qualified attorney for definitive legal advice",
        )

    def _create_empty_analysis(self, query: str, query_id: str, country: str) -> LegalAnalysis:
        """Create analysis when no results found."""
        return LegalAnalysis(
            query=query,
            query_id=query_id,
            classification="gray_area",
            confidence=0.0,
            applicable_laws=[],
            reasoning="No relevant legal provisions found in the database for this query.",
            legal_domains=[],
            jurisdiction=country,
            severity="low",
            recommended_action="Consult a qualified attorney. The legal database may not have coverage for this specific scenario.",
        )

    def interactive_mode(self, country: str = "nepal", language: str = "en"):
        """Run interactive CLI mode."""
        console.print(Panel.fit(
            f"[bold]Nepal Legal AI - Interactive Mode[/bold]\n"
            f"Country: {country.upper()} | Language: {language}\n"
            f"Type 'quit' or 'exit' to leave\n"
            f"Type 'help' for commands",
            border_style="blue",
        ))

        while True:
            try:
                query = Prompt.ask("\n[bold cyan]Enter legal scenario[/bold cyan]")

                if query.lower() in ("quit", "exit", "q"):
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if query.lower() in ("help", "h"):
                    self._show_help()
                    continue

                if not query.strip():
                    continue

                # Classify
                with console.status("[bold green]Analyzing...[/bold green]"):
                    analysis = self.classify(query, country=country, language=language)

                # Display results
                self._display_analysis(analysis)

            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.exception("Interactive mode error")

    def _display_analysis(self, analysis: LegalAnalysis):
        """Display analysis results in a formatted way."""
        # Classification with color
        colors = {
            "legal": "green",
            "illegal": "red",
            "illegal_with_conditions": "orange3",
            "partially_legal": "yellow",
            "requires_permits": "blue",
            "gray_area": "magenta",
            "jurisdiction_specific": "cyan",
        }
        color = colors.get(analysis.classification, "white")

        console.print(f"\n[bold]Classification:[/bold] [{color}]{analysis.classification.replace('_', ' ').title()}[/{color}]")
        console.print(f"[bold]Confidence:[/bold] {analysis.confidence:.1%}")
        console.print(f"[bold]Severity:[/bold] {analysis.severity.upper()}")
        console.print(f"[bold]Jurisdiction:[/bold] {analysis.jurisdiction.upper()}")

        if analysis.legal_domains:
            console.print(f"[bold]Legal Domains:[/bold] {', '.join(analysis.legal_domains)}")

        console.print(f"\n[bold]Reasoning:[/bold]")
        console.print(analysis.reasoning)

        if analysis.applicable_laws:
            console.print(f"\n[bold]Applicable Laws ({len(analysis.applicable_laws)}):[/bold]")
            table = Table(show_header=True, header_style="bold")
            table.add_column("#")
            table.add_column("Article")
            table.add_column("Title")
            table.add_column("Stance")
            table.add_column("Score")
            table.add_column("Explanation")

            for i, law in enumerate(analysis.applicable_laws, 1):
                stance_color = {
                    "violates": "red",
                    "supports": "green",
                    "conditional": "yellow",
                    "related": "blue",
                    "neutral": "white",
                }.get(law.stance, "white")

                table.add_row(
                    str(i),
                    law.article_number or law.id[:20],
                    law.title[:50],
                    f"[{stance_color}]{law.stance}[/{stance_color}]",
                    f"{law.relevance_score:.2f}",
                    law.explanation[:60] + "..." if len(law.explanation) > 60 else law.explanation,
                )
            console.print(table)

        console.print(f"\n[bold]Recommended Action:[/bold] {analysis.recommended_action}")
        console.print(f"\n[dim]{analysis.disclaimer}[/dim]")

    def _show_help(self):
        """Show help message."""
        help_text = """
[bold]Available Commands:[/bold]
  help, h     - Show this help
  quit, q     - Exit the program

[bold]Example Queries:[/bold]
  • "Can my employer fire me without notice?"
  • "Is caste discrimination punishable in Nepal?"
  • "Can police arrest me without a warrant?"
  • "What are my rights if I'm detained?"
  • "Can I start a business without registration?"
  • "Is dowry legal in Nepal?"
  • "What are the laws on child marriage?"
        """
        console.print(Panel(help_text, border_style="green"))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Legal Classifier")
    parser.add_argument("--query", type=str, help="Legal scenario to classify")
    parser.add_argument("--country", choices=["nepal", "india"], default="nepal")
    parser.add_argument("--language", choices=["en", "ne", "hi"], default="en")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM, use similarity only")
    parser.add_argument("--top-k", type=int, default=10, help="Number of articles to retrieve")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    classifier = LegalClassifier(use_llm=not args.no_llm)

    if args.interactive:
        classifier.interactive_mode(country=args.country, language=args.language)
    elif args.query:
        analysis = classifier.classify(args.query, country=args.country, language=args.language, top_k=args.top_k)
        classifier._display_analysis(analysis)
    else:
        parser.print_help()


if __name__ == "__main__":
    import hashlib
    main()