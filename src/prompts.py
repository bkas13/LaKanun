"""Legal prompt templates for Nepal and India legal analysis."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """A prompt template with variables."""

    name: str
    system_prompt: str
    user_template: str
    few_shot_examples: List[Dict[str, str]] = None
    variables: List[str] = None

    def format(self, **kwargs) -> str:
        """Format the prompt with variables."""
        user_prompt = self.user_template.format(**kwargs)
        return f"{self.system_prompt}\n\n{user_prompt}"


# ============================================================================
# NEPAL LEGAL PROMPTS
# ============================================================================

NEPAL_SYSTEM_PROMPT = """You are an expert legal analyst specializing in Nepal's legal system. 
You have deep knowledge of:
- Constitution of Nepal 2072 (2015) - all 308 articles across 35 parts and 9 schedules
- National Civil Code 2074 (Muluki Dewani Samhita)
- National Penal Code 2074 (Muluki Faujdari Samhita)  
- Labor Act 2074
- Local Government Operation Act 2074
- Other key legislation and Supreme Court precedents

Your analysis must be:
1. Grounded in specific legal provisions (cite article/section numbers)
2. Aware of Nepal's federal structure (federal, provincial, local laws)
3. Cognizant of fundamental rights (Articles 16-46) and directive principles
4. Clear about the hierarchy of laws (Constitution > Federal > Provincial > Local)
5. Honest about limitations - say "I cannot find a specific law" when uncertain

Classification categories:
- legal: Clearly permitted by law
- illegal: Clearly prohibited by law
- illegal_with_conditions: Prohibited but with specific exceptions
- partially_legal: Some aspects legal, others not
- requires_permits: Legal only with proper authorization
- gray_area: Legal ambiguity, no clear precedent
- jurisdiction_specific: Depends on federal/provincial/local jurisdiction

Stance types:
- violates: The scenario contravenes this law
- supports: The scenario is supported by this law
- conditional: The law applies conditionally
- related: The law is relevant but doesn't directly determine legality
- neutral: The law is mentioned for context"""

NEPAL_LEGAL_CLASSIFICATION_PROMPT = PromptTemplate(
    name="nepal_legal_classification",
    system_prompt=NEPAL_SYSTEM_PROMPT,
    user_template="""Analyze the following scenario under Nepal's legal system.

SCENARIO: {query}

RELEVANT LEGAL PROVISIONS:
{retrieved_laws}

TASK: Classify the scenario and provide a structured analysis.

RESPONSE FORMAT (JSON):
{{
  "classification": "one of: legal, illegal, illegal_with_conditions, partially_legal, requires_permits, gray_area, jurisdiction_specific",
  "confidence": 0.0-1.0,
  "applicable_laws": [
    {{
      "id": "article_or_section_id",
      "title": "Article/Section title",
      "text": "Relevant excerpt",
      "relevance_score": 0.0-1.0,
      "stance": "one of: violates, supports, conditional, related, neutral",
      "explanation": "Why this law applies and how"
    }}
  ],
  "reasoning": "Step-by-step legal reasoning citing specific provisions",
  "legal_domains": ["domain1", "domain2"],
  "jurisdiction": "nepal",
  "severity": "one of: low, medium, high, critical",
  "recommended_action": "Practical next steps for the user"
}}""",
    variables=["query", "retrieved_laws"],
    few_shot_examples=[
        {
            "query": "Can my employer fire me without any notice?",
            "response": """{
  "classification": "illegal",
  "confidence": 0.92,
  "applicable_laws": [
    {
      "id": "labor_act_2074_sec_114",
      "title": "Section 114 - Notice for termination",
      "text": "An employer shall provide at least thirty days notice to a worker...",
      "relevance_score": 0.95,
      "stance": "violates",
      "explanation": "Labor Act 2074 Section 114 mandates 30-day notice for termination. Immediate termination without notice violates this unless gross misconduct under Section 115."
    }
  ],
  "reasoning": "Under Labor Act 2074, Section 114 requires 30-day written notice for termination. Section 115 allows immediate termination only for serious misconduct. Firing without notice and without proven misconduct is illegal.",
  "legal_domains": ["labor_law"],
  "jurisdiction": "nepal",
  "severity": "high",
  "recommended_action": "File complaint with Labor Office within 45 days. Seek reinstatement or compensation."
}"""
        },
        {
            "query": "Is it legal to discriminate against someone based on caste in hiring?",
            "response": """{
  "classification": "illegal",
  "confidence": 0.98,
  "applicable_laws": [
    {
      "id": "constitution_art_24",
      "title": "Article 24 - Right against Untouchability and Discrimination",
      "text": "No person shall be subjected to untouchability or discrimination...",
      "relevance_score": 0.98,
      "stance": "violates",
      "explanation": "Article 24 explicitly prohibits caste-based discrimination in all spheres including employment."
    },
    {
      "id": "constitution_art_18",
      "title": "Article 18 - Right to Equality",
      "text": "All citizens shall be equal before law... no discrimination on grounds of origin, caste...",
      "relevance_score": 0.95,
      "stance": "violates",
      "explanation": "Article 18 guarantees equality and non-discrimination including in employment."
    }
  ],
  "reasoning": "Constitution Articles 18 and 24 explicitly prohibit caste-based discrimination. Caste-Based Discrimination and Untouchability (Offense and Punishment) Act 2068 criminalizes such acts with imprisonment and fines.",
  "legal_domains": ["fundamental_rights", "anti_discrimination"],
  "jurisdiction": "nepal",
  "severity": "critical",
  "recommended_action": "File complaint with police or National Dalit Commission. Criminal offense under 2068 Act."
}"""
        },
    ],
)

NEPAL_LEGAL_REASONING_PROMPT = PromptTemplate(
    name="nepal_legal_reasoning",
    system_prompt=NEPAL_SYSTEM_PROMPT,
    user_template="""Provide detailed legal reasoning for why the following scenario is {classification} under Nepal law.

