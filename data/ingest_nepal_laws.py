#!/usr/bin/env python3
"""
Download, parse, and ingest Nepal legal documents:
1. National Penal Code Act 2074 (Criminal Code)
2. Criminal Procedure Code 2074
3. National Civil Code 2074
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

try:
    import urllib.request
except ImportError:
    pass

BASE = Path(__file__).resolve().parent.parent
RAW_DIR = BASE / "raw" / "nepal_laws"
PROCESSED_DIR = BASE / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# PDF sources
PDFS = {
    "penal_code": {
        "url": "https://lpr.adb.org/sites/default/files/resource/%5Bnid%5D/36-nepal-106060-english.pdf",
        "filename": "nepal_penal_code_2074.pdf",
        "label": "National Penal (Code) Act, 2017 (2074)",
        "doc_type": "penal_code",
        "country": "nepal",
    },
    "criminal_procedure": {
        "url": "https://bwcimplementation.org/sites/default/files/resource/NP_Criminal%20Procedure%20Code_EN.pdf",
        "filename": "nepal_criminal_procedure_2074.pdf",
        "label": "National Criminal Procedure (Code) Act, 2017 (2074)",
        "doc_type": "criminal_procedure",
        "country": "nepal",
    },
    "civil_code": {
        "url": "https://www.jica.go.jp/Resource/activities/issues/governance/portal/nepal/ku57pq00002khibz-att/civil_code_1st_amendment_en.pdf",
        "filename": "nepal_civil_code_2074.pdf",
        "label": "National Civil (Code) Act, 2017 (2074)",
        "doc_type": "civil_code",
        "country": "nepal",
    },
}


def download_pdf(key, info):
    dest = RAW_DIR / info["filename"]
    if dest.exists() and dest.stat().st_size > 100000:
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
        print(f"  [error] Download failed: {e}")
        return None


def parse_penal_code(pdf_path):
    """Parse the Penal Code PDF into sections."""
    articles = []
    current_part = ""
    current_chapter = ""
    current_section_num = ""
    current_section_title = ""
    current_text_lines = []
    
    # Pattern for section numbers like "1." or "123."
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
                if not line:
                    continue
                # Skip page numbers and headers
                if re.match(r'^\d+$', line):
                    continue
                if "National Penal" in line and "Code" in line:
                    continue
                if "Revised" in line and len(line) < 20:
                    continue
                    
                # Part headers
                pm = part_pattern.match(line)
                if pm:
                    flush_section()
                    current_part = line
                    continue
                    
                # Chapter headers
                cm = chapter_pattern.match(line)
                if cm:
                    flush_section()
                    current_chapter = line
                    continue
                    
                # Section number on its own line
                sm = section_pattern.match(line)
                if sm:
                    flush_section()
                    current_section_num = sm.group(1)
                    continue
                    
                # Section number with title on same line
                sm2 = section_pattern2.match(line)
                if sm2 and int(sm2.group(1)) < 500:
                    # Check if it looks like a section start
                    num = sm2.group(1)
                    rest = sm2.group(2)
                    # Section titles are usually short and capitalized
                    if len(rest) < 120 and not rest.startswith("shall") and not rest.startswith("the "):
                        flush_section()
                        current_section_num = num
                        current_section_title = rest
                        continue
                
                # Accumulate text
                if current_section_num:
                    current_text_lines.append(line)
                elif not articles:
                    # Preamble text before first section
                    pass

    flush_section()
    return articles


def parse_criminal_procedure(pdf_path):
    """Parse Criminal Procedure Code."""
    articles = []
    current_chapter = ""
    current_section_num = ""
    current_section_title = ""
    current_text_lines = []
    
    section_pattern = re.compile(r'^(\d+)\.\s*$')
    section_pattern2 = re.compile(r'^(\d+)\.\s+(.+)')
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
                    "part": current_chapter,
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
                if "Criminal Procedure" in line and "Code" in line:
                    continue
                if "Revised" in line and len(line) < 20:
                    continue
                    
                cm = chapter_pattern.match(line)
                if cm:
                    flush_section()
                    current_chapter = line
                    continue
                    
                if schedule_pattern.match(line):
                    flush_section()
                    current_chapter = line
                    continue
                    
                sm = section_pattern.match(line)
                if sm:
                    flush_section()
                    current_section_num = sm.group(1)
                    continue
                    
                sm2 = section_pattern2.match(line)
                if sm2 and int(sm2.group(1)) < 500:
                    num = sm2.group(1)
                    rest = sm2.group(2)
                    if len(rest) < 120:
                        flush_section()
                        current_section_num = num
                        current_section_title = rest
                        continue
                
                if current_section_num:
                    current_text_lines.append(line)

    flush_section()
    return articles


def parse_civil_code(pdf_path):
    """Parse Civil Code."""
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
                if "Civil Code" in line and "Code" in line:
                    continue
                if "Revised" in line and len(line) < 20:
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
                if sm2 and int(sm2.group(1)) < 800:
                    num = sm2.group(1)
                    rest = sm2.group(2)
                    if len(rest) < 120:
                        flush_section()
                        current_section_num = num
                        current_section_title = rest
                        continue
                
                if current_section_num:
                    current_text_lines.append(line)

    flush_section()
    return articles


def categorize_article(text, doc_type):
    """Categorize an article based on its content."""
    text_lower = text.lower()
    
    if doc_type == "penal_code":
        if any(w in text_lower for w in ["murder", "homicide", "killing", "death"]):
            return "offences_against_person"
        if any(w in text_lower for w in ["theft", "steal", "robbery", "dacoity", "extortion"]):
            return "property_offences"
        if any(w in text_lower for w in ["fraud", "forgery", "cheating", "deception"]):
            return "fraud_and_forgery"
        if any(w in text_lower for w in ["rape", "sexual", "sexual assault", "harassment"]):
            return "sexual_offences"
        if any(w in text_lower for w in ["drug", "narcotic", "controlled substance"]):
            return "drug_offences"
        if any(w in text_lower for w in ["corruption", "bribery", "abuse of power"]):
            return "corruption_offences"
        if any(w in text_lower for w in ["marriage", "bigamy", "divorce", "matrimonial"]):
            return "offences_relating_marriage"
        if any(w in text_lower for w in ["kidnapping", "abduction", "hostage"]):
            return "offences_against_liberty"
        if any(w in text_lower for w in ["defamation", "criminal intimidation", "insult"]):
            return "defamation_and_intimidation"
        if any(w in text_lower for w in ["criminal trespass", "house breaking", "burglary"]):
            return "trespass_and_burglary"
        if any(w in text_lower for w in ["punishment", "sentence", "imprisonment", "fine"]):
            return "punishment_provisions"
        if any(w in text_lower for w in ["general exception", "act done by person bound", "accident", "necessity"]):
            return "general_exceptions"
        if any(w in text_lower for w in ["abet", "conspiracy", "attempt"]):
            return "abetment_and_conspiracy"
        if any(w in text_lower for w in ["public servant", "government"]):
            return "offences_by_public_servants"
        return "general_criminal_law"
    
    elif doc_type == "criminal_procedure":
        if any(w in text_lower for w in ["arrest", "bail", "detention"]):
            return "arrest_and_bail"
        if any(w in text_lower for w in ["investigation", "police", "search", "warrant"]):
            return "investigation"
        if any(w in text_lower for w in ["charge", "trial", "hearing"]):
            return "trial_proceedings"
        if any(w in text_lower for w in ["appeal", "revision", "review"]):
            return "appeals_and_revision"
        if any(w in text_lower for w in ["evidence", "witness", "testimony", "oath"]):
            return "evidence"
        if any(w in text_lower for w in ["judgment", "sentence", "conviction", "acquittal"]):
            return "judgment_and_sentence"
        if any(w in text_lower for w in ["complaint", "fir", "first information"]):
            return "complaints"
        return "criminal_procedure_general"
    
    elif doc_type == "civil_code":
        if any(w in text_lower for w in ["marriage", "divorce", "matrimonial", "spouse"]):
            return "marriage_and_family"
        if any(w in text_lower for w in ["property", "ownership", "possession", "easement"]):
            return "property_law"
        if any(w in text_lower for w in ["contract", "agreement", "obligation", "promise"]):
            return "contracts_and_obligations"
        if any(w in text_lower for w in ["tort", "negligence", "defamation", "damages"]):
            return "tort_law"
        if any(w in text_lower for w in ["inheritance", "succession", "will", "heir"]):
            return "inheritance_and_succession"
        if any(w in text_lower for w in ["adoption", "guardianship", "custody"]):
            return "adoption_and_guardianship"
        if any(w in text_lower for w in ["partition", "joint family", "coparcenary"]):
            return "partition_and_family_property"
        if any(w in text_lower for w in ["limitation", "prescription", "time bar"]):
            return "limitation"
        return "civil_law_general"
    
    return "general"


def build_output(all_articles, doc_type, label):
    """Build structured output for a document."""
    output = {
        "document_name": label,
        "document_type": doc_type,
        "country": "nepal",
        "source": "PDF - Official English Translation",
        "total_articles": len(all_articles),
        "articles": [],
    }
    
    for art in all_articles:
        category = categorize_article(art["full_text"], doc_type)
        output["articles"].append({
            "id": f"nepal_{doc_type}_{art['article_number']}",
            "article_number": art["article_number"],
            "title": art["title"],
            "full_text": art["full_text"],
            "category": category,
            "document_type": doc_type,
            "country": "nepal",
            "part": art.get("part", ""),
            "chapter": art.get("chapter", ""),
        })
    
    return output


def main():
    print("=" * 60)
    print("Nepal Legal Documents - Download & Parse")
    print("=" * 60)
    
    # Step 1: Download PDFs
    print("\n[1/4] Downloading PDFs...")
    downloaded = {}
    for key, info in PDFS.items():
        path = download_pdf(key, info)
        if path:
            downloaded[key] = path
    
    if not downloaded:
        print("No PDFs downloaded. Exiting.")
        sys.exit(1)
    
    # Step 2: Parse PDFs
    print("\n[2/4] Parsing PDFs...")
    all_outputs = []
    
    for key, path in downloaded.items():
        info = PDFS[key]
        print(f"\n  Parsing {info['label']}...")
        
        if key == "penal_code":
            articles = parse_penal_code(path)
        elif key == "criminal_procedure":
            articles = parse_criminal_procedure(path)
        elif key == "civil_code":
            articles = parse_civil_code(path)
        else:
            articles = []
        
        print(f"  Extracted {len(articles)} sections/articles")
        
        if articles:
            output = build_output(articles, info["doc_type"], info["label"])
            all_outputs.append(output)
    
    # Step 3: Save individual JSONs
    print("\n[3/4] Saving processed JSONs...")
    for output in all_outputs:
        out_path = PROCESSED_DIR / f"nepal_{output['document_type']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"  Saved {out_path} ({output['total_articles']} articles)")
    
    # Step 4: Merge with existing Nepal constitution
    print("\n[4/4] Building combined Nepal corpus...")
    constitution_path = PROCESSED_DIR / "nepal_constitution.json"
    combined = {
        "documents": [],
        "total_articles": 0,
        "articles": [],
    }
    
    # Add constitution
    if constitution_path.exists():
        with open(constitution_path) as f:
            const = json.load(f)
        combined["documents"].append({
            "name": const.get("document_name", "Nepal Constitution 2072"),
            "type": "constitution",
            "count": const["total_articles"],
        })
        for art in const["articles"]:
            art["country"] = "nepal"
            combined["articles"].append(art)
        combined["total_articles"] += const["total_articles"]
        print(f"  Added Constitution: {const['total_articles']} articles")
    
    # Add new laws
    for output in all_outputs:
        combined["documents"].append({
            "name": output["document_name"],
            "type": output["document_type"],
            "count": output["total_articles"],
        })
        for art in output["articles"]:
            combined["articles"].append(art)
        combined["total_articles"] += output["total_articles"]
        print(f"  Added {output['document_name']}: {output['total_articles']} sections")
    
    # Save combined
    combined_path = PROCESSED_DIR / "nepal_full_corpus.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"\n  Combined corpus saved: {combined_path}")
    print(f"  Total articles: {combined['total_articles']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for doc in combined["documents"]:
        print(f"  {doc['name']}: {doc['count']} articles")
    print(f"\n  TOTAL: {combined['total_articles']} articles")
    print("=" * 60)


if __name__ == "__main__":
    main()
