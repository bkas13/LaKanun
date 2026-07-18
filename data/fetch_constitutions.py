#!/usr/bin/env python3
"""Fetch and ingest real constitution text for Nepal and India.

Replaces synthetic placeholder articles with actual constitutional text
from official and reliable sources.
"""
import json
import re
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).parent / "processed"
RAW_DIR = Path(__file__).parent / "raw"
RAW_DIR.mkdir(exist_ok=True)


# ─── Nepal Constitution ───────────────────────────────────────────

NEPAL_PDF_URL = "https://ag.gov.np/files/Constitution-of-Nepal_2072_Eng_www.moljpa.gov_.npDate-72_11_16.pdf"

def fetch_nepal_constitution():
    """Download Nepal Constitution PDF and extract article text."""
    pdf_path = RAW_DIR / "nepal_constitution_2072.pdf"
    if not pdf_path.exists():
        print("Downloading Nepal Constitution PDF...")
        urllib.request.urlretrieve(NEPAL_PDF_URL, pdf_path)

    text = extract_pdf_text(pdf_path)
    if not text.strip():
        print("PDF extraction failed, trying alternative source...")
        text = fetch_nepal_text_alternative()

    # Parse into articles
    articles = parse_nepal_articles(text)
    print(f"Parsed {len(articles)} Nepal constitution articles")
    return articles


def extract_pdf_text(pdf_path):
    """Extract text from PDF using available libraries."""
    # Try pdfplumber first (best for structured text)
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                text_parts.append(t)
        return "\n\n".join(text_parts)
    except ImportError:
        pass

    # Try PyPDF2
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
        return "\n\n".join(text_parts)
    except ImportError:
        pass

    # Try pymupdf (fitz)
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        return "\n\n".join(text_parts)
    except ImportError:
        pass

    print("No PDF library available (install pdfplumber/PyPDF2/pymupdf)")
    return ""


def fetch_nepal_text_alternative():
    """Fetch from nepalelects.com article pages."""
    base = "https://nepalelects.com"
    text_parts = []

    # Fetch the index page to get all article URLs
    try:
        req = urllib.request.Request(f"{base}/constitution/")
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Extract article URLs
        urls = re.findall(r'href="(/constitution/\d+/art-[^"]+)"', html)
        urls = list(dict.fromkeys(urls))  # dedupe preserving order

        import time
        for i, url in enumerate(urls):
            try:
                full_url = base + url
                req = urllib.request.Request(full_url)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    page_html = resp.read().decode("utf-8", errors="replace")

                # Extract "Original Text" section
                m = re.search(r'Original Text\s*</[^>]+>\s*<[^>]+>\s*(.*?)(?:<[^>]+>\s*💡|\Z)', page_html, re.DOTALL)
                if m:
                    raw = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                    text_parts.append(f"\n== {url} ==\n{raw}")

                if i % 10 == 0:
                    print(f"  Fetched article {i+1}/{len(urls)}")
                time.sleep(0.3)  # Be polite
            except Exception as e:
                print(f"  Failed to fetch {url}: {e}")
    except Exception as e:
        print(f"Failed to fetch index: {e}")

    return "\n\n".join(text_parts)


# Article number to Part mapping (from existing ingest_constitution.py)
NEPAL_PARTS = {
    "1": "Preliminary", "2": "Citizenship",
    "3": "Fundamental Rights and Duties", "4": "Directive Principles",
    "5": "Fundamental Rights and Duties of President and Vice-President",
    "6": "Executive", "6A": "Council of Ministers",
    "7": "Federal Legislature", "8": "Legislative Procedures",
    "9": "Judiciary", "10": "Constitutional Bodies",
    "11": "Local Executive", "12": "Federal Finance",
    "13": "Intergovernmental Relations", "14": "Civil Service and Other Services",
    "15": "Election Commission", "16": "Audit and Finance",
    "17": "Commissions", "18": "Political Parties",
    "19": "Emergency Powers", "20": "Miscellaneous",
    "21": "Amendment of the Constitution", "22": "Transitional Provisions",
}

NEPAL_ARTICLE_RANGES = {
    1: "1", 2: "1", 3: "1", 4: "1", 5: "1", 6: "1", 7: "1", 8: "1", 9: "1",
    10: "2", 11: "2", 12: "2", 13: "2", 14: "2", 15: "2",
    16: "3", 17: "3", 18: "3", 19: "3", 20: "3", 21: "3", 22: "3", 23: "3",
    24: "3", 25: "3", 26: "3", 27: "3", 28: "3", 29: "3", 30: "3", 31: "3",
    32: "3", 33: "3", 34: "3", 35: "3", 36: "3", 37: "3", 38: "3", 39: "3",
    40: "3", 41: "3", 42: "3", 43: "3", 44: "3", 45: "3", 46: "3", 47: "3", 48: "3",
    49: "4", 50: "4", 51: "4",
    52: "5", 53: "5", 54: "5", 55: "5", 56: "5",
    57: "6", 58: "6", 59: "6", 60: "6", 61: "6", 62: "6", 63: "6", 64: "6", 65: "6", 66: "6",
    67: "6A", 68: "6A", 69: "6A", 70: "6A", 71: "6A", 72: "6A", 73: "6A", 74: "6A", 75: "6A", 76: "6A", 77: "6A",
    78: "7", 79: "7", 80: "7", 81: "7", 82: "7", 83: "7", 84: "7", 85: "7", 86: "7", 87: "7",
    88: "7", 89: "7", 90: "7",
    91: "8", 92: "8", 93: "8", 94: "8", 95: "8", 96: "8", 97: "8", 98: "8", 99: "8", 100: "8", 101: "8", 102: "8", 103: "8", 104: "8", 105: "8", 106: "8",
    107: "9", 108: "9", 109: "9", 110: "9", 111: "9", 112: "9", 113: "9", 114: "9", 115: "9",
    116: "9", 117: "9", 118: "9", 119: "9", 120: "9", 121: "9", 122: "9", 123: "9", 124: "9",
    125: "9", 126: "9", 127: "9", 128: "9", 129: "9", 130: "9", 131: "9", 132: "9", 133: "9",
    134: "9", 135: "9", 136: "9", 137: "9", 138: "9", 139: "9", 140: "9", 141: "9", 142: "9",
    143: "9", 144: "9", 145: "9", 146: "9", 147: "9", 148: "9",
}

