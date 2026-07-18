"""Issue-to-Law Finder — maps real-world scenarios to relevant legal provisions.

Given a natural language description of a legal issue, finds all applicable
provisions across Nepal and India laws and structures them into a brief.
"""

from typing import Optional
from backend.services.law import law_service


# ── Scenario Patterns ───────────────────────────────────────────────────
# Maps common issue descriptions to legal topic clusters

ISSUE_PATTERNS: list[dict] = [
    {
        "id": "arrested",
        "keywords": ["arrested", "arrest", "police", "custody", "detained", "detention", "picked up", "taken in"],
        "search_queries": ["arrest detention police custody", "right against arrest", "bail custody"],
        "categories": ["arrest_and_bail", "criminal_procedure_general"],
        "title": {
            "en": "Arrest & Police Custody",
            "ne": "गिरफ्तारी र प्रहरी हिरासत",
            "hi": "गिरफ्तारी और पुलिस हिरासत"
        }
    },
    {
        "id": "domestic_violence",
        "keywords": ["domestic", "violence", "wife", "husband", "abuse", "beating", "harassment", "stridhan", "dowry"],
        "search_queries": ["domestic violence spouse abuse", "protection order wife", "harassment"],
        "categories": ["domestic_violence_general"],
        "title": {
            "en": "Domestic Violence & Family Abuse",
            "ne": "घरेलु हिंसा र पारिवारिक दुर्व्यवहार",
            "hi": "घरेलू हिंसा और पारिवारिक दुर्व्यवहार"
        }
    },
    {
        "id": "property_dispute",
        "keywords": ["property", "land", "house", "building", "encroachment", "eviction", "tenant", "rent", "lease", "partition", "ancestral"],
        "search_queries": ["property rights land ownership", "tenant eviction lease", "partition ancestral property"],
        "categories": ["property_law", "transfer_of_property_general"],
        "title": {
            "en": "Property & Land Disputes",
            "ne": "सम्पत्ति र जमिन विवाद",
            "hi": "सम्पत्ति और भूमि विवाद"
        }
    },
    {
        "id": "workplace",
        "keywords": ["work", "job", "employer", "fired", "terminated", "wages", "salary", "injury", "accident", "worker", "employee", "labor", "labour"],
        "search_queries": ["employment wages termination", "workplace injury compensation", "worker rights labor"],
        "categories": ["labor_general", "wages_and_payment", "occupational_safety"],
        "title": {
            "en": "Employment & Workplace Issues",
            "ne": "रोजगार र कार्यस्थल समस्या",
            "hi": "रोजगार और कार्यस्थल समस्याएं"
        }
    },
    {
        "id": "consumer",
        "keywords": ["consumer", "product", "defective", "refund", "shop", "bought", "purchase", "service", "complaint", "warranty"],
        "search_queries": ["consumer protection defective product", "refund warranty complaint"],
        "categories": ["consumer_protection_general", "consumer_complaints"],
        "title": {
            "en": "Consumer Complaints",
            "ne": "उपभोक्ता शिकायत",
            "hi": "उपभोक्ता शिकायत"
        }
    },
    {
        "id": "inheritance",
        "keywords": ["inheritance", "succession", "will", "heir", "estate", "father", "mother", "died", "death", "property after death"],
        "search_queries": ["inheritance succession property", "will testament heirs"],
        "categories": ["inheritance_and_succession"],
        "title": {
            "en": "Inheritance & Succession",
            "ne": "उत्तराधिकार",
            "hi": "विरासत और उत्तराधिकार"
        }
    },
    {
        "id": "child",
        "keywords": ["child", "minor", "kidnapping", "abduction", "custody", "adoption", "abuse", "child labor", "school"],
        "search_queries": ["child protection minor rights", "custody guardianship adoption", "child labor exploitation"],
        "categories": ["child_protection", "juvenile_justice_general"],
        "title": {
            "en": "Child Protection & Welfare",
            "ne": "बाल सुरक्षा र कल्याण",
            "hi": "बाल सुरक्षा और कल्याण"
        }
    },
    {
        "id": "marriage_divorce",
        "keywords": ["marriage", "divorce", "wedding", "spouse", "alimony", "maintenance", "matrimonial", "bigamy"],
        "search_queries": ["marriage divorce spousal rights", "alimony maintenance", "matrimonial dispute"],
        "categories": ["marriage_and_family"],
        "title": {
            "en": "Marriage & Divorce",
            "ne": "विवाह र तलाक",
            "hi": "विवाह और तलाक"
        }
    },
    {
        "id": "cyber_fraud",
        "keywords": ["online", "cyber", "hack", "phishing", "fraud", "scam", "internet", "digital", "email", "password", "stolen online"],
        "search_queries": ["cyber crime online fraud", "digital evidence", "hacking data theft"],
        "categories": ["cyber_crime", "information_technology_general", "computer_offences"],
        "title": {
            "en": "Online Fraud & Cybercrime",
            "ne": "अनलाइन धोखाधडी र साइबर अपराध",
            "hi": "ऑनलाइन धोखाधडी और साइबर अपराध"
        }
    },
    {
        "id": "cheque_bounce",
        "keywords": ["cheque", "check", "bounce", "bounced", "dishonor", "insufficient", "bank"],
        "search_queries": ["cheque bounce dishonor", "negotiable instruments cheque"],
        "categories": ["cheque_bounce", "negotiable_instruments_general"],
        "title": {
            "en": "Cheque Bounce / Dishonored Payment",
            "ne": "चेक डिसऑनर / भुक्तानी अस्वीकृत",
            "hi": "चेक बाउंस / अस्वीकृत भुगतान"
        }
    },
    {
        "id": "accident",
        "keywords": ["accident", "crash", "collision", "motor", "vehicle", "car", "bike", "injury", "insurance", "claim"],
        "search_queries": ["motor vehicle accident", "accident compensation claim", "insurance claim"],
        "categories": ["accidents", "accident_claims", "motor_vehicles_general"],
        "title": {
            "en": "Motor Vehicle Accidents & Insurance",
            "ne": "सवारी साधन दुर्घटना र बीमा",
            "hi": "मोटर वाहन दुर्घटना और बीमा"
        }
    },
    {
        "id": "bail",
        "keywords": ["bail", "bond", "release", "surety", "custody", "jail", "prison", "released"],
        "search_queries": ["bail application procedure", "surety bond release"],
        "categories": ["arrest_and_bail"],
        "title": {
            "en": "Bail & Release from Custody",
            "ne": "जमानत र हिरासतबाट रिहाइ",
            "hi": "जमानत और हिरासत से रिहाई"
        }
    },
    {
        "id": "right_to_info",
        "keywords": ["information", "rti", "freedom of information", "government record", "transparency", "public authority"],
        "search_queries": ["right to information government", "freedom of information public authority"],
        "categories": ["right_to_information_general", "information_access"],
        "title": {
            "en": "Right to Information",
            "ne": "सूचनाको अधिकार",
            "hi": "सूचना का अधिकार"
        }
    },
]


