# Nepal Legal AI - Multilingual Legal Analysis Platform

A comprehensive legal AI platform for Nepal and India providing multilingual legal analysis, document retrieval, and conversational legal assistance.

## Features

- **Multilingual Support**: English, Nepali (नेपाली), Hindi (हिन्दी)
- **Dual Jurisdiction**: Nepal (Constitution 2072, Labor Act 2074, Civil/Penal Codes) & India (Constitution, IPC, CrPC, CPC, Contract Act)
- **RAG-Powered Analysis**: Retrieval-Augmented Generation with ChromaDB vector store
- **Explainable AI**: Structured legal reasoning with article citations and stance classification
- **REST API**: FastAPI with rate limiting, CORS, and optional API key auth
- **Web UI**: Streamlit interface with interactive analysis, search, and legal dictionary
- **Conversational Chatbot**: Multi-turn legal Q&A with context memory
- **Legal Dictionary**: 500+ bilingual legal terms with Devanagari script support

## Architecture

```
nepal_legal_project/
├── src/
│   ├── config.py              # Settings & constants
│   ├── scraper.py             # Async document fetcher
│   ├── parser.py              # PDF/HTML text extraction
│   ├── corpus_builder.py      # Structured corpus builder
│   ├── embeddings.py          # ChromaDB vector store
│   ├── classifier.py          # Legal analysis engine
│   ├── prompts.py             # LLM prompt templates
│   ├── api.py                 # FastAPI REST endpoints
│   ├── legal_dictionary.py    # Bilingual terminology
│   └── chatbot.py             # Conversational RAG
├── data/
│   ├── raw/                   # Downloaded documents
│   ├── processed/             # Parsed chunks
│   ├── embeddings/            # ChromaDB persistence
│   ├── corpus.json            # Structured corpus
│   └── legal_dictionary.json  # Terminology
├── app.py                     # Streamlit web UI
├── tests/
│   └── evaluation.py          # Benchmark framework
└── notebooks/                 # Analysis notebooks
```

## Quick Start

### 1. Installation

```bash
# Clone and navigate
cd nepal_legal_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Optional: Install LLM dependencies for enhanced reasoning
pip install -e ".[llm]"
```

### 2. Configuration

Create `.env` file:
```env
# Optional: LLM API keys for enhanced reasoning
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key

# Optional: API authentication
API_KEYS=your_api_key_1,your_api_key_2
```

### 3. Build the Corpus

```bash
# Ingest Nepal Constitution (308 articles)
python -m data.ingest_constitution

# Scrape legal documents (optional - requires internet)
python -m src.scraper --country nepal --category constitution
python -m src.scraper --country india --category legislation

# Build structured corpus from raw documents
python -m src.corpus_builder

# Index into vector store
python -m src.embeddings --index
```

### 4. Run the API Server

```bash
python -m src.api
# Server runs at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### 5. Run the Web UI

```bash
streamlit run app.py
# Opens at http://localhost:8501
```

### 6. Interactive CLI

```bash
# Legal classification
python -m src.classifier --interactive --country nepal

# Vector search
python -m src.embeddings --query "Can employer fire without notice?" --country nepal

# Chatbot
python -m src.chatbot --country nepal
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Legal scenario classification |
| GET | `/article/{id}` | Retrieve article by ID |
| GET | `/search` | Vector similarity search |
| GET | `/articles` | List articles by country/category |
| GET | `/health` | Health check & stats |
| POST | `/feedback` | Submit user feedback |
| GET | `/dictionary/search` | Legal term translation |

### Example API Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can my employer fire me without notice in Nepal?",
    "country": "nepal",
    "language": "en"
  }'
