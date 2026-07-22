"""Multilingual search — language detection, transliteration, query expansion.

Handles:
- Devanagari script queries (Nepali/Hindi text)
- Romanized Nepali/Hindi queries (e.g., "baato ma fohor", "hatya ka saboot")
- Mixed language queries
- Maps everything to English legal terms for corpus matching
"""

import re
import unicodedata
from typing import Dict, List, Optional, Set, Tuple

# ── Language Detection ───────────────────────────────────────────────

def detect_script(text: str) -> str:
    """Detect dominant script: 'devanagari', 'latin', or 'mixed'."""
    devanagari_count = 0
    latin_count = 0
    for ch in text:
        if ch.isalpha():
            cat = unicodedata.category(ch)
            if ch >= '\u0900' and ch <= '\u097F':  # Devanagari block
                devanagari_count += 1
            elif (ch >= 'a' and ch <= 'z') or (ch >= 'A' and ch <= 'Z'):
                latin_count += 1
    if devanagari_count > latin_count:
        return "devanagari"
    elif latin_count > devanagari_count:
        return "latin"
    elif devanagari_count > 0 and latin_count > 0:
        return "mixed"
    return "unknown"


# ── Romanized Nepali/Hindi → Devanagari Transliteration Map ─────────

# Common romanized Nepali/Hindi words that users type
ROMANIZED_MAP: Dict[str, List[str]] = {
    # Nepali common words
    "baato": ["बाटो", "road", "path", "way"],
    "bato": ["बाटो", "road", "path", "way"],
    "fohor": ["फोहोर", "garbage", "waste", "litter", "dirty", "filth"],
    "fohor": ["फोहोर", "garbage", "waste", "litter"],
    "sarkar": ["सरकार", "government", "state"],
    "kanoon": ["कानून", "law", "legal", "act"],
    "kanun": ["कानून", "law", "legal", "act"],
    "adalat": ["अदालत", "court", "tribunal"],
    "adalt": ["अदालत", "court", "tribunal"],
    "hatya": ["हत्या", "murder", "killing", "homicide"],
    "hattia": ["हत्या", "murder", "killing", "homicide"],
    "chor": ["चोर", "thief", "stealing", "theft", "robbery"],
    "chori": ["चोरी", "theft", "stealing", "robbery"],
    "loot": ["लुट", "robbery", "loot", "plunder"],
    "daka": ["डकैती", "dacoity", "robbery", "armed robbery"],
    "dakaiti": ["डकैती", "dacoity", "robbery"],
    "dhiti": ["हिंसा", "violence", "assault", "beating"],
    "maar": ["मार", "beating", "assault", "hit"],
    "chori": ["चोरी", "theft", "stealing"],
    "jagga": ["जग्गा", "land", "property", "plot"],
    "zamin": ["जमिन", "land", "ground", "property"],
    "ghar": ["घर", "house", "home", "dwelling"],
    "biwi": ["बीवी", "wife", "spouse"],
    "bivi": ["बीवी", "wife", "spouse"],
    "pati": ["पति", "husband", "spouse"],
    "bacha": ["बच्चा", "child", "minor", "children"],
    "bachcha": ["बच्चा", "child", "minor", "children"],
    "byaah": ["विवाह", "marriage", "wedding"],
    "biyah": ["विवाह", "marriage", "wedding"],
    "vivah": ["विवाह", "marriage", "wedding"],
    "talaq": ["तलाक", "divorce"],
    "talak": ["तलाक", "divorce"],
    "jagga": ["जग्गा", "land", "property"],
    "nokri": ["नोकरी", "job", "employment", "work"],
    "jyala": ["ज्याला", "wages", "salary", "pay"],
    "jwalā": ["ज्याला", "wages", "salary", "pay"],
    "paisa": ["पैसा", "money", "payment"],
    "rakkam": ["रकम", "amount", "sum", "money"],
    "sajaya": ["सजाय", "punishment", "penalty", "sentence"],
    "saza": ["सजा", "punishment", "penalty", "sentence"],
    "sazaa": ["सजा", "punishment", "penalty", "sentence"],
    "qaid": ["कैद", "imprisonment", "jail", "custody"],
    "qaidi": ["कैदी", "prisoner", "convict"],
    "jamanat": ["जमानत", "bail", "bond", "surety"],
    "girftari": ["गिरफ्तारी", "arrest", "detention"],
    "giraftari": ["गिरफ्तारी", "arrest", "detention"],
    "saboot": ["सबूत", "evidence", "proof"],
    "sabut": ["सबूत", "evidence", "proof"],
    "gawahi": ["गवाही", "testimony", "witness"],
    "gawah": ["गवाह", "witness"],
    "vakil": ["वकील", "lawyer", "advocate", "attorney"],
    "wakil": ["वकील", "lawyer", "advocate", "attorney"],
    "judge": ["न्यायाधीश", "judge", "magistrate"],
    "nyayadhish": ["न्यायाधीश", "judge"],
    "sarkari": ["सरकारी", "government", "official", "public"],
    "niji": ["निजी", "private", "personal"],
    "samjhauta": ["समझौता", "agreement", "contract", "settlement"],
    "kharid": ["खरीद", "purchase", "buying", "sale"],
    "bech": ["बेच", "sell", "sale", "selling"],
    "kiraaya": ["किराया", "rent", "lease"],
    "kiraya": ["किराया", "rent", "lease"],
    "byaj": ["ब्याज", "interest", "loan interest"],
    "karz": ["कर्ज", "loan", "debt"],
    "karja": ["कर्ज", "loan", "debt"],
    "gunah": ["गुनाह", "crime", "offence", "offense"],
    "jurma": ["जुर्म", "crime", "offence", "guilt"],
    "saza": ["सजा", "punishment", "penalty"],
    "jurm": ["जुर्म", "crime", "offence"],
    "police": ["पुलिस", "police", "law enforcement"],
    "thana": ["थाना", "police station"],
    "fir": ["प्राथमिकी", "FIR", "first information report"],
    "chukti": ["चुक्ता", "paid", "payment"],
    "damani": ["दामनी", "bribery", "corruption"],
    "bhrashtachar": ["भ्रष्टाचार", "corruption"],
    "bhrashtachar": ["भ्रष्टाचार", "corruption", "bribery"],
    "dhoka": ["धोखा", "fraud", "cheating", "deception"],
    "thaggi": ["ठगी", "fraud", "cheating", "scam"],
    "jaanzaari": ["जानकारी", "information", "knowledge"],
    "jankari": ["जानकारी", "information", "knowledge"],
    "adhikar": ["अधिकार", "right", "authority"],
    "adhikaar": ["अधिकार", "right", "authority"],
    "farman": ["फरमान", "order", "decree", "judgment"],
    "adesh": ["आदेश", "order", "direction"],
    "karyawahi": ["कार्यवाही", "proceeding", "procedure", "action"],
    "karwai": ["कार्यवाही", "proceeding", "procedure"],
    "mukadma": ["मुकदमा", "case", "lawsuit", "suit"],
    "mukadama": ["मुकदमा", "case", "lawsuit", "suit"],
    "dawa": ["दावा", "claim", "demand"],
    "dalil": ["दलील", "argument", "plea", "contention"],
    "hukum": ["हुकुम", "order", "decree", "ruling"],
    "fatwa": ["फतवा", "fatwa", "religious decree"],
    "kanooni": ["कानूनी", "legal", "lawful", "judicial"],
    "gairkanooni": ["गैरकानूनी", "illegal", "unlawful"],
    "gair-kanooni": ["गैरकानूनी", "illegal", "unlawful"],
    "vivad": ["विवाद", "dispute", "conflict", "controversy"],
    "samasya": ["समस्या", "problem", "issue"],
    "shikayat": ["शिकायत", "complaint", "grievance"],
    "aavedan": ["आवेदन", "application", "petition"],
    "nivedan": ["निवेदन", "request", "appeal"],
    "anurodh": ["अनुरोध", "request", "appeal"],
    "nepal": ["nepal", "नेपाल"],
    "bharat": ["india", "भारत", "india"],
    "india": ["india", "भारत"],
    # More Nepali common legal terms
    "sanghiya": ["संघीय", "federal"],
    "samvidhan": ["संविधान", "constitution"],
    "sansad": ["संसद", "parliament"],
    "mantri": ["मन्त्री", "minister"],
    "pradhan": ["प्रधान", "prime", "chief"],
    "rajnitik": ["राजनीतिक", "political"],
    "swatantra": ["स्वतन्त्र", "independent", "free"],
    "swatantrata": ["स्वतन्त्रता", "independence", "freedom", "liberty"],
    "bhedbhav": ["भेदभाव", "discrimination"],
    "samanata": ["समानता", "equality"],
    "manav": ["मानव", "human"],
    "nagarik": ["नागरिक", "citizen", "civic"],
    "kam": ["काम", "work", "labor"],
    "kaam": ["काम", "work", "labor"],
    "majdur": ["मजदूर", "worker", "laborer"],
    "jyala": ["ज्याला", "wages", "salary"],
    "chutti": ["छुट्टी", "leave", "holiday", "vacation"],
    "byapar": ["व्यापार", "business", "trade", "commerce"],
    "udyog": ["उद्योग", "industry", "enterprise"],
    "kheti": ["कृषि", "agriculture", "farming"],
    "van": ["वन", "forest"],
    "paryavaran": ["पर्यावरण", "environment"],
    "pradushan": ["प्रदूषण", "pollution"],
    "swasthya": ["स्वास्थ्य", "health"],
    "shiksha": ["शिक्षा", "education"],
    "pahichaan": ["पहिचान", "identity", "identification"],
    "nagrikta": ["नागरिकता", "citizenship"],
    "pravasi": ["प्रवासी", "migrant", "diaspora"],
    "mahila": ["महिला", "woman", "women"],
    "puruush": ["पुरुष", "man", "male"],
    "bal": ["बाल", "child", "minor"],
    "vriddh": ["वृद्ध", "elderly", "senior"],
    "apango": ["अपाङ्ग", "disabled", "handicapped"],
    "dalit": ["दलित", "dalit", "untouchable"],
    "janajati": ["जनजाती", "indigenous", "tribal"],
    "madhesi": ["मधेसी", "madhesi"],
    "pahadi": ["पहाडी", "pahadi", "hill"],
    "terai": ["तराई", "terai", "plains"],
    # ── Compound legal scenario phrases (romanized) ──────────────
    "chimeki": ["neighbor", "neighbour", "पड़ोसी", "छिमेकी"],
    "chhimeki": ["neighbor", "neighbour", "पड़ोसी", "छिमेकी"],
    "chimiki": ["neighbor", "neighbour", "पड़ोसी", "छिमेकी"],
    "nikaldyo": ["evict", "kicked out", "removed", "throw out", "निकाला"],
    "nikaaliyo": ["evict", "kicked out", "removed", "throw out"],
    "nikaal": ["evict", "remove", "throw out", "निकाल"],
    "ghar bata": ["from house", "out of house", "घर से"],
    "bata": ["from", "out of"],
    "hataayo": ["removed", "cleared", "displaced"],
    "ghar": ["house", "home", "dwelling", "घर"],
    "jagga": ["land", "property", "plot", "जग्गा"],
    "zamin": ["land", "ground", "property", "जमिन"],
    "kiraya": ["rent", "lease", "किराया"],
    "kiraaya": ["rent", "lease", "किराया"],
    "bhadatitika": ["tenant", "tenant rental"],
    "deposit": ["deposit", "security deposit", "जम्मा"],
    "landlord": ["landlord", "property owner", "मालिक"],
    "maar": ["beat", "hitting", "assault", "मार"],
    "maarpit": ["fight", "beating", "assault", "मारपीट"],
    "gali": ["abuse", "swearing", "verbal abuse", "गाली"],
    "dhiti": ["violence", "beating", "हिंसा"],
    "bribe": ["bribe", "ransom", "corruption", "घुस"],
    "ghoos": ["bribe", "ransom", "घुस"],
    "ilaj": ["treatment", "medical", "इलाज"],
    "galat": ["wrong", "incorrect", "false", "गलत"],
    "pakro": ["caught", "arrested", "detained", "पकड़ो"],
    "pakdyo": ["caught", "arrested", "stopped", "पकड़ा"],
    "rokyo": ["stopped", "halted", "रोका"],
    "hijack": ["hijack", "seize", "forcibly take"],
    "chhintyo": ["snatched", "grabbed", "forcibly taken"],
    "dahej": ["dowry", "दहेज"],
    "tikun": ["nagging", "pestering", "harassment"],
    "jhidak": ["snatching", "grabbing"],
    "divorce": ["divorce", "separation", "तलाक"],
    "talaq": ["divorce", "तलाक"],
    "byaah": ["marriage", "wedding", "विवाह"],
    "biyah": ["marriage", "wedding", "विवाह"],
    "nokri": ["job", "employment", "work", "नौकरी"],
    "naukri": ["job", "employment", "work", "नौकरी"],
    "jyala": ["wages", "salary", "pay", "ज्याला"],
    "tankhwah": ["salary", "wages", "तनख्वाह"],
    "pesi": ["money", "payment", "पैसे"],
    "thagi": ["fraud", "scam", "cheating", "ठगी"],
    "dhoka": ["fraud", "cheating", "deception", "धोखा"],
    "durghatana": ["accident", "crash", "दुर्घटना"],
    "chot": ["injury", "wound", "चोट"],
    "jamanat": ["bail", "bond", "surety", "जमानत"],
    "chhutti": ["release", "freedom", "leave", "छुट्टी"],
    "riha": ["release", "discharge", "रिहाई"],
    "sarkari": ["government", "official", "public", "सरकारी"],
    "karyalaya": ["office", "कार्यालय"],
    "sarkari karyalaya": ["government office", "सरकारी कार्यालय"],
    "aavedan": ["application", "petition", "आवेदन"],
    "pending": ["pending", "waiting", "stuck", "लामो समय"],
    "grievance": ["complaint", "grievance", "शिकायत"],
    "challan": ["challan", "fine", "ticket", "चालान"],
    "license": ["licence", "license", "driving", "परमिट"],
}