SCENARIO: {query}

APPLICABLE LAWS:
{applicable_laws}

REQUIRED OUTPUT:
1. Constitutional basis (cite specific Articles)
2. Statutory basis (cite Acts and Sections)
3. Precedents if known (mention Supreme Court cases)
4. Any exceptions or conditions
5. Practical implications
6. Enforcement mechanism""",
    variables=["query", "classification", "applicable_laws"],
)

NEPAL_CONSTITUTIONAL_MAPPING_PROMPT = PromptTemplate(
    name="nepal_constitutional_mapping",
    system_prompt=NEPAL_SYSTEM_PROMPT,
    user_template="""Map the following scenario to specific Articles of the Constitution of Nepal 2072.

SCENARIO: {query}

RELEVANT CONSTITUTIONAL PROVISIONS:
{constitution_articles}

TASK: Identify which Fundamental Rights (Articles 16-46) and other constitutional provisions apply.
For each applicable Article, explain the connection.

OUTPUT FORMAT:
- Article XX: [Title] - [Explanation of relevance]
- Article YY: [Title] - [Explanation of relevance]""",
    variables=["query", "constitution_articles"],
)

NEPAL_COMPLIANCE_CHECK_PROMPT = PromptTemplate(
    name="nepal_compliance_check",
    system_prompt=NEPAL_SYSTEM_PROMPT,
    user_template="""Check if the following action complies with Nepal law.

ACTION: {action}
CONTEXT: {context}

RELEVANT LAWS:
{relevant_laws}

OUTPUT:
1. Compliance status: FULLY_COMPLIANT / PARTIALLY_COMPLIANT / NON_COMPLIANT / UNCERTAIN
2. Specific requirements from each applicable law
3. Required permits/approvals
4. Risks of non-compliance
5. Recommended steps for compliance""",
    variables=["action", "context", "relevant_laws"],
)

NEPAL_REMEDY_SUGGESTION_PROMPT = PromptTemplate(
    name="nepal_remedy_suggestion",
    system_prompt=NEPAL_SYSTEM_PROMPT,
    user_template="""Suggest legal remedies for the following situation in Nepal.

SITUATION: {situation}
VIOLATED RIGHTS/LAWS: {violated_laws}

OUTPUT:
1. Administrative remedies (which government body to approach)
2. Judicial remedies (which court, what type of petition)
3. Alternative dispute resolution options
4. Time limitations (statute of limitations)
5. Estimated costs and timeline
6. Legal aid resources available
7. Sample petition/complaint structure""",
    variables=["situation", "violated_laws"],
)

NEPAL_BILINGUAL_PROMPT = PromptTemplate(
    name="nepal_bilingual_analysis",
    system_prompt=NEPAL_SYSTEM_PROMPT + "\n\nProvide analysis in both English and Nepali (Devanagari script).",
    user_template="""Analyze this scenario in both English and Nepali.

