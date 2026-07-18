#!/usr/bin/env python3
"""
Download, parse, and ingest additional Nepal legal documents.
Covers: Labor, Consumer Protection, Domestic Violence, Cyber Law,
Narcotics, Right to Information, Motor Vehicle, Civil Procedure.
"""
import json
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("pdfplumber not installed. Run: pip install pdfplumber")
    sys.exit(1)

import urllib.request

BASE = Path(__file__).resolve().parent.parent
RAW_DIR = BASE / "raw" / "nepal_laws"
PROCESSED_DIR = BASE / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Additional Nepal laws to fetch
EXTRA_NEPAL_PDFS = {
    "labor_act": {
        "url": "https://faolex.fao.org/docs/pdf/NEP225978.pdf",
        "filename": "nepal_labor_act_2074.pdf",
        "label": "Labour Act, 2074 (2017)",
        "doc_type": "labor_act",
    },
    "consumer_protection": {
        "url": "https://lawcommission.gov.np/en/wp-content/uploads/2019/09/The-Consumer-Protection-Act-2075-2018.pdf",
        "filename": "nepal_consumer_protection_2075.pdf",
        "label": "Consumer Protection Act, 2075 (2018)",
        "doc_type": "consumer_protection",
    },
    "domestic_violence": {
        "url": "https://www.wcwonline.org/pdf/lawcompilation/Nepal_Domestic%20Violence%20(Crime%20and%20Punishment)%20.pdf",
        "filename": "nepal_domestic_violence_2066.pdf",
        "label": "Domestic Violence (Offence and Punishment) Act, 2066 (2009)",
        "doc_type": "domestic_violence",
    },
    "electronic_transactions": {
        "url": "https://radiantca.com.np/assets/nav_file/Electronic%20Transaction%20Act%202063.pdf",
        "filename": "nepal_electronic_transactions_2063.pdf",
        "label": "Electronic Transactions Act, 2063 (2008)",
        "doc_type": "electronic_transactions",
    },
    "narcotic_drugs": {
        "url": "https://pharmainfonepal.com/wp-content/uploads/2020/12/Narcotic-control-act-2033.pdf",
        "filename": "nepal_narcotic_drugs_2033.pdf",
        "label": "Narcotic Drugs (Control) Act, 2033 (1976)",
        "doc_type": "narcotic_drugs",
    },
    "right_to_info": {
        "url": "https://natlex.ilo.org/dyn/natlex2/natlex2/files/download/87503/NPL87503.pdf",
        "filename": "nepal_rti_2064.pdf",
        "label": "Right to Information Act, 2064 (2007)",
        "doc_type": "right_to_information",
    },
    "civil_procedure": {
        "url": "https://www.jica.go.jp/Resource/activities/issues/governance/portal/nepal/ku57pq00002khibz-att/civil_code_1st_amendment_en.pdf",
        "filename": "nepal_civil_procedure_2074.pdf",
        "label": "National Civil Procedure Code, 2074 (2017)",
        "doc_type": "civil_procedure",
    },
}


