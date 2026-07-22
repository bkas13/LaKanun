"""Issue-to-Law Finder — maps real-world scenarios to relevant legal provisions.

Given a natural language description of a legal issue, finds all applicable
provisions across Nepal and India laws and structures them into a brief.

Enhanced with:
- Romanized/vernacular keyword matching (Nepali/Hindi transliterations)
- Multilingual query translation before matching
- Intent phrase matching for natural language descriptions
"""

from typing import Optional, List, Tuple
from backend.services.law import law_service
from backend.services.multilingual_search import translate_query, ROMANIZED_MAP, DEVANAGARI_TO_ENGLISH


# ── Scenario Patterns ───────────────────────────────────────────────────
# Maps common issue descriptions to legal topic clusters.
# Each pattern now includes:
#   - keywords: English keywords (original)
#   - vernacular: romanized Nepali/Hindi phrases that describe the same issue
#   - intent_phrases: natural language descriptions users might type
#   - search_queries: optimized English search queries for law retrieval

ISSUE_PATTERNS: list[dict] = [
    {
        "id": "arrested",
        "keywords": ["arrested", "arrest", "police", "custody", "detained", "detention", "picked up", "taken in"],
        "keywords_dev": ["गिरफ्तारी", "पुलिस", "थाना", "कैद", "हिरासत", "प्रहरी", "पक्राउ", "पक्रे", "जमानत"],
        "vernacular": ["girftari", "giraftari", "qaid", "police le pakro", "police le lagyo", "thana", "hirasat"],
        "intent_phrases": ["police took me", "police picked up", "someone arrested", "in custody", "taken to thana", "police holding"],
        "search_queries": ["arrest detention police custody", "right against arrest", "bail custody", "arrest procedure rights"],
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
        "keywords_dev": ["हिंसा", "मारपीट", "पत्नी", "श्रीमती", "पति", "श्रीमान", "दहेज", "गाली", "धम्की", "घरेलु", "कुटपिट"],
        "vernacular": ["gharelu hinsa", "biwile maar", "patile maar", "dahej", "tikun", "jhidak", "gali", "marpit"],
        "intent_phrases": ["husband beats me", "wife is being abused", "in-laws harassing", "dowry harassment", "physical abuse at home", "family violence"],
        "search_queries": ["domestic violence spouse abuse", "protection order wife", "harassment domestic", "dowry prohibition"],
        "categories": ["domestic_violence_general"],
        "title": {
            "en": "Domestic Violence & Family Abuse",
            "ne": "घरेलु हिंसा र पारिवारिक दुर्व्यवहार",
            "hi": "घरेलू हिंसा और पारिवारिक दुर्व्यवहार"
        }
    },
    {
        "id": "property_dispute",
        "keywords": ["property", "land", "house", "building", "encroachment", "partition", "ancestral", "zamin", "jagga"],
        "keywords_dev": ["सम्पत्ति", "सम्पत्तिमा", "सम्पत्तिको", "जग्गा", "जमिन", "घर", "झगडा", "विवाद", "पुस्तैनी", "जग्गाजमिन", "घरघडेरी"],
        "vernacular": ["jagga ko mamla", "ghar ko mamla", "zamin ko vivad", "bhitra chhutyeko", "jagga chiniyo", "kabja", "chhincha"],
        "intent_phrases": ["someone took my land", "property dispute", "encroached on my property", "ancestral property division", "house ownership dispute", "land grabbing"],
        "search_queries": ["property rights land ownership", "partition ancestral property", "encroachment property dispute", "land title ownership"],
        "categories": ["property_law", "transfer_of_property_general"],
        "title": {
            "en": "Property & Land Disputes",
            "ne": "सम्पत्ति र जमिन विवाद",
            "hi": "सम्पत्ति और भूमि विवाद"
        }
    },
    {
        "id": "workplace",
        "keywords": ["work", "job", "employer", "fired", "terminated", "wages", "salary", "injury", "worker", "employee", "labor", "labour"],
        "vernacular": ["nokri", "jyala", "majdur", "kaam", "lagadhari", "jagire", "naukri chhodyo", "tankhwah", "pesi"],
        "keywords_dev": ["रोजगार", "रोजगारदाता", "नोकरी", "जागिर", "काम", "कर्मचारी", "मजदूर", "श्रम", "तलब", "ज्याला", "हटाउनु", "निकाल्नु", "निकाल्यो", "बर्खास्त", "सूचना बिना", "अधिकार", "श्रम कानून", "उल्लंघन"],
        "intent_phrases": ["employer fired me", "not paying wages", "salary not given", "workplace injury", "lost my job", "employer exploiting", "no salary increment"],
        "search_queries": ["employment wages termination", "workplace injury compensation", "worker rights labor", "wrongful termination"],
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
        "keywords_dev": ["उपभोक्ता", "सामान", "दोषपूर्ण", "रेफन्ड", "फिर्ता", "पैसा फिर्ता", "बिल", "ग्यारेन्टी", "वारेन्टी", "पसल", "किनेको", "बेचेको", "मिसावट", "म्याद गुज्रिएको", "धोका", "ठगी"],
        "vernacular": ["kharid", "defective product", "paisa firta", "warranty", "complaint", "samaan bigriyo"],
        "intent_phrases": ["bought defective product", "shop not giving refund", "product not working", "consumer complaint", "service not provided", "warranty claim denied"],
        "search_queries": ["consumer protection defective product", "refund warranty complaint", "consumer rights defect"],
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
        "keywords_dev": ["उत्तराधिकार", "उत्तराधिकारी", "विरासत", "पुस्तैनी", "वसियतनामा", "हक", "हकदार", "वारिस", "अंश", "अंशबन्डा", "बाँडफाँड", "बुबा", "पिता", "आमा", "मृत्यु", "गुम्नुभयो", "मृतक", "भाइबहिनी", "सम्पत्ति"],
        "vernacular": ["virasat", "uttradhikar", "baap ko sampatti", "mritak ko sampatti", "warisan", "will"],
        "intent_phrases": ["father died property", "inheritance after death", "who gets the property", "succession rights", "will and testament", "legal heir property"],
        "search_queries": ["inheritance succession property", "will testament heirs", "intestate succession", "legal heir rights"],
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
        "keywords_dev": ["बाल", "बच्चा", "नाबालिग", "बालबालिका", "बाल श्रम", "स्कुल", "विद्यालय", "अपहरण", "हराएको", "बाल संरक्षण", "अभिभावक", "सन्तान", "हेरचाह"],
        "vernacular": ["bachcha", "bal", "apaharan", "harayeko bachcha", "bachcha ko haq", "paalana"],
        "intent_phrases": ["child custody", "kidnapped child", "child labor", "minor rights", "child abuse", "adoption process", "child not going to school"],
        "search_queries": ["child protection minor rights", "custody guardianship adoption", "child labor exploitation", "juvenile justice"],
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
        "keywords_dev": ["विवाह", "तलाक", "बिहे", "बैवाहिक", "पति", "पत्नी", "श्रीमान", "श्रीमती", "भरणपोषण", "सम्बन्ध विच्छेद", "बहुविवाह", "जीवनसम्बन्धी"],
        "vernacular": ["byaah", "talaq", "vivah", "alimony", "bivaha bhangai", "kharcha paani", "dampati"],
        "intent_phrases": ["want divorce", "marriage problems", "spouse not maintaining", "alimony rights", "domestic marriage dispute", "second marriage illegal"],
        "search_queries": ["marriage divorce spousal rights", "alimony maintenance", "matrimonial dispute", "divorce procedure"],
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
        "keywords_dev": ["अनलाइन", "इन्टरनेट", "साइबर", "ह्याक", "ठगी", "धोखाधडी", "पासवर्ड", "बैंक खाता", "धम्की", "उत्पीडन", "फोन", "कल", "एसएमएस", "गोपनीयता"],
        "vernacular": ["online thagi", "dhoka", "hack", "phishing", "password chori", "online fraud", "internet fraud"],
        "intent_phrases": ["online fraud happened", "someone hacked my account", "password stolen", "online scam", "digital fraud", "email phishing"],
        "search_queries": ["cyber crime online fraud", "digital evidence", "hacking data theft", "information technology offence"],
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
        "keywords_dev": ["चेक", "बैंक", "बाउन्स", "डिसऑनर", "भुक्तानी", "पैसा", "अस्वीकृत", "रकम", "ब्याज"],
        "vernacular": ["cheque bounce", "check bounce", "cheque dishonor", "paisa chhodyena bank"],
        "intent_phrases": ["cheque bounced", "cheque dishonored", "bank returned cheque", "insufficient funds cheque", "payment by cheque failed"],
        "search_queries": ["cheque bounce dishonor", "negotiable instruments cheque", "cheque dishonour punishment"],
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
        "keywords_dev": ["दुर्घटना", "गाडी", "मोटर", "सवारी", "बाइक", "कार", "चोट", "बीमा", "दाबी", "मुआब्जा", "सवारी साधन", "ट्राफिक"],
        "vernacular": ["durghatana", "bike accident", "gadi ko accident", "insurance claim", "chot", "sawari sadhan"],
        "intent_phrases": ["vehicle accident", "bike crash", "car collision", "accident injury", "insurance claim for accident", "hit and run"],
        "search_queries": ["motor vehicle accident", "accident compensation claim", "insurance claim", "road accident liability"],
        "categories": ["accidents", "accident_claims", "motor_vehicles_general"],
        "title": {
            "en": "Motor Vehicle Accidents & Insurance",
            "ne": "सवारी साधन दुर्घटना र बीमा",
            "hi": "मोटर वाहन दुर्घटना और बीमा"
        }
    },
    {
        "id": "bail",
        "keywords": ["bail", "bond", "release", "surety", "jail", "prison", "released"],
        "keywords_dev": ["जमानत", "जेल", "कैद", "रिहा", "रिहाइ", "हिरासत", "छुट्टी", "थाना", "अदालत", "धरौटी", "मुद्दा"],
        "vernacular": ["jamanat", "chhutti", "riha", "jail bata", "bond", "surety"],
        "intent_phrases": ["need bail", "someone in jail", "bail application", "release from custody", "surety bond", "how to get bail"],
        "search_queries": ["bail application procedure", "surety bond release", "bail conditions"],
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
        "keywords_dev": ["सूचना", "सूचनाको अधिकार", "जानकारी", "सरकारी", "सार्वजनिक", "अधिकार", "निवेदन", "उत्तर", "फाइल"],
        "vernacular": ["jankari", "jaankaari", "rti", "sarkari jaankari", "adhikar", "soochana"],
        "intent_phrases": ["right to information", "government not giving info", "file RTI", "access government records", "transparency in government"],
        "search_queries": ["right to information government", "freedom of information public authority", "RTI application"],
        "categories": ["right_to_information_general", "information_access"],
        "title": {
            "en": "Right to Information",
            "ne": "सूचनाको अधिकार",
            "hi": "सूचना का अधिकार"
        }
    },
    {
        "id": "police_harassment",
        "keywords": ["police harass", "police bribe", "bribe demand", "police extortion", "cop bribe", "police misbehave", "police misconduct", "illegal detention", "fake case", "police torture"],
        "keywords_dev": ["प्रहरी", "पुलिस", "घुस", "सताउने", "धम्की", "गाली", "मारपिट", "कुटपिट", "गिरफ्तारी", "हिरासत", "कारबाही", "उत्पीडन", "झूटो मुद्दा"],
        "vernacular": ["police bribe", "ghoos", "police satayo", "police ne maar", "jhojho case", "illegal pakad", "police prahar"],
        "intent_phrases": ["police asking for bribe", "police harassing me", "police beating in custody", "fake case filed by police", "police demanding money", "illegal police detention"],
        "search_queries": ["police misconduct harassment", "bribery extortion", "police complaint", "police accountability"],
        "categories": ["police_misconduct", "human_rights_violations"],
        "title": {
            "en": "Police Harassment or Bribery",
            "ne": "प्रहरी सताउने वा घुस माग्ने",
            "hi": "पुलिस उत्पीड़न या रिश्वत"
        }
    },
    {
        "id": "tenant_issues",
        "keywords": ["tenant", "landlord", "evict", "eviction", "deposit", "security deposit", "rent increase", "rental agreement", "lease agreement", "evict me", "kick out"],
        "keywords_dev": ["भाडा", "भाडाटिका", "किराया", "कोठा", "घर", "पसल", "निकासी", "निकाल्यो", "निकाल्द्यो", "धरौटी", "जग्गा", "सम्झौता", "लिखत", "ठेक्का", "भाडा बढ्यो"],
        "vernacular": ["kiraya", "bhadatitika", "landlord le nikalyo", "ghar khaali gar", "jagir bata nikalyo", "deposit ferra", "kiraaya badhyo", "chimeki le ghar bata nikaldyo", "nikaldyo"],
        "intent_phrases": ["landlord evicting me", " kicked me out", "eviction from house", "security deposit not returned", "rent increased suddenly", "rental agreement dispute", "neighbor kicked me out", "someone threw me out of house", "ghar bata nikaldyo", "forced to leave house"],
        "search_queries": ["tenant rights eviction", "security deposit landlord", "rental agreement rights", "eviction procedure tenant"],
        "categories": ["tenant_rights", "landlord_tenant"],
        "title": {
            "en": "Tenant Rights & Eviction",
            "ne": "भाडाटिका अधिकार र निकासी",
            "hi": "किरायेदार अधिकार और बेदखली"
        }
    },
    {
        "id": "traffic_stop",
        "keywords": ["traffic", "traffic police", "traffic fine", "challan", "license", "driving", "drunk driving", "speed", "traffic violation", "vehicle seized", "vehicle impound"],
        "keywords_dev": ["ट्राफिक", "सवारी", "जरिवाना", "चालान", "लाइसेन्स", "गाडी", "रोक्यो", "मादक पदार्थ", "मापसे", "दुर्घटना", "नियम", "उल्लंघन"],
        "vernacular": ["traffic", "challan", "license", "drunk driving", "fine", "gaadi pakdyo", "traffic le rokyo", "speed ma"],
        "intent_phrases": ["traffic police stopped me", "got a traffic challan", "license suspended", "vehicle seized by police", "drunk driving charge", "traffic fine too high"],
        "search_queries": ["traffic violation rights", "traffic police stop", "driving licence", "traffic fine challenge"],
        "categories": ["traffic_offences", "motor_vehicles_general"],
        "title": {
            "en": "Traffic Stop & Violations",
            "ne": "ट्राफिक रोक र उल्लंघन",
            "hi": "ट्रैफिक रोक और उल्लंघन"
        }
    },
    {
        "id": "medical_negligence",
        "keywords": ["doctor", "hospital", "medical", "negligence", "wrong treatment", "surgery", "medical error", "overcharge", "hospital bill", "emergency treatment", "medical records"],
        "keywords_dev": ["डाक्टर", "अस्पताल", "चिकित्सा", "लापरवाही", "उपचार", "औषधि", "बिरामी", "शल्यक्रिया", "स्वास्थ्य", "बीमा", "गलत उपचार", "जाँच"],
        "vernacular": ["doctor galat ilaj", "hospital bill", "medical negligence", "overcharge hospital", "surgery gayat", "treatment galat"],
        "intent_phrases": ["doctor gave wrong treatment", "hospital overcharging", "medical negligence", "surgery went wrong", "hospital not giving records", "medical malpractice"],
        "search_queries": ["medical negligence malpractice", "hospital overcharge", "doctor wrong treatment", "medical consumer complaint"],
        "categories": ["medical_negligence", "consumer_protection_general"],
        "title": {
            "en": "Medical Negligence",
            "ne": "चिकित्सा लापरवाही",
            "hi": "चिकित्सा लापरवाही"
        }
    },
    {
        "id": "neighbor_dispute",
        "keywords": ["neighbor", "neighbour", "noise", "boundary", "encroachment", "fence", "wall", "tree", "drainage", "nuisance", "disturbance", "loud music"],
        "keywords_dev": ["छिमेकी", "छिमेकी विवाद", "सीमा", "पर्खाल", "जग्गा", "घर", "रुख", "हल्ला", "गन्ध", "फोहोर", "पानी", "नाली", "गाली", "झैझगडा"],
        "vernacular": ["chimeki", "chhimeki", "chimiki", "naakaa", "ghar ko bhmitti", "pako ko jagga", "boundary dispute", "ghar bata hataayo"],
        "intent_phrases": ["neighbor dispute", "neighbor encroaching boundary", "neighbor making noise", "neighbor built on my land", "boundary wall dispute", "chimeki le ghar bata nikaldyo", "neighbor threw me out"],
        "search_queries": ["neighbor dispute boundary", "noise nuisance", "property encroachment neighbor", "boundary dispute resolution"],
        "categories": ["neighbor_disputes", "property_law"],
        "title": {
            "en": "Neighbor Disputes",
            "ne": "छिमेकी विवाद",
            "hi": "पड़ोसी विवाद"
        }
    },
    {
        "id": "government_service",
        "keywords": ["government service", "government office", "bribe", "rti", "delay", "application pending", "file pending", "government delay", "public service", "grievance"],
        "keywords_dev": ["सरकार", "सरकारी", "सार्वजनिक", "निवेदन", "फाइल", "ढिलाइ", "अनुमति", "दर्ता", "घुस", "सुझाव", "उजुरी", "गुनासो", "भत्ता", "सुविधा"],
        "vernacular": ["sarkari karyalaya", "sarkari daak", "bribe sarkar", "aavedan pending", "sarkari kaam", "grievance"],
        "intent_phrases": ["government office not responding", "application pending for months", "government service delay", "bribe demanded at government office", "file stuck in government office"],
        "search_queries": ["government service delay", "public service grievance", "right to information government"],
        "categories": ["public_service", "right_to_information_general"],
        "title": {
            "en": "Government Service Issues",
            "ne": "सरकारी सेवा समस्या",
            "hi": "सरकारी सेवा समस्या"
        }
    },
]