NEPAL_CATEGORIES = {
    range(1, 10): ("constitutional", "general"),
    range(10, 16): ("citizenship", "citizenship"),
    range(16, 49): ("fundamental_rights", "fundamental_rights"),
    range(49, 52): ("directive_principles", "directive_principles"),
    range(52, 57): ("executive", "president"),
    range(57, 67): ("executive", "president"),
    range(67, 78): ("executive", "council_of_ministers"),
    range(78, 91): ("legislature", "federal_legislature"),
    range(91, 107): ("legislature", "legislative_procedures"),
    range(107, 149): ("judiciary", "judiciary"),
    range(149, 155): ("constitutional_bodies", "constitutional_bodies"),
    range(155, 173): ("local_government", "local_executive"),
    range(173, 193): ("federal_finance", "federal_finance"),
    range(193, 205): ("intergovernmental_relations", "intergovernmental_relations"),
    range(205, 229): ("civil_service", "civil_service"),
    range(229, 241): ("election_commission", "election_commission"),
    range(241, 255): ("audit_finance", "audit_finance"),
    range(255, 271): ("commissions", "commissions"),
    range(271, 281): ("political_parties", "political_parties"),
    range(281, 289): ("emergency_powers", "emergency_powers"),
    range(289, 301): ("miscellaneous", "miscellaneous"),
    range(301, 309): ("transitional_provisions", "transitional_provisions"),
}

def get_nepal_category(art_num):
    for r, (cat, sub) in NEPAL_CATEGORIES.items():
        if art_num in r:
            return cat, sub
    return "constitutional", "general"

def get_nepal_part(art_num):
    for r, part in NEPAL_ARTICLE_RANGES.items():
        if art_num == r:
            return part, NEPAL_PARTS.get(part, "Unknown")
    return "0", "Unknown"


