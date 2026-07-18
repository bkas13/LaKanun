"""Configuration management for Nepal Legal AI."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent
    )
    data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data")
    raw_data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "raw")
    processed_data_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "processed")
    embeddings_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "embeddings")
    corpus_file: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "corpus.json")
    documents_file: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "documents.json")

    # Embedding model
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384
    chunk_size: int = 512
    chunk_overlap: int = 50

    # Vector store
    chroma_persist_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "embeddings" / "chroma")
    collection_prefix: str = "law"

    # LLM (optional)
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    llm_model: str = "claude-3-haiku-20240307"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048

    # Scraper
    scraper_rate_limit: float = 2.0  # requests per second
    scraper_timeout: int = 30
    scraper_max_retries: int = 3
    scraper_user_agents: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    ]

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    api_keys: List[str] = []  # Optional API keys for authentication

    # Supported countries and languages
    supported_countries: List[str] = ["nepal", "india"]
    supported_languages: List[str] = ["en", "ne", "hi"]

    # Legal domains
    legal_domains: List[str] = [
        "fundamental_rights",
        "criminal",
        "civil",
        "labor",
        "family",
        "property",
        "constitutional",
        "administrative",
        "tax",
        "commercial",
    ]

    # Classification categories
    classification_categories: List[str] = [
        "legal",
        "illegal",
        "illegal_with_conditions",
        "partially_legal",
        "requires_permits",
        "gray_area",
        "jurisdiction_specific",
    ]

    # Stance types
    stance_types: List[str] = [
        "violates",
        "supports",
        "conditional",
        "related",
        "neutral",
    ]

    # Severity levels
    severity_levels: List[str] = ["low", "medium", "high", "critical"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Country-specific source URLs
NEPAL_SOURCES = {
    "constitution": [
        "https://www.npc.gov.np/en/category/constitution/",
        "https://www.lawcommission.gov.np/en/constitution/",
    ],
    "legislation": [
        "https://www.lawcommission.gov.np/en/acts/",
        "https://www.molj.gov.np/",
    ],
    "case_law": [
        "https://www.supremecourt.gov.np/",
        "https://decisions.supremecourt.gov.np/",
    ],
    "regulations": [
        "https://www.nrb.org.np/",
        "https://www.ird.gov.np/",
    ],
}

INDIA_SOURCES = {
    "constitution": [
        "https://www.indiacode.nic.in/",
        "https://legislative.gov.in/constitution-of-india",
    ],
    "legislation": [
        "https://www.indiacode.nic.in/",
        "https://legislative.gov.in/acts",
    ],
    "case_law": [
        "https://judgments.ecourts.gov.in/",
        "https://main.sci.gov.in/",
    ],
    "regulations": [
        "https://www.rbi.org.in/",
        "https://www.sebi.gov.in/",
    ],
}

# Nepal Constitution article mapping (Fundamental Rights - Articles 16-51)
NEPAL_CONSTITUTION_FUNDAMENTAL_RIGHTS = {
    16: "Right to Live with Dignity",
    17: "Right to Freedom",
    18: "Right to Equality",
    19: "Right to Communication",
    20: "Right to Justice",
    21: "Right of Victim of Crime",
    22: "Right against Torture",
    23: "Right against Preventive Detention",
    24: "Right against Untouchability and Discrimination",
    25: "Right relating to Property",
    26: "Right to Religious Freedom",
    27: "Right to Information",
    28: "Right to Privacy",
    29: "Right against Exploitation",
    30: "Right to Clean Environment",
    31: "Right relating to Education",
    32: "Right to Language and Culture",
    33: "Right to Employment",
    34: "Right to Labour",
    35: "Right relating to Health",
    36: "Right relating to Food",
    37: "Right to Housing",
    38: "Rights of Women",
    39: "Rights of Children",
    40: "Rights of Dalits",
    41: "Rights of Senior Citizens",
    42: "Rights of Social Justice",
    43: "Right to Social Security",
    44: "Rights of Consumers",
    45: "Rights against Exile",
    46: "Right to Constitutional Remedies",
    47: "Rights of Citizens Living Abroad",
    48: "Right to Participate in State Structure",
    49: "Right to Live in Healthy Environment",
    50: "Rights regarding Nature Conservation",
    51: "Right to State Policy",
}

# Indian Constitution key articles
INDIA_CONSTITUTION_KEY_ARTICLES = {
    14: "Equality before law",
    15: "Prohibition of discrimination",
    16: "Equality of opportunity",
    17: "Abolition of Untouchability",
    19: "Protection of certain rights regarding freedom of speech",
    20: "Protection in respect of conviction for offences",
    21: "Protection of life and personal liberty",
    21A: "Right to education",
    22: "Protection against arrest and detention",
    23: "Prohibition of traffic in human beings and forced labour",
    24: "Prohibition of employment of children in factories",
    25: "Freedom of conscience and religion",
    32: "Remedies for enforcement of rights",
    39: "Directive Principles of State Policy",
    39A: "Equal justice and free legal aid",
    41: "Right to work, to education and to public assistance",
    42: "Provision for just and humane conditions of work",
    44: "Uniform civil code",
    50: "Separation of judiciary from executive",
}

# Legal aid contacts
LEGAL_AID_NEPAL = [
    {"name": "Nepal Bar Association", "phone": "01-4221231", "email": "nba@nepalbar.org.np"},
    {"name": "Legal Aid Commission", "phone": "01-4256007", "email": "info@lac.gov.np"},
    {"name": "INSEC (Human Rights)", "phone": "01-4269167", "email": "insec@insec.org.np"},
    {"name": "FWLD (Forum for Women, Law and Development)", "phone": "01-4228074", "email": "fwld@fwld.org"},
]

LEGAL_AID_INDIA = [
    {"name": "NALSA (National Legal Services Authority)", "phone": "011-23389308", "email": "nalsa-dla@nic.in"},
    {"name": "Supreme Court Legal Services Committee", "phone": "011-23389309", "email": "sclsc@nic.in"},
    {"name": "Delhi Legal Services Authority", "phone": "011-23389310", "email": "dlsa@nic.in"},
]