def _translate_to_english(description: str) -> Tuple[str, List[str]]:
    """Translate a description to English terms using multilingual search.

    Returns (english_query, all_expanded_terms).
    """
    lang, english_query, all_terms = translate_query(description)
    return english_query, all_terms


def identify_issue(description: str) -> Optional[dict]:
    """Identify the legal issue from a natural language description.

    Enhanced matching:
    1. Direct keyword matching (English)
    2. Vernacular keyword matching (romanized Nepali/Hindi)
    3. Intent phrase matching (natural language)
    4. Multilingual translation + re-matching

    Returns the best matching ISSUE_PATTERN or None.
    """
    desc_lower = description.lower().strip()

    # Step 1: Translate query to English for additional matching
    english_query, translated_terms = _translate_to_english(description)
    english_words = set(english_query.lower().split())
    translated_lower = {t.lower() for t in translated_terms if len(t) >= 3}

    best_match = None
    best_score = 0

    for pattern in ISSUE_PATTERNS:
        score = 0

        # 1. Direct English keyword matching
        for kw in pattern["keywords"]:
            if kw in desc_lower:
                score += len(kw.split()) * 2  # Multi-word keywords score higher

        # 2. Vernacular keyword matching
        for vw in pattern.get("vernacular", []):
            vw_lower = vw.lower()
            if vw_lower in desc_lower:
                score += len(vw_lower.split()) * 3  # Vernacular matches get bonus

        # 3. Intent phrase matching (fuzzy — check if key words from intent phrase appear)
        for phrase in pattern.get("intent_phrases", []):
            phrase_words = [w for w in phrase.lower().split() if len(w) > 3]
            if not phrase_words:
                continue
            matches = sum(1 for pw in phrase_words if pw in desc_lower)
            if matches >= 2:
                score += matches * 2
            # Also check against translated terms
            matches_translated = sum(1 for pw in phrase_words if pw in translated_lower or pw in english_words)
            if matches_translated >= 2:
                score += matches_translated * 1.5

        # 4. Translated term matching — check if translated English words match pattern keywords
        #    Cap: each translated term only counts once per pattern
        translated_used = set()
        for kw in pattern["keywords"]:
            kw_words = kw.split()
            for tw in translated_lower:
                if tw in translated_used:
                    continue
                if any(kw_part in tw or tw in kw_part for kw_part in kw_words if len(kw_part) >= 3):
                    translated_used.add(tw)
                    score += 1.5

        # 5. Devanagari keyword matching — matches direct Devanagari text in the description
        for kw_dev in pattern.get("keywords_dev", []):
            if kw_dev in desc_lower:
                score += len(kw_dev) * 0.4  # Longer Devanagari words = more specific, weighted

        if score > best_score:
            best_score = score
            best_match = pattern

    # Minimum threshold to consider an issue identified
    if best_score < 2:
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
        # Fallback: use the description as a search query with multilingual support
        results = law_service.search(description, country=country, top_k=10)
        return {
            "issue_identified": False,
            "title": description,
            "search_results": _format_results(results),
            "provisions": [],
            "guidance": {
                "en": "We couldn't identify a specific legal issue, but here are relevant search results.",
                "ne": "हामीले विशिष्ट कानूनी मुद्दा पहिचान गर्न सकेनौं, तर यहाँ सम्बन्धित खोजी परिणामहरू छन्।",
                "hi": "हम एक विशिष्ट कानूनी मुद्दे की पहचान नहीं कर सके, लेकिन यहां प्रासंगिक खोज परिणाम हैं।"
            }.get(lang, "We couldn't identify a specific legal issue, but here are relevant search results.")
        }

    # Execute searches from the pattern — also include the original description as a search query
    all_results = []
    seen_ids = set()

    # Add original description as a search query (multilingual support)
    search_queries = list(issue["search_queries"])
    if description.strip() not in search_queries:
        search_queries.insert(0, description.strip())

    for query in search_queries:
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
                    "confidence": r.get("confidence", "low"),
                    "citation": r.get("citation", ""),
                    "full_text": r["article"].get("full_text", ""),
                    "enactment_year": r["article"].get("_enactment_year", 0),
                    "last_verified": r["article"].get("_last_verified", ""),
                    "source_url": r["article"].get("_source_url", ""),
                    "effective_date": r["article"].get("_effective_date", ""),
                })

    # Sort by score, then deduplicate by title similarity
    all_results.sort(key=lambda x: x["score"], reverse=True)
    all_results = _deduplicate_results(all_results)

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


