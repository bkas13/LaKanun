#!/usr/bin/env python3
"""
Build the complete ल Kanun HTML application with:
- All Nepal and India legal documents
- Legal guides for common issues
- Legal templates
- Glossary, limitation periods, emergency contacts
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE / "data" / "processed"

# Load all Nepal data
nepal_docs = []
nepal_files = [
    "nepal_constitution.json",
    "nepal_penal_code.json",
    "nepal_criminal_procedure.json",
    "nepal_civil_code.json",
    "nepal_labor_act.json",
    "nepal_domestic_violence.json",
    "nepal_narcotic_drugs.json",
    "nepal_right_to_information.json",
    "nepal_electronic_transactions.json",
    "nepal_civil_procedure.json",
]

nepal_all = {"documents": [], "total_articles": 0, "articles": []}
for fname in nepal_files:
    fpath = PROCESSED_DIR / fname
    if fpath.exists():
        with open(fpath) as f:
            data = json.load(f)
        doc_name = data.get("document_name", data.get("title", fname.replace(".json","")))
        nepal_all["documents"].append({
            "name": doc_name,
            "type": data.get("document_type", fname.replace(".json","")),
            "count": data["total_articles"],
        })
        nepal_all["articles"].extend(data["articles"])
        nepal_all["total_articles"] += data["total_articles"]
        print(f"  Loaded {doc_name}: {data['total_articles']}")

# Load all India data (original + new)
india_original_path = PROCESSED_DIR / "india_laws.json"
with open(india_original_path) as f:
    india_original = json.load(f)

india_all = {"documents": [], "total_articles": india_original["total_articles"], "articles": list(india_original["articles"])}

# Original India docs
india_doc_counts = {}
for a in india_original["articles"]:
    dt = a.get("source_document", a.get("document_type", "unknown"))
    if dt not in india_doc_counts:
        india_doc_counts[dt] = 0
    india_doc_counts[dt] += 1
for dt, cnt in india_doc_counts.items():
    india_all["documents"].append({"name": dt.replace("_", " ").title(), "type": dt, "count": cnt})

# New India docs
india_new_files = [
    "india_evidence_act.json",
    "india_specific_reliefs.json",
    "india_transfer_of_property.json",
    "india_consumer_protection.json",
    "india_motor_vehicles.json",
    "india_domestic_violence.json",
    "india_information_technology.json",
    "india_negotiable_instruments.json",
    "india_juvenile_justice.json",
    "india_right_to_information.json",
    "india_partnership.json",
    "india_sale_of_goods.json",
]
for fname in india_new_files:
    fpath = PROCESSED_DIR / fname
    if fpath.exists():
        with open(fpath) as f:
            data = json.load(f)
        doc_name = data.get("document_name", fname.replace(".json","").replace("_"," ").title())
        india_all["documents"].append({
            "name": doc_name,
            "type": data.get("document_type", fname.replace(".json","")),
            "count": data["total_articles"],
        })
        india_all["articles"].extend(data["articles"])
        india_all["total_articles"] += data["total_articles"]
        print(f"  Loaded {doc_name}: {data['total_articles']}")

print(f"\nNepal total: {nepal_all['total_articles']}")
print(f"India total: {india_all['total_articles']}")
print(f"Grand total: {nepal_all['total_articles'] + india_all['total_articles']}")

# Minify JSON
nepal_json = json.dumps(nepal_all, ensure_ascii=False, separators=(',', ':'))
india_json = json.dumps(india_all, ensure_ascii=False, separators=(',', ':'))
print(f"Nepal JSON: {len(nepal_json)} bytes")
print(f"India JSON: {len(india_json)} bytes")

# Legal Guides
legal_guides = {
    "nepal": [
        {
            "title": "How to File a Police Report (FIR) in Nepal",
            "icon": "🚔",
            "category": "Criminal Law",
            "steps": [
                "Go to the nearest police station in the area where the offence occurred",
                "Tell the police officer what happened in detail — date, time, place, what was done",
                "The officer will write your statement in Nepali (you can request translation)",
                "Sign the statement after reading it carefully",
                "Ask for a copy of the FIR (First Information Report) — it's your right",
                "Note down the FIR number for future reference",
                "The police must start investigation within 24 hours for serious offences",
            ],
            "important_notes": [
                "Under Section 16 of the Criminal Procedure Code 2074, police MUST register your complaint",
                "If police refuse to register, you can complain to the District Police Office or the Attorney General",
                "Filing a false FIR is a criminal offence — Section 198 of the Penal Code",
                "For domestic violence, you can also file at the Women and Children Service Centre",
            ],
            "time_limit": "Varies by offence. Murder: no limit. Theft: 1 year. Fraud: 6 months.",
            "documents_needed": ["Citizenship certificate or ID", "Evidence (photos, messages, documents)", "Witness details if available"],
        },
        {
            "title": "Filing a Domestic Violence Case in Nepal",
            "icon": "🛡️",
            "category": "Family Law",
            "steps": [
                "You can file at the police station, District Court, or Women and Children Service Centre",
                "Under the Domestic Violence Act 2066, you can get an immediate Protection Order",
                "Tell the court/police about all violence — physical, psychological, sexual, economic",
                "The court can issue Protection Order within 24 hours in urgent cases",
                "You can get maintenance (up to NPR 15,000/month for spouse, NPR 7,500 for child)",
                "The court can order the abuser to leave the shared household",
                "Free legal aid is available through District Legal Aid Committees",
            ],
            "important_notes": [
                "Section 4: Domestic violence includes physical, psychological, sexual, and economic abuse",
                "Section 9: Protection Order can prohibit abuser from contacting you or entering your residence",
                "Section 10: Monetary relief can include maintenance, medical costs, and loss of earnings",
                "Police MUST register your complaint under the Domestic Violence Act",
            ],
            "time_limit": "Within 1 year of the last incident of violence",
            "documents_needed": ["Citizenship certificate", "Medical reports (if injured)", "Photos of injuries", "Witness details", "Marriage certificate (if married)"],
        },
        {
            "title": "Tenant Rights and Eviction in Nepal",
            "icon": "🏠",
            "category": "Property Law",
            "steps": [
                "Check your rental agreement — it governs the tenancy terms",
                "Under the National Civil Code 2074, landlord must give 3 months notice before eviction",
                "Rent can only be increased with proper notice (typically 3 months)",
                "Landlord cannot evict you without a court order",
                "If evicted illegally, you can file a case at the District Court",
                "Keep all rent receipts as proof of payment",
                "For disputes, try mediation first at the local ward office",
            ],
            "important_notes": [
                "Civil Code Section 284-300 governs lease/rental agreements",
                "Landlord must maintain the property in habitable condition",
                "Tenant has right to peaceful enjoyment of the premises",
                "Security deposit must be returned at end of tenancy (minus legitimate deductions)",
            ],
            "time_limit": "3 years for filing rent-related disputes",
            "documents_needed": ["Rental agreement", "Rent receipts", "Citizenship certificate", "Communication records with landlord"],
        },
        {
            "title": "Child Custody and Guardianship in Nepal",
            "icon": "👶",
            "category": "Family Law",
            "steps": [
                "Under the Civil Code 2074, both parents have equal rights to custody",
                "For children under 5, mother is generally given custody (Section 115)",
                "For children over 5, the court considers the child's best interest",
                "File a case at the District Court in the child's place of residence",
                "The court will hear from both parents and may appoint a welfare officer",
                "Maintenance must be paid by the non-custodial parent",
                "Visitation rights can be requested even if custody is denied",
            ],
            "important_notes": [
                "Section 114-118 of Civil Code 2074 governs custody",
                "The child's own wish is considered if they are over 10 years old",
                "Grandparents can also seek visitation rights",
                "Changing custody requires a new court order",
            ],
            "time_limit": "Can be filed at any time during the child's minority",
            "documents_needed": ["Birth certificate of child", "Marriage/divorce certificate", "Proof of income", "Evidence of living arrangements", "School records of child"],
        },
        {
            "title": "Filing a Consumer Complaint in Nepal",
            "icon": "🛒",
            "category": "Consumer Law",
            "steps": [
                "First try to resolve directly with the seller/service provider in writing",
                "If unresolved, file a complaint at the District Consumer Forum",
                "Complaint must be filed within 1 year of the deficiency",
                "Attach all evidence: bills, warranty cards, correspondence",
                "The Forum will hear both parties and give a decision within 90 days",
                "Compensation up to NPR 100,000 can be awarded by District Forum",
                "Appeal lies to the National Consumer Forum above NPR 100,000",
            ],
            "important_notes": [
                "Consumer Protection Act 2075 covers goods and services",
                "E-commerce transactions are also covered",
                "No court fee for complaints below NPR 50,000",
                "Legal aid available for consumers",
            ],
            "time_limit": "1 year from date of deficiency",
            "documents_needed": ["Purchase receipt/bill", "Warranty card", "Written complaint to seller", "Response from seller (if any)", "Evidence of defect/deficiency"],
        },
    ],
    "india": [
        {
            "title": "Filing an FIR in India",
            "icon": "🚔",
            "category": "Criminal Law",
            "steps": [
                "Go to the police station within whose jurisdiction the crime occurred",
                "Tell the Station House Officer (SHO) what happened",
                "The SHO is legally bound to register the FIR under Section 154 of CrPC",
                "Your statement will be recorded in writing",
                "Read the FIR carefully before signing",
                "Get a free copy of the FIR — this is your legal right",
                "Note the FIR number and police station details",
            ],
            "important_notes": [
                "Under Section 154 CrPC, police MUST register FIR for cognizable offences",
                "If police refuse, you can send your complaint to the Superintendent of Police by post",
                "You can also file an e-FIR on the police website of your state",
                "Zero FIR: You can file FIR at any police station regardless of jurisdiction",
                "Filing false FIR is punishable under Section 182/211 IPC",
            ],
            "time_limit": "No time limit for serious offences (murder, rape). Other offences: 1-3 years depending on the crime.",
            "documents_needed": ["ID proof (Aadhaar/PAN)", "Evidence (CCTV, photos, messages)", "Witness details", "Medical report (if assault)"],
        },
        {
            "title": "Domestic Violence Protection in India",
            "icon": "🛡️",
            "category": "Family Law",
            "steps": [
                "You can file a complaint at the police station or directly at the Magistrate's court",
                "Under the DV Act 2005, you can get a Protection Order within 24 hours",
                "The court can order: Protection Order, Residence Order, Monetary Relief, Custody Order",
                "You can also approach the Protection Officer or Service Provider",
                "Free legal aid is available under Section 12 of the DV Act",
                "The Magistrate can direct the respondent to undergo counselling",
                "A Dowry Prohibition Officer can also help",
            ],
            "important_notes": [
                "Section 3: Domestic violence includes physical, sexual, verbal, emotional, and economic abuse",
                "Section 18: Protection Order prohibits violence and contact",
                "Section 19: Residence Order protects your right to shared household",
                "Section 20: Monetary relief up to maintenance + medical + damages",
                "Section 21: Custody of children can be granted to the aggrieved person",
                "Applies to wife, mother, sister, widows, women in live-in relationships",
            ],
            "time_limit": "No time limit — can file anytime during or after the relationship",
            "documents_needed": ["ID proof", "Marriage certificate or proof of relationship", "Medical reports", "Photos of injuries", "Proof of shared household", "Salary/income proof of respondent"],
        },
        {
            "title": "Cheque Bounce — Legal Process in India",
            "icon": "💸",
            "category": "Financial Law",
            "steps": [
                "When a cheque bounces, the bank issues a 'Cheque Return Memo' with the reason",
                "Send a legal demand notice to the cheque drawer within 30 days of receiving the memo",
                "The notice must demand payment within 15 days from receipt",
                "If the drawer doesn't pay within 15 days, you can file a criminal case",
                "File the case in the court within 30 days after the 15-day notice period",
                "The case is filed under Section 138 of the Negotiable Instruments Act",
                "The court can impose imprisonment up to 2 years and/or fine up to twice the cheque amount",
            ],
            "important_notes": [
                "Section 138 NI Act: Cheque bounce is a criminal offence",
                "Mandatory: You MUST send a demand notice before filing a case",
                "The notice must be sent by registered post or speed post",
                "Keep proof of dispatch and delivery of the notice",
                "Compoundable offence — can be settled out of court with 75% payment",
            ],
            "time_limit": "30 days for notice, 30 days for filing case after notice period expires",
            "documents_needed": ["Bounced cheque", "Cheque return memo from bank", "Copy of demand notice", "Proof of sending notice (registered post receipt)", "Proof of delivery"],
        },
        {
            "title": "Cyber Crime — How to Report in India",
            "icon": "💻",
            "category": "Cyber Law",
            "steps": [
                "For online fraud/hacking, file a complaint at your local police station",
                "You can also report online at https://cybercrime.gov.in (National Cyber Crime Portal)",
                "Call the Cyber Crime Helpline: 1930 (24x7)",
                "For email-related crimes, report to the IT Act cells",
                "Preserve all evidence — screenshots, emails, transaction records",
                "Contact your bank immediately for financial fraud to freeze the account",
                "File under the Information Technology Act 2000 sections applicable to your case",
            ],
            "important_notes": [
                "Section 43 IT Act: Unauthorized access — compensation up to ₹5 crore",
                "Section 66 IT Act: Hacking — imprisonment up to 3 years + fine up to ₹5 lakh",
                "Section 66C IT Act: Identity theft — imprisonment up to 3 years + fine up to ₹1 lakh",
                "Section 66D IT Act: Cheating by impersonation — imprisonment up to 3 years + fine up to ₹1 lakh",
                "Section 66E IT Act: Privacy violation — imprisonment up to 3 years + fine up to ₹2 lakh",
                "Section 67 IT Act: Publishing obscene material — imprisonment up to 5 years + fine up to ₹10 lakh",
            ],
            "time_limit": "3 years for most cyber offences",
            "documents_needed": ["Screenshots of the crime", "URLs/links", "Email/chat records", "Bank statements (if financial fraud)", "ID proof", "Complaint to platform (if any)"],
        },
        {
            "title": "Tenant Rights and Eviction Process in India",
            "icon": "🏠",
            "category": "Property Law",
            "steps": [
                "Check your rental agreement for notice period and termination clauses",
                "Under the Rent Control Act (varies by state), landlord must give proper notice",
                "Usually 1-3 months notice is required depending on the state",
                "Landlord cannot evict without a court order",
                "If you receive an eviction notice, respond in writing within the notice period",
                "You can challenge eviction in court if you have valid grounds",
                "For disputes, approach the Rent Control Court or Civil Court",
            ],
            "important_notes": [
                "Transfer of Property Act Section 105-117 governs leases",
                "Rent Control Acts vary by state — check your state's specific law",
                "Landlord cannot cut electricity/water or use force to evict",
                "Security deposit must be returned with legitimate deductions only",
                "Tenant has right to essential repairs by landlord",
            ],
            "time_limit": "3-12 years depending on the state's limitation period",
            "documents_needed": ["Rental agreement", "Rent receipts", "ID proof", "Communication with landlord", "Photos of property condition"],
        },
        {
            "title": "Motor Vehicle Accident Claim Process in India",
            "icon": "🚗",
            "category": "Motor Law",
            "steps": [
                "First, ensure medical treatment — your health is priority",
                "File an FIR at the nearest police station if there are injuries",
                "Get the other driver's insurance details and vehicle number",
                "Send a legal notice to the at-fault party's insurance company",
                "File a claim at the Motor Accident Claims Tribunal (MACT) in your area",
                "The tribunal can award: medical expenses, lost wages, pain and suffering, vehicle repair",
                "No court fee for claims up to ₹5,000",
            ],
            "important_notes": [
                "Motor Vehicles Act 1988 Section 166: Claims Tribunal handles accident compensation",
                "Section 163A: No-fault liability — automatic compensation for death/disability",
                "Section 140: No-fault compensation of ₹50,000 for death, ₹25,000 for injury",
                "Section 166: Fault-based compensation — can be much higher",
                "Must file within 6 months of the accident",
            ],
            "time_limit": "6 months from date of accident (extendable up to 2 years in special circumstances)",
            "documents_needed": ["FIR copy", "Medical records and bills", "Death certificate (if fatal)", "Insurance policy details", "Vehicle details", "Salary proof (for lost wages)", "Repair estimate"],
        },
    ],
}

# Legal Templates
legal_templates = {
    "will": {
        "title": "Last Will and Testament",
        "nepal_title": "अन्तिम इच्छा र सम्पत्ति बाँडफाँड",
        "content": """LAST WILL AND TESTAMENT