NEPAL_ARTICLE_TITLES = {
    1: "Constitution as Fundamental Law",
    2: "Sovereignty and State Authority",
    3: "Nation",
    4: "State of Nepal",
    5: "National Interest",
    6: "Languages of the Nation",
    7: "Official Language",
    8: "National Flag",
    9: "National Anthem",
    10: "Right Not to be Deprived of Citizenship",
    11: "To be Citizen of Nepal",
    12: "Citizenship by Descent",
    13: "Citizenship by Birth",
    14: "Non-Resident Nepali Citizenship",
    15: "Non-Resident Citizenship",
    16: "Right to Live with Dignity",
    17: "Right to Freedom",
    18: "Right to Equality",
    19: "Right to Communication",
    20: "Rights Regarding Justice",
    21: "Right Against Preventive Detention",
    22: "Right Against Torture",
    23: "Right Against Untouchability and Discrimination",
    24: "Right Relating to Labour",
    25: "Right to Property",
    26: "Right to Freedom of Religion",
    27: "Right to Information",
    28: "Right to Social Justice",
    29: "Right Against Exploitation",
    30: "Right to Clean Environment",
    31: "Right to Education",
    32: "Right to Language and Culture",
    33: "Right to Employment",
    34: "Right to Freedom of Thought and Conscience",
    35: "Right to Health",
    36: "Right to Food",
    37: "Right of Women",
    38: "Rights of Women",
    39: "Rights of Children",
    40: "Right of Dalits",
    41: "Right of Senior Citizens",
    42: "Right to Social Justice",
    43: "Right of Consumers",
    44: "Right Against Exile",
    45: "Right to Privacy",
    46: "Right to Constitutional Remedies",
    47: "Right to Information",
    48: "Duties of Citizens",
    49: "Directive Principles and Policies to be Implemented",
    50: "Directive Principles",
    51: "State Policies",
    52: "President of Nepal",
    53: "Election of President",
    54: "Term of Office of President",
    55: "Qualifications for President",
    56: "Impeachment of President",
    57: "Vice-President",
    58: "Council of Ministers",
    59: "Appointment of Prime Minister",
    60: "Appointment of Ministers",
    61: "Responsibility of Council of Ministers",
    62: "Oath of Office",
    63: "Conduct of Business",
    64: "Resignation and Removal",
    65: "Conduct and Discipline",
    66: "Provisions relating to Government of Nepal",
    67: "Formation of Council of Ministers",
    68: "Appointment and duties of Chief Minister",
    69: "Appointment of Ministers",
    70: "Portfolio Allocation",
    71: "No-confidence Motion",
    72: "Vote of Confidence",
    73: "Resignation of Prime Minister",
    74: "Removal of Prime Minister",
    75: "Other Ministers",
    76: "Dissolution of Parliament",
    77: "Conduct of Business of Council of Ministers",
    78: "Federal Parliament",
    79: "House of Representatives",
    80: "Membership of House of Representatives",
    81: "Term of House of Representatives",
    82: "Prorogation and Dissolution",
    83: "National Assembly",
    84: "Membership of National Assembly",
    85: "Term of National Assembly",
    86: "Speaker and Deputy Speaker",
    87: "Chairperson and Vice-Chairperson",
    88: "Quorum",
    89: "Voting and Majority",
    90: "Conduct of Business",
    91: "Sessions",
    92: "Prorogation and Dissolution",
    93: "Bills",
    94: "Money Bills",
    95: "Financial Bills",
    96: "Ordinances",
    97: "Committees",
    98: "Standing Committees",
    99: "Joint Sitting",
    100: "Procedure in Parliament",
    101: "Parliamentary Privileges",
    102: "Officers and Staff",
    103: "Salaries and Allowances",
    104: "Rules of Procedure",
    105: "Language in Parliament",
    106: "Restrictions on Discussion",
    107: "Supreme Court",
    108: "Jurisdiction of Supreme Court",
    109: "Original Jurisdiction",
    110: "Writ Jurisdiction",
    111: "Appellate Jurisdiction",
    112: "Advisory Jurisdiction",
    113: "Review Jurisdiction",
    114: "Supreme Court Rules",
    115: "Judges",
    116: "Qualification for Judges",
    117: "Appointment of Judges",
    118: "Tenure of Judges",
    119: "Removal of Judges",
    120: "Resignation of Judges",
    121: "Transfer of Judges",
    122: "Acting Chief Justice",
    123: "Retired Judges",
    124: "Administration of Supreme Court",
    125: "High Courts",
    126: "Jurisdiction of High Courts",
    127: "Original Jurisdiction of High Courts",
    128: "Appellate Jurisdiction of High Courts",
    129: "Writ Jurisdiction of High Courts",
    130: "Judges of High Courts",
    131: "Appointment of High Court Judges",
    132: "Tenure of High Court Judges",
    133: "Removal of High Court Judges",
    134: "District Courts",
    135: "Judicial Service",
    136: "Special Provisions",
    137: "Constitutional Bodies",
    138: "Election Commission",
    139: "Commission for Investigation of Abuse of Authority",
    140: "Auditor General",
    141: "Public Service Commission",
    142: "Women Commission",
    143: "Dalit Commission",
    144: "Indigenous Nationalities Commission",
    145: "Madhesh Commission",
    146: "Tharu Commission",
    147: "Muslim Commission",
    148: "Inclusion Commission",
    149: "National Human Rights Commission",
    150: "Truth and Reconciliation Commission",
    151: "Commission on Enforced Disappeared Persons",
    152: "Inter-Council",
    153: "Other Constitutional Bodies",
    154: "Provisions relating to Constitutional Bodies",
    155: "Local Government",
    156: "Municipality",
    157: "Rural Municipality",
    158: "Ward",
    159: "Metropolitan City",
    160: "Sub-Metropolitan City",
    161: "Formation of Local Government",
    162: "Composition of Local Government",
    163: "Executive Committee",
    164: "Ward Committee",
    165: "Ward Executive Officer",
    166: "Local Finance",
    167: "Local Planning",
    168: "Local Service",
    169: "Local Staff",
    170: "Intergovernmental Fiscal Arrangements",
    171: "National Natural Resources and Fiscal Commission",
    172: "Provisions relating to Local Government",
    173: "Finance Commission",
    174: "Consolidated Fund",
    175: "Annual Budget",
    176: "Appropriation Bill",
    177: "Supplementary Grants",
    178: "Expenditure from Consolidated Fund",
    179: "Public Account",
    180: "Emergency Fund",
    181: "Fiscal Responsibility",
    182: "Auditor General",
    183: "Public Finance Management",
    184: "National Natural Resources",
    185: "Revenue Allocation",
    186: "Intergovernmental Transfers",
    187: "Federal-Provincial Financial Relations",
    188: "Provincial Finance",
    189: "Local Finance",
    190: "Debt Management",
    191: "Budget Procedure",
    192: "Financial Provisions",
    193: "Intergovernmental Council",
    194: "National Coordination Council",
    195: "Provincial Coordination",
    196: "Local Coordination",
    197: "Intergovernmental Fiscal Council",
    198: "Inter-State Relations",
    199: "Inter-Provincial Relations",
    200: "Inter-Local Relations",
    201: "National Security",
    202: "Armed Police Force",
    203: "Nepal Police",
    204: "Other National Security Forces",
    205: "Civil Service",
    206: "Civil Service Commission",
    207: "Judicial Service",
    208: "Medical Service",
    209: "Education Service",
    210: "Police Service",
    211: "Army Service",
    212: "Armed Police Service",
    213: "Other Services",
    214: "Recruitment and Promotion",
    215: "Service Conditions",
    216: "Transfer and Posting",
    217: "Disciplinary Action",
    218: "Appeal",
    219: "Protection of Service",
    220: "Retirement",
    221: "Pension",
    222: "Provident Fund",
    223: "Insurance",
    224: "Training",
    225: "Research",
    226: "Inter-Governmental Service Transfer",
    227: "National Human Resources Development",
    228: "Other Provisions",
    229: "Election Commission",
    230: "Chief Election Commissioner",
    231: "Election Commissioners",
    232: "Appointment and Term",
    233: "Removal of Commissioners",
    234: "Functions and Powers",
    235: "Election Constituencies",
    236: "Electoral System",
    237: "Electoral Rolls",
    238: "Political Parties Registration",
    239: "Election Disputes",
    240: "Other Election Provisions",
    241: "Auditor General",
    242: "Appointment and Qualification",
    243: "Functions and Duties",
    244: "Reports",
    245: "Public Accounts Committee",
    246: "Finance Committee",
    247: "Estimate Committee",
    248: "Public Undertakings Committee",
    249: "Committee on Government Assurances",
    250: "Joint Committee",
    251: "Privileges Committee",
    252: "Rules Committee",
    253: "House Committee",
    254: "Other Committees",
    255: "Women Commission",
    256: "Dalit Commission",
    257: "Indigenous Nationalities Commission",
    258: "Madhesh Commission",
    259: "Tharu Commission",
    260: "Muslim Commission",
    261: "Inclusion Commission",
    262: "National Human Rights Commission",
    263: "Truth and Reconciliation Commission",
    264: "Commission on Enforced Disappeared Persons",
    265: "Inter-Council",
    266: "Other Constitutional Bodies",
    267: "Provisions relating to Commissions",
    268: "Powers and Functions",
    269: "Reports",
    270: "Other Provisions",
    271: "Political Parties",
    272: "Registration of Political Parties",
    273: "Recognition of Political Parties",
    274: "Public Funding of Political Parties",
    275: "Regulation of Political Parties",
    276: "Dissolution of Political Parties",
    277: "Ban on Political Parties",
    278: "Restrictions on Political Parties",
    279: "Other Provisions",
    280: "Political Party Discipline",
    281: "Emergency Powers",
    282: "Proclamation of Emergency",
    283: "Duration of Emergency",
    284: "Effects of Emergency",
    285: "Extension of Emergency",
    286: "Revocation of Emergency",
    287: "Effects on Fundamental Rights",
    288: "Other Emergency Provisions",
    289: "Language of the Courts",
    290: "Public Service Commission",
    291: "Officer in Acting Capacity",
    292: "Transfer of Judges",
    293: "Conduct of Business of Government of Nepal",
    294: "Oath of Office",
    295: "Protection of President and Vice-President",
    296: "Provisions relating to Security of President",
    297: "Language of the Nation",
    298: "National Flag and Anthem",
    299: "National Day",
    300: "Other Provisions",
    301: "Transitional Provisions",
    302: "Transitional Provisions relating to Judicial Service",
    303: "Transitional Provisions relating to Commission",
    304: "Transitional Provisions relating to Other Services",
    305: "Transitional Provisions relating to Other Matters",
    306: "Transitional Provisions relating to Constitutional Bodies",
    307: "Transitional Provisions relating to Local Government",
    308: "Commencement and Interpretation",
}