def _format_results(results: list) -> list:
    """Format raw search results into the standard response shape."""
    return [
        {
            "id": r["article"].get("id", ""),
            "title": r["article"].get("title", ""),
            "article_number": r["article"].get("article_number", ""),
            "country": r["article"].get("country", ""),
            "category": r["article"].get("category", ""),
            "document_type": r["article"].get("document_type", ""),
            "source_document": r["article"].get("source_document", ""),
            "score": r["score"],
            "confidence": r.get("confidence", "low"),
            "citation": r.get("citation", ""),
            "full_text": r["article"].get("full_text", ""),
            "enactment_year": r["article"].get("_enactment_year", 0),
            "last_verified": r["article"].get("_last_verified", ""),
            "source_url": r["article"].get("_source_url", ""),
            "effective_date": r["article"].get("_effective_date", ""),
        }
        for r in results
    ]


def _deduplicate_results(results: list) -> list:
    """Remove near-duplicate results based on title similarity."""
    if not results:
        return results

    seen_titles: list[str] = []
    deduped = []

    for r in results:
        title_lower = r["title"].lower().strip()
        is_dup = False
        for seen in seen_titles:
            if _title_similarity(title_lower, seen) > 0.7:
                is_dup = True
                break
        if not is_dup:
            seen_titles.append(title_lower)
            deduped.append(r)

    return deduped


