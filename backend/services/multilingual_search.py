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


# ═══════════════════════════════════════════════════════════════════════════
# Devanagari → English Legal Term Map
# ═══════════════════════════════════════════════════════════════════════════
# Organized by legal domain for maintainability.
# Multi-word phrases should come before their component words
# (longest-match-first in _translate_devanagari).
# ═══════════════════════════════════════════════════════════════════════════

DEVANAGARI_TO_ENGLISH: Dict[str, List[str]] = {

    # ──────────────────────────────────────────────────────────────────────
    # 1. CONSTITUTION & FUNDAMENTAL RIGHTS
    # ──────────────────────────────────────────────────────────────────────
    "मौलिक हक": ["fundamental rights", "basic rights"],
    "मौलिक अधिकार": ["fundamental rights"],
    "नागरिकको हक": ["citizen rights", "civil rights"],
    "समानताको हक": ["right to equality"],
    "स्वतन्त्रताको हक": ["right to freedom"],
    "बाँच्न पाउने हक": ["right to life", "right to live"],
    "जीवनको हक": ["right to life"],
    "मर्यादित जीवनको हक": ["right to dignified life"],
    "शिक्षाको हक": ["right to education"],
    "स्वास्थ्यको हक": ["right to health"],
    "रोजगारीको हक": ["right to employment"],
    "सम्पत्तिको हक": ["right to property"],
    "सूचनाको हक": ["right to information"],
    "न्यायको हक": ["right to justice"],
    "कानूनी उपचारको हक": ["right to legal remedy"],
    "संवैधानिक उपचारको हक": ["right to constitutional remedy"],
    "धर्मको स्वतन्त्रता": ["freedom of religion"],
    "अभिव्यक्तिको स्वतन्त्रता": ["freedom of expression"],
    "विचारको स्वतन्त्रता": ["freedom of thought"],
    "संगठनको स्वतन्त्रता": ["freedom of association"],
    "भेला हुने स्वतन्त्रता": ["freedom of assembly"],
    "आवागमनको स्वतन्त्रता": ["freedom of movement"],
    "व्यवसायको स्वतन्त्रता": ["freedom of occupation"],
    "मानव अधिकार": ["human rights"],
    "मानवाधिकार": ["human rights"],
    "बालबालिकाको हक": ["childrens rights", "child rights"],
    "महिलाको हक": ["womens rights"],
    "दलितको हक": ["dalit rights"],
    "अपाङ्गताको हक": ["disability rights"],
    "शोषण विरुद्धको हक": ["right against exploitation"],
    "यातना विरुद्धको हक": ["right against torture"],
    "नजरबन्द विरुद्धको हक": ["right against arbitrary detention"],
    "गोपनीयताको हक": ["right to privacy"],
    "संवैधानिक": ["constitutional"],
    "संवैधानिक परिषद": ["constitutional council"],
    "संविधानसभा": ["constituent assembly"],
    "संविधान संशोधन": ["constitutional amendment"],
    "मौलिक कर्तव्य": ["fundamental duties"],
    "राज्यका निर्देशक सिद्धान्त": ["directive principles of state"],

    # ──────────────────────────────────────────────────────────────────────
    # 2. COURT SYSTEM & LEGAL PROFESSIONALS
    # ──────────────────────────────────────────────────────────────────────
    "अदालत": ["court", "tribunal"],
    "न्यायालय": ["court", "justice"],
    "सर्वोच्च अदालत": ["supreme court"],
    "सर्वोच्च न्यायालय": ["supreme court"],
    "उच्च अदालत": ["high court"],
    "जिल्ला अदालत": ["district court"],
    "जिल्ला न्यायालय": ["district court"],
    "अपील अदालत": ["appellate court"],
    "अपीलीय न्यायालय": ["appellate court"],
    "विशेष अदालत": ["special court"],
    "प्रशासकीय अदालत": ["administrative court"],
    "सैनिक अदालत": ["military court"],
    "अन्तरिम अदालत": ["interim court"],
    "संवैधानिक इजलास": ["constitutional bench"],
    "पूर्ण इजलास": ["full bench"],
    "इजलास": ["bench", "court session"],
    "न्यायाधीश": ["judge", "magistrate"],
    "प्रधान न्यायाधीश": ["chief justice"],
    "मुख्य न्यायाधीश": ["chief justice"],
    "न्यायमूर्ति": ["justice", "judge"],
    "न्यायिक": ["judicial"],
    "न्यायिक समिति": ["judicial committee"],
    "न्यायिक नियुक्ति": ["judicial appointment"],
    "न्यायिक पुनरावलोकन": ["judicial review"],
    "वकील": ["lawyer", "advocate", "attorney"],
    "वकिल": ["lawyer", "advocate", "attorney"],
    "कानून व्यवसायी": ["legal practitioner", "lawyer"],
    "सरकारी वकील": ["government lawyer", "public prosecutor"],
    "न्यायिक अधिकारी": ["judicial officer"],
    "न्याय सहायक": ["court clerk", "legal assistant"],
    "अधिवक्ता": ["advocate", "barrister"],
    "महान्यायाधिवक्ता": ["attorney general"],
    "न्यायिक निकाय": ["judicial body"],
    "न्यायिक निर्णय": ["judicial decision", "judgment"],
    "बार एसोसिएसन": ["bar association"],
    "कानुन व्यवसायी": ["legal professional"],
    "लिखित जवाफ": ["written response", "defense"],
    "समन": ["summons", "notice"],
    "पेशी": ["hearing date", "court date"],

    # ──────────────────────────────────────────────────────────────────────
    # 3. CRIMINAL LAW
    # ──────────────────────────────────────────────────────────────────────
    "हत्या": ["murder", "homicide", "killing"],
    "हत्याको": ["murder", "homicide"],
    "हत्याको मुद्दा": ["murder case"],
    "हत्यारोपण": ["murder accusation"],
    "हत्यारा": ["murderer", "killer"],
    "ज्यान मार्ने": ["homicide", "deadly"],
    "ज्यान मार्ने उद्योग": ["attempt to murder"],
    "चोरी": ["theft", "stealing", "robbery"],
    "चोर": ["thief", "stealing"],
    "चोरपकाड": ["thief caught", "stolen goods recovered"],
    "लुट": ["robbery", "loot"],
    "लुटपाट": ["robbery", "looting", "plunder"],
    "डकैती": ["dacoity", "robbery", "armed robbery"],
    "डकैत": ["dacoit", "robber"],
    "बलात्कार": ["rape", "sexual assault"],
    "बलात्कारको मुद्दा": ["rape case"],
    "यौन दुव्र्यवहार": ["sexual abuse", "sexual harassment"],
    "यौन हिंसा": ["sexual violence"],
    "यौनजन्य हिंसा": ["gender-based violence"],
    "गिरफ्तारी": ["arrest", "detention"],
    "गिरफ्तार": ["arrested", "under arrest"],
    "पक्राउ": ["arrest", "apprehend"],
    "पक्राउ पुर्जी": ["arrest warrant"],
    "जमानत": ["bail", "bond", "surety"],
    "जमानत माग": ["bail application"],
    "जमानतदार": ["surety", "guarantor"],
    "सजाय": ["punishment", "penalty", "sentence"],
    "सजा": ["punishment", "penalty", "sentence"],
    "मृत्युदण्ड": ["death penalty", "capital punishment"],
    "जरिवाना": ["fine", "monetary penalty"],
    "दण्ड": ["punishment", "penalty"],
    "दण्ड संहिता": ["penal code", "criminal code"],
    "जुर्म": ["crime", "offence", "offense"],
    "जुर्माना": ["fine", "penalty"],
    "गुनाह": ["crime", "offence", "guilt"],
    "गुनासो": ["complaint", "grievance"],
    "गुनासो सुनुवाइ": ["complaint hearing"],
    "अपराध": ["crime", "offence", "criminal act"],
    "अपराधी": ["criminal", "offender", "convict"],
    "अपराधिक मामिला": ["criminal case"],
    "सबूत": ["evidence", "proof"],
    "प्रमाण": ["evidence", "proof", "testimony"],
    "प्रमाणको भार": ["burden of proof"],
    "गवाही": ["testimony", "witness statement"],
    "गवाह": ["witness"],
    "प्राथमिकी": ["FIR", "first information report"],
    "प्राथमिक": ["primary", "initial"],
    "प्राथमिक उपचार": ["first aid"],
    "वारन्ट": ["warrant"],
    "वारंट": ["warrant"],
    "जाँच": ["investigation", "inquiry", "examination"],
    "अनुसन्धान": ["investigation", "research", "inquiry"],
    "अभियोग": ["charge", "accusation", "indictment"],
    "अभियोग पत्र": ["charge sheet", "indictment"],
    "फैसला": ["judgment", "decision", "verdict"],
    "सफाइ": ["acquittal", "acquitted"],
    "दोषी": ["guilty", "culprit", "offender"],
    "दोषी ठहर": ["conviction", "found guilty"],
    "निर्दोष": ["innocent", "not guilty"],
    "कैद": ["imprisonment", "jail", "custody"],
    "कैदी": ["prisoner", "convict"],
    "कैदखाना": ["jail", "prison"],
    "कारागार": ["prison", "jail"],
    "जेल": ["jail", "prison"],
    "पुलिस": ["police", "law enforcement"],
    "प्रहरी": ["police"],
    "प्रहरी स्टेशन": ["police station"],
    "थाना": ["police station"],
    "पुलिस स्टेशन": ["police station"],
    "एसपी": ["superintendent of police", "police chief"],
    "डीएसपी": ["deputy superintendent of police"],
    "प्रहरी निरीक्षक": ["police inspector"],
    "हिंसा": ["violence", "assault"],
    "मारपीट": ["assault", "fighting", "beating"],
    "कुटपिट": ["beating", "assault", "battery"],
    "धम्की": ["threat", "intimidation", "menace"],
    "धम्क्याउनु": ["to threaten", "threatening"],
    "धोखा": ["fraud", "cheating", "deception"],
    "धोखाधडी": ["fraud", "cheating", "scam"],
    "ठगी": ["fraud", "cheating", "scam"],
    "ठग": ["fraudster", "cheat", "scammer"],
    "लागुऔषध": ["drugs", "narcotics"],
    "लागूऔषध": ["narcotics", "drugs"],
    "गाँजा": ["marijuana", "cannabis"],
    "मादक पदार्थ": ["intoxicating substance", "alcohol", "drugs"],
    "अश्लील": ["obscene", "pornographic", "indecent"],
    "अश्लील सामग्री": ["obscene material", "pornography"],
    "मानव बेचबिखन": ["human trafficking"],
    "बेचबिखन": ["trafficking", "selling"],
    "अपहरण": ["kidnapping", "abduction"],
    "अपहरणकर्ता": ["kidnapper"],
    "हराएको": ["missing", "lost"],
    "हुलिया सहायता": ["help desk"],
    "ज्यानमारा": ["life-threatening", "dangerous"],
    "दुर्घटना": ["accident", "crash"],
    "सवारी दुर्घटना": ["traffic accident", "vehicle accident"],
    "चेक बाउन्स": ["cheque bounce", "check dishonor"],

    # ──────────────────────────────────────────────────────────────────────
    # 4. CIVIL LAW
    # ──────────────────────────────────────────────────────────────────────
    "देवानी": ["civil"],
    "देवानी मुद्दा": ["civil case"],
    "देवानी संहिता": ["civil code"],
    "देवानी कार्यविधि": ["civil procedure"],
    "सिविल": ["civil"],
    "अनुबन्ध": ["contract", "agreement"],
    "अनुबन्धको उल्लंघन": ["breach of contract"],
    "सम्झौता": ["agreement", "contract", "settlement"],
    "समझौता": ["agreement", "contract", "settlement"],
    "साँच्चो": ["genuine", "authentic"],
    "कबुलियत": ["agreement", "bond"],
    "मौखिक सम्झौता": ["oral agreement", "verbal contract"],
    "लिखित सम्झौता": ["written agreement", "written contract"],
    "जग्गा सम्झौता": ["land agreement", "property contract"],
    "दावा": ["claim", "demand"],
    "दावी": ["claim", "demand"],
    "प्रतिदावी": ["counterclaim"],
    "मुद्दा": ["case", "lawsuit", "suit"],
    "मुकदमा": ["case", "lawsuit", "suit"],
    "मुद्दा दर्ता": ["case registration"],
    "मुद्दा नं": ["case number"],
    "मुद्दा फैसला": ["case decision", "judgment"],
    "पुनरावेदन": ["appeal", "appeal petition"],
    "पुनरावेदन अदालत": ["appeal court"],
    "पुनरावलोकन": ["review", "reconsideration"],
    "निवेदन": ["petition", "application", "request"],
    "उजुरी": ["complaint", "petition", "plaint"],
    "उजुरी दर्ता": ["complaint registration"],
    "उजुरीकर्ता": ["complainant", "petitioner"],
    "हक": ["right", "entitlement", "claim"],
    "हकदार": ["entitled person", "claimant", "beneficiary"],
    "हकदारी": ["entitlement", "claim right"],
    "न्याय": ["justice"],
    "अन्याय": ["injustice", "unfairness"],
    "क्षतिपूर्ति": ["compensation", "damages", "reparation"],
    "क्षति": ["damage", "loss", "harm"],
    "मर्जी": ["consent", "will", "wish"],
    "सहमति": ["consent", "agreement", "approval"],
    "रजिस्टर": ["register", "registry", "registration"],
    "रजिस्टरी": ["registry", "registration"],
    "रजिष्ट्रार": ["registrar"],

    # ──────────────────────────────────────────────────────────────────────
    # 5. PROPERTY & LAND
    # ──────────────────────────────────────────────────────────────────────
    "सम्पत्ति": ["property", "assets"],
    "सम्पत्तिमा": ["property", "in property"],
    "सम्पत्तिको": ["property", "of property"],
    "सम्पत्तिहरू": ["property", "properties"],
    "सम्पत्तिशाली": ["wealthy", "property owner"],
    "सम्पत्ति विवाद": ["property dispute"],
    "सम्पत्तिको हस्तान्तरण": ["transfer of property"],
    "स्थावर सम्पत्ति": ["immovable property", "real estate"],
    "चल सम्पत्ति": ["movable property"],
    "जग्गा": ["land", "property", "plot"],
    "जग्गा धनी": ["landowner"],
    "जग्गाको मालिक": ["landowner", "property owner"],
    "जग्गा विवाद": ["land dispute"],
    "जग्गा नापी": ["land measurement", "land survey"],
    "जग्गा पास": ["land transfer approval"],
    "जमिन": ["land", "ground", "property"],
    "जमिनको मालिक": ["landowner"],
    "जग्गाजमिन": ["land", "property", "land property"],
    "जमिनदार": ["landlord", "landowner"],
    "घर": ["house", "home", "dwelling"],
    "घरधनी": ["house owner", "landlord"],
    "घरघडेरी": ["house", "property", "real estate"],
    "घरजग्गा": ["house and land", "real estate"],
    "घरभाडा": ["house rent"],
    "घरबेटी": ["landlord", "house owner"],
    "भाडा": ["rent", "lease"],
    "भाडा सम्झौता": ["rent agreement", "lease agreement"],
    "भाडामा दिनु": ["to rent out", "to lease"],
    "भाडावाल": ["tenant", "renter"],
    "ठेके": ["contract", "agreement"],
    "ठेक्का": ["contract", "lease", "tenancy"],
    "ठेक्कापट्टा": ["contract", "lease agreement"],
    "लालपुर्जा": ["land title deed", "land registration certificate"],
    "रजिस्ट्रेसन": ["registration"],
    "पास": ["approval", "clearance", "transfer"],
    "राजीनामा": ["property transfer deed", "sale deed"],
    "राजिनामा": ["property transfer", "sale deed"],
    "कबुलियत पत्र": ["bond", "agreement deed"],
    "नापी": ["measurement", "survey"],
    "नक्सा": ["map", "blueprint"],
    "साँध": ["boundary", "border"],
    "साँधसीमा": ["boundary", "border limit"],
    "सीमा": ["border", "boundary", "limit"],
    "सिमाना": ["border", "boundary", "frontier"],
    "अतिक्रमण": ["encroachment", "trespass"],
    "अतिक्रमणकारी": ["encroacher", "trespasser"],
    "कब्जा": ["possession", "occupancy", "encroachment"],
    "कब्जियत": ["possession", "occupation"],
    "भोगचलन": ["possession", "usage", "enjoyment"],
    "सुकम्बासी": ["squatter", "landless"],
    "मोही": ["tenant farmer", "cultivator"],
    "जोत": ["cultivation", "farming", "tillage"],
    "जोताहा": ["farmer", "cultivator", "tenant"],
    "हकभोग": ["right of possession"],
    "अंश": ["share", "portion", "partition", "inheritance share"],
    "अंशबन्डा": ["partition", "inheritance division", "family settlement"],
    "अंशियार": ["co-sharer", "coparcener", "sharer"],
    "अंश छुट्याउनु": ["to partition", "to allocate share"],
    "भाग": ["share", "part", "portion"],
    "भाग लगाउनु": ["to apportion", "to divide"],
    "बाँडफाँड": ["distribution", "division", "partition"],
    "बाँड्नु": ["to divide", "to distribute"],
    "हिस्सा": ["share", "portion", "part"],
    "हिस्सेदार": ["shareholder", "partner", "co-owner"],
    "पूर्वाधिकार": ["pre-emptive right", "priority right"],
    "निस्सा": ["endorsement"],
    "मालिक": ["owner", "proprietor"],
    "मालिकाना": ["ownership", "proprietorship"],
    "स्वामित्व": ["ownership", "title"],
    "साझेदारी": ["partnership", "joint ownership"],
    "साझेदार": ["partner", "co-owner"],
    "जिमिन्दारी": ["responsibility", "liability"],

    # ──────────────────────────────────────────────────────────────────────
    # 6. INHERITANCE & SUCCESSION
    # ──────────────────────────────────────────────────────────────────────
    "उत्तराधिकार": ["inheritance", "succession", "heirship"],
    "उत्तराधिकारको": ["inheritance", "of inheritance"],
    "उत्तराधिकारी": ["heir", "successor", "inheritor"],
    "उत्तराधिकारी नियुक्ति": ["appointment of heir"],
    "उत्तराधिकारको मुद्दा": ["inheritance case", "succession case"],
    "विरासत": ["inheritance", "legacy", "heritage"],
    "विरासतको मुद्दा": ["inheritance dispute"],
    "पुस्तैनी": ["ancestral", "hereditary"],
    "पुस्तैनी सम्पत्ति": ["ancestral property"],
    "पुस्तौंदेखि": ["generations old", "ancestral"],
    "वसियतनामा": ["will", "testament"],
    "वसियत": ["will", "testament", "bequest"],
    "वसियतकर्ता": ["testator", "person making will"],
    "वारिस": ["heir", "legal heir", "successor"],
    "कानूनी वारिस": ["legal heir"],
    "वारिसनामा": ["succession certificate"],
    "वारिस प्रमाणपत्र": ["heir certificate", "succession certificate"],
    "बुबाको सम्पत्ति": ["fathers property"],
    "आमाबुबाको सम्पत्ति": ["parents property"],
    "मृतकको सम्पत्ति": ["deceased property"],
    "मृतकको अंश": ["deceased share"],
    "कोइ हक": ["whose right", "who is entitled"],
    "को हक": ["who is entitled"],
    "धर्मपुत्र": ["adopted son"],
    "धर्मपुत्री": ["adopted daughter"],
    "धर्मपुत्र ग्रहण": ["adoption"],
    "त्यागपत्र": ["renunciation", "relinquishment deed"],
    "त्याग": ["renunciation", "abandonment", "sacrifice"],
    "जेठो छोरा": ["eldest son"],
    "कान्छो छोरा": ["youngest son"],
    "अंशियारा": ["female co-sharer"],
    "स्त्री अंश": ["womens share"],

    # ──────────────────────────────────────────────────────────────────────
    # 7. FAMILY & MARRIAGE LAW
    # ──────────────────────────────────────────────────────────────────────
    "विवाह": ["marriage", "wedding"],
    "बिहे": ["marriage", "wedding"],
    "वैवाहिक": ["matrimonial", "marital"],
    "विवाह दर्ता": ["marriage registration"],
    "विवाहको प्रमाणपत्र": ["marriage certificate"],
    "बाल विवाह": ["child marriage"],
    "बहुविवाह": ["polygamy"],
    "अन्तरजातीय विवाह": ["intercaste marriage"],
    "प्रेम विवाह": ["love marriage"],
    "अरेन्ज म्यारिज": ["arranged marriage"],
    "तलाक": ["divorce"],
    "सम्बन्ध विच्छेद": ["divorce", "separation", "dissolution"],
    "सम्बन्ध विच्छेदको मुद्दा": ["divorce case"],
    "विवाह विच्छेद": ["divorce", "dissolution of marriage"],
    "छुट्टिएको": ["separated", "estranged"],
    "पृथक बसाई": ["separate living", "separation"],
    "छोराछोरीको जिम्मा": ["custody of children", "child custody"],
    "बाल संरक्षण": ["child custody", "child protection"],
    "संरक्षण": ["custody", "protection", "guardianship"],
    "संरक्षक": ["guardian", "custodian"],
    "नाफा": ["alimony", "maintenance"],
    "भरणपोषण": ["alimony", "maintenance", "child support"],
    "भरण": ["maintenance", "support"],
    "गुजारा": ["maintenance", "livelihood", "subsistence"],
    "मुख्तियार": ["authorization", "power of attorney"],
    "लालनपालन": ["upbringing", "maintenance", "child rearing"],
    "तालाक": ["divorce"],
    "मुस्लिम तलाक": ["muslim divorce", "talaq"],
    "दहेज": ["dowry"],
    "दाइजो": ["dowry"],
    "दहेज मुद्दा": ["dowry case"],
    "घरेलु हिंसा": ["domestic violence"],
    "घरायसी हिंसा": ["domestic violence", "family violence"],
    "सम्बन्ध दर्ता": ["relationship registration"],

    # Family & Relationships
    "बुबा": ["father"],
    "पिता": ["father"],
    "बाबु": ["father"],
    "आमा": ["mother"],
    "भाइ": ["brother"],
    "दाइ": ["elder brother"],
    "बहिनी": ["sister"],
    "दिदी": ["elder sister"],
    "दाजु": ["elder brother"],
    "दाजुभाइ": ["brothers", "siblings"],
    "भाइबहिनी": ["siblings", "brothers and sisters"],
    "छोरा": ["son"],
    "छोरी": ["daughter"],
    "नाति": ["grandson"],
    "नातिनी": ["granddaughter"],
    "नाती": ["grandchild"],
    "सन्तान": ["children", "offspring", "descendants"],
    "परिवार": ["family"],
    "परिजन": ["family members", "relatives"],
    "आफन्त": ["relative", "kin", "family member"],
    "नातेदार": ["relative", "kinsman"],
    "नाता": ["relation", "kinship", "connection"],
    "श्रीमान": ["husband"],
    "श्रीमती": ["wife"],
    "पति": ["husband", "spouse"],
    "पत्नी": ["wife"],
    "बीवी": ["wife", "spouse"],
    "लोग्ने": ["husband"],
    "स्वास्नी": ["wife"],
    "जीवनसाथी": ["life partner", "spouse"],
    "ज्वाइँ": ["son in law"],
    "बुहारी": ["daughter in law"],
    "ससुरा": ["father in law"],
    "सासु": ["mother in law"],
    "हजुरबुबा": ["grandfather"],
    "हजुरआमा": ["grandmother"],
    "मामा": ["maternal uncle"],
    "माइजु": ["maternal aunt"],
    "फुपू": ["paternal aunt"],
    "काका": ["paternal uncle"],
    "भान्जा": ["nephew", "sisters son"],
    "भान्जी": ["niece", "sisters daughter"],
    "भतिजा": ["nephew", "brothers son"],
    "भतिजी": ["niece", "brothers daughter"],
    "जेठान": ["elder brothers wife"],
    "देवर": ["younger brother of husband"],
    "सालो": ["younger brother of wife"],
    "साली": ["younger sister of wife"],
    "कोइ": ["anyone", "someone"],
    "कोही": ["someone", "anybody"],

    # ──────────────────────────────────────────────────────────────────────
    # 8. DEATH & RELATED MATTERS
    # ──────────────────────────────────────────────────────────────────────
    "मृत्यु": ["death", "demise"],
    "मृत्यु भएको": ["deceased", "died"],
    "मृत्यु प्रमाणपत्र": ["death certificate"],
    "मरे": ["died", "dead"],
    "मरेको": ["dead", "died"],
    "मृतक": ["deceased", "dead person"],
    "मृतकको": ["of the deceased"],
    "मरण": ["death"],
    "गुम्नुभयो": ["died", "passed away", "deceased"],
    "गुमाए": ["lost", "bereaved"],
    "गुमाएको": ["lost", "deceased"],
    "बित्नुभयो": ["passed away", "died"],
    "बितेको": ["deceased", "late"],
    "मर्नु": ["to die"],
    "मृत्यु भएको व्यक्ति": ["deceased person"],
    "शव": ["dead body", "corpse"],
    "लाश": ["dead body", "corpse"],
    "मृत्युको कारण": ["cause of death"],
    "पोस्टमार्टम": ["autopsy", "postmortem"],
    "दाहसंस्कार": ["cremation", "funeral"],
    "अन्त्येष्टि": ["funeral", "last rites"],
    "कोरोनर": ["coroner"],

    # ──────────────────────────────────────────────────────────────────────
    # 9. DISPUTES & CONFLICT
    # ──────────────────────────────────────────────────────────────────────
    "झगडा": ["dispute", "fight", "quarrel"],
    "झैझगडा": ["dispute", "quarrel"],
    "विवाद": ["dispute", "conflict", "controversy"],
    "विवादको मुद्दा": ["dispute case"],
    "विवाद समाधान": ["dispute resolution"],
    "लडाइ": ["fight", "quarrel"],
    "लडाइ गर्नु": ["to fight", "quarreling"],
    "लफडा": ["dispute", "trouble", "quarrel"],
    "झैँ": ["like", "similar", "resembling"],
    "बिबाद": ["dispute", "conflict"],
    "बिबाद समाधान": ["dispute resolution"],

    # ──────────────────────────────────────────────────────────────────────
    # 10. LEGAL PROCEDURE & DOCUMENTS
    # ──────────────────────────────────────────────────────────────────────
    "कार्यविधि": ["procedure", "process"],
    "देवानी कार्यविधि": ["civil procedure"],
    "फौजदारी कार्यविधि": ["criminal procedure"],
    "प्रक्रिया": ["procedure", "process"],
    "दर्खास्त": ["application", "petition"],
    "निवेदन": ["petition", "application", "request"],
    "निवेदक": ["petitioner", "applicant"],
    "विपक्षी": ["opponent", "defendant", "respondent"],
    "वादी": ["plaintiff", "petitioner", "claimant"],
    "प्रतिवादी": ["defendant", "respondent"],
    "प्रतिवाद": ["defense", "response"],
    "मुद्दा दर्ता": ["case registration", "filing"],
    "पेशी": ["hearing date", "listing"],
    "पेशीको मिति": ["hearing date"],
    "सुनुवाइ": ["hearing", "trial"],
    "सुनुवाइको मिति": ["hearing date"],
    "बहस": ["argument", "pleading"],
    "बहस नोट": ["written argument", "brief"],
    "फैसला": ["judgment", "decision", "verdict"],
    "अन्तिम फैसला": ["final judgment"],
    "अन्तरिम आदेश": ["interim order"],
    "अन्तरिम फैसला": ["interim judgment"],
    "आदेश": ["order", "direction", "command"],
    "निर्णय": ["decision", "ruling", "verdict"],
    "निर्णयकर्ता": ["decision maker", "adjudicator"],
    "तामेली": ["service of notice", "delivery"],
    "तामेल गर्नु": ["to serve notice", "to deliver"],
    "म्याद": ["time limit", "deadline", "term"],
    "म्याद गुज्रिएको": ["expired", "time-barred"],
    "हदम्याद": ["statute of limitations", "limitation period"],
    "सीमाबध्द समय": ["limitation period"],
    "बयान": ["statement", "deposition", "confession"],
    "बयान गर्नु": ["to testify", "to make a statement"],
    "हाजिर हुनु": ["to appear in court"],
    "हाजिर": ["present", "in attendance"],
    "जरिवाना": ["fine", "penalty"],
    "क्षतिपूर्ति रकम": ["compensation amount"],
    "अन्तरिम राहत": ["interim relief"],
    "राहत": ["relief", "remedy", "redress"],
    "उपचार": ["remedy", "treatment"],
    "कानूनी उपचार": ["legal remedy"],
    "कानूनी सहायता": ["legal aid", "legal assistance"],
    "निःशुल्क कानूनी सहायता": ["free legal aid"],
    "मुलतबी": ["stay order", "suspended"],
    "रोक्का": ["attachment", "freeze", "seizure"],
    "रोक्का गर्नु": ["to attach", "to freeze", "to seize"],

    # ──────────────────────────────────────────────────────────────────────
    # 11. EMPLOYMENT & LABOR
    # ──────────────────────────────────────────────────────────────────────
    "रोजगार": ["employment", "job"],
    "रोजगारी": ["employment", "job"],
    "रोजगारदाता": ["employer"],
    "नोकरी": ["job", "employment", "work"],
    "नोकरी गर्नु": ["to work", "employed"],
    "नोकरी छोड्नु": ["to quit job", "resignation"],
    "नोकरीबाट हटाउनु": ["to fire", "to terminate", "dismiss"],
    "जागिर": ["job", "employment", "service"],
    "जागीर": ["job", "employment"],
    "जागिरे": ["employee", "salaried person"],
    "ज्याला": ["wages", "salary", "pay"],
    "ज्यालादारी": ["wage labor", "daily wages"],
    "तलब": ["salary", "wages"],
    "तनख्वाह": ["salary", "wages"],
    "भत्ता": ["allowance", "benefit"],
    "मजदूर": ["worker", "laborer"],
    "श्रम": ["labor", "labour"],
    "श्रमिक": ["worker", "laborer"],
    "श्रम कानून": ["labor law"],
    "श्रम अधिकार": ["labor rights"],
    "काम": ["work", "labor"],
    "कामदार": ["worker", "employee"],
    "कर्मचारी": ["employee", "staff"],
    "काम गर्नु": ["to work"],
    "कामको समय": ["working hours"],
    "ओभरटाइम": ["overtime"],
    "बिदा": ["leave", "holiday", "vacation"],
    "छुट्टी": ["leave", "holiday", "vacation"],
    "बिरामी बिदा": ["sick leave"],
    "मातृत्व बिदा": ["maternity leave"],
    "पितृत्व बिदा": ["paternity leave"],
    "सार्वजनिक बिदा": ["public holiday"],
    "सामाजिक सुरक्षा": ["social security"],
    "सामाजिक सुरक्षा कोष": ["social security fund"],
    "पेन्सन": ["pension", "retirement benefit"],
    "सञ्चय कोष": ["provident fund"],
    "ग्र्याचुअटी": ["gratuity"],
    "सेवा सुविधा": ["service benefits", "facilities"],
    "सेवा सम्झौता": ["service agreement", "employment contract"],
    "सेवा अवधि": ["service period", "tenure"],
    "हटाउनु": ["to fire", "to remove", "to dismiss"],
    "निकाल्नु": ["to fire", "to expel"],
    "निकाल्यो": ["to fire", "to expel", "fired"],
    "निकाले": ["to fire", "to expel", "fired"],
    "निकालिन्": ["to fire", "to expel", "fired"],
    "हटाउनु": ["to fire", "to remove", "to dismiss"],
    "हटायो": ["to fire", "to remove", "to dismiss", "fired"],
    "हटाए": ["to fire", "to remove", "to dismiss", "fired"],
    "हटाइन्": ["to fire", "to remove", "to dismiss", "fired"],
    "झगडा गर्यो": ["quarreled", "disputed"],
    "झगडा गरे": ["quarreled", "disputed"],
    "झगडा गर्दै": ["quarreling", "disputing"],
    "बिना": ["without", "no"],
    "बर्खास्त": ["dismissal", "termination"],
    "बर्खास्त गर्नु": ["to dismiss", "to terminate"],
    "राजीनामा": ["resignation", "sale deed"],
    "राजीनामा दिनु": ["to resign"],
    "हडताल": ["strike"],
    "तालाबन्दी": ["lockout"],
    "सामूहिक सम्झौता": ["collective bargaining agreement"],
    "ट्रेड युनियन": ["trade union"],
    "मध्यस्थता": ["mediation", "arbitration"],

    # ──────────────────────────────────────────────────────────────────────
    # 12. CONSUMER & BUSINESS
    # ──────────────────────────────────────────────────────────────────────
    "उपभोक्ता": ["consumer"],
    "उपभोक्ता अधिकार": ["consumer rights"],
    "उपभोक्ता संरक्षण": ["consumer protection"],
    "उपभोक्ता मञ्च": ["consumer forum"],
    "उपभोक्ता अदालत": ["consumer court"],
    "सामान": ["goods", "product", "item"],
    "सामानको गुणस्तर": ["product quality"],
    "दोषपूर्ण सामान": ["defective goods"],
    "मिसावट": ["adulteration", "contamination"],
    "म्याद गुज्रिएको": ["expired"],
    "रेफन्ड": ["refund"],
    "फिर्ता": ["refund", "return"],
    "पैसा फिर्ता": ["money back", "refund"],
    "बिल": ["bill", "invoice", "receipt"],
    "रसिद": ["receipt"],
    "वारेन्टी": ["warranty", "guarantee"],
    "ग्यारेन्टी": ["guarantee", "warranty"],
    "व्यवसाय": ["business", "occupation"],
    "व्यापार": ["business", "trade", "commerce"],
    "व्यापारिक": ["commercial", "business"],
    "व्यवसायी": ["businessperson", "trader"],
    "उद्योग": ["industry", "enterprise"],
    "उद्योगी": ["industrialist", "business owner"],
    "पसल": ["shop", "store"],
    "पसले": ["shopkeeper", "merchant"],
    "दर्ता": ["registration", "enrollment"],
    "फर्म": ["firm"],
    "कम्पनी": ["company", "corporation"],
    "साझेदारी फर्म": ["partnership firm"],
    "साझेदार": ["partner"],
    "एकल व्यवसाय": ["sole proprietorship"],
    "लाभ": ["profit", "gain"],
    "नोक्सान": ["loss", "damage"],
    "हानि": ["loss", "damage", "harm"],

    # ──────────────────────────────────────────────────────────────────────
    # 13. EDUCATION
    # ──────────────────────────────────────────────────────────────────────
    "शिक्षा": ["education"],
    "शैक्षिक": ["educational", "academic"],
    "विद्यालय": ["school"],
    "स्कुल": ["school"],
    "कलेज": ["college"],
    "विश्वविद्यालय": ["university"],
    "शिक्षक": ["teacher"],
    "विद्यार्थी": ["student"],
    "परीक्षा": ["exam", "examination"],
    "नतिजा": ["result"],
    "प्रमाणपत्र": ["certificate", "diploma"],
    "शैक्षिक योग्यता": ["educational qualification"],
    "छात्रवृत्ति": ["scholarship"],
    "भर्ना": ["admission", "enrollment"],
    "अनिवार्य शिक्षा": ["compulsory education"],
    "निःशुल्क शिक्षा": ["free education"],
    "शिक्षाको हक": ["right to education"],

    # ──────────────────────────────────────────────────────────────────────
    # 14. HEALTH & MEDICAL
    # ──────────────────────────────────────────────────────────────────────
    "स्वास्थ्य": ["health"],
    "स्वास्थ्य बीमा": ["health insurance"],
    "अस्पताल": ["hospital"],
    "डाक्टर": ["doctor", "physician"],
    "चिकित्सक": ["doctor", "physician"],
    "उपचार": ["treatment", "medical treatment"],
    "औषधि": ["medicine", "drug"],
    "औषधी": ["medicine", "medication"],
    "बिरामी": ["patient", "sick", "ill"],
    "रोग": ["disease", "illness"],
    "चिकित्सा सेवा": ["medical service", "healthcare"],
    "स्वास्थ्य सेवा": ["health service"],
    "चिकित्सा लापरवाही": ["medical negligence", "malpractice"],
    "चिकित्सा जाँच": ["medical examination"],
    "विकलांगता": ["disability", "handicap"],
    "अपाङ्गता": ["disability"],

    # ──────────────────────────────────────────────────────────────────────
    # 15. GOVERNMENT & ADMINISTRATION
    # ──────────────────────────────────────────────────────────────────────
    "सरकार": ["government", "state"],
    "सरकारी": ["government", "official", "public"],
    "निजी": ["private", "personal", "non-government"],
    "संघीय सरकार": ["federal government"],
    "प्रादेशिक सरकार": ["provincial government"],
    "स्थानीय सरकार": ["local government"],
    "गाउँपालिका": ["rural municipality"],
    "नगरपालिका": ["municipality"],
    "महानगरपालिका": ["metropolitan city"],
    "उपमहानगरपालिका": ["sub-metropolitan city"],
    "वडा": ["ward"],
    "सार्वजनिक": ["public"],
    "सार्वजनिक सेवा": ["public service"],
    "सूचना": ["information", "notice"],
    "सूचनाको हक": ["right to information"],
    "प्रशासन": ["administration"],
    "प्रशासकीय": ["administrative"],
    "अनुमति": ["permission", "authorization", "license"],
    "अनुमति पत्र": ["permit", "license"],
    "लाइसेन्स": ["license", "permit"],
    "राहदानी": ["passport"],
    "पासपोर्ट": ["passport"],
    "मतदाता": ["voter"],
    "मतदान": ["voting", "election"],
    "चुनाव": ["election"],
    "निर्वाचन": ["election"],
    "निर्वाचन आयोग": ["election commission"],
    "मतपत्र": ["ballot paper"],
    "उम्मेदवार": ["candidate"],
    "सांसद": ["member of parliament", "MP"],
    "सांसदहरू": ["members of parliament"],
    "प्रतिनिधि सभा": ["house of representatives"],
    "राष्ट्रिय सभा": ["national assembly"],
    "मन्त्री": ["minister"],
    "मन्त्रिपरिषद": ["council of ministers", "cabinet"],
    "प्रधानमन्त्री": ["prime minister"],
    "राष्ट्रपति": ["president"],
    "उपराष्ट्रपति": ["vice president"],
    "मुख्यमन्त्री": ["chief minister"],
    "प्रदेश": ["province", "state"],
    "प्रदेश सभा": ["provincial assembly"],
    "संसद": ["parliament"],
    "विधेयक": ["bill", "proposed law"],
    "ऐन": ["act", "statute", "law"],
    "कानून": ["law", "legal", "act"],
    "कानूनी": ["legal", "lawful", "judicial"],
    "गैरकानूनी": ["illegal", "unlawful"],
    "अध्यादेश": ["ordinance"],
    "नियम": ["rule", "regulation"],
    "नियमावली": ["rules", "regulations"],
    "कार्यविधि नियम": ["rules of procedure"],

    # ──────────────────────────────────────────────────────────────────────
    # 16. CONSTITUTIONAL BODIES & INSTITUTIONS
    # ──────────────────────────────────────────────────────────────────────
    "संविधान": ["constitution"],
    "संवैधानिक": ["constitutional"],
    "संविधान संशोधन": ["constitutional amendment"],
    "लोक सेवा आयोग": ["public service commission"],
    "निर्वाचन आयोग": ["election commission"],
    "महालेखापरीक्षक": ["auditor general", "comptroller"],
    "अख्तियार दुरुपयोग अनुसन्धान आयोग": ["commission for investigation of abuse of authority", "CIAA"],
    "अख्तियार": ["commission for investigation", "CIAA"],
    "मानव अधिकार आयोग": ["human rights commission"],
    "राष्ट्रिय मानव अधिकार आयोग": ["national human rights commission"],
    "राष्ट्रिय योजना आयोग": ["national planning commission"],
    "महिला आयोग": ["womens commission"],
    "दलित आयोग": ["dalit commission"],
    "आदिवासी जनजाती आयोग": ["indigenous commission"],
    "मधेसी आयोग": ["madhesi commission"],
    "थारु आयोग": ["tharu commission"],
    "मुस्लिम आयोग": ["muslim commission"],
    "प्रदेश लोक सेवा": ["provincial public service"],
    "बैंक": ["bank"],
    "वित्तीय": ["financial"],
    "कर": ["tax"],
    "कर कार्यालय": ["tax office"],
    "आयकर": ["income tax"],
    "भ्याट": ["VAT", "value added tax"],
    "भन्सार": ["customs", "customs duty"],

    # ──────────────────────────────────────────────────────────────────────
    # 17. RIGHTS & CITIZENSHIP
    # ──────────────────────────────────────────────────────────────────────
    "अधिकार": ["right", "authority", "power"],
    "अधिकारी": ["authority", "officer"],
    "अधिकारहरू": ["rights"],
    "नागरिक": ["citizen", "civic"],
    "नागरिकता": ["citizenship"],
    "नागरिकता प्रमाणपत्र": ["citizenship certificate"],
    "स्वतन्त्रता": ["freedom", "liberty", "independence"],
    "स्वतन्त्र": ["free", "independent"],
    "समानता": ["equality"],
    "समान": ["equal", "same"],
    "भेदभाव": ["discrimination"],
    "जातीय भेदभाव": ["caste discrimination", "racial discrimination"],
    "लिङ्गीय भेदभाव": ["gender discrimination"],
    "सुरक्षा": ["security", "safety", "protection"],
    "गरिबी": ["poverty"],
    "सामाजिक": ["social"],
    "राजनीतिक": ["political"],
    "आर्थिक": ["economic"],
    "सांस्कृतिक": ["cultural"],
    "सहुलियत": ["privilege", "concession", "facility"],

    # ──────────────────────────────────────────────────────────────────────
    # 18. CRIME & POLICE (additional)
    # ──────────────────────────────────────────────────────────────────────
    "फौजदारी": ["criminal"],
    "फौजदारी मुद्दा": ["criminal case"],
    "फौजदारी संहिता": ["criminal code"],
    "फौजदारी कानून": ["criminal law"],
    "लागूऔषध मुद्दा": ["narcotics case", "drug case"],
    "सवारी जरिवाना": ["traffic fine", "traffic ticket"],
    "ट्राफिक नियम": ["traffic rules"],
    "मादक पदार्थ सेवन": ["alcohol consumption", "drinking"],
    "सार्वजनिक मुद्दा": ["public interest case"],
    "मुलतबी": ["execution suspended", "stay"],
    "रिहा": ["release", "discharge", "set free"],
    "रिहाइ": ["release", "acquittal"],
    "सफाइ पाउनु": ["to be acquitted"],
    "दोषी ठहरिनु": ["to be convicted"],
    "दाखिल": ["deposit", "submission"],
    "दाखिल खारेज": ["admitted and dismissed"],
    "खारेज": ["dismissed", "cancelled", "void"],
    "जफत": ["confiscation", "seizure"],
    "जफत गर्नु": ["to confiscate", "to seize"],

    # ──────────────────────────────────────────────────────────────────────
    # 19. QUANTITY & MONEY
    # ──────────────────────────────────────────────────────────────────────
    "पैसा": ["money", "cash", "payment"],
    "रकम": ["amount", "sum", "money"],
    "मूल्य": ["price", "value", "cost"],
    "दर": ["rate"],
    "ब्याज": ["interest", "loan interest"],
    "कर्ज": ["loan", "debt"],
    "ऋण": ["debt", "loan"],
    "सापटी": ["loan", "borrowing"],
    "बचत": ["savings"],
    "लगानी": ["investment"],
    "रुपियाँ": ["rupees", "currency"],
    "रुपैयाँ": ["rupees", "currency"],
    "नोट": ["note", "currency note"],
    "सिक्का": ["coin"],
    "बजेट": ["budget"],
    "वार्षिक": ["annual", "yearly"],
    "मासिक": ["monthly"],
    "दैनिक": ["daily"],
    "हप्ता": ["week"],
    "महिना": ["month"],
    "वर्ष": ["year"],
    "आज": ["today"],
    "हिजो": ["yesterday"],
    "भोलि": ["tomorrow"],
    "पहिले": ["before", "ago", "previously"],
    "पछि": ["after", "later"],

    # ──────────────────────────────────────────────────────────────────────
    # 20. ACTIONS & VERBS (common)
    # ──────────────────────────────────────────────────────────────────────
    "गर्नु": ["to do", "to perform", "to make"],
    "गरेको": ["done", "did"],
    "गर्दै": ["doing"],
    "भएको": ["happened", "occurred", "been"],
    "भयो": ["happened", "occurred", "done"],
    "हुनु": ["to happen", "to be"],
    "दिनु": ["to give"],
    "दिएको": ["given"],
    "लिनु": ["to take"],
    "लिएको": ["taken"],
    "राख्नु": ["to keep", "to put"],
    "राखेको": ["kept", "put"],
    "हाल्नु": ["to put", "to insert"],
    "हालेको": ["put", "inserted"],
    "जानु": ["to go"],
    "गएको": ["went", "gone"],
    "आउनु": ["to come"],
    "आएको": ["came", "come"],
    "भन्नु": ["to say", "to tell"],
    "भनेको": ["said", "told"],
    "हेर्नु": ["to see", "to look"],
    "हेरेको": ["saw", "seen"],
    "चाहिनु": ["to need", "to be required"],
    "चाहियो": ["needed", "required"],
    "पाउनु": ["to get", "to receive", "to be allowed"],
    "पाएको": ["got", "received"],
    "सक्नु": ["can", "to be able"],
    "सकेको": ["could", "was able"],
    "थाहा": ["know", "knowledge", "information"],
    "थाहा पाउनु": ["to know", "to find out"],
    "जानकारी": ["information", "knowledge", "notice"],
    "सोध्नु": ["to ask", "to inquire"],
    "सोधेको": ["asked"],
    "बुझ्नु": ["to understand", "to comprehend"],
    "बुझेको": ["understood"],
    "माग्नु": ["to request", "to demand", "to beg"],
    "मागेको": ["requested", "demanded"],
    "खोज्नु": ["to search", "to seek", "to look for"],
    "खोजेको": ["searched", "looked for"],
    "पाउनु": ["to obtain", "to get"],
    "देखाउनु": ["to show"],
    "देखाएको": ["shown"],
    "लेख्नु": ["to write"],
    "लेखेको": ["written"],
    "पढ्नु": ["to read"],
    "पढेको": ["read"],
    "बेच्नु": ["to sell"],
    "बेचेको": ["sold"],
    "किन्नु": ["to buy"],
    "किनेको": ["bought"],
    "भर्नु": ["to fill"],
    "भरेको": ["filled"],
    "चढाउनु": ["to submit", "to file", "to offer"],
    "चढाएको": ["submitted", "filed"],
    "रोक्नु": ["to stop", "to prevent"],
    "रोकेको": ["stopped", "prevented"],
    "हटाउनु": ["to remove"],
    "हटाएको": ["removed"],
    "खोल्नु": ["to open"],
    "खोलेको": ["opened"],
    "बन्द गर्नु": ["to close"],
    "बन्द गरेको": ["closed"],

    # ──────────────────────────────────────────────────────────────────────
    # 21. PAST TENSE VERB CONJUGATIONS (3rd person)
    # ──────────────────────────────────────────────────────────────────────
    # Past 3sm = -यो, Past 3p = -ए, Past 3sf = -इन्
    # Present 3s = -छ, Present 3p = -छन्, Present continuous = -दैछ
    "गर्यो": ["did", "committed", "performed"],
    "गरे": ["did", "committed"],
    "गरिन्": ["did", "committed"],
    "गर्छ": ["does", "commits"],
    "गर्छन्": ["do", "commit"],
    "गर्दैछ": ["is doing", "is committing"],
    "गर्दैछन्": ["are doing", "are committing"],
    "गर्नुभयो": ["did", "done"],
    "भयो": ["happened", "occurred", "was"],
    "भए": ["happened", "occurred", "were"],
    "भइन्": ["happened", "occurred"],
    "हुन्छ": ["happens", "is", "occurs"],
    "हुन्छन्": ["happen", "are"],
    "दियो": ["gave", "granted"],
    "दिए": ["gave", "granted"],
    "दिइन्": ["gave", "granted"],
    "दिन्छ": ["gives", "grants"],
    "दिन्छन्": ["give", "grant"],
    "लियो": ["took"],
    "लिए": ["took"],
    "लिइन्": ["took"],
    "लिन्छ": ["takes"],
    "लिन्छन्": ["take"],
    "हाल्यो": ["put", "inserted"],
    "हाले": ["put", "inserted"],
    "हालिन्": ["put", "inserted"],
    "हाल्छ": ["puts", "inserts"],
    "हाल्छन्": ["put", "insert"],
    "राख्यो": ["kept", "put"],
    "राखे": ["kept", "put"],
    "राखिन्": ["kept", "put"],
    "राख्छ": ["keeps", "puts"],
    "राख्छन्": ["keep", "put"],
    "पायो": ["got", "received", "obtained"],
    "पाए": ["got", "received", "obtained"],
    "पाइन्": ["got", "received", "obtained"],
    "पाउँछ": ["gets", "receives"],
    "पाउँछन्": ["get", "receive"],
    "भन्यो": ["said", "told"],
    "भने": ["said", "told"],
    "भनिन्": ["said", "told"],
    "भन्छ": ["says", "tells"],
    "भन्छन्": ["say", "tell"],
    "माग्यो": ["demanded", "requested", "asked"],
    "मागे": ["demanded", "requested"],
    "मागिन्": ["demanded", "requested"],
    "माग्छ": ["demands", "requests"],
    "माग्छन्": ["demand", "request"],
    "खोस्यो": ["snatched", "took away", "seized"],
    "खोसे": ["snatched", "took away"],
    "खोसिन्": ["snatched", "took away"],
    "खोस्छ": ["snatches", "seizes"],
    "खोस्छन्": ["snatch", "seize"],
    "मार्यो": ["killed", "murdered"],
    "मारे": ["killed", "murdered"],
    "मारिन्": ["killed", "murdered"],
    "मार्छ": ["kills", "murders"],
    "मार्छन्": ["kill", "murder"],
    "कुट्यो": ["beat", "beat up"],
    "कुटे": ["beat", "beat up"],
    "कुटिन्": ["beat", "beat up"],
    "कुट्छ": ["beats"],
    "कुट्छन्": ["beat"],
    "गयो": ["went", "left"],
    "गए": ["went", "left"],
    "गइन्": ["went", "left"],
    "जान्छ": ["goes", "leaves"],
    "जान्छन्": ["go", "leave"],
    "आयो": ["came", "arrived"],
    "आए": ["came", "arrived"],
    "आइन्": ["came", "arrived"],
    "आउँछ": ["comes", "arrives"],
    "आउँछन्": ["come", "arrive"],
    "मर्यो": ["died"],
    "मरे": ["died"],
    "मरिन्": ["died"],
    "मर्छ": ["dies"],
    "मर्छन्": ["die"],
    "लेख्यो": ["wrote"],
    "लेखे": ["wrote"],
    "लेखिन्": ["wrote"],
    "लेख्छ": ["writes"],
    "लेख्छन्": ["write"],
    "बेच्यो": ["sold"],
    "बेचे": ["sold"],
    "बेचिन्": ["sold"],
    "बेच्छ": ["sells"],
    "बेच्छन्": ["sell"],
    "किन्यो": ["bought", "purchased"],
    "किने": ["bought", "purchased"],
    "किनिन्": ["bought", "purchased"],
    "किन्छ": ["buys"],
    "किन्छन्": ["buy"],
    "बाँड्यो": ["divided", "partitioned"],
    "बाँडे": ["divided", "partitioned"],
    "बाँडिन्": ["divided", "partitioned"],
    "बाँड्छ": ["divides"],
    "बाँड्छन्": ["divide"],
    "लड्यो": ["fought"],
    "लडे": ["fought"],
    "लडिन्": ["fought"],
    "लड्छ": ["fights"],
    "लड्छन्": ["fight"],
    "तोड्यो": ["broke", "broken"],
    "तोडे": ["broke", "broken"],
    "तोडिन्": ["broke", "broken"],
    "तोड्छ": ["breaks"],
    "तोड्छन्": ["break"],
    "गुमायो": ["lost"],
    "गुमाए": ["lost"],
    "गुमाइन्": ["lost"],
    "गुमाउँछ": ["loses"],
    "गुमाउँछन्": ["lose"],
    "रोक्यो": ["stopped", "prevented"],
    "रोके": ["stopped", "prevented"],
    "रोक्छ": ["stops", "prevents"],
    "रोक्छन्": ["stop", "prevent"],
    "फाले": ["threw away", "discarded"],
    "फाल्यो": ["threw away", "discarded"],
    "उठायो": ["picked up", "raised", "collected"],
    "उठाए": ["picked up", "raised"],
    "भर्यो": ["filled"],
    "भरे": ["filled"],

    # ──────────────────────────────────────────────────────────────────────
    # 22. HINDI WORDS (common in Devanagari queries)
    # ──────────────────────────────────────────────────────────────────────
    "मैं": ["I", "me"],
    "मुझे": ["me", "to me"],
    "मेरा": ["my", "mine"],
    "मेरी": ["my", "mine"],
    "मेरे": ["my", "mine"],
    "हम": ["we", "us"],
    "हमारा": ["our", "ours"],
    "हमारी": ["our", "ours"],
    "हमारे": ["our", "ours"],
    "तुम": ["you"],
    "तुम्हारा": ["your", "yours"],
    "तुम्हारी": ["your", "yours"],
    "तुम्हारे": ["your", "yours"],
    "उसने": ["he", "she", "he did", "she did"],
    "उन्होंने": ["they", "they did"],
    "उसका": ["his", "her", "its"],
    "उसकी": ["his", "her", "its"],
    "उसके": ["his", "her", "its"],
    "उनका": ["their", "theirs"],
    "उनकी": ["their", "theirs"],
    "उनके": ["their", "theirs"],
    "इस": ["this"],
    "उस": ["that"],
    "यह": ["this", "it"],
    "वह": ["that", "he", "she", "it"],
    "ये": ["these", "they"],
    "वे": ["those", "they"],
    "किया": ["did"],
    "की": ["did", "done", "of"],
    "किए": ["did", "done"],
    "दिया": ["gave"],
    "दी": ["gave"],
    "दिए": ["gave"],
    "लिया": ["took"],
    "ली": ["took"],
    "लिए": ["took", "taken", "for"],
    "हुआ": ["happened", "occurred"],
    "हुई": ["happened", "occurred"],
    "हुए": ["happened", "occurred"],
    "था": ["was"],
    "थी": ["was"],
    "थे": ["were"],
    "थीं": ["were"],
    "गया": ["went", "gone"],
    "गई": ["went", "gone"],
    "गए": ["went", "gone"],
    "सकता": ["can", "able to"],
    "सकती": ["can", "able to"],
    "सकते": ["can", "able to"],
    "चाहिए": ["should", "must", "needed"],
    "होगा": ["will be", "probably"],
    "होगी": ["will be"],
    "होंगे": ["will be"],
    "साथ": ["with", "together"],
    "बाद": ["after", "later"],
    "पहले": ["before", "earlier", "previously"],
    "दौरान": ["during", "while"],
    "बिना": ["without"],
    "तक": ["until", "till", "up to"],
    "द्वारा": ["by", "through"],
    "विरुद्ध": ["against"],
    "खिलाफ": ["against"],
    "अंदर": ["inside", "within"],
    "बाहर": ["outside"],
    "ऊपर": ["above", "on", "upon"],
    "नीचे": ["below", "under"],
    "पास": ["near", "nearby", "at"],
    "ने": ["", "by"],
    "से": ["from", "with", "by", "than"],
    "को": ["to", "for", "at"],
    "के लिए": ["for"],
    "के बारे में": ["about", "regarding"],
    "और": ["and", "more"],
    "या": ["or"],
    "लेकिन": ["but"],
    "इसलिए": ["therefore", "so"],
    "क्योंकि": ["because"],
    "अगर": ["if"],
    "तो": ["then", "so"],
    "जब": ["when"],
    "तब": ["then"],
    "कब": ["when"],
    "कहाँ": ["where"],
    "क्यों": ["why"],
    "कैसे": ["how"],
    "कितना": ["how much", "how many"],
    "कौन": ["who"],
    "क्या": ["what"],
    "कोई": ["someone", "anyone", "some"],
    "कुछ": ["something", "some"],
    "सब": ["all", "every"],
    "कोई भी": ["any", "anyone"],
    "बहुत": ["very", "much", "a lot"],
    "थोड़ा": ["little", "a bit", "few"],
    "अधिक": ["more", "excess", "extra"],
    "कम": ["less", "fewer"],
    "ही": ["only", "just"],
    "भी": ["also", "too", "as well"],
    "अभी": ["now", "just now"],
    "अब": ["now"],
    "फिर": ["again", "then"],
    "बस": ["enough", "just", "only"],

    # ──────────────────────────────────────────────────────────────────────
    # 23. TIME, PLACE & COMMON ADVERBS
    # ──────────────────────────────────────────────────────────────────────
    "यहाँ": ["here"],
    "त्यहाँ": ["there"],
    "कहाँ": ["where"],
    "अहिले": ["now", "currently"],
    "त्यसपछि": ["after that", "then"],
    "त्यसअघि": ["before that"],
    "यसपछि": ["after this"],
    "जतिबेला": ["when"],
    "जहिले": ["whenever"],
    "सधैं": ["always", "forever"],
    "कहिल्यै": ["never"],
    "प्राय": ["often", "usually"],
    "कहिलेकाही": ["sometimes"],
    "फेरि": ["again", "anew"],
    "अझै": ["still", "yet"],
    "पनि": ["also", "too", "as well"],
    "मात्र": ["only", "just"],
    "धेरै": ["many", "much", "a lot"],
    "थोरै": ["few", "little"],
    "सबै": ["all", "every"],
    "केही": ["some", "something"],
    "अरू": ["other", "others", "more"],
    "आउँदो": ["next", "coming"],
    "गएको": ["last", "previous"],
    "अर्को": ["another", "other"],
    "यो": ["this"],
    "त्यो": ["that"],
    "यी": ["these"],
    "ती": ["those"],
    "को": ["who", "whose", "of"],
    "के": ["what"],
    "किन": ["why"],
    "कसरी": ["how"],
    "कति": ["how much", "how many"],
    "कुन": ["which"],

    # ──────────────────────────────────────────────────────────────────────
    # 22. ONLINE / CYBER
    # ──────────────────────────────────────────────────────────────────────
    "इन्टरनेट": ["internet", "online"],
    "अनलाइन": ["online"],
    "वेबसाइट": ["website"],
    "सामाजिक सञ्जाल": ["social media", "social network"],
    "फेसबुक": ["facebook"],
    "इमेल": ["email"],
    "पासवर्ड": ["password"],
    "ह्याक": ["hack", "hacking", "cyber attack"],
    "ह्याकर": ["hacker"],
    "साइबर अपराध": ["cyber crime"],
    "साइबर सुरक्षा": ["cyber security"],
    "डाटा": ["data"],
    "गोपनीयता": ["privacy", "confidentiality"],
    "बैंक खाता": ["bank account"],
    "मोबाइल": ["mobile", "cell phone"],
    "फोन": ["phone", "telephone"],
    "एसएमएस": ["sms", "text message"],
    "कल": ["call", "phone call"],
    "धम्कीपूर्ण कल": ["threatening call"],
    "उत्पीडन": ["harassment"],

    # ──────────────────────────────────────────────────────────────────────
    # 23. ENVIRONMENT & LAND
    # ──────────────────────────────────────────────────────────────────────
    "पर्यावरण": ["environment"],
    "प्रदूषण": ["pollution"],
    "वायु प्रदूषण": ["air pollution"],
    "जल प्रदूषण": ["water pollution"],
    "ध्वनि प्रदूषण": ["noise pollution"],
    "फोहोर": ["garbage", "waste", "litter", "filth"],
    "वन": ["forest"],
    "जङ्गल": ["forest", "jungle"],
    "रुख": ["tree"],
    "नदी": ["river"],
    "खोला": ["stream", "rivulet"],
    "ताल": ["lake"],
    "पानी": ["water"],
    "जल": ["water"],
    "जमिन": ["land", "ground", "soil"],
    "माटो": ["soil", "earth"],
    "खानी": ["mine", "mineral"],

    # ──────────────────────────────────────────────────────────────────────
    # 24. AGRICULTURE
    # ──────────────────────────────────────────────────────────────────────
    "कृषि": ["agriculture", "farming"],
    "किसान": ["farmer"],
    "बाली": ["crop"],
    "गोरु": ["ox", "bullock"],
    "गाई": ["cow"],
    "भैसी": ["buffalo"],
    "बाख्रा": ["goat"],
    "खेती": ["farming", "cultivation"],
    "जोत्नु": ["to plow", "to till"],
    "सिँचाइ": ["irrigation"],
    "मल": ["fertilizer", "manure"],
    "विउ": ["seed"],
    "उत्पादन": ["production", "yield", "output"],
    "अन्न": ["grain", "food grain"],

    # ──────────────────────────────────────────────────────────────────────
    # 25. COMMON PRONOUNS & QUESTION WORDS
    # ──────────────────────────────────────────────────────────────────────
    "म": ["i", "me"],
    "मेरो": ["my", "mine"],
    "हामी": ["we", "us"],
    "हाम्रो": ["our", "ours"],
    "तिमी": ["you"],
    "तिम्रो": ["your", "yours"],
    "तपाईं": ["you", "your honor"],
    "तपाईंको": ["your", "yours"],
    "उसको": ["his", "her", "its"],
    "उनीहरूको": ["their", "theirs"],
    "उहाँको": ["his", "her", "your honor"],
    "सबैको": ["everyones"],
    "आफ्नो": ["own", "ones own"],
    "कसैको": ["someones", "anyones"],
    "कारण": ["reason", "cause", "because"],
    "कारणले": ["because of", "due to"],
    "तर": ["but", "however"],
    "र": ["and"],
    "वा": ["or"],
    "अथवा": ["or"],
    "किनकि": ["because"],
    "यदि": ["if"],
    "भने": ["if", "then", "said"],
    "तापनि": ["nevertheless", "even then"],

    # ──────────────────────────────────────────────────────────────────────
    # 26. NEGATION & CONFIRMATION
    # ──────────────────────────────────────────────────────────────────────
    "हो": ["yes", "is", "are", "correct"],
    "होइन": ["no", "not", "is not"],
    "छ": ["is", "are", "exists"],
    "छैन": ["is not", "does not exist", "none"],
    "थियो": ["was"],
    "थिएन": ["was not"],
    "हुनेछ": ["will be"],
    "हुँदैन": ["cannot", "will not happen", "impossible"],
    "नभएको": ["without", "lacking", "not having"],
    "मान्य": ["valid", "acceptable"],
    "अमान्य": ["invalid", "unacceptable"],
    "साच्चिकै": ["really", "truly", "indeed"],
    "सत्य": ["truth", "true", "real"],
    "झूट": ["lie", "false", "untruth"],
    "मिथ्या": ["false", "untrue"],
}

