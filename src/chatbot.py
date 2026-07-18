"""Conversational Legal Chatbot with RAG for Nepal and India."""

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from src.classifier import LegalClassifier, LegalAnalysis
from src.config import settings, LEGAL_AID_INDIA, LEGAL_AID_NEPAL
from src.embeddings import EmbeddingManager
from src.legal_dictionary import LegalDictionary, get_legal_dictionary

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class ChatMessage:
    """A single chat message."""

    role: str  # user, assistant, system
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ChatSession:
    """A conversation session."""

    session_id: str
    country: str
    language: str
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: Dict = None):
        self.messages.append(ChatMessage(role=role, content=content, metadata=metadata or {}))
        self.updated_at = datetime.utcnow().isoformat()

    def get_history(self, max_turns: int = 10) -> List[ChatMessage]:
        """Get recent conversation history."""
        return self.messages[-max_turns * 2:]  # user + assistant pairs

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "country": self.country,
            "language": self.language,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "context": self.context,
        }


class LegalChatbot:
    """Conversational legal assistant with RAG."""

    def __init__(
        self,
        country: str = "nepal",
        language: str = "en",
        classifier: LegalClassifier = None,
        embedding_manager: EmbeddingManager = None,
        legal_dictionary: LegalDictionary = None,
        use_llm: bool = True,
    ):
        self.country = country.lower()
        self.language = language.lower()
        self.use_llm = use_llm

        self.classifier = classifier or LegalClassifier(use_llm=use_llm)
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.legal_dictionary = legal_dictionary or get_legal_dictionary()

        # Session management
        self.current_session: Optional[ChatSession] = None
        self.sessions_dir = Path(settings.data_dir) / "chat_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Legal aid resources
        self.legal_aid = LEGAL_AID_NEPAL if self.country == "nepal" else LEGAL_AID_INDIA

        # Disclaimer
        self.disclaimer = (
            "⚠️ This is AI-generated legal information, not professional legal advice. "
            "Consult a qualified attorney for legal matters."
        )

    def start_session(self, session_id: str = None) -> ChatSession:
        """Start a new chat session."""
        session_id = session_id or str(uuid.uuid4())[:8]
        self.current_session = ChatSession(
            session_id=session_id,
            country=self.country,
            language=self.language,
        )

        # Add system message
        system_msg = self._get_system_message()
        self.current_session.add_message("system", system_msg)

        logger.info(f"Started chat session {session_id} for {self.country}/{self.language}")
        return self.current_session

    def _get_system_message(self) -> str:
        """Get system message for the chat."""
        country_name = "Nepal" if self.country == "nepal" else "India"
        lang_name = {"en": "English", "ne": "नेपाली", "hi": "हिन्दी"}.get(self.language, "English")

        return (
            f"You are a legal assistant for {country_name} law. "
            f"Respond in {lang_name}. "
            f"Always ground answers in specific legal provisions. "
            f"If uncertain, say 'I cannot find a specific law covering this.' "
            f"Include the disclaimer: {self.disclaimer}"
        )

    def chat(self, user_input: str) -> str:
        """Process user input and generate response."""
        if not self.current_session:
            self.start_session()

        # Add user message
        self.current_session.add_message("user", user_input)

        # Check for special commands
        if user_input.lower().strip() in ("/help", "help"):
            return self._show_help()
        elif user_input.lower().strip() in ("/legal_aid", "legal aid"):
            return self._show_legal_aid()
        elif user_input.lower().strip() in ("/translate", "translate"):
            return self._handle_translation_request(user_input)
        elif user_input.lower().strip().startswith("/article "):
            return self._handle_article_lookup(user_input)

        # Determine query type
        query_type = self._classify_query_type(user_input)

        if query_type == "greeting":
            response = self._handle_greeting()
        elif query_type == "legal_question":
            response = self._handle_legal_question(user_input)
        elif query_type == "article_explanation":
            response = self._handle_article_explanation(user_input)
        elif query_type == "procedure":
            response = self._handle_procedure_question(user_input)
        elif query_type == "remedy":
            response = self._handle_remedy_question(user_input)
        else:
            response = self._handle_general_query(user_input)

        # Add assistant response
        self.current_session.add_message("assistant", response)

        return response

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of user query."""
        query_lower = query.lower()

        # Greeting patterns
        greetings = ["hello", "hi", "namaste", "नमस्ते", "नमस्कार", "hi there", "hey"]
        if any(g in query_lower for g in greetings) and len(query) < 50:
            return "greeting"

        # Article lookup
        if any(kw in query_lower for kw in ["article", "अनुच्छेद", "धारा", "section"]):
            if any(char.isdigit() for char in query):
                return "article_explanation"

        # Procedure questions
        procedure_keywords = [
            "how to", "process", "procedure", "file", "register", "apply",
            "कसरी", "प्रक्रिया", "दर्ता", "फाइल", "आवेदन",
            "कैसे", "प्रक्रिया", "दर्ज", "आवेदन"
        ]
        if any(kw in query_lower for kw in procedure_keywords):
            return "procedure"

        # Remedy questions
        remedy_keywords = [
            "remedy", "what can i do", "solution", "help", "rights",
            "उपचार", "के गर्ने", "अधिकार", "मद्दत",
            "उपाय", "क्या करूं", "अधिकार", "मदद"
        ]
        if any(kw in query_lower for kw in remedy_keywords):
            return "remedy"

        # General legal question
        legal_keywords = [
            "legal", "law", "illegal", "punishable", "right", "court",
            "कानूनी", "कानून", "अपराध", "अदालत", "अधिकार",
            "कानूनी", "कानून", "अपराध", "अदालत", "अधिकार"
        ]
        if any(kw in query_lower for kw in legal_keywords):
            return "legal_question"

        return "general"

    def _handle_greeting(self) -> str:
        """Handle greeting messages."""
        greetings = {
            "en": "Hello! I'm your legal assistant for Nepal/India law. How can I help you today?",
            "ne": "नमस्ते! म नेपाल/भारतको कानूनी सहायक हूँ। आज तपाईंलाई कसरी मद्दत गर्न सक्छु?",
            "hi": "नमस्ते! मैं नेपाल/भारत के कानून के लिए आपका कानूनी सहायक हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?"
        }
        return greetings.get(self.language, greetings["en"]) + f"\n\n{self.disclaimer}"

    def _handle_legal_question(self, query: str) -> str:
        """Handle general legal questions using the classifier."""
        try:
            analysis = self.classifier.classify(
                query=query,
                country=self.country,
                language=self.language,
            )

            return self._format_analysis_response(analysis)
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return self._fallback_response(query)

    def _handle_article_explanation(self, query: str) -> str:
        """Explain a specific article/section."""
        # Extract article number
        import re
        numbers = re.findall(r'\d+', query)
        if not numbers:
            return "Please specify an article or section number."

        article_num = numbers[0]
        article_id = f"{self.country}_constitution_art_{article_num}"

        # Try to get from vector store
        article = self.embedding_manager.get_article(article_id)

        if article:
            meta = article["metadata"]
            text = article["text"]

            response = f"**Article {article_num} - {meta.get('title', '')}**\n\n"
            response += f"*Source: {meta.get('source', '')}*\n\n"
            response += text[:2000]
            if len(text) > 2000:
                response += "\n\n... (text truncated)"
        else:
            # Search for it
            results = self.embedding_manager.search(
                query=f"Article {article_num}",
                country=self.country,
                top_k=3,
            )

            if results:
                response = f"**Search results for Article {article_num}:**\n\n"
                for i, r in enumerate(results, 1):
                    meta = r.metadata
                    response += f"{i}. **{meta.get('title', 'Unknown')}** ({meta.get('article_number', '')})\n"
                    response += f"   Relevance: {r.score:.1%}\n"
                    response += f"   {r.text[:300]}...\n\n"
            else:
                response = f"I cannot find Article {article_num} in the {self.country} legal database."

        return response + f"\n\n{self.disclaimer}"

    def _handle_procedure_question(self, query: str) -> str:
        """Handle procedural questions."""
        # Search for relevant procedures
        results = self.embedding_manager.search(
            query=query,
            country=self.country,
            category="civil",  # Procedures often in civil/admin law
            top_k=5,
        )

        if not results:
            return self._fallback_response(query)

        response = "**Procedure Information:**\n\n"
        for i, r in enumerate(results[:3], 1):
            meta = r.metadata
            response += f"{i}. **{meta.get('title', 'Unknown')}** ({meta.get('article_number', '')})\n"
            response += f"   {r.text[:500]}...\n\n"

        response += self._get_legal_aid_suggestion()
        return response + f"\n\n{self.disclaimer}"

    def _handle_remedy_question(self, query: str) -> str:
        """Handle remedy/solution questions."""
        # First classify to understand the legal issue
        analysis = self.classifier.classify(
            query=query,
            country=self.country,
            language=self.language,
        )

        if not analysis.applicable_laws:
            return self._fallback_response(query)

        response = "**Legal Remedies Available:**\n\n"

        for law in analysis.applicable_laws:
            if law.stance in ("violates", "conditional"):
                response += f"📋 **Based on {law.title}:**\n"
                response += f"   {law.explanation}\n\n"

        response += "**Recommended Steps:**\n"
        response += analysis.recommended_action + "\n\n"
        response += self._get_legal_aid_suggestion()

        return response + f"\n\n{self.disclaimer}"

    def _handle_general_query(self, query: str) -> str:
        """Handle general queries with search."""
        results = self.embedding_manager.search(
            query=query,
            country=self.country,
            top_k=5,
        )

        if not results:
            return (
                "I couldn't find specific legal information for your query. "
                "Could you rephrase or provide more details?\n\n"
                f"{self.disclaimer}"
            )

        response = "**Relevant Legal Information:**\n\n"
        for i, r in enumerate(results[:3], 1):
            meta = r.metadata
            response += f"{i}. **{meta.get('title', 'Unknown')}** ({meta.get('article_number', '')})\n"
            response += f"   Relevance: {r.score:.1%}\n"
            response += f"   {r.text[:400]}...\n\n"

        return response + f"\n\n{self.disclaimer}"

    def _fallback_response(self, query: str) -> str:
        """Fallback when no specific answer found."""
        responses = {
            "en": "I cannot find a specific law covering this exact scenario. "
                  "This may be a gray area or require professional legal interpretation. "
                  "I recommend consulting a qualified attorney.",
            "ne": "म यो विशेष परिस्थितिलाई कवर गर्ने विशेष कानुन फेला पार्न सकेन। "
                  "यो ग्रे क्षेत्र हो वा पेशेवर कानूनी व्याख्याको आवश्यकता पर्न सक्छ। "
                  "म योग्य वकीलसँग परामर्श गर्न सुझाउँछु।",
            "hi": "मैं इस सटीक परिदृश्य को कवर करने वाला कोई विशिष्ट कानून नहीं ढूंढ सका। "
                  "यह एक ग्रे क्षेत्र हो सकता है या पेशेवर कानूनी व्याख्या की आवश्यकता हो सकती है। "
                  "मैं एक योग्य वकील से परामर्श करने की सलाह देता हूँ।"
        }
        return responses.get(self.language, responses["en"]) + f"\n\n{self.disclaimer}"

    def _format_analysis_response(self, analysis: LegalAnalysis) -> str:
        """Format classification analysis as chat response."""
        # Classification with emoji
        class_emoji = {
            "legal": "✅",
            "illegal": "❌",
            "illegal_with_conditions": "⚠️",
            "partially_legal": "⚖️",
            "requires_permits": "📋",
            "gray_area": "🤔",
            "jurisdiction_specific": "🏛️",
        }.get(analysis.classification, "❓")

        class_label = analysis.classification.replace("_", " ").title()

        response = f"{class_emoji} **Classification: {class_label}** ({analysis.confidence:.0%} confidence)\n\n"

        # Severity
        sev_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(analysis.severity, "")
        response += f"{sev_emoji} **Severity:** {analysis.severity.title()}\n"

        if analysis.legal_domains:
            response += f"📚 **Domains:** {', '.join(analysis.legal_domains)}\n"

        response += "\n"

        # Key applicable laws
        if analysis.applicable_laws:
            response += "**Key Applicable Laws:**\n"
            for i, law in enumerate(analysis.applicable_laws[:3], 1):
                stance_emoji = {
                    "violates": "🔴",
                    "supports": "🟢",
                    "conditional": "🟡",
                    "related": "🔵",
                }.get(law.stance, "⚪")
                response += f"{i}. {stance_emoji} **{law.title}** ({law.article_number})\n"
                response += f"   {law.explanation[:200]}...\n\n"

        # Reasoning
        response += f"**Reasoning:**\n{analysis.reasoning}\n\n"

        # Recommended action
        response += f"**Recommended Action:**\n{analysis.recommended_action}\n\n"

        # Legal aid
        response += self._get_legal_aid_suggestion()

        return response + f"\n\n{self.disclaimer}"

    def _get_legal_aid_suggestion(self) -> str:
        """Get legal aid contact suggestion."""
        aid = self.legal_aid[0] if self.legal_aid else None
        if not aid:
            return ""

        return (
            f"**🆘 Free Legal Aid:** "
            f"{aid['name']} - {aid['phone']} ({aid.get('email', '')})"
        )

    def _show_help(self) -> str:
        """Show help message."""
        help_text = {
            "en": """
