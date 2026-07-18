#!/usr/bin/env python3
"""
Download, parse, and ingest additional India legal documents.
Covers: Evidence Act, Specific Relief, Transfer of Property, Consumer Protection,
Motor Vehicles, DV Act, IT Act, Negotiable Instruments, Juvenile Justice, RTI,
Partnership, Sale of Goods.
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
RAW_DIR = BASE / "raw" / "india_laws"
PROCESSED_DIR = BASE / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)

INDIA_PDFS = {
    "evidence_act": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/15351/1/iea_1872.pdf",
        "filename": "india_evidence_act_1872.pdf",
        "label": "Indian Evidence Act, 1872",
        "doc_type": "evidence_act",
    },
    "specific_reliefs": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/1583/7/A1963-47.pdf",
        "filename": "india_specific_reliefs_1963.pdf",
        "label": "Specific Relief Act, 1963",
        "doc_type": "specific_reliefs",
    },
    "transfer_of_property": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/2338/1/A1882-04.pdf",
        "filename": "india_transfer_of_property_1882.pdf",
        "label": "Transfer of Property Act, 1882",
        "doc_type": "transfer_of_property",
    },
    "consumer_protection": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/18964/1/cpa.pdf",
        "filename": "india_consumer_protection_2019.pdf",
        "label": "Consumer Protection Act, 2019",
        "doc_type": "consumer_protection",
    },
    "motor_vehicles": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/9460/1/a1988-59.pdf",
        "filename": "india_motor_vehicles_1988.pdf",
        "label": "Motor Vehicles Act, 1988",
        "doc_type": "motor_vehicles",
    },
    "domestic_violence": {
        "url": "https://prsindia.org/files/bills_acts/acts_parliament/2005/the-protection-of-women-from-domestic-violence-act-2005.pdf",
        "filename": "india_domestic_violence_2005.pdf",
        "label": "Protection of Women from Domestic Violence Act, 2005",
        "doc_type": "domestic_violence",
    },
    "it_act": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/13116/1/it_act_2000_updated.pdf",
        "filename": "india_it_act_2000.pdf",
        "label": "Information Technology Act, 2000",
        "doc_type": "information_technology",
    },
    "negotiable_instruments": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/15327/1/negotiable_instruments_act%2C_1881.pdf",
        "filename": "india_ni_act_1881.pdf",
        "label": "Negotiable Instruments Act, 1881",
        "doc_type": "negotiable_instruments",
    },
    "juvenile_justice": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/2148/1/a2016-2.pdf",
        "filename": "india_juvenile_justice_2015.pdf",
        "label": "Juvenile Justice (Care and Protection of Children) Act, 2015",
        "doc_type": "juvenile_justice",
    },
    "rti": {
        "url": "https://cic.gov.in/sites/default/files/RTI-Act_English.pdf",
        "filename": "india_rti_2005.pdf",
        "label": "Right to Information Act, 2005",
        "doc_type": "right_to_information",
    },
    "partnership": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/19863/1/indian_partnership_act_1932.pdf",
        "filename": "india_partnership_1932.pdf",
        "label": "Indian Partnership Act, 1932",
        "doc_type": "partnership",
    },
    "sale_of_goods": {
        "url": "https://www.indiacode.nic.in/bitstream/123456789/2390/1/193003.pdf",
        "filename": "india_sale_of_goods_1930.pdf",
        "label": "Sale of Goods Act, 1930",
        "doc_type": "sale_of_goods",
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

    cat_rules = {
        "evidence_act": {
            "fact in issue": "facts_and_proof",
            "relevant": "relevancy",
            "admission": "admissions",
            "estoppel": "estoppel",
            "examination": "examination_of_witnesses",
            "cross-examination": "examination_of_witnesses",
            "expert": "expert_evidence",
            "document": "documentary_evidence",
            "burden": "burden_of_proof",
            "presumption": "presumptions",
            "oral": "oral_evidence",
        },
        "specific_reliefs": {
            "injunction": "injunctions",
            "specific performance": "specific_performance",
            "declaration": "declaratory_decrees",
            "rectification": "rectification_and_rescission",
            "rescission": "rectification_and_rescission",
            "cancellation": "cancellation_of_instruments",
            "possession": "possession",
            "contract": "contracts",
        },
        "transfer_of_property": {
            "mortgage": "mortgages",
            "sale": "sale_of_property",
            "lease": "leases",
            "gift": "gifts",
            "exchange": "exchanges",
            "actionable claim": "actionable_claims",
            "transfer": "general_transfer",
            "property": "general_transfer",
        },
        "consumer_protection": {
            "complaint": "consumer_complaints",
            "deficiency": "deficiency_of_service",
            "goods": "goods_and_services",
            "unfair": "unfair_trade_practices",
            "price": "price_regulation",
            "consumer commission": "consumer_courts",
            "district forum": "consumer_courts",
            "national commission": "consumer_courts",
            "product": "product_liability",
            "e-commerce": "ecommerce",
        },
        "motor_vehicles": {
            "licence": "driving_licence",
            "permit": "permits",
            "insurance": "insurance",
            "accident": "accidents",
            "claim": "accident_claims",
            "offence": "traffic_offences",
            "penalty": "penalties",
            "vehicle": "vehicle_registration",
            "registration": "vehicle_registration",
        },
        "domestic_violence": {
            "physical": "physical_violence",
            "sexual": "sexual_violence",
            "verbal": "verbal_abuse",
            "emotional": "emotional_abuse",
            "economic": "economic_abuse",
            "shared household": "shared_household",
            "protection order": "protection_orders",
            "residence order": "residence_orders",
            "monetary relief": "monetary_relief",
            "custody": "custody",
            "shelter": "shelter",
            "medical": "medical_facilities",
        },
        "information_technology": {
            "digital signature": "digital_signatures",
            "cyber": "cyber_crime",
            "hacking": "computer_related_offences",
            "data": "data_protection",
            "privacy": "privacy",
            "electronic": "electronic_governance",
            "certificate": "certifying_authorities",
            "penalty": "penalties",
            "appeal": "appeals",
        },
        "negotiable_instruments": {
            "cheque": "cheque_bounce",
            "dishonour": "cheque_bounce",
            "promissory note": "promissory_notes",
            "bill of exchange": "bills_of_exchange",
            "endorsement": "endorsements",
            "holder": "holders_and_drawers",
            "negotiation": "negotiation",
            "liability": "liability_of_parties",
        },
        "juvenile_justice": {
            "child": "child_protection",
            "juvenile": "juvenile_justice",
            "adoption": "adoption",
            "rehabilitation": "rehabilitation",
            "special home": "special_homes",
            "child care": "child_care_institutions",
            "board": "juvenile_boards",
        },
        "right_to_information": {
            "public authority": "public_authorities",
            "information": "information_access",
            "disclosure": "disclosure",
            "exemption": "exemptions",
            "third party": "third_party_info",
            "appeal": "appeals",
            "commission": "info_commission",
            "records": "records_management",
        },
        "partnership": {
            "partner": "partnership_firm",
            "firm": "partnership_firm",
            "registration": "registration",
            "dissolution": "dissolution",
            "liability": "liability_of_partners",
            "authority": "authority_of_partners",
            "winding up": "winding_up",
        },
        "sale_of_goods": {
            "condition": "conditions_and_warranties",
            "warranty": "conditions_and_warranties",
            "transfer": "transfer_of_ownership",
            "performance": "performance_of_contract",
            "buyer": "rights_of_buyer",
            "seller": "rights_of_seller",
            "price": "price",
            "delivery": "delivery",
            "unpaid": "unpaid_seller",
        },
    }

    if doc_type in cat_rules:
        for kw, cat in cat_rules[doc_type].items():
            if kw in text_lower:
                return cat

    return f"{doc_type}_general"


def build_output(all_articles, doc_type, label, country="india"):
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
    print("India Additional Legal Documents - Download & Parse")
    print("=" * 60)

    # Step 1: Download
    print("\n[1/3] Downloading PDFs...")
    downloaded = {}
    for key, info in INDIA_PDFS.items():
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
        info = INDIA_PDFS[key]
        print(f"\n  Parsing {info['label']}...")
        articles = generic_section_parser(path)
        print(f"  Extracted {len(articles)} sections")
        if articles:
            output = build_output(articles, info["doc_type"], info["label"])
            all_outputs.append(output)

    # Step 3: Save
    print("\n[3/3] Saving processed JSONs...")
    for output in all_outputs:
        out_path = PROCESSED_DIR / f"india_{output['document_type']}.json"
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