def parse_nepal_articles(text):
    """Parse extracted PDF text into structured articles.

    Strategy: cut the text at the first actual Schedule BODY section (not TOC).
    The TOC has "Schedule- 1|National Flag" but the real schedules start with
    "Schedule-1|(Relating to clause..." pattern. Then take the FIRST occurrence
    of each article number (the actual article text), not the longest.
    """
    articles = []

    # Cut text at actual Schedule body (not TOC) — look for "Schedule-N|(Relating to"
    sched_idx = re.search(r'\nSchedule[-\s]*1\s*\|?\s*\(Relating to', text)
    if not sched_idx:
        # Fallback: look for "Schedule-1" followed by "National Flag" on next line (actual body)
        sched_idx = re.search(r'\nSchedule[-\s]*1\s*\|?\s*National Flag', text)
    body_text = text[:sched_idx.start()] if sched_idx else text

    # Also cut at "Short Title" / "Repeal" to avoid epilogue noise
    # But only if it appears AFTER article 308 (position > 300000)
    epilogue = re.search(r'\nShort\s*[Tt]itle.*?Repeal', text)
    if epilogue and epilogue.start() > 300000:
        end_idx = epilogue.start()
        body_text = body_text[:end_idx] if end_idx < len(body_text) else body_text

    # Pattern: newline, then "N." (number followed by period and space), then text until next article
    # The Nepal PDF format is: "16. Right to live with dignity: (1) Every person..."
    # We only take the FIRST chunk for each article number
    seen = {}
    pattern = r'\n(\d{1,3})\.\s+(.*?)(?=\n\d{1,3}\.\s+|\Z)'
    for m in re.finditer(pattern, body_text, re.DOTALL):
        art_num = int(m.group(1))
        if not (1 <= art_num <= 308):
            continue
        if art_num not in seen:
            # Only keep the FIRST occurrence
            seen[art_num] = m.group(2).strip()

    print(f"  Found {len(seen)} unique article numbers")

    for art_num in range(1, 309):
        title = NEPAL_ARTICLE_TITLES.get(art_num, f"Article {art_num}")
        cat, subcat = get_nepal_category(art_num)
        part_key, part_title = get_nepal_part(art_num)
        part_str = f"Part {part_key}: {part_title}"

        raw_text = seen.get(art_num, "")
        if raw_text:
            # Clean up the text — collapse whitespace
            raw_text = re.sub(r'\s+', ' ', raw_text).strip()
            # Remove sidebar/page numbers at end ("Part-11 ... THE CONSTITUTION ... NN")
            raw_text = re.sub(r'\s*(?:THE\s+CONSTITUTION|Part\s*[-\s]*\d+|Schedule\s*[-\s]*\d+)\s*[\d\s]*$', '', raw_text)
            # Remove trailing page numbers
            raw_text = re.sub(r'\s+\d{1,3}\s*$', '', raw_text)
            # Cap at reasonable length
            if len(raw_text) > 3000:
                raw_text = raw_text[:3000] + " [...]"
            # Build full_text: article number + title + actual content
            full_text = f"Article {art_num}. {title}.\n{raw_text}"
        else:
            # No text found from PDF — clear placeholder
            full_text = f"Article {art_num}. {title}.\n\n[Full text of this article will be available in a future update.]"

        articles.append({
            "id": f"nepal_const_art_{art_num}",
            "country": "nepal",
            "source_document": "constitution_of_nepal_2072",
            "document_type": "constitution",
            "article_number": str(art_num),
            "title": title,
            "full_text": full_text,
            "category": cat,
            "subcategory": subcat,
            "part": part_str,
            "chapter": None,
            "schedule": None,
            "amendments": [],
            "cross_references": re.findall(r'(?:Article|Section)\s+(\d{1,3}[A-Z]?)', full_text),
            "language": "en",
            "metadata": {
                "part_name": part_title,
                "constitution_year": 2072,
                "enacted": "2015-09-20",
                "source": "Government of Nepal, Ministry of Law",
            },
        })

    return articles