def identify_issue(description: str) -> Optional[dict]:
    """Identify the legal issue from a natural language description.

    Returns the best matching ISSUE_PATTERN or None.
    """
    desc_lower = description.lower()

    best_match = None
    best_score = 0

    for pattern in ISSUE_PATTERNS:
        score = 0
        for kw in pattern["keywords"]:
            if kw in desc_lower:
                # Longer keyword matches are more specific
                score += len(kw.split())

        if score > best_score:
            best_score = score
            best_match = pattern

    if best_score == 0:
        return None
    return best_match


def find_laws_for_issue(
    description: str,
    country: Optional[str] = None,
    lang: str = "en",
) -> dict:
    """Map a legal issue description to relevant provisions.

    Returns a structured brief with matching laws, provisions, and guidance.
    """
    issue = identify_issue(description)

    if issue is None:
        # Fallback: use the description as a search query
        results = law_service.search(description, country=country, top_k=10)
        return {
            "issue_identified": False,
            "title": description,
            "search_results": [
                {
                    "id": r["article"].get("id", ""),
                    "title": r["article"].get("title", ""),
                    "article_number": r["article"].get("article_number", ""),
                    "country": r["article"].get("country", ""),
                    "category": r["article"].get("category", ""),
                    "document_type": r["article"].get("document_type", ""),
                    "source_document": r["article"].get("source_document", ""),
                    "score": r["score"],
                    "full_text": r["article"].get("full_text", ""),
                    "enactment_year": r["article"].get("_enactment_year", 0),
                }
                for r in results
            ],
            "provisions": [],
            "guidance": {
                "en": "We couldn't identify a specific legal issue, but here are relevant search results.",
                "ne": "हामीले विशिष्ट कानूनी मुद्दा पहिचान गर्न सकेनौं, तर यहाँ सम्बन्धित खोजी परिणामहरू छन्।",
                "hi": "हम एक विशिष्ट कानूनी मुद्दे की पहचान नहीं कर सके, लेकिन यहां प्रासंगिक खोज परिणाम हैं।"
            }.get(lang, "We couldn't identify a specific legal issue, but here are relevant search results.")
        }

    # Execute searches from the pattern
    all_results = []
    seen_ids = set()

    for query in issue["search_queries"]:
        results = law_service.search(query, country=country, top_k=8)
        for r in results:
            aid = r["article"].get("id", "")
            if aid not in seen_ids:
                seen_ids.add(aid)
                all_results.append({
                    "id": aid,
                    "title": r["article"].get("title", ""),
                    "article_number": r["article"].get("article_number", ""),
                    "country": r["article"].get("country", ""),
                    "category": r["article"].get("category", ""),
                    "document_type": r["article"].get("document_type", ""),
                    "source_document": r["article"].get("source_document", ""),
                    "score": r["score"],
                    "full_text": r["article"].get("full_text", ""),
                    "enactment_year": r["article"].get("_enactment_year", 0),
                })

    # Sort by score
    all_results.sort(key=lambda x: x["score"], reverse=True)

    # Generate guidance based on issue type
    guidance = _get_guidance(issue["id"], lang)

    return {
        "issue_identified": True,
        "issue_id": issue["id"],
        "title": issue["title"].get(lang, issue["title"]["en"]),
        "search_results": all_results[:15],
        "provisions": _extract_key_provisions(all_results, country),
        "guidance": guidance,
    }