# Reverse map for English → Devanagari (useful for result highlighting)
ENGLISH_TO_DEVANAGARI: Dict[str, str] = {}
for dev_word, eng_words in DEVANAGARI_TO_ENGLISH.items():
    for eng in eng_words:
        if eng not in ENGLISH_TO_DEVANAGARI:
            ENGLISH_TO_DEVANAGARI[eng] = dev_word


# ── Nepali Inflection Handling ──────────────────────────────────────

# Common Nepali suffixes to strip for dictionary lookup (in order of length)
NEPALI_SUFFIXES = [
    "हरूबाट", "हरूले", "हरूमा", "हरूको", "हरूका", "हरूलाई",
    "बाट", "लाई", "ले", "मा", "को", "का", "की",
    "हरू", "ने", "से", "पर", "तक",
]

# Common Nepali noun inflections that change the word ending
# Maps inflected endings to base endings
NEPALI_INFLECTION_MAP = {
    "हरू": "",       # plural
    "हरुलाई": "हरू",  # plural + dative
    "हरूले": "हरू",  # plural + ergative
    "हरूमा": "हरू",  # plural + locative
    "हरूको": "हरू",  # plural + genitive
    "हरूका": "हरू",  # plural + genitive
    "हरूबाट": "हरू", # plural + ablative
    "मा": "",
    "ले": "",
    "को": "",
    "का": "",
    "की": "",
    "बाट": "",
    "लाई": "",
    "संग": "",
    "सँग": "",
}