```

### Example Response

```json
{
  "query_id": "abc123",
  "query": "Can my employer fire me without notice in Nepal?",
  "classification": "illegal",
  "confidence": 0.92,
  "applicable_laws": [
    {
      "id": "nepal_labor_act_2074_sec_114",
      "title": "Section 114 - Notice for termination",
      "text": "An employer shall provide at least thirty days notice...",
      "relevance_score": 0.95,
      "stance": "violates",
      "explanation": "Labor Act 2074 Section 114 mandates 30-day written notice..."
    }
  ],
  "reasoning": "Under Labor Act 2074, Section 114 requires 30-day notice...",
  "legal_domains": ["labor_law"],
  "jurisdiction": "nepal",
  "severity": "high",
  "recommended_action": "File complaint with Labor Office within 45 days"
}
```

## Legal Coverage

### Nepal
- Constitution of Nepal 2072 (308 articles, 35 parts, 9 schedules)
- National Civil Code 2074 (Muluki Dewani Samhita)
- National Penal Code 2074 (Muluki Faujdari Samhita)
- Labor Act 2074
- Local Government Operation Act 2074
- Supreme Court precedents

### India
- Constitution of India (448 articles)
- Indian Penal Code (511 sections)
- Code of Criminal Procedure (484 sections)
- Code of Civil Procedure (158 sections)
- Indian Contract Act (266 sections)
- Minimum Wages Act (31 sections)
- Supreme Court & High Court precedents

## Classification Categories

| Category | Description |
|----------|-------------|
| `legal` | Clearly permitted by law |
| `illegal` | Clearly prohibited by law |
| `illegal_with_conditions` | Prohibited with specific exceptions |
| `partially_legal` | Some aspects legal, others not |
| `requires_permits` | Legal only with authorization |
| `gray_area` | Legal ambiguity, no clear precedent |
| `jurisdiction_specific` | Depends on federal/provincial/local law |

## Stance Types

| Stance | Meaning |
|--------|---------|
| `violates` | Scenario contravenes this law |
| `supports` | Scenario is supported by this law |
| `conditional` | Law applies conditionally |
| `related` | Law is relevant but not determinative |
| `neutral` | Law mentioned for context |

## Evaluation

```bash
# Run benchmark evaluation
python -m tests.evaluation

# Generates tests/evaluation_report.md with:
# - Accuracy by country & domain
# - Precision@k for article retrieval
# - Confusion matrix
# - Confidence calibration
# - Failure analysis
```

## Project Structure Details

### Core Modules

- **config.py**: Centralized settings via Pydantic, environment variables, legal domain mappings
- **scraper.py**: Async aiohttp scraper with rate limiting, robots.txt respect, resume capability
- **parser.py**: PDF (pdfplumber) & HTML (BeautifulSoup) extraction with language detection
- **corpus_builder.py**: Structures documents into articles with chunks, relationships, metadata
- **embeddings.py**: Multilingual sentence-transformers + ChromaDB with metadata filtering
- **classifier.py**: RAG pipeline with LLM fallback to similarity-only mode
- **prompts.py**: Country-specific few-shot prompt templates (Nepal/India)
- **api.py**: FastAPI with rate limiting, CORS, optional API key auth
- **legal_dictionary.py**: 500+ terms with English/Nepali/Hindi + Devanagari
- **chatbot.py**: Conversational RAG with session memory, legal aid resources

### Data Files

- `data/corpus.json`: Structured legal articles with chunks
- `data/nepal_constitution.json`: Full Constitution articles
- `data/india_laws.json`: Key Indian acts
- `data/legal_dictionary.json`: Bilingual terminology
- `data/documents.json`: Scraped document metadata
- `data/embeddings/chroma/`: ChromaDB persistence

## Development

### Code Quality

```bash
# Format
black src/ tests/

# Lint
ruff src/ tests/

# Type check
mypy src/

# Test
pytest tests/ -v --cov=src
```

### Adding New Legal Sources

1. Add source URLs to `config.py` (NEPAL_SOURCES / INDIA_SOURCES)
2. Run scraper: `python -m src.scraper --country nepal --category legislation`
3. Rebuild corpus: `python -m src.corpus_builder`
4. Re-index: `python -m src.embeddings --index`

### Customizing Prompts

Edit `src/prompts.py` to modify:
- Classification prompts with few-shot examples
- Reasoning templates
- Constitutional mapping
- Compliance check formats

## Disclaimer

**This is AI-generated legal analysis, not professional legal advice.** The system provides information based on legal texts but may not reflect the latest amendments, judicial interpretations, or jurisdiction-specific nuances. Always consult a qualified attorney for legal matters.

## Legal Aid Resources

### Nepal
- Nepal Bar Association: 01-4221231
- Legal Aid Commission: 01-4256007
- INSEC (Human Rights): 01-4269167
- FWLD: 01-4228074

### India
- NALSA: 011-23389308
- Supreme Court Legal Services: 011-23389309
- District Legal Services Authorities (all districts)

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure code quality checks pass
5. Submit pull request

## Roadmap

- [ ] Provincial/State law coverage
- [ ] Case law database with citations
- [ ] Fine-tuned Nepali legal embedding model
- [ ] Mobile app with offline mode
- [ ] Integration with court case management systems
- [ ] Automated legislative tracking