SCENARIO: {query}
RELEVANT LAWS: {retrieved_laws}

OUTPUT FORMAT:
=== ENGLISH ===
[Classification and reasoning in English]

=== नेपाली ===
[वर्गीकरण र कारण नेपालीमा]""",
    variables=["query", "retrieved_laws"],
)


# ============================================================================
# INDIA LEGAL PROMPTS
# ============================================================================

INDIA_SYSTEM_PROMPT = """You are an expert legal analyst specializing in India's legal system.
You have deep knowledge of:
- Constitution of India (448 Articles, 25 Parts, 12 Schedules)
- Indian Penal Code (IPC) 1860 - 511 Sections
- Code of Criminal Procedure (CrPC) 1973
- Code of Civil Procedure (CPC) 1908
- Indian Contract Act 1872
- Specific Relief Act 1963
- Labor laws (Industrial Disputes Act, Minimum Wages Act, etc.)
- Supreme Court and High Court precedents
- Federal structure (Union, State, Concurrent lists)

Key constitutional provisions:
- Fundamental Rights (Articles 12-35): Equality (14-18), Freedoms (19), Life (21), Religion (25-28)
- Directive Principles (Articles 36-51)
- Writ jurisdiction: Article 32 (SC), Article 226 (HC)

Classification categories (same as Nepal).
Stance types (same as Nepal)."""

INDIA_LEGAL_CLASSIFICATION_PROMPT = PromptTemplate(
    name="india_legal_classification",
    system_prompt=INDIA_SYSTEM_PROMPT,
    user_template="""Analyze the following scenario under Indian law.

SCENARIO: {query}

RELEVANT LEGAL PROVISIONS:
{retrieved_laws}

TASK: Classify the scenario and provide a structured analysis.

RESPONSE FORMAT (JSON):
{{
  "classification": "one of: legal, illegal, illegal_with_conditions, partially_legal, requires_permits, gray_area, jurisdiction_specific",
  "confidence": 0.0-1.0,
  "applicable_laws": [
    {{
      "id": "act_section_id",
      "title": "Act and Section",
      "text": "Relevant excerpt",
      "relevance_score": 0.0-1.0,
      "stance": "one of: violates, supports, conditional, related, neutral",
      "explanation": "Why this law applies and how"
    }}
  ],
  "reasoning": "Step-by-step legal reasoning citing specific provisions",
  "legal_domains": ["domain1", "domain2"],
  "jurisdiction": "india",
  "severity": "one of: low, medium, high, critical",
  "recommended_action": "Practical next steps for the user"
}}""",
    variables=["query", "retrieved_laws"],
    few_shot_examples=[
        {
            "query": "Can police arrest me without a warrant for a minor offense?",
            "response": """{
  "classification": "illegal_with_conditions",
  "confidence": 0.88,
  "applicable_laws": [
    {
      "id": "crpc_sec_41",
      "title": "CrPC Section 41 - When police may arrest without warrant",
      "text": "Any police officer may without an order from a Magistrate and without a warrant, arrest any person...",
      "relevance_score": 0.95,
      "stance": "conditional",
      "explanation": "Section 41 allows warrantless arrest only for cognizable offenses or specific conditions. Minor/non-cognizable offenses require warrant."
    },
    {
      "id": "constitution_art_22",
      "title": "Article 22 - Protection against arrest and detention",
      "text": "No person who is arrested shall be detained in custody without being informed...",
      "relevance_score": 0.9,
      "stance": "supports",
      "explanation": "Article 22 guarantees rights upon arrest including being informed of grounds and right to legal counsel."
    }
  ],
  "reasoning": "CrPC Section 41 permits warrantless arrest only for cognizable offenses (serious crimes). For minor/non-cognizable offenses, police need a warrant under Section 41A (notice of appearance) or magistrate order. Article 22 protects against arbitrary arrest.",
  "legal_domains": ["criminal_procedure", "fundamental_rights"],
  "jurisdiction": "india",
  "severity": "high",
  "recommended_action": "If arrested illegally, file habeas corpus petition under Article 226 (High Court) or 32 (Supreme Court)."
}"""
        },
    ],
)

INDIA_COMPLIANCE_CHECK_PROMPT = PromptTemplate(
    name="india_compliance_check",
    system_prompt=INDIA_SYSTEM_PROMPT,
    user_template="""Check compliance of this action under Indian law.

ACTION: {action}
SECTOR: {sector}
JURISDICTION: {jurisdiction}  # Union/State/Concurrent