# Verb tense suffixes mapping conjugated forms back to infinitive endings
# A single tense suffix can map to multiple infinitive endings (e.g., -नु vs -उनु)
# The stemmer tries each and keeps candidates found in the dictionary
NEPALI_VERB_TENSE_MAP: List[Tuple[str, str]] = [
    ("यो", "नु"),     # past 3sm → infinitive (निकाल्यो → निकाल्नु)
    ("यो", "उनु"),    # past 3sm → -उनु infinitive (हटायो → हटाउनु)
    ("ए", "नु"),      # past 3p → infinitive (निकाले → निकाल्नु)
    ("ए", "उनु"),     # past 3p → -उनु infinitive (हटाए → हटाउनु)
    ("इन्", "नु"),    # past 3sf → infinitive (निकालिन् → निकाल्नु)
    ("इन्", "उनु"),   # past 3sf → -उनु infinitive (हटाइन् → हटाउनु)
    ("छ", "नु"),      # present 3s → infinitive (निकाल्छ → निकाल्नु)
    ("छन्", "नु"),    # present 3p → infinitive (निकाल्छन् → निकाल्नु)
    ("छिन्", "नु"),   # present 3sf → infinitive
    ("छौ", "नु"),     # present 2p/1p → infinitive
]


def _stem_nepali_word(word: str) -> List[str]:
    """Strip common Nepali suffixes to find the base form for dictionary lookup.
    
    Returns the original word and possible base forms (with suffixes stripped).
    """
    candidates = [word]
    
    # Try stripping one suffix at a time
    for suffix in sorted(NEPALI_SUFFIXES, key=len, reverse=True):
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            base = word[: -len(suffix)]
            candidates.append(base)
    
    # Try common noun/adposition inflection forms
    for suffix, replacement in NEPALI_INFLECTION_MAP.items():
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            candidate = word[: -len(suffix)] + replacement
            if candidate != word:
                candidates.append(candidate)
    
    # Try verb tense → infinitive mapping
    # This lets conjugated verb forms (निकाल्यो → निकाल्नु) match dictionary entries
    for suffix, replacement in NEPALI_VERB_TENSE_MAP:
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            candidate = word[: -len(suffix)] + replacement
            if candidate not in candidates:
                candidates.append(candidate)
    
    return candidates


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


def _translate_devanagari(query: str) -> Tuple[str, str, List[str]]:
    """Translate Devanagari script query to English terms with inflection handling."""
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
    
    # Single word matches for unmatched words (with inflection)
    for i, word in enumerate(words):
        if i not in matched_positions:
            candidates = _stem_nepali_word(word)
            found = False
            for candidate in candidates:
                if candidate in DEVANAGARI_TO_ENGLISH:
                    translations = DEVANAGARI_TO_ENGLISH[candidate]
                    all_terms.extend(translations)
                    english_parts.extend(translations)
                    found = True
                    break
            if not found and len(word) > 2:
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