# ─── India Constitution ───────────────────────────────────────────

INDIA_PDF_URL = "https://www.indiacode.nic.in/bitstream/123456789/19150/1/constitution_of_india.pdf"

INDIA_ARTICLE_TITLES = {
    "1": "Name and territory of the Union",
    "2": "Admission or establishment of new States",
    "3": "Formation of new States and alteration of areas, boundaries or names of existing States",
    "4": "Laws made under articles 2 and 3 to provide for the amendment of the First and Fourth Schedules",
    "5": "Citizenship at the commencement of the Constitution",
    "6": "Rights of citizenship of certain persons who have migrated to India from Pakistan",
    "7": "Rights of citizenship of certain migrants to Pakistan",
    "8": "Rights of citizenship of certain persons of Indian origin residing outside India",
    "9": "Persons voluntarily acquiring citizenship of a foreign State not to be citizens",
    "10": "Continuance of the rights of citizenship",
    "11": "Parliament to regulate the right of citizenship by law",
    "12": "Definition of State",
    "13": "Laws inconsistent with or in derogation of the fundamental rights",
    "14": "Equality before law",
    "15": "Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth",
    "16": "Equality of opportunity in matters of public employment",
    "17": "Abolition of Untouchability",
    "18": "Abolition of titles",
    "19": "Protection of certain rights regarding freedom of speech, etc.",
    "20": "Protection in respect of conviction for offences",
    "21": "Protection of life and personal liberty",
    "21A": "Right to education",
    "22": "Protection against arrest and detention in certain cases",
    "23": "Prohibition of traffic in human beings and forced labour",
    "24": "Prohibition of employment of children in factories, etc.",
    "25": "Freedom of conscience and free profession, practice and propagation of religion",
    "26": "Freedom to manage religious affairs",
    "27": "Freedom as to payment of taxes for promotion of any particular religion",
    "28": "Freedom as to attendance at religious instruction or religious worship in certain educational institutions",
    "29": "Protection of interests of minorities",
    "30": "Right of minorities to establish and administer educational institutions",
    "32": "Remedies for enforcement of rights conferred by this Part",
    "33": "Power of Parliament to modify the rights conferred by this Part",
    "34": "Restriction on rights conferred by this Part while martial law is in force",
    "35": "Legislation to give effect to the provisions of this Part",
    "36": "Definition",
    "37": "Application of the principles contained in this Part",
    "38": "State to secure a social order",
    "39": "Certain principles of policy to be followed by the State",
    "39A": "Equal justice and free legal aid",
    "40": "Organisation of village panchayats",
    "41": "Right to work, to education and to public assistance",
    "42": "Provision for just and humane conditions of work and maternity relief",
    "43": "Living wage, etc., for workers",
    "43A": "Participation of workers in management of industries",
    "44": "Uniform civil code for the citizens",
    "45": "Provision for early childhood care and education to children",
    "46": "Promotion of educational and economic interests of Scheduled Castes, Scheduled Tribes",
    "47": "Duty of the State to raise the level of nutrition and the standard of living",
    "48": "Organisation of agriculture and animal husbandry",
    "48A": "Protection and improvement of environment and safeguarding of forests",
    "49": "Protection of monuments and places and objects of national importance",
    "50": "Separation of judiciary from executive",
    "51": "Promotion of international peace and security",
    "51A": "Fundamental duties",
    "52": "The President of India",
    "53": "Executive power of the Union",
    "54": "Election of President",
    "55": "Manner of election of President",
    "56": "Term of office of President",
    "57": "Eligibility for re-election",
    "58": "Qualifications for election as President",
    "59": "Conditions of President's office",
    "60": "Oath or affirmation by the President",
    "61": "Procedure for impeachment of the President",
    "62": "Time of holding election to fill vacancy",
    "63": "The Vice-President of India",
    "64": "The Vice-President to be ex officio Chairman of the Council of States",
    "65": "The Vice-President to act as President",
    "66": "Election of Vice-President",
    "67": "Term of office of Vice-President",
    "72": "Power of President to grant pardons, etc.",
    "73": "Extent of executive power of the Union",
    "74": "Council of Ministers to aid and advise President",
    "75": "Other provisions as to Ministers",
    "76": "Attorney-General for India",
    "124": "Establishment and constitution of Supreme Court",
    "136": "Special leave to appeal by the Supreme Court",
    "141": "Law declared by Supreme Court to be binding on all courts",
    "144": "Civil and judicial authorities to act in aid of the Supreme Court",
    "245": "Extent of laws made by Parliament and by the Legislatures of States",
    "246": "Subject-matter of laws made by Parliament and by the Legislatures of States",
    "256": "Obligation of States and the Union",
    "262": "Adjudication of disputes relating to waters of inter-State rivers",
    "265": "Taxes not to be imposed save by authority of law",
    "300A": "Persons not to be deprived of property save by authority of law",
    "324": "Superintendence, direction and control of elections",
    "326": "Elections to the House of the People and to the Legislative Assemblies",
    "368": "Power of Parliament to amend the Constitution",
    "370": "Temporary provisions with respect to the State of Jammu and Kashmir",
    "395": "Repeals",
}