def _title_similarity(a: str, b: str) -> float:
    """Simple word-level Jaccard similarity between two titles."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


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
        "tenant_issues": {
            "en": "For tenant/eviction issues: (1) A landlord cannot evict you without proper legal notice (usually 15-30 days). (2) Your security deposit must be returned within the timeframe specified in your agreement. (3) You have the right to challenge an eviction in court. (4) Keep copies of your rental agreement and all payment receipts. (5) If physically forced out, file a police complaint immediately.",
            "ne": "भाडाटिका/निकासी समस्याका लागि: (१) भाडादाताले उचित कानूनी सूचना बिना निकाल्न सक्दैनन् (सामान्यतया १५-३० दिन)। (२) तपाईंको सुरक्षा जम्मा सम्झौतामा निर्धारित समयसीमाभित्र फिर्ता गर्नुपर्छ। (३) निकासीको विरुद्ध अदालतमा चुनौती दिने अधिकार छ। (४) भाडा सम्झौता र सबै भुक्तानी रसीदहरूको प्रतिलिपि राख्नुहोस्। (५) शारीरिक रूपमा बाहिर गरिएमा, तुरुन्तै प्रहरी शिकायत दर्ता गर्नुहोस्।",
            "hi": "किरायेदार/बेदखली समस्याओं के लिए: (1) मकान मालिक बिना उचित कानूनी नोटिस के आपको नहीं निकाल सकता (आमतौर पर 15-30 दिन)। (2) आपकी सुरक्षा जमा राशि आपके समझौते में निर्धारित समयसीमा के भीतर लौटाई जानी चाहिए। (3) बेदखली को अदालत में चुनौती देने का अधिकार है। (4) अपने किराया समझौते और सभी भुगतान रसीदों की प्रतियां रखें। (5) शारीरिक रूप से बाहर निकाले जाने पर, तुरंत पुलिस शिकायत दर्ज करें।",
        },
        "neighbor_dispute": {
            "en": "For neighbor disputes: (1) Try to resolve the issue through direct, calm communication first. (2) Document any encroachment with photos and measurements. (3) For boundary disputes, request a survey from the local land revenue office. (4) File a complaint with the local municipality if it's a nuisance issue. (5) As a last resort, file a civil suit for injunction.",
            "ne": "छिमेकी विवादका लागि: (१) पहिले प्रत्यक्ष, शान्त संवादमार्फत समस्या समाधान गर्ने प्रयास गर्नुहोस्। (२) कुनै पनि अतिक्रमणको फोटो र मापनसहित प्रमाणित गर्नुहोस्। (३) सीमा विवादका लागि, स्थानीय भूमि राजस्व कार्यालयबाट सर्वेक्षण अनुरोध गर्नुहोस्। (४) निकृष्ट कार्य भएमा, स्थानीय नगरपालिकामा शिकायत दर्ता गर्नुहोस्। (५) अन्तिम उपायको रूपमा, निषेधाज्ञाको लागि दीवानी मुद्दा दर्ता गर्नुहोस्।",
            "hi": "पड़ोसी विवादों के लिए: (1) पहले सीधे, शांत संवाद के माध्यम से समस्या को सुलझाने की कोशिश करें। (2) किसी भी अतिक्रमण की फोटो और मापन के साथ दस्तावेजीकरण करें। (3) सीमा विवाद के लिए, स्थानीय भूमि राजस्व कार्यालय से सर्वेक्षण का अनुरोध करें। (4) उपद्रव की स्थिति में, स्थानीय नगरपालिका में शिकायत दर्ज करें। (5) अंतिम उपाय के रूप में, निषेधाज्ञा के लिए दीवानी मुकदमा दर्ज करें।",
        },
    }

    default_guidance = {
        "en": "Based on your description, we've found relevant legal provisions. Review the results below and consult a qualified lawyer for advice specific to your situation.",
        "ne": "तपाईंको विवरणको आधारमा, हामीले सम्बन्धित कानूनी उपबन्धहरू फेला पारेका छौं। तलका परिणामहरू समीक्षा गर्नुहोस् र तपाईंको अवस्थाका लागि विशिष्ट सल्लाहका लागि योग्य वकीलसँग परामर्श गर्नुहोस्।",
        "hi": "आपके विवरण के आधार पर, हमने प्रासंगिक कानूनी प्रावधान पाए हैं। नीचे दिए गए परिणामों की समीक्षा करें और अपनी स्थिति के अनुसार विशिष्ट सलाह के लिए एक योग्य वकील से परामर्श करें।",
    }

    return guidance_map.get(issue_id, default_guidance).get(lang, guidance_map.get(issue_id, default_guidance).get("en", ""))