**Available Commands:**
- `/help` - Show this help
- `/legal_aid` - Show free legal aid contacts
- `/translate <term>` - Translate legal term
- `/article <number>` - Look up specific article

**Example Questions:**
- "Can my employer fire me without notice?"
- "Is caste discrimination punishable?"
- "What are my rights if police arrest me?"
- "How do I file a case in court?"
- "Explain Article 18 of Nepal Constitution"
            """,
            "ne": """
**उपलब्ध आदेशहरू:**
- `/help` - यो सहायता देखाउँछ
- `/legal_aid` - निःशुल्क कानूनी सहायता सम्पर्क
- `/translate <शब्द>` - कानूनी शब्द अनुवाद
- `/article <नम्बर>` - विशेष अनुच्छेद खोज्नुहोस्

**उदाहरण प्रश्नहरू:**
- "के मेरो नियोक्ता मलाई बिना नोटिस निकाला गर्न सक्छ?"
- "जातीय विभेद दण्डनीय छ?"
- "पुलिस मलाई गिरफ्तार गर्दा मेरो अधिकार के हुन्?"
- "अदालतमा मुद्दा कसरी दर्ता गर्ने?"
- "नेपाल संविधानको अनुच्छेद १८ व्याख्या गर्नुहोस्"
            """,
            "hi": """