# Common Nepali/Hindi stop words (romanized) to filter out
ROMANIZED_STOP_WORDS = frozenset([
    "ma", "mero", "mero", "ko", "ka", "ke", "le", "lai", "ma",
    "yo", "tyo", "yo", "te", "ra", "ani", "tara", "ki", "na",
    "ho", "haina", "cha", "chha", "thyo", "thiya", "huncha",
    "garnu", "hunu", "parcha", "saknu", "parne", "hune",
    "malai", "hami", "tapai", "timi", "u", "uni", "uniharuko",
    "ko lagi", "ma", "tira", "bata", "sangai", "saath",
    "mero", "timro", "usko", "hamro", "tesko",
    # Hindi common words
    "main", "mein", "mera", "meri", "mere", "hum", "hamara",
    "tum", "tumhara", "apna", "uska", "uski", "uske",
    "ye", "wo", "yeh", "vah", "yehi", "wahi",
    "ka", "ki", "ke", "ko", "se", "me", "par", "pe",
    "aur", "ya", "ki", "kya", "hai", "hain", "tha", "thi",
    "hoga", "hogi", "honge", "karega", "karegi", "karenge",
    "karna", "karna", "hona", "honā",
])


# ── Devanagari to English Legal Term Map ────────────────────────────

DEVANAGARI_TO_ENGLISH: Dict[str, List[str]] = {
    # Courts & Legal System
    "अदालत": ["court", "tribunal"],
    "न्यायालय": ["court", "justice"],
    "सर्वोच्च अदालत": ["supreme court"],
    "सर्वोच्च न्यायालय": ["supreme court"],
    "उच्च अदालत": ["high court"],
    "जिल्ला अदालत": ["district court"],
    "अपील अदालत": ["appellate court"],
    "अपीलीय न्यायालय": ["appellate court"],
    "न्यायाधीश": ["judge", "magistrate"],
    "वकील": ["lawyer", "advocate", "attorney"],
    "वकिल": ["lawyer", "advocate", "attorney"],
    
    # Criminal Law
    "हत्या": ["murder", "homicide", "killing"],
    "हत्याको": ["murder", "homicide"],
    "चोरी": ["theft", "stealing", "robbery"],
    "चोर": ["thief", "stealing"],
    "लुट": ["robbery", "loot"],
    "डकैती": ["dacoity", "robbery", "armed robbery"],
    "गिरफ्तारी": ["arrest", "detention"],
    "जमानत": ["bail", "bond", "surety"],
    "सजाय": ["punishment", "penalty", "sentence"],
    "सजा": ["punishment", "penalty", "sentence"],
    "जुर्म": ["crime", "offence", "offense"],
    "गुनाह": ["crime", "offence"],
    "सबूत": ["evidence", "proof"],
    "गवाही": ["testimony", "witness"],
    "गवाह": ["witness"],
    "प्राथमिकी": ["FIR", "first information report"],
    "वारन्ट": ["warrant"],
    "वारंट": ["warrant"],
    "कैद": ["imprisonment", "jail", "custody"],
    "कैदी": ["prisoner", "convict"],
    "पुलिस": ["police", "law enforcement"],
    "थाना": ["police station"],
    "पुलिस स्टेशन": ["police station"],
    "हिंसा": ["violence", "assault"],
    "धम्की": ["threat", "intimidation"],
    "धोखा": ["fraud", "cheating", "deception"],
    "ठगी": ["fraud", "cheating", "scam"],
    
    # Civil Law
    "सम्पत्ति": ["property", "assets"],
    "जग्गा": ["land", "property", "plot"],
    "जमिन": ["land", "ground", "property"],
    "घर": ["house", "home", "dwelling"],
    "विवाह": ["marriage", "wedding"],
    "तलाक": ["divorce"],
    "विवाह विच्छेद": ["divorce", "matrimonial"],
    "पति": ["husband", "spouse"],
    "बीवी": ["wife", "spouse"],
    "बच्चा": ["child", "minor", "children"],
    "अनुबन्ध": ["contract", "agreement"],
    "समझौता": ["agreement", "contract", "settlement"],
    "किराया": ["rent", "lease"],
    "ब्याज": ["interest", "loan interest"],
    "कर्ज": ["loan", "debt"],
    "दावा": ["claim", "demand"],
    "मुकदमा": ["case", "lawsuit", "suit"],
    
    # Rights & Governance
    "अधिकार": ["right", "authority"],
    "अधिकारहरू": ["rights"],
    "कानून": ["law", "legal", "act"],
    "कानूनी": ["legal", "lawful", "judicial"],
    "संविधान": ["constitution"],
    "सरकार": ["government", "state"],
    "सरकारी": ["government", "official", "public"],
    "नागरिक": ["citizen", "civic"],
    "नागरिकता": ["citizenship"],
    "स्वतन्त्रता": ["freedom", "liberty", "independence"],
    "समानता": ["equality"],
    "भेदभाव": ["discrimination"],
    "मानव": ["human"],
    "मानवाधिकार": ["human rights"],
    
    # Employment
    "नोकरी": ["job", "employment", "work"],
    "ज्याला": ["wages", "salary", "pay"],
    "मजदूर": ["worker", "laborer"],
    "श्रम": ["labor", "labour"],
    "काम": ["work", "labor"],
    
    # Other
    "भ्रष्टाचार": ["corruption", "bribery"],
    "जानकारी": ["information", "knowledge"],
    "शिकायत": ["complaint", "grievance"],
    "विवाद": ["dispute", "conflict"],
    "कार्यवाही": ["proceeding", "procedure", "action"],
    "आदेश": ["order", "direction"],
    "दामनी": ["bribery", "corruption"],
    "पर्यावरण": ["environment"],
    "प्रदूषण": ["pollution"],
    "वन": ["forest"],
    "स्वास्थ्य": ["health"],
    "शिक्षा": ["education"],
    "पहिचान": ["identity", "identification"],
    "प्रवासी": ["migrant", "diaspora"],
    "महिला": ["woman", "women"],
    "बाल": ["child", "minor"],
    "वृद्ध": ["elderly", "senior"],
    "दलित": ["dalit"],
    "जनजाती": ["indigenous", "tribal"],
    "मधेसी": ["madhesi"],
    "पहाडी": ["pahadi", "hill"],
    "तराई": ["terai", "plains"],
    "संघीय": ["federal"],
    "संसद": ["parliament"],
    "मन्त्री": ["minister"],
    "प्रधान": ["prime", "chief"],
    "राजनीतिक": ["political"],
    "व्यापार": ["business", "trade", "commerce"],
    "उद्योग": ["industry", "enterprise"],
    "कृषि": ["agriculture", "farming"],
}


