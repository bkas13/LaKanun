"""Nepali/Hindi Legal Dictionary with Devanagari script support."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class LegalTerm:
    """A legal term with translations."""

    english: str
    nepali: str
    hindi: str
    definition_en: str = ""
    definition_ne: str = ""
    definition_hi: str = ""
    category: str = ""
    context: str = ""
    synonyms_en: List[str] = None
    synonyms_ne: List[str] = None
    synonyms_hi: List[str] = None

    def __post_init__(self):
        if self.synonyms_en is None:
            self.synonyms_en = []
        if self.synonyms_ne is None:
            self.synonyms_ne = []
        if self.synonyms_hi is None:
            self.synonyms_hi = []

    def to_dict(self) -> Dict:
        return {
            "english": self.english,
            "nepali": self.nepali,
            "hindi": self.hindi,
            "definition_en": self.definition_en,
            "definition_ne": self.definition_ne,
            "definition_hi": self.definition_hi,
            "category": self.category,
            "context": self.context,
            "synonyms_en": self.synonyms_en,
            "synonyms_ne": self.synonyms_ne,
            "synonyms_hi": self.synonyms_hi,
        }


class LegalDictionary:
    """Bilingual legal terminology system for Nepal and India."""

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.terms: Dict[str, LegalTerm] = {}
        self._load_builtin_terms()

    def _load_builtin_terms(self):
        """Load comprehensive built-in legal terms."""
        terms_data = [
            # Court Hierarchy
            LegalTerm("Supreme Court", "सर्वोच्च अदालत", "सर्वोच्च न्यायालय",
                "Highest court in the country", "देशको सबैभन्दा उच्च अदालत", "देश का सर्वोच्च न्यायालय",
                "court_hierarchy", "Apex judicial body",
                ["apex court", "top court"], ["सर्वोच्च अदालत"], ["सर्वोच्च न्यायालय"]),
            LegalTerm("High Court", "उच्च अदालत", "उच्च न्यायालय",
                "State/provincial level high court", "प्रदेश/प्रान्त स्तरको उच्च अदालत", "राज्य/प्रान्त स्तर का उच्च न्यायालय",
                "court_hierarchy", "Intermediate appellate court",
                ["provincial high court", "state high court"], ["उच्च अदालत"], ["उच्च न्यायालय"]),
            LegalTerm("District Court", "जिल्ला अदालत", "जिला न्यायालय",
                "First instance trial court", "पहिलो चरणको मुद्दा चलाउने अदालत", "पहले चरण का मुकदमा चलाने वाला न्यायालय",
                "court_hierarchy", "Trial court of original jurisdiction",
                ["trial court", "court of first instance"], ["जिल्ला अदालत"], ["जिला न्यायालय"]),
            LegalTerm("Appellate Court", "अपील अदालत", "अपीलीय न्यायालय",
                "Court that hears appeals", "अपील सुन्ने अदालत", "अपील सुनने वाला न्यायालय",
                "court_hierarchy", "Intermediate appellate review",
                ["court of appeals"], ["अपील अदालत"], ["अपीलीय न्यायालय"]),

            # Legal Procedures
            LegalTerm("Bail", "जमानत", "जमानत",
                "Temporary release from custody pending trial", "मुद्दा चल्दा क्यानिदबाट मुक्त गराउने प्रक्रिया", "मुकदमा चलते समय हिरासत से अस्थायी रिहाई",
                "procedure", "Pre-trial release mechanism",
                ["release on bail", "bail bond"], ["जमानत", "म्यादी जमानत"], ["जमानत", "जमानतनाम"]),
            LegalTerm("FIR (First Information Report)", "प्राथमिकी रिपोर्ट", "प्रथम सूचना रिपोर्ट (एफआईआर)",
                "Initial police report of a cognizable offense", "संज्ञानयोग्य अपराधको पहिलो पुलिस रिपोर्ट", "संज्ञेय अपराध की प्रारंभिक पुलिस रिपोर्ट",
                "procedure", "Triggers criminal investigation",
                ["police report", "complaint"], ["प्राथमिकी", "एफआईआर"], ["एफआईआर", "प्रथम सूचना रिपोर्ट"]),
            LegalTerm("Warrant", "वारन्ट", "वारंट",
                "Court order authorizing arrest/search", "गिरफ्तारी/तलाशीको अदालती आदेश", "गिरफ्तारी/तलाशी का लिए अदालती आदेश",
                "procedure", "Judicial authorization for law enforcement action",
                ["arrest warrant", "search warrant"], ["गिरफ्तारी वारन्ट", "तलाशी वारन्ट"], ["गिरफ्तारी वारंट", "तलाशी वारंट"]),
            LegalTerm("Appeal", "अपील", "अपील",
                "Request to higher court to review decision", "उच्च अदालतमा निर्णय पुनर्विचारको अनुरोध", "उच्च न्यायालय में निर्णय के पुनर्विचार का अनुरोध",
                "procedure", "Appellate review process",
                ["appeal filing", "appeal petition"], ["अपील दर्ता", "अपील मुद्दा"], ["अपील दाखिल", "अपील याचिका"]),
            LegalTerm("Summons", "हाजिर पर्चा", "समन्स/हाजिरी नोटिस",
                "Court order to appear", "अदालतमा हाजिर हुनको आदेश", "न्यायालय में हाजिर होने का आदेश",
                "procedure", "Compulsory appearance order",
                ["court summons", "appearance notice"], ["हाजिर पर्चा", "उपस्थिति आदेश"], ["समन्स", "हाजिरी नोटिस"]),
            LegalTerm("Affidavit", "शपथपत्र", "शपथपत्र/एफिडेविट",
                "Sworn written statement", "शपथपूर्वक लेखित बयान", "शपथपूर्वक लिखित बयान",
                "procedure", "Evidence in written form under oath",
                ["sworn statement", "declaration"], ["शपथपत्र", "घोषणापत्र"], ["शपथपत्र", "घोषणापत्र"]),
            LegalTerm("Injunction", "निषेधाज्ञा", "निषेधाज्ञा/इंजंक्शन",
                "Court order to do/refrain from act", "काम गर्न/नगर्नको अदालती आदेश", "कोई कार्य करने/न करने का अदालती आदेश",
                "procedure", "Equitable relief",
                ["stay order", "restraining order"], ["रोक आदेश", "निषेधाज्ञा"], ["रोक आदेश", "निषेधाज्ञा"]),

            # Property Law
            LegalTerm("Mortgage", "बन्धक/कर्जा", "बंधक/गिरवी",
                "Property as security for loan", "ऋणको सुरक्षाका लागि सम्पत्ति बन्धक राख्ने", "ऋण की सुरक्षा के लिए संपत्ति गिरवी रखना",
                "property", "Secured lending instrument",
                ["pledge", "hypothecation"], ["बन्धक", "कर्जा"], ["बंधक", "गिरवी"]),
            LegalTerm("Lease", "भाडा/लीज", "लीज/पट्टा",
                "Contract for property use", "सम्पत्ति प्रयोगको ठेका/सम्झौता", "संपत्ति उपयोग का लिए अनुबंध",
                "property", "Tenancy agreement",
                ["tenancy", "rent agreement"], ["भाडा ठेका", "लीज"], ["लीज", "किरायानामा"]),
            LegalTerm("Easement", "मार्गाधिकार/सुविधा", "सुखाधिकार/मार्गाधिकार",
                "Right to use another's land", "अर्काको जमिन प्रयोग गर्ने अधिकार", "दूसरे की जमीन उपयोग करने का अधिकार",
                "property", "Non-possessory interest in land",
                ["right of way"], ["मार्गाधिकार", "सार्वजनिक मार्ग"], ["मार्गाधिकार", "रास्ते का अधिकार"]),
            LegalTerm("Title Deed", "लालपुरजा/मालिकाना पत्र", "मालिकाना पत्र/टाइटल डीड",
                "Document proving ownership", "मालिकाना प्रमाण गर्ने दस्तावेज", "मालिकाना साबित करने वाला दस्तावेज",
                "property", "Ownership evidence",
                ["deed", "ownership document"], ["लालपुरजा", "मालिकाना कागजात"], ["मालिकाना पत्र", "स्वामित्व दस्तावेज"]),
            LegalTerm("Encumbrance", "भार/बाधा", "भार/प्रतिबन्ध",
                "Claim or liability on property", "सम्पत्तिमा कुनै दावा वा दायित्व", "संपत्ति पर कोई दावा या दायित्व",
                "property", "Burden on property title",
                ["lien", "charge"], ["बन्धक भार", "कर्ज भार"], ["बंधक भार", "प्रभार"]),

            # Family Law
            LegalTerm("Divorce", "विवाह विच्छेद", "तलाक/विवाह विच्छेद",
                "Legal dissolution of marriage", "विवाहको कानूनी समाप्ति", "विवाह का कानूनी विघटन",
                "family", "Marriage termination",
                ["dissolution of marriage"], ["विवाह विच्छेद", "सम्बन्ध विच्छेद"], ["तलाक", "विवाह विच्छेद"]),
            LegalTerm("Custody", "संरक्षण/अभिभावकत्व", "संरक्षण/अभिभावकत्व",
                "Legal responsibility for child", "बालबालिकाको कानूनी जिम्मेवारी", "बच्चे की कानूनी जिम्मेदारी",
                "family", "Child care and control",
                ["guardianship", "child custody"], ["बाल संरक्षण", "अभिभावकत्व"], ["बाल संरक्षण", "अभिभावकत्व"]),
            LegalTerm("Alimony", "भरणपोषण/गुजारा", "गुजारा भत्ता/निर्वाह व्यय",
                "Financial support after divorce", "विवाह विच्छेदपछि आर्थिक सहयोग", "तलाक के बाद आर्थिक सहायता",
                "family", "Spousal maintenance",
                ["maintenance", "spousal support"], ["भरणपोषण", "जीवन निर्वाह खर्च"], ["गुजारा भत्ता", "निर्वाह व्यय"]),
            LegalTerm("Adoption", "दत्तक ग्रहण", "गोद लेना/दत्तक ग्रहण",
                "Legal parent-child relationship creation", "कानूनी रूपमा अभिभावक-बालक सम्बन्ध बनाउने", "कानूनी रूप से माता-पिता-बच्चा सम्बन्ध बनाना",
                "family", "Legal parentage establishment",
                ["legal adoption"], ["दत्तक", "कानूनी वारिस"], ["गोद लेना", "दत्तक ग्रहण"]),
            LegalTerm("Marriage Registration", "विवाह दर्ता", "विवाह पंजीकरण",
                "Official recording of marriage", "विवाहको सरकारी दर्ता", "विवाह का आधिकारिक पंजीकरण",
                "family", "Legal marriage recognition",
                ["marriage certificate"], ["विवाह प्रमाणपत्र", "विवाह दर्ता"], ["विवाह प्रमाणपत्र", "विवाह पंजीकरण"]),

            # Criminal Law
            LegalTerm("Offense", "अपराध", "अपराध",
                "Act punishable by law", "कानुनले दण्डनीय बनाएको काम", "कानून द्वारा दंडनीय कार्य",
                "criminal", "Criminal act",
                ["crime", "violation"], ["अपराध", "कानुन उल्लंघन"], ["अपराध", "कानून उल्लंघन"]),
            LegalTerm("Penalty", "दण्ड/जुर्माना", "दण्ड/जुर्माना",
                "Punishment for offense", "अपराधको लागि दण्ड", "अपराध के लिए सजा",
                "criminal", "Legal sanction",
                ["punishment", "fine"], ["दण्ड", "सजा"], ["दण्ड", "सजा"]),
            LegalTerm("Imprisonment", "कैद/बन्दी", "कैद/कारावास",
                "Confinement in prison", "जेलमा राख्ने दण्ड", "जेल में रखने की सजा",
                "criminal", "Deprivation of liberty",
                ["incarceration", "jail"], ["कैद", "बन्दी"], ["कैद", "कारावास"]),
            LegalTerm("Cognizable Offense", "संज्ञानयोग्य अपराध", "संज्ञेय अपराध",
                "Police can arrest without warrant", "पुलिसले वारन्ट बिना गिरफ्तार गर्न सक्ने अपराध", "पुलिस बिना वारंट गिरफ्तार कर सकती है",
                "criminal", "Serious offense allowing warrantless arrest",
                ["serious offense"], ["संज्ञानयोग्य अपराध", "गम्भीर अपराध"], ["संज्ञेय अपराध", "गंभीर अपराध"]),
            LegalTerm("Non-Cognizable Offense", "असंज्ञानयोग्य अपराध", "असंज्ञेय अपराध",
                "Police need warrant to arrest", "पुलिसले वारन्ट लिएर मात्र गिरफ्तार गर्न सक्ने अपराध", "पुलिस को गिरफ्तार करने के लिए वारंट चाहिए",
                "criminal", "Minor offense requiring warrant",
                ["minor offense"], ["असंज्ञानयोग्य अपराध", "सामान्य अपराध"], ["असंज्ञेय अपराध", "सामान्य अपराध"]),
            LegalTerm("Bailable Offense", "जमानती अपराध", "जमानती अपराध",
                "Bail as a matter of right", "जमानत पाउने अधिकारभएको अपराध", "जमानत पाने का अधिकार वाला अपराध",
                "criminal", "Right to bail",
                ["bailable"], ["जमानती अपराध"], ["जमानती अपराध"]),
            LegalTerm("Non-Bailable Offense", "अजमानती अपराध", "अजमानती अपराध",
                "Bail at court discretion", "अदालतको विवेकमा जमानत दिने अपराध", "अदालत के विवेक पर जमानत देने वाला अपराध",
                "criminal", "Discretionary bail",
                ["non-bailable"], ["अजमानती अपराध"], ["अजमानती अपराध"]),

            # Constitutional Terms
            LegalTerm("Constitution", "संविधान", "संविधान",
                "Supreme law of the land", "देशको सर्वोच्च कानून", "देश का सर्वोच्च कानून",
                "constitutional", "Fundamental governing document",
                ["supreme law", "charter"], ["संविधान", "मूल कानून"], ["संविधान", "मूल कानून"]),
            LegalTerm("Amendment", "संशोधन", "संशोधन",
                "Formal change to constitution", "संविधानमा औपचारिक परिवर्तन", "संविधान में औपचारिक परिवर्तन",
                "constitutional", "Constitutional modification",
                ["constitutional amendment"], ["संविधान संशोधन"], ["संविधान संशोधन"]),
            LegalTerm("Writ", "रिट/परमादेश", "रिट/परमादेश",
                "Court order to government body", "सरकारी निकायलाई अदालती आदेश", "सरकारी निकाय को अदालती आदेश",
                "constitutional", "Constitutional remedy",
                ["habeas corpus", "mandamus", "certiorari"], ["बन्दी प्रत्यक्षीकरण", "परमादेश"], ["बंदी प्रत्यक्षीकरण", "परमादेश"]),
            LegalTerm("Ordinance", "अध्यादेश", "अध्यादेश",
                "Executive law when legislature not in session", "व्यवस्थापिका सत्र नभएको बेला कार्यपालिकाको कानून", "विधायिका सत्र न होने पर कार्यपालिका का कानून",
                "constitutional", "Temporary legislative power",
                ["executive order"], ["अध्यादेश", "कार्यपालिकाको आदेश"], ["अध्यादेश", "कार्यपालिका आदेश"]),
            LegalTerm("Fundamental Rights", "मौलिक अधिकार", "मौलिक अधिकार",
                "Basic human rights guaranteed by constitution", "संविधानले ग्यारेन्शी गरेको मौलिक मानव अधिकार", "संविधान द्वारा गारंटीकृत मूल मानव अधिकार",
                "constitutional", "Core constitutional protections",
                ["basic rights", "human rights"], ["मौलिक अधिकार", "मानव अधिकार"], ["मौलिक अधिकार", "मानव अधिकार"]),
            LegalTerm("Directive Principles", "निर्देशक सिद्धान्त", "निर्देशक सिद्धान्त",
                "Guidelines for state policy", "राज्य नीतिका लागि दिशानिर्देश", "राज्य नीति के लिए दिशानिर्देश",
                "constitutional", "Non-justiciable state obligations",
                ["state policy guidelines"], ["निर्देशक सिद्धान्त", "राज्य नीति"], ["निर्देशक सिद्धान्त", "राज्य नीति"]),

            # Nepal Specific Terms
            LegalTerm("Birta (Land Grant)", "बिर्ता", "बिर्ता",
                "Tax-free land grant by state", "राज्यद्वारा करमुक्त जमिन दान", "राज्य द्वारा करमुक्त जमीन अनुदान",
                "nepal_specific", "Historical land tenure system",
                ["land grant", "tax-free land"], ["बिर्ता", "करमुक्त जमिन"], ["बिर्ता", "करमुक्त जमीन"]),
            LegalTerm("Guthi (Trust Land)", "गुठी", "गुठी",
                "Religious/charitable trust land", "धार्मिक/परोपकारी ट्रस्टको जमिन", "धार्मिक/परोपकारी ट्रस्ट की जमीन",
                "nepal_specific", "Traditional trust property",
                ["trust land", "endowment"], ["गुठी", "धार्मिक सम्पत्ति"], ["गुठी", "धार्मिक संपत्ति"]),
            LegalTerm("Kipat (Communal Land)", "किपात", "किपात",
                "Communal land ownership system", "सामुदायिक जमिन मालिकत्व प्रणाली", "सामुदायिक भूमि स्वामित्व प्रणाली",
                "nepal_specific", "Indigenous land tenure (Limbu, Rai)",
                ["communal land", "tribal land"], ["किपात", "सामुदायिक जमिन"], ["किपात", "सामुदायिक जमीन"]),
            LegalTerm("Raikar (State Land)", "रैकर", "रैकर",
                "State-owned land with revenue rights", "राज्यको स्वामित्वका राजस्व अधिकारसहित जमिन", "राज्य स्वामित्व की राजस्व अधिकारों वाली जमीन",
                "nepal_specific", "Main land tenure category",
                ["state land", "crown land"], ["रैकर", "सरकारी जमिन"], ["रैकर", "सरकारी जमीन"]),
            LegalTerm("Muluki Ain (National Code)", "मुलुकी ऐन", "मुलुकी ऐन",
                "Unified civil/criminal code", "एकीकृत दीवानी/फौजदारी संहिता", "एकीकृत दीवानी/फौजदारी संहिता",
                "nepal_specific", "National legal code (1854, 2074)",
                ["national code", "civil code"], ["मुलुकी ऐन", "राष्ट्रिय संहिता"], ["मुलुकी ऐन", "राष्ट्रीय संहिता"]),
            LegalTerm("Muluki Dewani Samhita", "मुलुकी दीवानी संहिता", "मुलुकी दीवानी संहिता",
                "National Civil Code 2074", "राष्ट्रिय दीवानी संहिता २०७४", "राष्ट्रीय दीवानी संहिता २०७४",
                "nepal_specific", "Civil law codification",
                ["civil code 2074"], ["मुलुकी दीवानी संहिता २०७४"], ["मुलुकी दीवानी संहिता २०७४"]),
            LegalTerm("Muluki Faujdari Samhita", "मुलुकी फौजदारी संहिता", "मुलुकी फौजदारी संहिता",
                "National Penal Code 2074", "राष्ट्रिय फौजदारी संहिता २०७४", "राष्ट्रीय फौजदारी संहिता २०७४",
                "nepal_specific", "Criminal law codification",
                ["penal code 2074"], ["मुलुकी फौजदारी संहिता २०७४"], ["मुलुकी फौजदारी संहिता २०७४"]),

            # India Specific Terms
            LegalTerm("HUF (Hindu Undivided Family)", "हिन्दू अविभाजित परिवार", "हिन्दू अविभाजित परिवार (एचयूएफ)",
                "Joint Hindu family for tax/legal purposes", "कर/कानूनी प्रयोजनका लागि संयुक्त हिन्दू परिवार", "कर/कानूनी उद्देश्यों के लिए संयुक्त हिन्दू परिवार",
                "india_specific", "Tax entity and property holding",
                ["joint family", "coparcenary"], ["हिन्दू अविभाजित परिवार", "संयुक्त परिवार"], ["हिन्दू अविभाजित परिवार", "संयुक्त परिवार"]),
            LegalTerm("Panchayat", "पञ्चायत", "पंचायत",
                "Village local self-government", "गाउँस्तरीय स्थानीय स्वशासन", "ग्राम स्तरीय स्थानीय स्वशासन",
                "india_specific", "Grassroots democracy institution",
                ["village council", "local body"], ["पञ्चायत", "गाउँ सभा"], ["पंचायत", "ग्राम सभा"]),
            LegalTerm("Lok Sabha", "लोकसभा/प्रतिनिधि सभा", "लोक सभा",
                "Lower house of Parliament", "संसदको निम्न सदन", "संसद का निम्न सदन",
                "india_specific", "House of the People",
                ["lower house", "house of people"], ["लोकसभा", "प्रतिनिधि सभा"], ["लोक सभा", "जनता का सदन"]),
            LegalTerm("Rajya Sabha", "राज्यसभा/राष्ट्रिय सभा", "राज्य सभा",
                "Upper house of Parliament", "संसदको उच्च सदन", "संसद का उच्च सदन",
                "india_specific", "Council of States",
                ["upper house", "council of states"], ["राज्यसभा", "राष्ट्रिय सभा"], ["राज्य सभा", "राज्यों की परिषद"]),
            LegalTerm("President's Rule", "राष्ट्रपतिको शासन", "राष्ट्रपति शासन",
                "Central rule in state under Article 356", "अनुच्छेद ३५६ अन्तर्गत राज्मा केन्द्रको शासन", "अनुच्छेद ३५६ के तहत राज्य में केंद्र का शासन",
                "india_specific", "Emergency provision",
                ["state emergency", "article 356"], ["राष्ट्रपतिको शासन", "अनुच्छेद ३५६"], ["राष्ट्रपति शासन", "अनुच्छेद ३५६"]),
            LegalTerm("Ordinance Making Power", "अध्यादेश जारी गर्ने अधिकार", "अध्यादेश जारी करने की शक्ति",
                "Executive legislative power (Art 123/213)", "कार्यपालिकाको व्यवस्थापिका शक्ति (अनुच्छेद १२३/२१३)", "कार्यपालिका की विधायी शक्ति (अनुच्छेद १२३/२१३)",
                "india_specific", "Temporary law-making by executive",
                ["executive legislation"], ["अध्यादेश अधिकार", "कार्यपालिकाको कानून"], ["अध्यादेश शक्ति", "कार्यपालिका का कानून"]),

            # Additional Important Terms
            LegalTerm("Habeas Corpus", "बन्दी प्रत्यक्षीकरण", "बंदी प्रत्यक्षीकरण",
                "Writ to produce detained person", "बन्दी व्यक्तिलाई अदालतमा उपस्थित गर्ने परमादेश", "बंदी व्यक्ति को न्यायालय में पेश करने का आदेश",
                "constitutional", "Protection against illegal detention",
                ["writ of liberty"], ["बन्दी प्रत्यक्षीकरण", "स्वतन्त्रताको रिट"], ["बंदी प्रत्यक्षीकरण", "स्वतंत्रता का रिट"]),
            LegalTerm("Mandamus", "परमादेश", "परमादेश",
                "Writ compelling duty performance", "कर्तव्य पालना गर्न बाध्य गर्ने अदालती आदेश", "कर्तव्य पालन के लिए बाध्य करने का अदालती आदेश",
                "constitutional", "Command to perform legal duty",
                ["writ of command"], ["परमादेश", "कर्तव्य पालन आदेश"], ["परमादेश", "कर्तव्य पालन आदेश"]),
            LegalTerm("Certiorari", "सर्टियोरेरी/पुनर्विलोकन", "सर्टियोरेरी/पुनर्विलोकन",
                "Writ reviewing lower court decision", "निम्न अदालतको निर्णय पुनर्विलोकन गर्ने आदेश", "निचली अदालत के निर्णय की समीक्षा का आदेश",
                "constitutional", "Judicial review of quasi-judicial decisions",
                ["writ of review"], ["पुनर्विलोकन", "निर्णय समीक्षा"], ["पुनर्विलोकन", "निर्णय समीक्षा"]),
            LegalTerm("Prohibition", "प्रोहिबिशन/निषेध", "प्रोहिबिशन/निषेध",
                "Writ preventing excess jurisdiction", "अधिकारातिक्रम रोक्ने अदालती आदेश", "अधिकारातिक्रम रोकने का अदालती आदेश",
                "constitutional", "Prevents judicial overreach",
                ["writ of prohibition"], ["निषेधाज्ञा", "अधिकारातिक्रम रोक्ने"], ["निषेध", "अधिकारातिक्रम रोकने"]),
            LegalTerm("Quo Warranto", "क्वो वारेन्टो/अधिकार पृच्छा", "क्वो वारेन्टो/अधिकार पृच्छा",
                "Writ challenging right to office", "पद धारणको अधिकार चुनौती दिने रिट", "पद धारण के अधिकार को चुनौती देने वाली रिट",
                "constitutional", "Challenges unauthorized office holding",
                ["writ of right to office"], ["अधिकार पृच्छा", "पदाधिकार चुनौती"], ["अधिकार पृच्छा", "पदाधिकार चुनौती"]),
            LegalTerm("Public Interest Litigation (PIL)", "जनहित याचिका", "जनहित याचिका (पीआईएल)",
                "Litigation for public cause", "सार्वजनिक हितका लागि मुद्दा", "सार्वजनिक हित के लिए मुकदमा",
                "procedure", "Access to justice for marginalized",
                ["social action litigation"], ["जनहित याचिका", "सार्वजनिक हितको मुद्दा"], ["जनहित याचिका", "सार्वजनिक हित का मुकदमा"]),
            LegalTerm("Locus Standi", "लोकस स्टान्डी/मुद्दा लगाउने अधिकार", "लोकस स्टान्डी/मुकदमा करने का अधिकार",
                "Right to bring legal action", "कानूनी कार्यवाही सुरु गर्ने अधिकार", "कानूनी कार्यवाही शुरू करने का अधिकार",
                "procedure", "Standing to sue",
                ["standing", "right to sue"], ["मुद्दा लगाउने अधिकार", "खडा हुन पर्ने"], ["मुकदमा करने का अधिकार", "खड़ा होने का अधिकार"]),
            LegalTerm("Res Judicata", "रिज जुडिकाटा/निर्णीत विषय", "रिज जुडिकाटा/निर्णीत विषय",
                "Matter already judged", "पहिले नै निर्णय भएको विषय", "पहले ही निर्णीत विषय",
                "procedure", "Prevents re-litigation",
                ["claim preclusion", "issue preclusion"], ["निर्णीत विषय", "पहिले नै फैसला भएको"], ["निर्णीत विषय", "पहले ही फैसला हुआ"]),
            LegalTerm("Statute of Limitations", "कालबधि/मियाद", "कालबाधि/परिसीमा अवधि",
                "Time limit for legal action", "कानूनी कार्यवाहीका लागि समय सीमा", "कानूनी कार्यवाही के लिए समय सीमा",
                "procedure", "Prescription period",
                ["limitation period", "prescription"], ["मियाद", "कालबधि"], ["परिसीमा अवधि", "कालबाधि"]),
        ]

        for term in terms_data:
            self.terms[term.english.lower()] = term
            self.terms[term.nepali.lower()] = term
            self.terms[term.hindi.lower()] = term

        logger.info(f"Loaded {len(terms_data)} built-in legal terms")

    def search(self, query: str, target_lang: str = "ne") -> List[Dict]:
        """Search for legal term translations."""
        query_lower = query.lower().strip()
        results = []

        # Exact match
        if query_lower in self.terms:
            term = self.terms[query_lower]
            results.append(self._format_result(term, target_lang))

        # Partial matches
        for key, term in self.terms.items():
            if query_lower in key and term not in [r.get("english") for r in results]:
                if len(results) < 10:
                    results.append(self._format_result(term, target_lang))

        return results

    def _format_result(self, term: LegalTerm, target_lang: str) -> Dict:
        """Format term for API response."""
        result = {
            "english": term.english,
            "nepali": term.nepali,
            "hindi": term.hindi,
            "category": term.category,
        }

        if target_lang == "ne":
            result["translation"] = term.nepali
            result["definition"] = term.definition_ne or term.definition_en
        else:
            result["translation"] = term.hindi
            result["definition"] = term.definition_hi or term.definition_en

        if term.context:
            result["context"] = term.context

        return result

    def translate_term(self, term: str, target_lang: str = "ne") -> Optional[str]:
        """Translate a single legal term."""
        term_lower = term.lower().strip()
        if term_lower in self.terms:
            t = self.terms[term_lower]
            if target_lang == "ne":
                return t.nepali
            elif target_lang == "hi":
                return t.hindi
        return None

    def get_by_category(self, category: str) -> List[Dict]:
        """Get all terms in a category."""
        results = []
        for term in self.terms.values():
            if term.category == category:
                results.append(term.to_dict())
        return results

    def save_to_file(self, filepath: Path):
        """Save dictionary to JSON file."""
        data = {k: v.to_dict() for k, v in self.terms.items()}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved dictionary to {filepath}")

    def load_from_file(self, filepath: Path):
        """Load dictionary from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for key, value in data.items():
            term = LegalTerm(**value)
            self.terms[key] = term

        logger.info(f"Loaded {len(data)} terms from {filepath}")


# Global instance
_legal_dictionary = None


def get_legal_dictionary() -> LegalDictionary:
    """Get global legal dictionary instance."""
    global _legal_dictionary
    if _legal_dictionary is None:
        _legal_dictionary = LegalDictionary()
    return _legal_dictionary


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    d = LegalDictionary()

    # Test searches
    print("=== Bail ===")
    for r in d.search("bail", "ne"):
        print(f"  {r['english']} -> {r['nepali']}")

    print("\n=== Caste ===")
    for r in d.search("caste", "hi"):
        print(f"  {r['english']} -> {r['hindi']}")

    print("\n=== Nepal Specific ===")
    for r in d.search("birta", "ne"):
        print(f"  {r['english']} -> {r['nepali']}")

    print("\n=== India Specific ===")
    for r in d.search("huf", "hi"):
        print(f"  {r['english']} -> {r['hindi']}")

    # Save
    d.save_to_file(Path("data/legal_dictionary.json"))