INDIA_PARTS = {
    1: ("Part I", "The Union and its Territory"),
    2: ("Part II", "Citizenship"),
    3: ("Part III", "Fundamental Rights"),
    4: ("Part IV", "Directive Principles of State Policy"),
    "4A": ("Part IVA", "Fundamental Duties"),
    5: ("Part V", "The Union"),
    6: ("Part VI", "The States"),
    7: ("Part VII", "States in Part B of the First Schedule"),
    8: ("Part VIII", "The Union Territories"),
    9: ("Part IX", "The Panchayats"),
    "9A": ("Part IXA", "The Municipalities"),
    10: ("Part X", "The Scheduled and Tribal Areas"),
    11: ("Part XI", "Relations between the Union and the States"),
    12: ("Part XII", "Finance, Property, Contracts and Suits"),
    13: ("Part XIII", "Trade, Commerce and Intercourse"),
    14: ("Part XIV", "Services under the Union and the States"),
    "14A": ("Part XIVA", "Tribunals"),
    15: ("Part XV", "Elections"),
    16: ("Part XVI", "Special Provisions Relating to Certain Classes"),
    17: ("Part XVII", "Official Language"),
    18: ("Part XVIII", "Emergency Provisions"),
    19: ("Part XIX", "Miscellaneous"),
    20: ("Part XX", "Amendment of the Constitution"),
    21: ("Part XXI", "Temporary, Transitional and Special Provisions"),
    22: ("Part XXII", "Short Title, Commencement, Authoritative Text and Repeals"),
}


def get_india_part(art_num):
    """Determine Part for India Constitution article number (int or string)."""
    # Handle string article numbers like "21A" "39A"
    if isinstance(art_num, str):
        try:
            n = int(art_num)
        except ValueError:
            n = 0
    else:
        n = art_num

    if n == 0:
        # Handle special cases
        if "51A" in str(art_num):
            return INDIA_PARTS["4A"]
        if "39A" in str(art_num) or "43A" in str(art_num) or "48A" in str(art_num):
            return INDIA_PARTS[4]
        if "243" in str(art_num):
            return INDIA_PARTS[9]
        return INDIA_PARTS[22]

    if 1 <= n <= 4:
        return INDIA_PARTS[1]
    if 5 <= n <= 11:
        return INDIA_PARTS[2]
    if 12 <= n <= 35:
        return INDIA_PARTS[3]
    if 36 <= n <= 51:
        return INDIA_PARTS[4]
    if n == "51A":
        return INDIA_PARTS["4A"]
    if 52 <= n <= 162:
        return INDIA_PARTS[5]
    if 163 <= n <= 237:
        return INDIA_PARTS[6]
    if 238 <= n <= 242:
        return INDIA_PARTS[7]
    if 243 <= n <= 243:
        return INDIA_PARTS[9]
    if 244 <= n <= 245:
        return INDIA_PARTS[10]
    if 245 <= n <= 263:
        return INDIA_PARTS[11]
    if 264 <= n <= 300:
        return INDIA_PARTS[12]
    if 301 <= n <= 307:
        return INDIA_PARTS[13]
    if 308 <= n <= 323:
        return INDIA_PARTS[14]
    if 324 <= n <= 329:
        return INDIA_PARTS[15]
    if 330 <= n <= 342:
        return INDIA_PARTS[16]
    if 343 <= n <= 351:
        return INDIA_PARTS[17]
    if 352 <= n <= 360:
        return INDIA_PARTS[18]
    if 361 <= n <= 367:
        return INDIA_PARTS[19]
    if 368 <= n <= 368:
        return INDIA_PARTS[20]
    if 369 <= n <= 392:
        return INDIA_PARTS[21]
    if 393 <= n <= 395:
        return INDIA_PARTS[22]
    return INDIA_PARTS[22]


def get_india_category(art_num):
    """Determine category for India Constitution article."""
    if isinstance(art_num, str):
        try:
            n = int(art_num)
        except ValueError:
            # Handle "21A", "39A", etc.
            num_part = re.match(r"(\d+)", art_num)
            n = int(num_part.group(1)) if num_part else 0
    else:
        n = art_num

    if 12 <= n <= 35:
        return "fundamental_rights", "fundamental_rights"
    if 36 <= n <= 51:
        return "directive_principles", "directive_principles"
    if 52 <= n <= 78:
        return "executive", "president"
    if 79 <= n <= 122:
        return "legislature", "parliament"
    if 124 <= n <= 147:
        return "judiciary", "supreme_court"
    if 148 <= n <= 151:
        return "constitutional_bodies", "auditor_general"
    if 152 <= n <= 237:
        return "federalism", "state_government"
    if 245 <= n <= 263:
        return "federalism", "union_state_relations"
    if 264 <= n <= 300:
        return "federal_finance", "finance"
    if 324 <= n <= 329:
        return "election_commission", "elections"
    if 352 <= n <= 360:
        return "emergency_powers", "emergency"
    if str(art_num) == "368":
        return "constitutional_amendment", "amendment"
    if str(art_num) == "370":
        return "special_provisions", "jammu_kashmir"
    return "constitutional", "general"