**उपलब्ध कमांड:**
- `/help` - यह सहायता दिखाएं
- `/legal_aid` - मुफ्त कानूनी सहायता संपर्क
- `/translate <शब्द>` - कानूनी शब्द अनुवाद
- `/article <नंबर>` - विशिष्ट अनुच्छेद खोजें

**उदाहरण प्रश्न:**
- "क्या मेरा नियोक्ता मुझे बिना नोटिस के निकाल सकता है?"
- "क्या जाति भेदभाव दंडनीय है?"
- "अगर पुलिस मुझे गिरफ्तार करे तो मेरे अधिकार क्या हैं?"
- "अदालत में मामला कैसे दर्ज करें?"
- "नेपाल संविधान के अनुच्छेद 18 की व्याख्या करें"
            """
        }
        return help_text.get(self.language, help_text["en"])

    def _show_legal_aid(self) -> str:
        """Show legal aid contacts."""
        response = "**Free Legal Aid Resources:**\n\n"

        for aid in self.legal_aid:
            response += f"📞 **{aid['name']}**\n"
            response += f"   Phone: {aid['phone']}\n"
            if aid.get('email'):
                response += f"   Email: {aid['email']}\n"
            response += "\n"

        if self.country == "nepal":
            response += "**District Legal Aid Committees** available in all 77 districts.\n"
        else:
            response += "**District Legal Services Authorities (DLSA)** available in all districts.\n"

        return response

    def _handle_translation_request(self, query: str) -> str:
        """Handle translation requests."""
        # Extract term after /translate
        term = query.split(" ", 1)[1] if " " in query else ""
        if not term:
            return "Usage: `/translate <legal term>`"

        result = self.legal_dictionary.search(term, self.language)
        if result and result.get("results"):
            r = result["results"][0]
            lang_name = {"ne": "नेपाली", "hi": "हिन्दी"}.get(self.language, "Target")
            return f"**{r.get('english', term)}** → **{r.get(self.language, 'Not found')}** ({lang_name})"
        return f"Translation not found for '{term}'"

    def _handle_article_lookup(self, query: str) -> str:
        """Handle /article command."""
        import re
        numbers = re.findall(r'\d+', query)
        if not numbers:
            return "Usage: `/article <number>`"

        article_num = numbers[0]
        return self._handle_article_explanation(f"Article {article_num}")

    def save_session(self, filepath: Path = None) -> Path:
        """Save current session to file."""
        if not self.current_session:
            raise ValueError("No active session")

        if filepath is None:
            filepath = self.sessions_dir / f"session_{self.current_session.session_id}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.current_session.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Session saved to {filepath}")
        return filepath

    def load_session(self, filepath: Path) -> ChatSession:
        """Load session from file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        session = ChatSession(
            session_id=data["session_id"],
            country=data["country"],
            language=data["language"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            context=data.get("context", {}),
        )

        for msg_data in data["messages"]:
            session.messages.append(ChatMessage(**msg_data))

        self.current_session = session
        return session

    def list_sessions(self) -> List[Path]:
        """List saved sessions."""
        return sorted(self.sessions_dir.glob("session_*.json"))

    def interactive_mode(self):
        """Run interactive CLI chat."""
        self.start_session()

        console.print(Panel.fit(
            f"[bold]Nepal Legal AI Chatbot[/bold]\n"
            f"Country: {self.country.upper()} | Language: {self.language}\n"
            f"Type '/help' for commands, 'quit' to exit",
            border_style="blue",
        ))

        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

                if user_input.lower().strip() in ("quit", "exit", "q", "bye"):
                    console.print("[yellow]Goodbye! Stay legally informed.[/yellow]")
                    break

                if not user_input.strip():
                    continue

                response = self.chat(user_input)

                console.print(Panel(
                    Markdown(response),
                    title="[bold green]Assistant[/bold green]",
                    border_style="green",
                ))

            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.exception("Chat error")

        # Auto-save session
        if self.current_session and len(self.current_session.messages) > 1:
            self.save_session()


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Legal Chatbot for Nepal/India")
    parser.add_argument("--country", choices=["nepal", "india"], default="nepal")
    parser.add_argument("--language", choices=["en", "ne", "hi"], default="en")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM, use similarity only")
    parser.add_argument("--session", type=str, help="Load existing session file")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    chatbot = LegalChatbot(
        country=args.country,
        language=args.language,
        use_llm=not args.no_llm,
    )

    if args.session:
        chatbot.load_session(Path(args.session))
        console.print(f"[green]Loaded session: {args.session}[/green]")
    else:
        chatbot.start_session()

    chatbot.interactive_mode()


if __name__ == "__main__":
    main()