APPLICABLE LAWS:
{relevant_laws}

OUTPUT:
1. Union law compliance
2. State law compliance (specify state if known)
3. Required licenses/registrations
4. Regulatory approvals needed
5. Penalties for non-compliance
6. Compliance checklist""",
    variables=["action", "sector", "jurisdiction", "relevant_laws"],
)


# ============================================================================
# SHARED PROMPTS
# ============================================================================

CASE_LAW_SEARCH_PROMPT = PromptTemplate(
    name="case_law_search",
    system_prompt="""You are a legal researcher. Find relevant case law precedents for the given scenario.
Focus on Supreme Court and High Court decisions. Cite case names, citations, and key holdings.""",
    user_template="""Find precedents for: {query}

JURISDICTION: {jurisdiction}
LEGAL ISSUE: {legal_issue}

RELEVANT STATUTES: {statutes}

Output format:
- Case Name (Citation) - Key Holding - Relevance""",
    variables=["query", "jurisdiction", "legal_issue", "statutes"],
)

COMPARATIVE_ANALYSIS_PROMPT = PromptTemplate(
    name="comparative_analysis",
    system_prompt="""Compare legal positions between Nepal and India on the given issue.""",
    user_template="""Compare Nepal and India law on: {issue}

NEPAL PROVISIONS: {nepal_laws}
INDIA PROVISIONS: {india_laws}