def _extract_key_provisions(results: list, country: Optional[str] = None) -> list:
    """Extract the most important provisions from search results, grouped by country."""
    nepal = []
    india = []

    for r in results[:10]:
        entry = {
            "id": r["id"],
            "title": r["title"],
            "article_number": r["article_number"],
            "source_document": r["source_document"],
        }
        if r["country"] == "nepal":
            nepal.append(entry)
        elif r["country"] == "india":
            india.append(entry)

    provisions = []
    if nepal:
        provisions.append({"country": "nepal", "articles": nepal[:5]})
    if india:
        provisions.append({"country": "india", "articles": india[:5]})

    return provisions


def _get_guidance(issue_id: str, lang: str = "en") -> str:
    """Get issue-specific guidance text."""
    guidance_map = {
        "arrested": {
            "en": "If you or someone you know has been arrested: (1) The police must inform you of the reason within 1 hour. (2) You must be produced before a magistrate within 24 hours. (3) You have the right to consult a lawyer before any questioning. (4) Do not sign any document without reading it. (5) Contact a legal aid organization if you cannot afford a lawyer.",
            "ne": "तपाईं वा तपाईंलाई थाहा भएको कोही गिरफ्तार भएमा: (१) प्रहरीले १ घण्टाभित्र कारण बताउनुपर्छ। (२) २४ घण्टाभित्र न्यायाधीशसामु प्रस्तुत गर्नुपर्छ। (३) पूछताछ अघि वकीलसँग भेट्ने अधिकार छ। (४) कुनै पनि कागजात बिना पढेको हस्ताक्षर नगर्नुहोस्। (५) वकील भाडा गर्न नसकेमा कानूनी सहायता संस्थासँग सम्पर्क गर्नुहोस्।",
            "hi": "यदि आप या आपका कोई जानने वाला गिरफ्तार हुआ है: (1) पुलिस को 1 घंटे के भीतर कारण बताना होगा। (2) 24 घंटे के भीतर मजिस्ट्रेट के सामने पेश करना होगा। (3) पूछताछ से पहले वकील से मिलने का अधिकार है। (4) बिना पढ़े कोई दस्तावेज पर हस्ताक्षर न करें। (5) वकील का खर्च उठाने में असमर्थ होने पर कानूनी सहायता संगठन से संपर्क करें।",
        },
        "domestic_violence": {
            "en": "For domestic violence: (1) Call the police helpline immediately. (2) You can get a protection order within 48 hours. (3) You have the right to stay in the shared household. (4) Document all injuries with photos and medical records. (5) Contact a women's rights organization for support.",
            "ne": "घरेलु हिंसाका लागि: (१) तुरुन्तै प्रहरी हेल्पलाइनमा फोन गर्नुहोस्। (२) ४८ घण्टाभित्र सुरक्षा आदेश पाउन सक्नुहुन्छ। (३) साझा घरमा बस्ने अधिकार छ। (४) सबै चोटपटकको फोटो र मेडिकल रेकर्ड राख्नुहोस्। (५) सहयोगका लागि महिला अधिकार संस्थासँग सम्पर्क गर्नुहोस्।",
            "hi": "घरेलू हिंसा के लिए: (1) तुरंत पुलिस हेल्पलाइन पर कॉल करें। (2) 48 घंटे के भीतर सुरक्षा आदेश मिल सकता है। (3) साझा घर में रहने का अधिकार है। (4) सभी चोटों की फोटो और मेडिकल रिकॉर्ड रखें। (5) सहायता के लिए महिला अधिकार संगठन से संपर्क करें।",
        },
        "property_dispute": {
            "en": "For property disputes: (1) Gather all ownership documents (deed, tax receipts, survey records). (2) File a case in the appropriate district court. (3) For ancestral property, all legal heirs have equal rights. (4) Mediation is often faster and cheaper than litigation. (5) A lawyer can help determine the correct legal procedure.",
            "ne": "सम्पत्ति विवादका लागि: (१) सबै स्वामित्व कागजात जम्मा गर्नुहोस् (बैनापत्त्र, कर रसीद, सर्वेक्षण)। (२) उपयुक्त जिल्ला अदालतमा मुद्दा दर्ता गर्नुहोस्। (३) पुस्तैनी सम्पत्तिमा सबै वैध उत्तराधिकारीको समान अधिकार छ। (४) मध्यस्थता प्रायः मुद्दा भन्दा छिटो र सस्तो हुन्छ। (५) वकीलले सही कानूनी प्रक्रिया निर्धारण गर्न मद्दत गर्न सक्छ।",
            "hi": "सम्पत्ति विवाद के लिए: (1) सभी स्वामित्व दस्तावेज इकट्ठा करें (विलेख, कर रसीद, सर्वेक्षण)। (2) उचित जिला न्यायालय में मामला दर्ज करें। (3) पैतृक सम्पत्ति में सभी वैध उत्तराधिकारियों को समान अधिकार है। (4) मध्यस्थता अक्सर मुकदमे से तेज और सस्ती है। (5) वकील सही कानूनी प्रक्रिया निर्धारित करने में मदद कर सकता है।",
        },
    }

    default_guidance = {
        "en": "Based on your description, we've found relevant legal provisions. Review the results below and consult a qualified lawyer for advice specific to your situation.",
        "ne": "तपाईंको विवरणको आधारमा, हामीले सम्बन्धित कानूनी उपबन्धहरू फेला पारेका छौं। तलका परिणामहरू समीक्षा गर्नुहोस् र तपाईंको अवस्थाका लागि विशिष्ट सल्लाहका लागि योग्य वकीलसँग परामर्श गर्नुहोस्।",
        "hi": "आपके विवरण के आधार पर, हमने प्रासंगिक कानूनी प्रावधान पाए हैं। नीचे दिए गए परिणामों की समीक्षा करें और अपनी स्थिति के अनुसार विशिष्ट सलाह के लिए एक योग्य वकील से परामर्श करें।",
    }

    return guidance_map.get(issue_id, default_guidance).get(lang, guidance_map.get(issue_id, default_guidance).get("en", ""))