def download_pdf(key, info):
    dest = RAW_DIR / info["filename"]
    if dest.exists() and dest.stat().st_size > 10000:
        print(f"  [skip] {info['filename']} already exists ({dest.stat().st_size} bytes)")
        return dest
    print(f"  Downloading {info['label']}...")
    try:
        req = urllib.request.Request(info["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        dest.write_bytes(data)
        print(f"  Saved {dest} ({len(data)} bytes)")
        return dest
    except Exception as e:
        print(f"  [error] Download failed for {key}: {e}")
        return None


def generic_section_parser(pdf_path, max_section=800):
    """Generic parser that extracts sections from a legal PDF."""
    articles = []
    current_part = ""
    current_chapter = ""
    current_section_num = ""
    current_section_title = ""
    current_text_lines = []

    section_pattern = re.compile(r'^(\d+)\.\s*$')
    section_pattern2 = re.compile(r'^(\d+)\.\s+(.+)')
    part_pattern = re.compile(r'^Part\s*[-–—]\s*(\d+|[IVXLC]+)', re.IGNORECASE)
    chapter_pattern = re.compile(r'^Chapter[- ]*(\d+|[IVXLC]+)', re.IGNORECASE)
    schedule_pattern = re.compile(r'^Schedule[- ]*(\d+)', re.IGNORECASE)

    def flush_section():
        nonlocal current_section_num, current_section_title, current_text_lines
        if current_section_num and current_text_lines:
            full_text = " ".join(current_text_lines).strip()
            if len(full_text) > 20:
                title = current_section_title or f"Section {current_section_num}"
                articles.append({
                    "article_number": current_section_num,
                    "title": title,
                    "full_text": full_text,
                    "part": current_part,
                    "chapter": current_chapter,
                })
        current_section_num = ""
        current_section_title = ""
        current_text_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line or re.match(r'^\d+$', line):
                    continue
                # Skip common headers
                if any(skip in line.lower() for skip in ["revised", "act no", "act number", "date of authentication"]):
                    if len(line) < 40:
                        continue

                pm = part_pattern.match(line)
                if pm:
                    flush_section()
                    current_part = line
                    continue

                cm = chapter_pattern.match(line)
                if cm:
                    flush_section()
                    current_chapter = line
                    continue

                sm = schedule_pattern.match(line)
                if sm:
                    flush_section()
                    current_chapter = line
                    continue

                sm = section_pattern.match(line)
                if sm:
                    flush_section()
                    current_section_num = sm.group(1)
                    continue

                sm2 = section_pattern2.match(line)
                if sm2 and int(sm2.group(1)) < max_section:
                    num = sm2.group(1)
                    rest = sm2.group(2)
                    if len(rest) < 150:
                        flush_section()
                        current_section_num = num
                        current_section_title = rest
                        continue

                if current_section_num:
                    current_text_lines.append(line)

    flush_section()
    return articles


def categorize_article(text, doc_type):
    """Categorize an article based on content and document type."""
    text_lower = text.lower()

    # Document-specific categorization
    cat_map = {
        "labor_act": {
            "keywords": {
                "wages": "wages_and_payment",
                "salary": "wages_and_payment",
                "minimum wage": "wages_and_payment",
                "overtime": "wages_and_payment",
                "leave": "leave_and_holidays",
                "holiday": "leave_and_holidays",
                "termination": "termination_and_dismissal",
                "dismissal": "termination_and_dismissal",
                "retrenchment": "termination_and_dismissal",
                "trade union": "trade_unions",
                "collective bargaining": "trade_unions",
                "strike": "trade_unions",
                "harassment": "harassment_and_discrimination",
                "discrimination": "harassment_and_discrimination",
                "child labor": "child_labor",
                "women": "womens_rights",
                "safety": "occupational_safety",
                "health": "occupational_safety",
                "accident": "occupational_safety",
                "epf": "social_security",
                "gratuity": "social_security",
                "social security": "social_security",
            },
            "default": "labor_general",
        },
        "consumer_protection": {
            "keywords": {
                "complaint": "consumer_complaints",
                "deficiency": "consumer_complaints",
                "goods": "goods_and_services",
                "service": "goods_and_services",
                "price": "price_regulation",
                "overcharge": "price_regulation",
                "refund": "consumer_remedies",
                "compensation": "consumer_remedies",
                "unfair": "unfair_practices",
                "fraud": "unfair_practices",
                "false": "unfair_practices",
                "product liability": "product_liability",
                "defective": "product_liability",
                "consumer commission": "consumer_courts",
                "district forum": "consumer_courts",
            },
            "default": "consumer_general",
        },
        "domestic_violence": {
            "keywords": {
                "physical": "physical_violence",
                "assault": "physical_violence",
                "hurt": "physical_violence",
                "sexual": "sexual_violence",
                "rape": "sexual_violence",
                "psychological": "psychological_violence",
                "mental": "psychological_violence",
                "emotional": "psychological_violence",
                "economic": "economic_violence",
                "property": "economic_violence",
                "protection order": "protection_orders",
                "restrain": "protection_orders",
                "shelter": "shelter_and_relief",
                "maintenance": "maintenance_and_support",
                "child": "children_and_dv",
                "custody": "children_and_dv",
            },
            "default": "domestic_violence_general",
        },
        "electronic_transactions": {
            "keywords": {
                "cyber": "cyber_crime",
                "hack": "cyber_crime",
                "password": "cyber_crime",
                "digital signature": "digital_signatures",
                "electronic record": "electronic_records",
                "data": "data_protection",
                "privacy": "data_protection",
                "computer": "computer_offences",
                "virus": "computer_offences",
                "phishing": "cyber_crime",
                "identity theft": "cyber_crime",
            },
            "default": "electronic_transactions_general",
        },
        "narcotic_drugs": {
            "keywords": {
                "cultivation": "cultivation_and_production",
                "manufacture": "cultivation_and_production",
                "production": "cultivation_and_production",
                "sale": "sale_and_distribution",
                "distribution": "sale_and_distribution",
                "possession": "possession_and_use",
                "consumption": "possession_and_use",
                "use": "possession_and_use",
                "trafficking": "trafficking",
                "smuggling": "trafficking",
                "import": "import_and_export",
                "export": "import_and_export",
                "schedule": "drug_schedules",
                "controlled": "drug_schedules",
            },
            "default": "narcotics_general",
        },
        "right_to_information": {
            "keywords": {
                "public authority": "public_authorities",
                "information": "information_access",
                "disclosure": "disclosure",
                "exemption": "exemptions",
                "third party": "third_party_info",
                "appeal": "appeals",
                "commission": "info_commission",
                "records": "records_management",
            },
            "default": "rti_general",
        },
    }

    # Default categorization for criminal/civil codes
    default_cats = {
        "penal_code": {
            "murder": "offences_against_person",
            "homicide": "offences_against_person",
            "theft": "property_offences",
            "steal": "property_offences",
            "robbery": "property_offences",
            "fraud": "fraud_and_forgery",
            "rape": "sexual_offences",
            "drug": "drug_offences",
            "corruption": "corruption_offences",
            "marriage": "offences_relating_marriage",
            "kidnapping": "offences_against_liberty",
            "defamation": "defamation_and_intimidation",
            "trespass": "trespass_and_burglary",
            "punishment": "punishment_provisions",
        },
        "criminal_procedure": {
            "arrest": "arrest_and_bail",
            "bail": "arrest_and_bail",
            "investigation": "investigation",
            "trial": "trial_proceedings",
            "appeal": "appeals_and_revision",
            "evidence": "evidence",
            "judgment": "judgment_and_sentence",
            "complaint": "complaints",
        },
        "civil_code": {
            "marriage": "marriage_and_family",
            "property": "property_law",
            "contract": "contracts_and_obligations",
            "tort": "tort_law",
            "inheritance": "inheritance_and_succession",
            "adoption": "adoption_and_guardianship",
            "partition": "partition_and_family_property",
        },
        "civil_procedure": {
            "suit": "civil_suits",
            "plaint": "civil_suits",
            "decree": "decrees_and_orders",
            "appeal": "appeals",
            "execution": "execution_of_decrees",
            "injunction": "injunctions",
            "evidence": "evidence",
            "witness": "witnesses",
        },
    }

    if doc_type in cat_map:
        mapping = cat_map[doc_type]
        for kw, cat in mapping["keywords"].items():
            if kw in text_lower:
                return cat
        return mapping["default"]
    elif doc_type in default_cats:
        mapping = default_cats[doc_type]
        for kw, cat in mapping.items():
            if kw in text_lower:
                return cat
        return f"{doc_type}_general"
    return "general"


def build_output(all_articles, doc_type, label, country="nepal"):
    """Build structured output for a document."""
    output = {
        "document_name": label,
        "document_type": doc_type,
        "country": country,
        "source": "PDF - Official English Translation",
        "total_articles": len(all_articles),
        "articles": [],
    }
    for art in all_articles:
        category = categorize_article(art["full_text"], doc_type)
        output["articles"].append({
            "id": f"{country}_{doc_type}_{art['article_number']}",
            "article_number": art["article_number"],
            "title": art["title"],
            "full_text": art["full_text"],
            "category": category,
            "document_type": doc_type,
            "country": country,
            "part": art.get("part", ""),
            "chapter": art.get("chapter", ""),
        })
    return output


def main():
    print("=" * 60)
    print("Nepal Additional Legal Documents - Download & Parse")
    print("=" * 60)

    # Step 1: Download
    print("\n[1/3] Downloading PDFs...")
    downloaded = {}
    for key, info in EXTRA_NEPAL_PDFS.items():
        path = download_pdf(key, info)
        if path:
            downloaded[key] = path

    if not downloaded:
        print("No PDFs downloaded. Exiting.")
        sys.exit(1)

    # Step 2: Parse
    print("\n[2/3] Parsing PDFs...")
    all_outputs = []
    for key, path in downloaded.items():
        info = EXTRA_NEPAL_PDFS[key]
        print(f"\n  Parsing {info['label']}...")
        articles = generic_section_parser(path)
        print(f"  Extracted {len(articles)} sections")
        if articles:
            output = build_output(articles, info["doc_type"], info["label"])
            all_outputs.append(output)

    # Step 3: Save
    print("\n[3/3] Saving processed JSONs...")
    for output in all_outputs:
        out_path = PROCESSED_DIR / f"nepal_{output['document_type']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"  Saved {out_path.name} ({output['total_articles']} articles)")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = 0
    for output in all_outputs:
        print(f"  {output['document_name']}: {output['total_articles']} sections")
        total += output['total_articles']
    print(f"\n  NEW TOTAL: {total} sections from {len(all_outputs)} documents")
    print("=" * 60)


if __name__ == "__main__":
    main()