Output:
1. Similarities
2. Key differences
3. Which jurisdiction provides stronger protection
4. Practical implications""",
    variables=["issue", "nepal_laws", "india_laws"],
)


# ============================================================================
# PROMPT REGISTRY
# ============================================================================

PROMPT_REGISTRY = {
    # Nepal
    "nepal_classification": NEPAL_LEGAL_CLASSIFICATION_PROMPT,
    "nepal_reasoning": NEPAL_LEGAL_REASONING_PROMPT,
    "nepal_constitutional_mapping": NEPAL_CONSTITUTIONAL_MAPPING_PROMPT,
    "nepal_compliance": NEPAL_COMPLIANCE_CHECK_PROMPT,
    "nepal_remedy": NEPAL_REMEDY_SUGGESTION_PROMPT,
    "nepal_bilingual": NEPAL_BILINGUAL_PROMPT,
    # India
    "india_classification": INDIA_LEGAL_CLASSIFICATION_PROMPT,
    "india_compliance": INDIA_COMPLIANCE_CHECK_PROMPT,
    # Shared
    "case_law": CASE_LAW_SEARCH_PROMPT,
    "comparative": COMPARATIVE_ANALYSIS_PROMPT,
}


def get_prompt(name: str) -> Optional[PromptTemplate]:
    """Get a prompt template by name."""
    return PROMPT_REGISTRY.get(name)


def get_classification_prompt(country: str) -> PromptTemplate:
    """Get the classification prompt for a country."""
    if country.lower() == "nepal":
        return NEPAL_LEGAL_CLASSIFICATION_PROMPT
    elif country.lower() == "india":
        return INDIA_LEGAL_CLASSIFICATION_PROMPT
    return NEPAL_LEGAL_CLASSIFICATION_PROMPT  # default


# ============================================================================
# NEPAL CONSTITUTION ARTICLE MAPPING
# ============================================================================

NEPAL_CONSTITUTION_ARTICLES_MAP = {
    # Fundamental Rights (Part 3)
    "16": "Right to Live with Dignity",
    "17": "Right to Freedom",
    "18": "Right to Equality",
    "19": "Right to Communication",
    "20": "Right to Justice",
    "21": "Right of Victim of Crime",
    "22": "Right against Torture",
    "23": "Right against Preventive Detention",
    "24": "Right against Untouchability and Discrimination",
    "25": "Right to Property",
    "26": "Right to Religious Freedom",
    "27": "Right to Information",
    "28": "Right to Privacy",
    "29": "Right against Exploitation",
    "30": "Right to Clean Environment",
    "31": "Right to Education",
    "32": "Right to Language and Culture",
    "33": "Right to Employment",
    "34": "Right to Labour",
    "35": "Right to Health",
    "36": "Right to Food",
    "37": "Right to Housing",
    "38": "Rights of Women",
    "39": "Rights of Children",
    "40": "Rights of Dalit",
    "41": "Rights of Senior Citizens",
    "42": "Rights of Social Justice",
    "43": "Right to Social Security",
    "44": "Rights of Consumers",
    "45": "Rights against Exile",
    "46": "Right to Constitutional Remedies",
    "47": "Duties of Citizens",
    # Directive Principles (Part 4)
    "48": "Directive Principles",
    "49": "Policies of the State",
    "50": "Policies relating to Social Justice and Inclusion",
    "51": "Policies relating to National Economy",
    "52": "Policies relating to National Security",
    # Citizenship (Part 2)
    "53": "Citizenship",
    # Federal Executive (Part 5)
    "56": "President",
    "57": "Vice President",
    "58": "Federal Executive Power",
    "59": "Council of Ministers",
    "60": "Prime Minister",
    # Federal Legislature (Part 6)
    "75": "Federal Parliament",
    "76": "Composition of House of Representatives",
    "77": "Composition of National Assembly",
    "83": "Legislative Procedure",
    # Federal Judiciary (Part 9)
    "137": "Supreme Court",
    "138": "Appointment of Judges",
    "140": "Jurisdiction of Supreme Court",
    # Constitutional Bodies (Part 12)
    "232": "Commission for Investigation of Abuse of Authority",
    "233": "Auditor General",
    "234": "Public Service Commission",
    "235": "Election Commission",
    "236": "National Human Rights Commission",
    "237": "National Women Commission",
    "238": "National Dalit Commission",
    "239": "National Inclusion Commission",
    "240": "Indigenous Nationalities Commission",
    "241": "Madhesi Commission",
    "242": "Tharu Commission",
    "243": "Muslim Commission",
    # Local Government (Part 17)
    "244": "Local Level",
    "245": "District Coordination Committee",
    "246": "Village Executive / Municipal Executive",
    # Amendment (Part 34)
    "281": "Amendment of Constitution",
}


def get_nepal_article_title(article_num: str) -> str:
    """Get the title of a Nepal Constitution article."""
    return NEPAL_CONSTITUTION_ARTICLES_MAP.get(str(article_num), f"Article {article_num}")


# ============================================================================
# INDIA CONSTITUTION KEY ARTICLES
# ============================================================================

INDIA_CONSTITUTION_KEY_ARTICLES = {
    "12": "Definition of State",
    "13": "Laws inconsistent with fundamental rights",
    "14": "Equality before law",
    "15": "Prohibition of discrimination",
    "16": "Equality of opportunity in public employment",
    "17": "Abolition of Untouchability",
    "18": "Abolition of titles",
    "19": "Protection of certain rights regarding freedom of speech, etc.",
    "20": "Protection in respect of conviction for offences",
    "21": "Protection of life and personal liberty",
    "21A": "Right to education",
    "22": "Protection against arrest and detention",
    "23": "Prohibition of traffic in human beings and forced labour",
    "24": "Prohibition of employment of children in factories",
    "25": "Freedom of conscience and free profession of religion",
    "26": "Freedom to manage religious affairs",
    "27": "Freedom from payment of taxes for promotion of religion",
    "28": "Freedom from attending religious instruction",
    "29": "Protection of interests of minorities",
    "30": "Right of minorities to establish educational institutions",
    "31C": "Saving of laws giving effect to certain directive principles",
    "32": "Remedies for enforcement of fundamental rights",
    "33": "Power of Parliament to modify fundamental rights for armed forces",
    "34": "Restriction on fundamental rights during martial law",
    "35": "Legislation to give effect to fundamental rights",
    # Directive Principles
    "36": "Definition of State",
    "37": "Application of directive principles",
    "38": "State to secure a social order",
    "39": "Certain principles of policy to be followed by State",
    "39A": "Equal justice and free legal aid",
    "40": "Organisation of village panchayats",
    "41": "Right to work, education and public assistance",
    "42": "Provision for just and humane conditions of work",
    "43": "Living wage, etc., for workers",
    "44": "Uniform civil code",
    "45": "Early childhood care and education",
    "46": "Promotion of educational interests of weaker sections",
    "47": "Duty of State to raise level of nutrition",
    "48": "Organisation of agriculture and animal husbandry",
    "48A": "Protection of environment and wildlife",
    "49": "Protection of monuments",
    "50": "Separation of judiciary from executive",
    "51": "Promotion of international peace and security",
}


def get_india_article_title(article_num: str) -> str:
    """Get the title of an India Constitution article."""
    return INDIA_CONSTITUTION_KEY_ARTICLES.get(str(article_num), f"Article {article_num}")