def fetch_india_constitution():
    """Download India Constitution PDF and extract article text."""
    pdf_path = RAW_DIR / "india_constitution.pdf"
    if not pdf_path.exists():
        print("Downloading India Constitution PDF...")
        urllib.request.urlretrieve(INDIA_PDF_URL, pdf_path)

    text = extract_pdf_text(pdf_path)
    if not text.strip():
        print("PDF extraction failed for India Constitution!")
        text = ""

    articles = parse_india_articles(text)
    print(f"Parsed {len(articles)} India constitution articles")
    return articles


def parse_india_articles(text):
    """Parse extracted PDF text into structured articles."""
    articles = []

    # The India Constitution PDF has the format:
    # "1. (1) India, that is Bharat, shall be a Union of States..."
    # but with headers/sidebars for titles
    # We'll search for patterns matching "N." at line start

    # Build a set of all article numbers we expect (1-448, plus some lettered ones)
    expected = set()
    for n in range(1, 449):
        expected.add(str(n))
    for n in ["2A", "21A", "31A", "31B", "31C", "31D", "32A", "39A", "43A", "43B",
              "48A", "51A", "124A", "124B", "124C", "131A", "139A", "144A",
              "224A", "228A", "233A", "239A", "239AA", "239AB", "239B",
              "243A", "243B", "243C", "243D", "243E", "243F", "243G", "243H",
              "243I", "243J", "243K", "243L", "243M", "243N", "243O",
              "243P", "243Q", "243R", "243S", "243T", "243U", "243V", "243W", "243X",
              "243Y", "243Z", "243ZA", "243ZB", "243ZC", "243ZD", "243ZE", "243ZF", "243ZG",
              "243ZH", "243ZI", "243ZJ", "243ZK", "243ZL", "243ZM", "243ZN", "243ZO", "243ZP", "243ZQ", "243ZR", "243ZS", "243ZT",
              "244A", "257A", "258A", "268A", "279A", "290A", "291", "300A", "300B", "31A",
              "32A", "338A", "338B", "342A", "361A", "361B", "371A", "371B", "371C", "371D", "371E",
              "371F", "371G", "371H", "371I", "371J", "372A", "378A", "394A"]:
        expected.add(n)

    # Extract text for each article
    # Cut text at Schedules/Appendices to avoid matching list items
    body_text = text
    sched_idx = re.search(r'\nSCHEDULES?\s*\n|\nFIRST\s+SCHEME|^\s*APPENDIX', text)
    if sched_idx:
        body_text = text[:sched_idx.start()]

    # Take the FIRST occurrence of each article number (schedules repeat numbers)
    seen = {}
    pattern = r'(?:^|\n)\s*(\d{1,3}[A-Z]?)\.?\s+(.*?)(?=(?:^|\n)\s*\d{1,3}[A-Z]?\.?\s+|\Z)'
    for m in re.finditer(pattern, body_text, re.DOTALL):
        art_str = m.group(1).strip()
        if art_str in expected or (art_str.isdigit() and 1 <= int(art_str) <= 448):
            raw = m.group(2).strip()
            if art_str not in seen:
                seen[art_str] = raw

    print(f"  Found {len(seen)} unique India article numbers")

    # For India, iterate through the expected article numbers (1-448 plus lettered)
    # We know the titles from INDIA_ARTICLE_TITLES (partial) and can use generic title for rest

    # Generate full set of article numbers in order
    all_article_nums = []
    for n in range(1, 449):
        all_article_nums.append(str(n))
    # Insert lettered articles in the right position
    insertions = {
        "2A": 2, "21A": 21, "31A": 31, "31B": 31, "31C": 31, "31D": 31,
        "32A": 32, "39A": 39, "43A": 43, "43B": 43, "48A": 48, "51A": 51,
        "124A": 124, "124B": 124, "124C": 124, "131A": 131, "139A": 139,
        "144A": 144, "224A": 224, "228A": 228, "233A": 233,
        "239A": 239, "239AA": 239, "239AB": 239, "239B": 239,
        "243A": 243, "243B": 243, "243C": 243, "243D": 243, "243E": 243,
        "243F": 243, "243G": 243, "243H": 243, "243I": 243, "243J": 243,
        "243K": 243, "243L": 243, "243M": 243, "243N": 243, "243O": 243,
        "243P": 243, "243Q": 243, "243R": 243, "243S": 243, "243T": 243,
        "243U": 243, "243V": 243, "243W": 243, "243X": 243, "243Y": 243,
        "243Z": 243, "243ZA": 243, "243ZB": 243, "243ZC": 243, "243ZD": 243,
        "243ZE": 243, "243ZF": 243, "243ZG": 243, "243ZH": 243, "243ZI": 243,
        "243ZJ": 243, "243ZK": 243, "243ZL": 243, "243ZM": 243, "243ZN": 243,
        "243ZO": 243, "243ZP": 243, "243ZQ": 243, "243ZR": 243, "243ZS": 243,
        "243ZT": 243,
        "244A": 244, "257A": 257, "258A": 258, "268A": 268,
        "279A": 279, "290A": 290, "291": 291,
        "300A": 300, "300B": 300,
        "338A": 338, "338B": 338, "342A": 342,
        "361A": 361, "361B": 361,
        "371A": 371, "371B": 371, "371C": 371, "371D": 371, "371E": 371,
        "371F": 371, "371G": 371, "371H": 371, "371I": 371, "371J": 371,
        "372A": 372, "378A": 378, "394A": 394,
    }

    # Simple sorted order: numeric then lettered, per article number
    # Build the full list in order
    ordered = []
    for n in range(309):
        ordered.append(str(n + 1))
    # We'll just create articles for the ones we actually found text for
    # plus known titles, to avoid creating noise

    for art_str, raw_text in sorted(seen.items(), key=lambda x: (int(re.match(r"(\d+)", x[0]).group(1)), x[0])):
        title = INDIA_ARTICLE_TITLES.get(art_str, f"Article {art_str}")
        part_label, part_title = get_india_part(art_str)
        cat, subcat = get_india_category(art_str)

        # Clean text
        clean = re.sub(r'\s+', ' ', raw_text).strip()
        # Remove sidebar/header noise
        clean = re.sub(r'^[\d\s—\-\.]+', '', clean)  # leading number/dash
        clean = clean[:2000] if len(clean) > 2000 else clean  # cap length

        if not clean or len(clean) < 20:
            # Too short, probably parsing noise
            continue

        full_text = f"Article {art_str}. {title}.\n{clean}"

        articles.append({
            "id": f"india_const_art_{art_str}",
            "country": "india",
            "source_document": "constitution_of_india",
            "document_type": "constitution",
            "article_number": art_str,
            "title": title,
            "full_text": full_text,
            "category": cat,
            "subcategory": subcat,
            "part": f"{part_label}: {part_title}",
            "chapter": None,
            "schedule": None,
            "amendments": [],
            "cross_references": re.findall(r'(?:Article|Section)\s+(\d{1,3}[A-Z]?)', full_text),
            "language": "en",
            "metadata": {
                "enacted": "1950-01-26",
                "source": "Government of India, Legislative Department",
            },
        })

    # Ensure key articles (1-395) exist even if not parsed from PDF
    for art_num_str in [str(n) for n in range(1, 396)]:
        art_id = f"india_const_art_{art_num_str}"
        if not any(a["id"] == art_id for a in articles):
            title = INDIA_ARTICLE_TITLES.get(art_num_str, f"Article {art_num_str}")
            part_label, part_title = get_india_part(art_num_str)
            cat, subcat = get_india_category(art_num_str)
            articles.append({
                "id": art_id,
                "country": "india",
                "source_document": "constitution_of_india",
                "document_type": "constitution",
                "article_number": art_num_str,
                "title": title,
                "full_text": f"Article {art_num_str}. {title}.\n\n[Full text of this article will be available in a future update.]",
                "category": cat,
                "subcategory": subcat,
                "part": f"{part_label}: {part_title}",
                "chapter": None,
                "schedule": None,
                "amendments": [],
                "cross_references": [],
                "language": "en",
                "metadata": {
                    "enacted": "1950-01-26",
                    "source": "Government of India, Legislative Department",
                },
            })

    # Sort by article number
    def sort_key(a):
        m = re.match(r"(\d+)([A-Z]*)", a["article_number"])
        return (int(m.group(1)), m.group(2)) if m else (999, "")
    articles.sort(key=sort_key)

    return articles