# ── Query Translation ───────────────────────────────────────────────

def translate_query(query: str) -> Tuple[str, str, List[str]]:
    """
    Detect language, translate to English, return (detected_lang, english_query, all_terms).
    
    Returns:
        detected_lang: 'en', 'ne', 'hi', 'romanized_ne', 'romanized_hi', 'mixed'
        english_query: translated English terms
        all_terms: all expanded search terms
    """
    script = detect_script(query)
    
    if script == "devanagari":
        return _translate_devanagari(query)
    elif script == "latin":
        return _translate_romanized(query)
    elif script == "mixed":
        return _translate_mixed(query)
    return "en", query, [query]


def _translate_devanagari(query: str) -> Tuple[str, List[str]]:
    """Translate Devanagari script query to English terms."""
    words = query.split()
    all_terms = []
    english_parts = []
    
    # Try multi-word matches first (longest match)
    i = 0
    matched_positions = set()
    while i < len(words):
        matched = False
        for length in range(min(4, len(words) - i), 0, -1):
            phrase = " ".join(words[i:i+length])
            if phrase in DEVANAGARI_TO_ENGLISH:
                translations = DEVANAGARI_TO_ENGLISH[phrase]
                all_terms.extend(translations)
                english_parts.extend(translations)
                for j in range(i, i+length):
                    matched_positions.add(j)
                i += length
                matched = True
                break
        if not matched:
            i += 1
    
    # Single word matches for unmatched words
    for i, word in enumerate(words):
        if i not in matched_positions:
            if word in DEVANAGARI_TO_ENGLISH:
                translations = DEVANAGARI_TO_ENGLISH[word]
                all_terms.extend(translations)
                english_parts.extend(translations)
            elif len(word) > 2:
                all_terms.append(word)
    
    english_query = " ".join(english_parts) if english_parts else query
    return "devanagari", english_query, all_terms