I, [YOUR FULL NAME], son/daughter of [FATHER'S NAME], residing at [FULL ADDRESS], holder of Citizenship Number [NUMBER], do hereby declare this to be my last Will and Testament:

1. REVOCATION: I hereby revoke all previous wills and codicils made by me.

2. APPOINTMENT OF EXECUTOR: I appoint [EXECUTOR NAME], son/daughter of [FATHER'S NAME], residing at [ADDRESS], as the Executor of this Will.

3. FUNERAL DIRECTIVES: My body shall be [buried/cremated] according to [religious/cultural] customs.

4. DEBTS AND LIABILITIES: I direct that all my just debts, funeral expenses, and costs of administration be paid from my estate.

5. DISTRIBUTION OF PROPERTY:

   a) My residential property at [ADDRESS] shall devolve upon [NAME(S)].
   
   b) My bank account(s) at [BANK NAME], account number(s) [NUMBER(S)], shall devolve upon [NAME(S)].
   
   c) My personal belongings, jewelry, and household items shall devolve upon [NAME(S)].
   
   d) My [other property description] shall devolve upon [NAME(S)].

6. GUARDIANSHIP OF MINOR CHILDREN: In the event of my death, I appoint [NAME] as the legal guardian of my minor children [CHILDREN'S NAMES].

7. RESIDUARY ESTATE: Any property not specifically mentioned above shall be distributed equally among [NAMES/RELATIONSHIPS].

8. This Will is made by me of my own free will, without any coercion or undue influence, and I am of sound mind and legal age.

Signed on this [DAY] day of [MONTH], [YEAR].

_______________________________
[YOUR FULL NAME]
Signature

WITNESSES:
1. [WITNESS 1 NAME], [ADDRESS], [ID NUMBER]
   Signature: _______________

2. [WITNESS 2 NAME], [ADDRESS], [ID NUMBER]
   Signature: _______________""",
    },
    "power_of_attorney": {
        "title": "General Power of Attorney",
        "nepal_title": "सामान्य बाइनामा पत्र",
        "content": """GENERAL POWER OF ATTORNEY

I, [GRANTOR NAME], son/daughter of [FATHER'S NAME], residing at [ADDRESS], holder of Citizenship Number [NUMBER], do hereby appoint:

ATTORNEY: [ATTORNEY NAME], son/daughter of [FATHER'S NAME], residing at [ADDRESS], holder of Citizenship Number [NUMBER]

As my true and lawful Attorney to act on my behalf in the following matters:

1. To appear before any government office, court, tribunal, or authority on my behalf.

2. To sign, execute, and deliver any documents, contracts, agreements, or instruments on my behalf.

3. To represent me in all matters relating to my property at [PROPERTY DESCRIPTION].

4. To open, operate, and close bank accounts on my behalf at [BANK NAME(S)].

5. To collect and receive any money, dividends, interest, or other payments due to me.

6. To file and prosecute or defend any legal proceedings on my behalf.

7. To sign and submit tax returns and other government filings on my behalf.

8. To do all other acts and things as may be necessary or expedient in connection with the above matters.

This Power of Attorney is given subject to the following conditions:
- [Any specific conditions or limitations]
- [Time limit if any]

This Power of Attorney shall remain in effect until revoked by me in writing.

Signed on this [DAY] day of [MONTH], [YEAR].

_______________________________
[GRANTOR NAME]
Signature

WITNESS 1:
[WITNESS NAME], [ADDRESS], [ID NUMBER]
Signature: _______________

WITNESS 2:
[WITNESS NAME], [ADDRESS], [ID NUMBER]
Signature: _______________""",
    },
    "rental_agreement": {
        "title": "Residential Rental Agreement",
        "nepal_title": "आवासीय भाडा सम्झौता",
        "content": """RESIDENTIAL RENTAL AGREEMENT

This Rental Agreement is made on [DATE] between:

LANDLORD: [LANDLORD NAME], son/daughter of [FATHER'S NAME], residing at [ADDRESS], holder of Citizenship/Aadhaar Number [NUMBER]

TENANT: [TENANT NAME], son/daughter of [FATHER'S NAME], residing at [ADDRESS], holder of Citizenship/Aadhaar Number [NUMBER]

1. PROPERTY: The Landlord agrees to rent to the Tenant the residential property at [FULL ADDRESS], consisting of [NUMBER] rooms, [other details].

2. TERM: The tenancy shall commence on [START DATE] and continue for [DURATION], renewable by mutual written agreement.

3. RENT: The Tenant shall pay monthly rent of [AMOUNT] [NPR/₹], due on the [DAY] of each month.

4. SECURITY DEPOSIT: The Tenant shall pay a security deposit of [AMOUNT] [NPR/₹], refundable at the end of tenancy (subject to legitimate deductions for damages or unpaid rent).

5. UTILITIES: The following utilities shall be paid by the Tenant: [electricity/water/gas/internet]. The Landlord shall pay: [property tax/maintenance].

6. MAINTENANCE: The Landlord shall maintain the property in habitable condition and make necessary repairs. The Tenant shall keep the property clean and report any damage promptly.

7. SUBLETTING: The Tenant shall not sublet the property without prior written consent of the Landlord.

8. TERMINATION: Either party may terminate this agreement by giving [3 MONTHS] written notice. The Landlord may terminate immediately if rent is unpaid for [3] months or for breach of any term.

9. INSPECTION: The Landlord may inspect the property with reasonable notice (48 hours).

10. LAWS: This agreement is governed by the laws of [Nepal/India] and the applicable Rent Control Act.

11. DISPUTES: Any disputes shall be resolved by [mediation/court] in [JURISDICTION].

SIGNED by the parties:

Landlord: _________________________ Date: _________

Tenant: _________________________ Date: _________

WITNESS:
[WITNESS NAME] Signature: _______________""",
    },
    "legal_notice": {
        "title": "Legal Notice Template",
        "nepal_title": "कानुनी नोटिस",
        "content": """LEGAL NOTICE

Date: [DATE]

To:
[RECIPIENT NAME]
[RECIPIENT ADDRESS]

Through: [ADVOCATE NAME], Advocate
[ADVOCATE ADDRESS]

SUBJECT: [BRIEF SUBJECT OF THE NOTICE]

Sir/Madam,

I, [YOUR NAME], son/daughter of [FATHER'S NAME], holder of Citizenship/Aadhaar Number [NUMBER], resident of [ADDRESS], through my Advocate [ADVOCATE NAME], do hereby serve this legal notice upon you as follows:

1. FACTS:
   [State the facts of the case in chronological order]
   [e.g., "That on [DATE], I entered into an agreement with you for [PURPOSE]"]
   [e.g., "That as per the agreement, I paid you [AMOUNT]"]
   [e.g., "That you have failed to [YOUR OBLIGATION]"]

2. DEMAND:
   In view of the above facts, I hereby demand that you:
   a) [Specific demand 1]
   b) [Specific demand 2]
   c) [Specific demand 3]

   within [NUMBER] days from the receipt of this notice.

3. CONSEQUENCES:
   In case of your failure to comply with the above demands within the stipulated time, I shall be constrained to initiate legal proceedings against you for recovery of [AMOUNT], damages, costs, and other reliefs as may be deemed appropriate by the court, at your risk as to costs.

This notice is issued without prejudice to my other rights and remedies available under law.

Place: [CITY]
Date: [DATE]

_______________________________
[YOUR NAME]
(Through Advocate [ADVOCATE NAME])

ADVOCATE'S CERTIFICATE:
I, [ADVOCATE NAME], Advocate, do hereby certify that the contents of this notice are true to the best of my knowledge and that I have duly authorized the issuance of this notice.

Signature: _______________
Bar Registration No: [NUMBER]""",
    },
    "affidavit": {
        "title": "General Affidavit",
        "nepal_title": "साधारण शपथपत्र",
        "content": """AFFIDAVIT

I, [DEPONENT NAME], son/daughter of [FATHER'S NAME], residing at [FULL ADDRESS], holder of Citizenship/Aadhaar Number [NUMBER], do hereby solemnly affirm and state as follows:

1. That I am the deponent of this affidavit and I am well acquainted with the facts stated herein.

2. That [STATE FACT 1 - e.g., "I was born on [DATE] at [PLACE]"]

3. That [STATE FACT 2 - e.g., "I have been residing at the above address since [YEAR]"]

4. That [STATE FACT 3 - e.g., "I am unmarried/married and have [NUMBER] children"]

5. That [STATE FACT 4 - e.g., "I am the owner of the property described as [DESCRIPTION]"]

6. That [STATE FACT 5 - e.g., "The contents of this affidavit are true and correct to the best of my knowledge and belief"]

7. That I am making this affidavit for the purpose of [PURPOSE - e.g., "submitting my application for [REASON]"]

DEPONENT

Verified at [PLACE] on this [DAY] day of [MONTH], [YEAR] that the contents of this affidavit are true and correct to the best of my knowledge and belief, and nothing material has been concealed therefrom.

_______________________________
[DEPONENT NAME]

OATH COMMISSIONER/NOTARY:
Before me,

[NAME]
Oath Commissioner/Notary Public
Date: [DATE]
Seal: _______________""",
    },
}

# Glossary
glossary = [
    {"term": "FIR", "nepal": "प्रथम सूचना प्रतिवेदन", "hindi": "प्रथम सूचना रिपोर्ट (FIR)", "meaning": "First Information Report — initial police report of a crime"},
    {"term": "Bail", "nepal": "जमानत", "hindi": "जमानत", "meaning": "Temporary release of an accused person pending trial"},
    {"term": "Warrant", "nepal": "वारेन्ट", "hindi": "वारंट", "meaning": "Court order authorizing arrest or search"},
    {"term": "Plaint", "nepal": "दावा पत्र", "hindi": "दीवानी वाद पत्र", "meaning": "Document filed to start a civil case"},
    {"term": "Decree", "nepal": "निर्णय", "hindi": "डिक्री", "meaning": "Final court decision in a civil case"},
    {"term": "Injunction", "nepal": "निषेधाज्ञा", "hindi": "निषेधाज्ञा", "meaning": "Court order to do or stop doing something"},
    {"term": "Affidavit", "nepal": "शपथपत्र", "hindi": "शपथपत्र", "meaning": "Sworn written statement made under oath"},
    {"term": "Power of Attorney", "nepal": "बाइनामा पत्र", "hindi": "मुख्तारनामा", "meaning": "Document authorizing someone to act on your behalf"},
    {"term": "Will", "nepal": "अन्तिम इच्छा", "hindi": "वसीयत", "meaning": "Legal document specifying how property is distributed after death"},
    {"term": "Divorce", "nepal": "विवाह विच्छेद", "hindi": "तलाक", "meaning": "Legal dissolution of a marriage"},
    {"term": "Custody", "nepal": "अभिभावकत्व", "hindi": "हिरासत", "meaning": "Legal right to care for a child"},
    {"term": "Maintenance", "nepal": "भरणपोषण", "hindi": "गुजारा भत्ता", "meaning": "Financial support for spouse/children"},
    {"term": "Limitation", "nepal": "सीमाबद्धता", "hindi": "अवधि", "meaning": "Time limit for filing a legal case"},
    {"term": "Jurisdiction", "nepal": "न्यायिक क्षेत्राधिकार", "hindi": "न्यायिकाधिकार", "meaning": "Court's authority to hear a case"},
    {"term": "Appeal", "nepal": "अपील", "hindi": "अपील", "meaning": "Request to a higher court to review a decision"},
    {"term": "Adjournment", "nepal": "स्थगन", "hindi": "स्थगन", "meaning": "Postponement of a court hearing"},
    {"term": "Bench Warrant", "nepal": "बेन्च वारेन्ट", "hindi": "बेन्च वारंट", "meaning": "Court order for arrest of a person who fails to appear"},
    {"term": "Habeas Corpus", "nepal": "बन्दी प्रत्यक्षीकरण", "hindi": "बंदी प्रत्यक्षीकरण", "meaning": "Writ to produce a detained person before court"},
    {"term": "Mandamus", "nepal": "आदेशात्मक रrit", "hindi": "परमादेश", "meaning": "Writ ordering a public official to perform their duty"},
    {"term": "Certiorari", "nepal": "परमादेश", "hindi": "प्रतिशोधात्मक रिट", "meaning": "Writ to quash an order of a lower court"},
]

# Limitation periods
limitation_periods = {
    "nepal": [
        {"case_type": "Murder / Culpable Homicide", "period": "No limitation", "law": "Criminal Procedure Code 2074"},
        {"case_type": "Rape / Sexual Assault", "period": "No limitation", "law": "Criminal Procedure Code 2074"},
        {"case_type": "Kidnapping / Abduction", "period": "No limitation", "law": "Criminal Procedure Code 2074"},
        {"case_type": "Theft", "period": "1 year", "law": "Criminal Procedure Code 2074"},
        {"case_type": "Fraud / Cheating", "period": "6 months", "law": "Criminal Procedure Code 2074"},
        {"case_type": "Criminal Breach of Trust", "period": "6 months", "law": "Criminal Procedure Code 2074"},
        {"case_type": "Defamation", "period": "6 months", "law": "Criminal Procedure Code 2074"},
        {"case_type": "Assault (Simple)", "period": "6 months", "law": "Criminal Procedure Code 2074"},
        {"case_type": "Property Damage", "period": "1 year", "law": "Criminal Procedure Code 2074"},
        {"case_type": "Civil Suit (General)", "period": "3 years", "law": "Civil Procedure Code 2074"},
        {"case_type": "Contract Dispute", "period": "3 years", "law": "Civil Code 2074"},
        {"case_type": "Rent Recovery", "period": "3 years", "law": "Civil Code 2074"},
        {"case_type": "Property Dispute", "period": "12 years", "law": "Civil Code 2074"},
        {"case_type": "Partition Suit", "period": "12 years", "law": "Civil Code 2074"},
        {"case_type": "Domestic Violence", "period": "1 year from last incident", "law": "Domestic Violence Act 2066"},
        {"case_type": "Consumer Complaint", "period": "1 year", "law": "Consumer Protection Act 2075"},
        {"case_type": "Motor Vehicle Accident Claim", "period": "6 months (extendable to 2 years)", "law": "Motor Vehicle Act"},
        {"case_type": "RTI Appeal", "period": "30 days from response", "law": "RTI Act 2064"},
    ],
    "india": [
        {"case_type": "Murder / Culpable Homicide", "period": "No limitation", "law": "Section 468 CrPC"},
        {"case_type": "Rape", "period": "No limitation (if reported within 1 year or victim is minor)", "law": "Section 468 CrPC"},
        {"case_type": "Kidnapping / Abduction", "period": "No limitation", "law": "Section 468 CrPC"},
        {"case_type": "Dowry Death", "period": "No limitation", "law": "Section 468 CrPC"},
        {"case_type": "Theft", "period": "3 years", "law": "Section 468 CrPC"},
        {"case_type": "Fraud / Cheating", "period": "3 years", "law": "Section 468 CrPC"},
        {"case_type": "Criminal Breach of Trust", "period": "3 years", "law": "Section 468 CrPC"},
        {"case_type": "Defamation", "period": "3 years (compoundable)", "law": "Section 468 CrPC"},
        {"case_type": "Cheque Bounce", "period": "30 days for notice + 30 days for case", "law": "Section 138 NI Act"},
        {"case_type": "Civil Suit (General)", "period": "3 years", "law": "Limitation Act 1963"},
        {"case_type": "Contract Dispute", "period": "3 years", "law": "Limitation Act 1963"},
        {"case_type": "Money Recovery", "period": "3 years", "law": "Limitation Act 1963"},
        {"case_type": "Property Dispute", "period": "12 years", "law": "Limitation Act 1963"},
        {"case_type": "Partition Suit", "period": "12 years", "law": "Limitation Act 1963"},
        {"case_type": "Motor Vehicle Accident Claim", "period": "6 months (extendable to 2 years)", "law": "Motor Vehicles Act 1988"},
        {"case_type": "Consumer Complaint", "period": "2 years from cause of action", "law": "Consumer Protection Act 2019"},
        {"case_type": "Domestic Violence", "period": "No time limit", "law": "DV Act 2005"},
        {"case_type": "RTI Appeal", "period": "30 days from response", "law": "RTI Act 2005"},
        {"case_type": "Writ Petition", "period": "No fixed limit (reasonable delay)", "law": "Constitution of India"},
    ],
}

# Emergency contacts
emergency_contacts = {
    "nepal": [
        {"service": "Police Emergency", "number": "100", "note": "All emergencies"},
        {"service": "Police Control", "number": "110", "note": "Police control room"},
        {"service": "Ambulance", "number": "102", "note": "Medical emergency"},
        {"service": "Fire Brigade", "number": "101", "note": "Fire emergency"},
        {"service": "Women Helpline", "number": "1188", "note": "24x7 for women in distress"},
        {"service": "Child Helpline", "number": "1098", "note": "For children in need"},
        {"service": "Tourist Police", "number": "1144", "note": "For tourists"},
        {"service": "Anti-Corruption", "number": "1170", "note": "CIAA"},
        {"service": "National Human Rights Commission", "number": "1166", "note": "Rights violations"},
        {"service": "Legal Aid", "number": "1167", "note": "Free legal assistance"},
    ],
    "india": [
        {"service": "Police Emergency", "number": "100", "note": "All emergencies"},
        {"service": "Ambulance", "number": "108", "note": "Medical emergency"},
        {"service": "Fire Brigade", "number": "101", "note": "Fire emergency"},
        {"service": "Women Helpline", "number": "181", "note": "24x7 for women in distress"},
        {"service": "Women Helpline (Police)", "number": "1091", "note": "Police women's cell"},
        {"service": "Child Helpline", "number": "1098", "note": "For children in need"},
        {"service": "Cyber Crime Helpline", "number": "1930", "note": "Report cyber crimes online at cybercrime.gov.in"},
        {"service": "Anti-Corruption Helpline", "number": "1031", "note": "CBI anti-corruption"},
        {"service": "Consumer Helpline", "number": "1800-11-4000", "note": "National Consumer Helpline"},
        {"service": "Legal Aid", "number": "15100", "note": "NALSA Free Legal Services"},
        {"service": "Road Accident Emergency", "number": "1073", "note": "NHAI Highway helpline"},
        {"service": "Disaster Management", "number": "108", "note": "NDMA"},
    ],
}

# Court hierarchy
court_hierarchy = {
    "nepal": [
        {"level": "Supreme Court", "nepali": "सर्वोच्च अदालत", "jurisdiction": "Final appellate court, constitutional interpretation", "location": "Kathmandu"},
        {"level": "High Court", "nepali": "उच्च अदालत", "jurisdiction": "Appellate and original jurisdiction in fundamental rights cases", "location": "Each province (7 provinces)"},
        {"level": "District Court", "nepali": "जिल्ला अदालत", "jurisdiction": "Original jurisdiction in civil and criminal cases", "location": "Each district (77 districts)"},
        {"level": "Specialized Courts", "nepali": "विशेष अदालतहरू", "jurisdiction": "Labour Court, Revenue Tribunal, etc.", "location": "Various"},
        {"level": "Village/Municipality Court", "nepali": "गाउँपालिका अदालत", "jurisdiction": "Minor civil and criminal disputes", "location": "Local level"},
    ],
    "india": [
        {"level": "Supreme Court", "hindi": "सर्वोच्च न्यायालय", "jurisdiction": "Final appellate court, constitutional interpretation, Article 32 writs", "location": "New Delhi"},
        {"level": "High Court", "hindi": "उच्च न्यायालय", "jurisdiction": "Appellate and original jurisdiction, Article 226 writs", "location": "Each state/UT (25 HCs)"},
        {"level": "District & Sessions Court", "hindi": "जिला एवं सत्र न्यायालय", "jurisdiction": "Original criminal jurisdiction, appellate from lower courts", "location": "Each district"},
        {"level": "Civil Court (Junior Division)", "hindi": "दीवानी न्यायालय", "jurisdiction": "Civil suits up to specified value", "location": "Tehsil/Taluk"},
        {"level": "Metropolitan Magistrate", "hindi": "महानगर मजिस्ट्रेट", "jurisdiction": "Criminal cases in metropolitan areas", "location": "Metro cities"},
        {"level": "Executive Magistrate", "hindi": "कार्यकारी मजिस्ट्रेट", "jurisdiction": "Preventive actions, Section 144, emergencies", "location": "District/Sub-division"},
        {"level": "Family Court", "hindi": "पारिवारिक न्यायालय", "jurisdiction": "Marriage, divorce, custody, maintenance", "location": "Designated cities"},
        {"level": "Consumer Commission", "hindi": "उपभोक्ता आयोग", "jurisdiction": "Consumer disputes", "location": "District/State/National"},
        {"level": "Labour Court / Industrial Tribunal", "hindi": "श्रम न्यायालय", "jurisdiction": "Labour disputes, industrial conflicts", "location": "Various"},
    ],
}

print(f"\nLegal guides: {len(legal_guides['nepal'])} Nepal + {len(legal_guides['india'])} India")
print(f"Templates: {len(legal_templates)}")
print(f"Glossary terms: {len(glossary)}")
print(f"Limitation periods: {len(limitation_periods['nepal'])} Nepal + {len(limitation_periods['india'])} India")
print(f"Emergency contacts: {len(emergency_contacts['nepal'])} Nepal + {len(emergency_contacts['india'])} India")
print(f"Court hierarchy: {len(court_hierarchy['nepal'])} Nepal + {len(court_hierarchy['india'])} India")

# Save all supplementary data
supp_data = {
    "guides": legal_guides,
    "templates": legal_templates,
    "glossary": glossary,
    "limitation_periods": limitation_periods,
    "emergency_contacts": emergency_contacts,
    "court_hierarchy": court_hierarchy,
}
supp_path = PROCESSED_DIR / "supplementary_data.json"
with open(supp_path, "w", encoding="utf-8") as f:
    json.dump(supp_data, f, ensure_ascii=False, indent=2)
print(f"\nSaved supplementary data to {supp_path}")