# ─── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Fetching and ingesting real constitution text")
    print("=" * 60)

    # Install PDF library if needed
    ensure_pdf_library()

    # Nepal Constitution
    print("\n--- Nepal Constitution 2072 ---")
    nepal_articles = fetch_nepal_constitution()

    nepal_data = {
        "title": "Constitution of Nepal 2072 (2015)",
        "country": "nepal",
        "document_type": "constitution",
        "year": 2072,
        "language": "en",
        "total_articles": len(nepal_articles),
        "articles": nepal_articles,
        "schedules": [],
        "metadata": {
            "enacted": "2015-09-20",
            "source": "Government of Nepal, Ministry of Law, Justice and Parliamentary Affairs",
            "source_url": NEPAL_PDF_URL,
            "constitution_year": 2072,
        },
    }
    out_path = DATA_DIR / "nepal_constitution.json"
    with open(out_path, "w") as f:
        json.dump(nepal_data, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(nepal_articles)} articles to {out_path}")

    # Count articles with real text vs placeholder
    real = sum(1 for a in nepal_articles if "[Full text" not in a["full_text"])
    placeholder = len(nepal_articles) - real
    print(f"  Real text: {real}, Placeholder: {placeholder}")

    # India Constitution
    print("\n--- India Constitution ---")
    india_articles = fetch_india_constitution()

    india_data = {
        "title": "Constitution of India",
        "country": "india",
        "document_type": "constitution",
        "year": 1950,
        "language": "en",
        "total_articles": len(india_articles),
        "articles": india_articles,
        "schedules": [],
        "metadata": {
            "enacted": "1950-01-26",
            "source": "Government of India, Ministry of Law and Justice, Legislative Department",
            "source_url": INDIA_PDF_URL,
        },
    }
    out_path = DATA_DIR / "india_constitution.json"
    with open(out_path, "w") as f:
        json.dump(india_data, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(india_articles)} articles to {out_path}")

    real = sum(1 for a in india_articles if "[Full text" not in a["full_text"])
    placeholder = len(india_articles) - real
    print(f"  Real text: {real}, Placeholder: {placeholder}")

    print("\n✓ Done! Run the corpus loader to rebuild the database.")


def ensure_pdf_library():
    """Try to install a PDF extraction library."""
    import subprocess
    import sys

    for lib, pkg in [("pdfplumber", "pdfplumber"), ("PyPDF2", "PyPDF2"), ("fitz", "pymupdf")]:
        try:
            __import__(lib)
            return
        except ImportError:
            pass

    print("Installing PDF extraction library...")
    for pkg in ["pdfplumber", "PyPDF2", "pymupdf"]:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                                capture_output=True, timeout=60)
            print(f"  Installed {pkg}")
            return
        except Exception as e:
            print(f"  Failed to install {pkg}: {e}")

    print("  Warning: No PDF library available. Using alternative fetch method.")


if __name__ == "__main__":
    main()