def _translate_romanized(query: str) -> Tuple[str, List[str]]:
    """Translate romanized Nepali/Hindi to English terms."""
    words = query.lower().split()
    all_terms = []
    english_parts = []
    is_nepali_heavy = False
    is_hindi_heavy = False
    
    # Filter stop words and match
    for word in words:
        if word in ROMANIZED_STOP_WORDS or len(word) < 2:
            continue
        
        if word in ROMANIZED_MAP:
            translations = ROMANIZED_MAP[word]
            all_terms.extend(translations)
            english_parts.extend(translations)
            # Heuristic: if we find common Nepali words, it's likely Nepali
            if word in ["ma", "ko", "le", "lai", "cha", "huncha", "garnu", "parcha"]:
                is_nepali_heavy = True
            if word in ["main", "mein", "hai", "hain", "tha", "ko", "ki"]:
                is_hindi_heavy = True
    
    # If no matches, try treating each word as potential English
    if not all_terms:
        return "en", query, [w for w in words if len(w) > 2]
    
    lang = "romanized_ne" if is_nepali_heavy else ("romanized_hi" if is_hindi_heavy else "romanized")
    english_query = " ".join(english_parts)
    return lang, english_query, all_terms


def _translate_mixed(query: str) -> Tuple[str, List[str]]:
    """Handle mixed script queries."""
    # Split by script
    devanagari_words = []
    latin_words = []
    current = []
    current_script = None
    
    for ch in query:
        if ch.isalpha() or ch == ' ':
            if ch >= '\u0900' and ch <= '\u097F':
                script = "devanagari"
            elif (ch >= 'a' and ch <= 'z') or (ch >= 'A' and ch <= 'Z'):
                script = "latin"
            else:
                script = current_script
            
            if script != current_script and current:
                word = "".join(current).strip()
                if word:
                    if current_script == "devanagari":
                        devanagari_words.append(word)
                    elif current_script == "latin":
                        latin_words.append(word)
                current = []
            current.append(ch)
            current_script = script
    
    if current:
        word = "".join(current).strip()
        if word:
            if current_script == "devanagari":
                devanagari_words.append(word)
            elif current_script == "latin":
                latin_words.append(word)
    
    all_terms = []
    # Process Devanagari part
    if devanagari_words:
        _, _, dev_terms = _translate_devanagari(" ".join(devanagari_words))
        all_terms.extend(dev_terms)
    
    # Process Latin part  
    if latin_words:
        _, _, rom_terms = _translate_romanized(" ".join(latin_words))
        all_terms.extend(rom_terms)
    
    english_query = " ".join(all_terms)
    return "mixed", english_query, all_terms
