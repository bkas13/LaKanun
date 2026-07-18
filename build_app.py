#!/usr/bin/env python3
"""Build the self-contained app.html with smart search, i18n, and onboarding carousel.

Reads minified JSON data and generates a single HTML file that works
offline in any browser with no server required.

Usage:
    python build_app.py
    open app.html
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "app.html"

NEPAL_JSON = "__NEPAL_JSON__"
INDIA_JSON = "__INDIA_JSON__"
SUPP_JSON = "__SUPP_JSON__"


def load_json(name: str) -> dict:
    path = PROCESSED / name
    with open(path, encoding="utf-8") as f:
        return json.load(f)


HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ल Kanun — Nepal & India Legal Corpus</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#F9FAFB;color:#111827}
.sidebar{position:fixed;top:0;left:0;width:260px;height:100vh;background:#1F2937;color:#E5E7EB;padding:1.5rem 1rem;overflow-y:auto;z-index:10}
.sidebar h2{color:#F9FAFB;font-size:1.3rem;margin-bottom:.25rem}
.sidebar .tagline{color:#9CA3AF;font-size:.75rem;margin-bottom:1rem}
.sidebar hr{border:none;border-top:1px solid #374151;margin:.75rem 0}
.sidebar label{display:block;font-size:.75rem;color:#9CA3AF;margin-bottom:.3rem;margin-top:.75rem;text-transform:uppercase;letter-spacing:.05em}
.sidebar select{width:100%;padding:.5rem;border-radius:6px;border:1px solid #4B5563;background:#374151;color:#E5E7EB;font-size:.85rem}
.sidebar .stats{display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin-top:.75rem}
.sidebar .stat{background:rgba(255,255,255,.05);border-radius:8px;padding:.6rem;text-align:center}
.sidebar .stat .val{font-size:1.2rem;font-weight:700;color:#F9FAFB}
.sidebar .stat .lbl{font-size:.7rem;color:#9CA3AF}
.sidebar .disclaimer{font-size:.7rem;color:#6B7280;font-style:italic;margin-top:1rem;padding:.5rem;background:rgba(255,255,255,.05);border-radius:6px}
.sidebar .doc-list{font-size:.7rem;color:#9CA3AF;margin-top:.5rem;line-height:1.6}
.sidebar .doc-list b{color:#D1D5DB}
.main{margin-left:260px;padding:2rem 2.5rem;max-width:1100px}
.header{text-align:center;margin-bottom:2rem}
.header h1{font-size:2rem;font-weight:700;color:#111827}
.header p{color:#6B7280;font-size:.95rem;margin-top:.25rem}
.tabs{display:flex;gap:0;border-bottom:2px solid #E5E7EB;margin-bottom:1.5rem;flex-wrap:wrap}
.tab{padding:.6rem 1.25rem;cursor:pointer;font-size:.85rem;font-weight:500;color:#6B7280;border-bottom:2px solid transparent;margin-bottom:-2px;transition:color .15s}
.tab:hover{color:#111827}
.tab.active{color:#111827;font-weight:600;border-bottom-color:#111827}
.tab-content{display:none}.tab-content.active{display:block}
.search-row{display:flex;gap:.75rem;margin-bottom:1rem;align-items:end;flex-wrap:wrap}
.search-row .field{flex:1;min-width:150px}
.search-row label{font-size:.75rem;color:#6B7280;display:block;margin-bottom:.3rem}
.search-row input,.search-row select{width:100%;padding:.55rem .75rem;border:1px solid #D1D5DB;border-radius:6px;font-size:.85rem}
.search-row input:focus,.search-row select:focus{outline:none;border-color:#6366F1;box-shadow:0 0 0 2px rgba(99,102,241,.15)}
.btn{padding:.55rem 1.25rem;border:none;border-radius:6px;font-size:.85rem;font-weight:500;cursor:pointer;transition:background .15s}
.btn-primary{background:#111827;color:white}.btn-primary:hover{background:#374151}
.card{background:white;border:1px solid #E5E7EB;border-radius:8px;padding:1rem;margin:.5rem 0;border-left:3px solid #D1D5DB;cursor:pointer}
.card:hover{border-left-color:#6366F1}
.card .meta{font-size:.75rem;color:#9CA3AF;margin-bottom:.5rem}
.card .title{font-weight:600;color:#111827;font-size:.9rem}
.card .text{font-size:.8rem;color:#6B7280;margin-top:.5rem;line-height:1.5;white-space:pre-wrap;display:none}
.badge{display:inline-block;padding:.15rem .5rem;border-radius:100px;font-size:.65rem;font-weight:500;background:#F3F4F6;color:#374151;margin-right:.25rem}
.badge-nepal{background:#FEF2F2;color:#991B1B}.badge-india{background:#EFF6FF;color:#1E40AF}
.part-header{background:#F3F4F6;padding:.5rem .85rem;border-radius:6px;margin:.6rem 0 .4rem 0;font-weight:600;color:#1F2937;font-size:.85rem;border:1px solid #E5E7EB}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin-bottom:1rem}
.metric{background:white;border:1px solid #E5E7EB;border-radius:8px;padding:.75rem;text-align:center;border-left:3px solid #D1D5DB}
.metric .val{font-size:1.3rem;font-weight:700;color:#111827}.metric .lbl{font-size:.7rem;color:#9CA3AF}
.about-card{background:white;border:1px solid #E5E7EB;border-radius:8px;padding:1.25rem;margin:.75rem 0;border-left:3px solid #6366F1}
.results-info{font-size:.85rem;color:#6B7280;margin-bottom:.75rem}
.sidebar::-webkit-scrollbar{width:4px}.sidebar::-webkit-scrollbar-thumb{background:#4B5563;border-radius:2px}
.guide-card{background:white;border:1px solid #E5E7EB;border-radius:8px;padding:1.25rem;margin:.75rem 0;cursor:pointer}
.guide-card:hover{border-left:3px solid #6366F1}
.guide-card h3{font-size:.95rem;color:#111827;margin-bottom:.5rem}
.guide-card .cat{font-size:.7rem;color:#9CA3AF;margin-bottom:.5rem}
.guide-card .steps{display:none;margin-top:.75rem}
.guide-card .steps ol{padding-left:1.25rem;line-height:1.8;font-size:.8rem;color:#374151}
.guide-card .notes{margin-top:.75rem;padding:.5rem;background:#FEF2F2;border-radius:6px;font-size:.75rem;color:#991B1B}
.guide-card .time{margin-top:.5rem;font-size:.75rem;color:#6B7280}
.guide-card .docs{margin-top:.5rem;font-size:.75rem;color:#6B7280}
.template-card{background:white;border:1px solid #E5E7EB;border-radius:8px;padding:1.25rem;margin:.75rem 0}
.template-card h3{font-size:.95rem;color:#111827;margin-bottom:.25rem}
.template-card .nep{font-size:.8rem;color:#6B7280;margin-bottom:.75rem}
.template-card pre{background:#F3F4F6;padding:1rem;border-radius:6px;font-size:.75rem;line-height:1.6;white-space:pre-wrap;max-height:400px;overflow-y:auto;display:none}
.glossary-table{width:100%;border-collapse:collapse;font-size:.8rem}
.glossary-table th{background:#F3F4F6;padding:.5rem;text-align:left;font-weight:600;border-bottom:2px solid #E5E7EB}
.glossary-table td{padding:.5rem;border-bottom:1px solid #E5E7EB}
.glossary-table tr:hover{background:#F9FAFB}
.limitation-table{width:100%;border-collapse:collapse;font-size:.8rem}
.limitation-table th{background:#F3F4F6;padding:.5rem;text-align:left;font-weight:600;border-bottom:2px solid #E5E7EB}
.limitation-table td{padding:.5rem;border-bottom:1px solid #E5E7EB}
.contact-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:.75rem}
.contact-item{background:white;border:1px solid #E5E7EB;border-radius:8px;padding:1rem;text-align:center}
.contact-item .num{font-size:1.5rem;font-weight:700;color:#6366F1}
.contact-item .svc{font-size:.85rem;font-weight:600;color:#111827;margin:.25rem 0}
.contact-item .note{font-size:.7rem;color:#6B7280}
mark{background:#FEF08A;border-radius:2px;padding:0 2px}
.onb-overlay{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:100;display:flex;align-items:center;justify-content:center}
.onb-overlay.hidden{display:none}
.onb-card{background:white;border-radius:16px;max-width:680px;width:92%;padding:2.5rem 2.5rem 1.75rem;position:relative;box-shadow:0 25px 60px rgba(0,0,0,.3)}
.onb-card h2{font-size:1.35rem;color:#111827;margin-bottom:.6rem}
.onb-card p{font-size:.9rem;color:#4B5563;line-height:1.7;margin-bottom:.75rem}
.onb-card .onb-icon{font-size:2.25rem;margin-bottom:.6rem}
.onb-dots{display:flex;gap:.5rem;justify-content:center;margin:1rem 0}
.onb-dot{width:8px;height:8px;border-radius:50%;background:#D1D5DB}
.onb-dot.active{background:#6366F1;width:20px;border-radius:4px}
.onb-nav{display:flex;justify-content:space-between;align-items:center;margin-top:1rem}
.onb-skip{font-size:.8rem;color:#9CA3AF;cursor:pointer;border:none;background:none}
.onb-skip:hover{color:#6B7280}
.onb-next{padding:.5rem 1.25rem;border:none;border-radius:6px;font-size:.85rem;font-weight:500;cursor:pointer;background:#111827;color:white}
.onb-next:hover{background:#374151}
.onb-close{position:absolute;top:1rem;right:1rem;font-size:1.2rem;color:#9CA3AF;cursor:pointer;border:none;background:none;line-height:1}
.onb-close:hover{color:#111827}
</style>
</head>
<body>

<div class="onb-overlay" id="onbOverlay">
<div class="onb-card">
<button class="onb-close" onclick="dismissOnboarding()">&times;</button>
<div class="onb-icon" id="onbIcon"></div>
<h2 id="onbTitle"></h2>
<p id="onbText"></p>
<div class="onb-dots" id="onbDots"></div>
<div class="onb-nav">
<button class="onb-skip" onclick="dismissOnboarding()" data-i18n="onb_skip">Skip</button>
<button class="onb-next" id="onbNext" onclick="nextOnboarding()">Next</button>
</div>
</div>
</div>

<div class="sidebar">
<h2>⚖️ ल Kanun</h2>
<div class="tagline" data-i18n="tagline">कानुनी जानकारी प्रणाली</div>
<hr>
<label data-i18n="lbl_language">Language</label>
<select id="langSelect" onchange="switchLang(this.value)">
<option value="en">English</option>
<option value="ne">नेपाली</option>
<option value="hi">हिन्दी</option>
</select>
<label data-i18n="lbl_country">Country</label>
<select id="countryFilter" onchange="applyFilters()">
<option value="all" data-i18n="opt_all_countries">All Countries</option>
<option value="nepal" data-i18n="opt_nepal">🇳🇵 Nepal</option>
<option value="india" data-i18n="opt_india">🇮🇳 India</option>
</select>
<label data-i18n="lbl_category">Category</label>
<select id="categoryFilter" onchange="applyFilters()"></select>
<label data-i18n="lbl_doc_type">Document Type</label>
<select id="docTypeFilter" onchange="applyFilters()"></select>
<hr>
<div class="stats">
<div class="stat"><div class="val" id="totalNepal">0</div><div class="lbl" data-i18n="lbl_nepal">Nepal</div></div>
<div class="stat"><div class="val" id="totalIndia">0</div><div class="lbl" data-i18n="lbl_india">India</div></div>
<div class="stat" style="grid-column:span 2"><div class="val" id="totalAll">0</div><div class="lbl" data-i18n="lbl_total">Total Provisions</div></div>
</div>
<div class="doc-list" id="docList"></div>
<div class="disclaimer" data-i18n="disclaimer">⚠️ AI-generated legal information. Not professional legal advice.</div>
</div>

<div class="main">
<div class="header">
<h1>⚖️ ल Kanun</h1>
<p data-i18n="header_sub">Complete Legal Corpus — Nepal & Indian Laws</p>
</div>
<div class="tabs">
<div class="tab active" onclick="switchTab('search',this)" data-i18n="tab_search">🔍 Search</div>
<div class="tab" onclick="switchTab('nepal',this)" data-i18n="tab_nepal">🇳🇵 Nepal</div>
<div class="tab" onclick="switchTab('india',this)" data-i18n="tab_india">🇮🇳 India</div>
<div class="tab" onclick="switchTab('guides',this)" data-i18n="tab_guides">📚 Legal Guides</div>
<div class="tab" onclick="switchTab('templates',this)" data-i18n="tab_templates">📄 Templates</div>
<div class="tab" onclick="switchTab('reference',this)" data-i18n="tab_reference">📖 Reference</div>
</div>

<div id="tab-search" class="tab-content active">
<div class="search-row">
<div class="field" style="flex:3">
<label data-i18n="lbl_query">Search Query</label>
<input type="text" id="searchInput" data-i18n-placeholder="ph_search" placeholder="e.g. theft punishment, domestic violence, cheque bounce, child custody, cyber crime" onkeydown="if(event.key==='Enter')doSearch()">
</div>
<div class="field" style="flex:1">
<label data-i18n="lbl_max_results">Max Results</label>
<select id="topK"><option>10</option><option>20</option><option>50</option></select>
</div>
<div class="field" style="flex:0 0 auto">
<button class="btn btn-primary" onclick="doSearch()" data-i18n="btn_search">🔍 Search</button>
</div>
</div>
<div id="searchResults"></div>
</div>

<div id="tab-nepal" class="tab-content">
<div class="metrics" id="nepalMetrics"></div>
<div id="nepalContent"></div>
</div>

<div id="tab-india" class="tab-content">
<div id="indiaContent"></div>
</div>

<div id="tab-guides" class="tab-content">
<div id="guidesContent"></div>
</div>

<div id="tab-templates" class="tab-content">
<div id="templatesContent"></div>
</div>

<div id="tab-reference" class="tab-content">
<div id="referenceContent"></div>
</div>
</div>

<script>
const NEPAL_DATA=__NEPAL_JSON__;
const INDIA_DATA=__INDIA_JSON__;
const SUPP=__SUPP_JSON__;
const ALL=NEPAL_DATA.articles.concat(INDIA_DATA.articles);

const I18N={
en:{
tagline:"Legal Information System",
lbl_language:"Language",lbl_country:"Country",lbl_category:"Category",
lbl_doc_type:"Document Type",lbl_nepal:"Nepal",lbl_india:"India",
lbl_total:"Total Provisions",
disclaimer:"⚠️ AI-generated legal information. Not professional legal advice.",
header_sub:"Complete Legal Corpus — Nepal & Indian Laws",
tab_search:"🔍 Search",tab_nepal:"🇳🇵 Nepal",tab_india:"🇮🇳 India",
tab_guides:"📚 Legal Guides",tab_templates:"📄 Templates",tab_reference:"📖 Reference",
lbl_query:"Search Query",lbl_max_results:"Max Results",btn_search:"🔍 Search",
ph_search:"e.g. theft punishment, domestic violence, cheque bounce",
opt_all_countries:"All Countries",opt_nepal:"🇳🇵 Nepal",opt_india:"🇮🇳 India",
results_found:"Found {{n}} results for",
from_provisions:"(from {{m}} provisions)",
no_results:"No results found. Try different keywords.",
onb_skip:"Skip",onb_next:"Next",onb_done:"Get Started",
onb_steps:[
{icon:"⚖️",title:"Welcome to ल Kanun",text:"6,200+ legal provisions from 28 Nepal & Indian laws — searchable, offline, and free. Whether you're a citizen or a legal professional, this tool puts the law at your fingertips."},
{icon:"👤",title:"For Everyone — Everyday Use",text:"Not sure where to start? Use the search bar to look up common legal topics: theft punishment, domestic violence, cheque bounce, child custody, or property rights. The Legal Guides tab walks you step-by-step through filing a police report, applying for RTI, or contesting a consumer complaint — no lawyer needed to understand your rights."},
{icon:"⚖️",title:"For Legal Professionals",text:"Use the Nepal and India tabs to browse entire statutes section-by-section. Filter by country, category, or document type in the sidebar. Cross-reference provisions across jurisdictions — compare Nepal's Penal Code with India's IPC side by side. The search supports synonym expansion: searching 'homicide' also finds 'murder' and 'culpable homicide'."},
{icon:"🌐",title:"Get the Most Out of It",text:"Switch the language to नेपाली or हिन्दी for instant translation of every UI element. Use country and category filters to narrow results. Click any card to expand the full text. Bookmark this page — it works completely offline, no server or internet needed after first load."},
{icon:"🚀",title:"Ready to Explore?",text:"Start by searching a legal topic, or browse the Nepal and India law tabs. Check Legal Guides for practical how-to walkthroughs. This page works offline — bookmark it for quick access anytime, anywhere."}
]
},
ne:{
tagline:"कानुनी जानकारी प्रणाली",
lbl_language:"भाषा",lbl_country:"देश",lbl_category:"श्रेणी",
lbl_doc_type:"कागजात प्रकार",lbl_nepal:"नेपाल",lbl_india:"भारत",
lbl_total:"कुल विवरणहरू",
disclaimer:"⚠️ AI-जनित कानुनी जानकारी। व्यावसायिक कानुनी सल्लाह होइन।",
header_sub:"सम्पूर्ण कानुनी कोर्पस — नेपाल र भारतीय कानुनहरू",
tab_search:"🔍 खोज्नुहोस्",tab_nepal:"🇳🇵 नेपाल",tab_india:"🇮🇳 भारत",
tab_guides:"📚 कानुनी मार्गदर्शन",tab_templates:"📄 ढाँचाहरू",tab_reference:"📖 सन्दर्भ",
lbl_query:"खोज प्रश्न",lbl_max_results:"अधिकतम परिणाम",btn_search:"🔍 खोज्नुहोस्",
ph_search:"जस्तै: चोरीको सजाय, घरेलु हिंसा, चेक बाउन्स",
opt_all_countries:"सबै देशहरू",opt_nepal:"🇳🇵 नेपाल",opt_india:"🇮🇳 भारत",
results_found:"{{n}} वटा परिणाम भेटियो",
from_provisions:"(मध्ये {{m}} विवरणहरूबाट)",
no_results:"कुनै परिणाम भेटिएन। फरक शब्दहरू प्रयास गर्नुहोस्।",
onb_skip:"छोड्नुहोस्",onb_next:"अर्को",onb_done:"सुरु गर्नुहोस्",
onb_steps:[
{icon:"⚖️",title:"ल Kanun मा स्वागत छ",text:"२८ वटा नेपाल र भारतीय कानुनबाट ६,२००+ कानुनी विवरणहरू — खोज्न मिल्ने, अफलाइन, र निःशुल्क। तपाईं नागरिक हुनुहोस् वा कानुनी पेशेवर, यो उपकरणले कानुन तपाईंको हातमा राख्छ।"},
{icon:"👤",title:"सबैका लागि — दैनिक उपयोग",text:"कहाँबाट सुरु गर्ने थाहा छैन? खोज बारमा सामान्य कानुनी विषयहरू खोज्नुहोस्: चोरीको सजाय, घरेलु हिंसा, चेक बाउन्स, बालबालिकाको हेरचाह, वा सम्पत्तिको अधिकार। कानुनी मार्गदर्शन ट्याबले पुलिस रिपोर्ट दर्ता, RTI आवेदन, वा उपभोक्ता शिकायत दर्ताका लागि कदम-दर-कदम मार्गदर्शन गर्छ — तपाईंको अधिकार बुझ्न कुनै वकील चाहिँदैन।"},
{icon:"⚖️",title:"कानुनी पेशेवरहरूका लागि",text:"नेपाल र भारत ट्याबहरूमा सम्पूर्ण कानुनहरू धारा-अनुसार ब्राउज गर्नुहोस्। साइडबारमा देश, श्रेणी, वा कागजात प्रकारले फिल्टर गर्नुहोस्। विभिन्न अधिकारक्षेत्रहरूमा क्रस-रेफरेन्स गर्नुहोस् — नेपालको दण्ड संहिता र भारतको IPC एकसाथ तुलना गर्नुहोस्। खोजले संज्ञा विस्तार गर्छ: 'homicide' खोज्दा 'murder' र 'culpable homicide' पनि देखिन्छ।"},
{icon:"🌐",title:"पूर्ण रूपमा उपयोग गर्नुहोस्",text:"भाषा नेपाली वा हिन्दीमा स्विच गर्नुहोस् — सबै UI तत्वहरू तुरुन्त अनुवाद हुन्छन्। देश र श्रेणी फिल्टरले नतिजा सीमित गर्नुहोस्। जुनसुकै कार्डमा क्लिक गरेर पूर्ण पाठ विस्तार गर्नुहोस्। यो पृष्ठ बुकमार्क गर्नुहोस् — पहिलो लोडपछि पूर्ण रूपमा अफलाइन काम गर्छ।"},
{icon:"🚀",title:"अन्वेषण गर्न तयार?",text:"कानुनी विषय खोजेर सुरु गर्नुहोस्, वा नेपाल र भारत कानुन ट्याबहरू ब्राउज गर्नुहोस्। व्यावहारिक कसरी-गर्ने मार्गदर्शनका लागि कानुनी मार्गदर्शन जाँच गर्नुहोस्। यो पृष्ठ अफलाइन काम गर्छ — जुनसुकै समय, जुनसुकै ठाउँमा छिटो पहुँचका लागि बुकमार्क गर्नुहोस्।"}
]
},
hi:{
tagline:"कानूनी जानकारी प्रणाली",
lbl_language:"भाषा",lbl_country:"देश",lbl_category:"श्रेणी",
lbl_doc_type:"दस्तावेज़ प्रकार",lbl_nepal:"नेपाल",lbl_india:"भारत",
lbl_total:"कुल प्रावधान",
disclaimer:"⚠️ AI-जनित कानूनी जानकारी। पेशेवर कानूनी सलाह नहीं।",
header_sub:"संपूर्ण कानूनी कोर्पस — नेपाल और भारतीय कानून",
tab_search:"🔍 खोजें",tab_nepal:"🇳🇵 नेपाल",tab_india:"🇮🇳 भारत",
tab_guides:"📚 कानूनी मार्गदर्शन",tab_templates:"📄 टेम्पलेट",tab_reference:"📖 संदर्भ",
lbl_query:"खोज प्रश्न",lbl_max_results:"अधिकतम परिणाम",btn_search:"🔍 खोजें",
ph_search:"जैसे: चोरी की सज़ा, घरेलू हिंसा, चेक बाउंस",
opt_all_countries:"सभी देश",opt_nepal:"🇳🇵 नेपाल",opt_india:"🇮🇳 भारत",
results_found:"{{n}} परिणाम मिले",
from_provisions:"(कुल {{m}} प्रावधानों में से)",
no_results:"कोई परिणाम नहीं मिला। अलग शब्द आज़माएं।",
onb_skip:"छोड़ें",onb_next:"अगला",onb_done:"शुरू करें",
onb_steps:[
{icon:"⚖️",title:"ल Kanun में आपका स्वागत है",text:"नेपाल और भारतीय कानूनों को कवर करने वाली एक व्यापक कानूनी जानकारी प्रणाली। 28 दस्तावेज़ों में 6,200+ कानूनी प्रावधान ब्राउज़ करें — पूरी तरह ऑफलाइन।"},
{icon:"🔍",title:"स्मार्ट कानूनी खोज",text:"विशेषण विस्तार, धुंधला मिलान और परिणाम हाइलाइटिंग के साथ सभी कानूनों में खोजें। 'चोरी', 'हत्या', 'चेक बाउंस' या 'घरेलू हिंसा' जैसे शब्द आज़माएं।"},
{icon:"🌐",title:"बहुभाषिक सहायता",text:"साइडबार में भाषा ड्रॉपडाउन का उपयोग करके अंग्रेजी, नेपाली और हिंदी के बीच स्विच करें। सभी UI तत्व तुरंत अनुवादित होते हैं।"},
{icon:"📚",title:"मार्गदर्शन और टेम्पलेट",text:"मामला दर्ज करने, दस्तावेज़ आवेदन और अधिक के लिए चरण-दर-चरण कानूनी मार्गदर्शन प्राप्त करें। साथ ही तैयार कानूनी दस्तावेज़ टेम्पलेट।"},
{icon:"🚀",title:"शुरू करें",text:"कानूनी विषय खोजकर शुरू करें, या नेपाल और भारत कानून टैब ब्राउज़ करें। कभी भी ऑफलाइन पहुँच के लिए इस पृष्ठ को बुकमार्क करें।"}
]
}
};

function switchLang(lang){
localStorage.setItem('kanun_lang',lang);
document.querySelectorAll('[data-i18n]').forEach(el=>{
const key=el.getAttribute('data-i18n');
if(I18N[lang]&&I18N[lang][key])el.textContent=I18N[lang][key];
});
document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{
const key=el.getAttribute('data-i18n-placeholder');
if(I18N[lang]&&I18N[lang][key])el.placeholder=I18N[lang][key];
});
}

let onbIdx=0;
const onbKey='kanun_onb_seen';

function renderOnboarding(){
const lang=localStorage.getItem('kanun_lang')||'en';
const steps=I18N[lang].onb_steps;
const s=steps[onbIdx];
document.getElementById('onbIcon').textContent=s.icon;
document.getElementById('onbTitle').textContent=s.title;
document.getElementById('onbText').textContent=s.text;
const dotsHtml=steps.map((_,i)=>'<div class="onb-dot'+(i===onbIdx?' active':'')+'"></div>').join('');
document.getElementById('onbDots').innerHTML=dotsHtml;
const nextBtn=document.getElementById('onbNext');
if(onbIdx===steps.length-1){
nextBtn.textContent=I18N[lang].onb_done;
nextBtn.onclick=dismissOnboarding;
}else{
nextBtn.textContent=I18N[lang].onb_next;
nextBtn.onclick=nextOnboarding;
}
const skipBtn=document.querySelector('.onb-skip');
if(skipBtn)skipBtn.textContent=I18N[lang].onb_skip;
}

function nextOnboarding(){
const lang=localStorage.getItem('kanun_lang')||'en';
const steps=I18N[lang].onb_steps;
if(onbIdx<steps.length-1){onbIdx++;renderOnboarding();}
}

function dismissOnboarding(){
document.getElementById('onbOverlay').classList.add('hidden');
localStorage.setItem(onbKey,'1');
}

function checkOnboarding(){
if(!localStorage.getItem(onbKey)){
document.getElementById('onbOverlay').classList.remove('hidden');
onbIdx=0;
renderOnboarding();
}else{
document.getElementById('onbOverlay').classList.add('hidden');
}
}

const STOP_WORDS=new Set(['the','a','an','is','are','was','were','be','been','being',
'have','has','had','do','does','did','will','would','could','should','may','might',
'shall','can','need','dare','ought','used','to','of','in','for','on','with','at',
'by','from','as','into','through','during','before','after','above','below',
'between','out','off','over','under','again','further','then','once','here',
'there','when','where','why','how','all','each','every','both','few','more',
'most','other','some','such','no','nor','not','only','own','same','so',
'than','too','very','just','because','but','and','or','if','while','about',
'against','it','its','this','that','these','those','i','me','my','we','our',
'you','your','he','him','his','she','her','they','them','their','what','which',
'who','whom']);

const SYNONYMS={
theft:['stealing','stolen','robbery','larceny','burglary','shoplifting','pickpocket'],
murder:['homicide','killing','death','manslaughter','culpable','corpse'],
cheque:['check','bounced','bouncing','dishonour','insufficient'],
domestic:['wife','husband','spouse','partner','family','marital','abuse'],
child:['minor','juvenile','kid','children','infant','adolescent'],
cyber:['online','internet','digital','computer','hack','hacking','phishing','email'],
fraud:['scam','cheat','deception','forgery','embezzlement','defraud'],
bail:['bond','release','surety','custody','arrested'],
marriage:['wedding','matrimonial','divorce','spouse','husband','wife'],
property:['land','real estate','house','building','immovable','premises'],
employment:['worker','employee','labour','labor','job','wages','salary','employer'],
accident:['collision','crash','injury','motor','vehicle','road'],
evidence:['proof','testimonial','documentary','witness','exhibit'],
contract:['agreement','deal','pact','covenant','promise','obligation'],
consumer:['buyer','purchaser','customer','deficiency','complaint'],
negotiable:['instrument','promissory','bill of exchange','cheque'],
partnership:['partner','firm','business','LLP','co-partner'],
goods:['product','commodity','item','wares','merchandise'],
election:['vote','voting','ballot','candidate','constituency'],
amendment:['modification','alteration','change','revision','repeal'],
penalty:['punishment','sentence','fine','imprisonment','jail'],
court:['tribunal','judge','justice','bench','judiciary','magistrate'],
appeal:['revision','review','petition','challenge','litigation'],
warrant:['summons','notice','order','direction','decree'],
intellectual:['patent','trademark','copyright','IP','royalty']
};

function expandQuery(q){
const words=q.toLowerCase().split(/\s+/).filter(w=>w.length>2&&!STOP_WORDS.has(w));
const expanded=new Set(words);
for(const w of words){
for(const[syns,terms]of Object.entries(SYNONYMS)){
const group=[syns,...terms];
if(group.some(g=>w.includes(g)||g.includes(w)))group.forEach(t=>expanded.add(t));
}
}
return[...expanded];
}

function fuzzyScore(text,term){
const idx=text.indexOf(term);
if(idx===-1)return 0;
let score=5;
if(idx===0)score+=3;
const before=idx>0?text[idx-1]:' ';
if(before===' '||before==='\n')score+=2;
return score;
}

function smartSearch(query){
const q=query.toLowerCase().trim();
if(!q)return[];
const expanded=expandQuery(q);
const filtered=getFiltered();
const results=[];
for(const a of filtered){
const text=(a.full_text+' '+a.title).toLowerCase();
const titleLower=a.title.toLowerCase();
let score=0;
if(text.includes(q))score+=15;
if(titleLower.includes(q))score+=12;
for(const t of expanded){
if(t.length<3)continue;
score+=fuzzyScore(text,t)*0.8;
score+=fuzzyScore(titleLower,t);
}
const countryBoost=a.country==='nepal'?1.05:1.0;
score*=countryBoost;
if(score>0)results.push({a,score,expanded});
}
results.sort((x,y)=>y.score-x.score);
return results;
}

function highlightTerms(text,query,expanded){
let escaped=query.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
let result=text.replace(new RegExp('('+escaped+')','gi'),'<mark>$1</mark>');
for(const t of expanded){
if(t.length<3||t===query)continue;
const tEscaped=t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
result=result.replace(new RegExp('('+tEscaped+')','gi'),'<mark>$1</mark>');
}
return result;
}

document.getElementById('totalNepal').textContent=NEPAL_DATA.total_articles;
document.getElementById('totalIndia').textContent=INDIA_DATA.total_articles;
document.getElementById('totalAll').textContent=ALL.length;

let docListHtml='<b>Nepal:</b><br>';
NEPAL_DATA.documents.forEach(d=>{docListHtml+='• '+d.name+' ('+d.count+')<br>'});
docListHtml+='<br><b>India:</b><br>';
INDIA_DATA.documents.forEach(d=>{docListHtml+='• '+d.name+' ('+d.count+')<br>'});
document.getElementById('docList').innerHTML=docListHtml;

const cats=[...new Set(ALL.map(a=>a.category))].sort();
document.getElementById('categoryFilter').innerHTML='<option value="all">All Categories</option>'+cats.map(c=>'<option value="'+c+'">'+c.replace(/_/g,' ')+'</option>').join('');

const docTypes=[...new Set(ALL.map(a=>a.document_type))].sort();
document.getElementById('docTypeFilter').innerHTML='<option value="all">All Types</option>'+docTypes.map(d=>'<option value="'+d+'">'+d.replace(/_/g,' ')+'</option>').join('');

function switchTab(name,el){
document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
el.classList.add('active');
document.getElementById('tab-'+name).classList.add('active');
}

function getFiltered(){
const c=document.getElementById('countryFilter').value;
const cat=document.getElementById('categoryFilter').value;
const dt=document.getElementById('docTypeFilter').value;
return ALL.filter(a=>{
if(c!=='all'&&a.country!==c)return false;
if(cat!=='all'&&a.category!==cat)return false;
if(dt!=='all'&&a.document_type!==dt)return false;
return true;
});
}

function applyFilters(){}

function doSearch(){
const q=document.getElementById('searchInput').value.trim();
if(!q)return;
const topK=parseInt(document.getElementById('topK').value);
const lang=localStorage.getItem('kanun_lang')||'en';
const t=I18N[lang];
const results=smartSearch(q);
const top=results.slice(0,topK);
let html='<div class="results-info">'+t.results_found.replace('{{n}}',top.length)+' "'+q+'" '+t.from_provisions.replace('{{m}}',getFiltered().length)+'</div>';
for(const r of top){
const a=r.a;
const bc=a.country==='nepal'?'badge-nepal':'badge-india';
const dn=a.document_type?a.document_type.replace(/_/g,' '):'';
const hl=highlightTerms(a.full_text.substring(0,2000),q,r.expanded);
const hlTitle=highlightTerms(a.title,q,r.expanded);
html+='<div class="card" onclick="this.querySelector(\'.text\').style.display=this.querySelector(\'.text\').style.display===\'none\'?\'block\':\'none\'">';
html+='<div class="meta"><span class="badge '+bc+'">'+a.country.toUpperCase()+'</span> <span class="badge">'+dn+'</span> <span class="badge">'+a.category.replace(/_/g,' ')+'</span> Art/Sec '+a.article_number+' — Score: '+Math.round(r.score)+'</div>';
html+='<div class="title">'+hlTitle+'</div>';
html+='<div class="text">'+hl+'</div>';
html+='</div>';
}
if(top.length===0)html+='<div style="padding:1rem;color:#9CA3AF;font-size:.85rem">'+t.no_results+'</div>';
document.getElementById('searchResults').innerHTML=html;
}

(function(){
const m=document.getElementById('nepalMetrics');
NEPAL_DATA.documents.forEach(d=>{m.innerHTML+='<div class="metric"><div class="val">'+d.count+'</div><div class="lbl">'+d.name+'</div></div>'});
const byDoc={};
for(const a of NEPAL_DATA.articles){const d=a.document_type||'constitution';if(!byDoc[d])byDoc[d]=[];byDoc[d].push(a)}
let html='';
for(const[doc,arts]of Object.entries(byDoc)){
html+='<div class="part-header">📄 '+doc.replace(/_/g,' ').replace(/\b\w/g,l=>l.toUpperCase())+' ('+arts.length+')</div>';
for(const a of arts.slice(0,30)){
html+='<div class="card" onclick="this.querySelector(\'.text\').style.display=this.querySelector(\'.text\').style.display===\'none\'?\'block\':\'none\'">';
html+='<div class="meta"><span class="badge badge-nepal">NEPAL</span> <span class="badge">'+a.category.replace(/_/g,' ')+'</span> Sec '+a.article_number+'</div>';
html+='<div class="title">'+a.title+'</div>';
html+='<div class="text">'+a.full_text+'</div>';
html+='</div>';
}
if(arts.length>30)html+='<div style="font-size:.75rem;color:#9CA3AF;padding:.25rem .5rem">... and '+(arts.length-30)+' more</div>';
}
document.getElementById('nepalContent').innerHTML=html;
})();

(function(){
const byDoc={};
for(const a of INDIA_DATA.articles){const d=a.source_document||a.document_type||'Unknown';if(!byDoc[d])byDoc[d]=[];byDoc[d].push(a)}
let html='<div class="metrics">';
for(const[d,arts]of Object.entries(byDoc)){html+='<div class="metric"><div class="val">'+arts.length+'</div><div class="lbl">'+d.replace(/_/g,' ')+'</div></div>'}
html+='</div>';
for(const[d,arts]of Object.entries(byDoc)){
html+='<div class="part-header">📄 '+d.replace(/_/g,' ').replace(/\b\w/g,l=>l.toUpperCase())+' ('+arts.length+')</div>';
for(const a of arts.slice(0,25)){
html+='<div class="card" onclick="this.querySelector(\'.text\').style.display=this.querySelector(\'.text\').style.display===\'none\'?\'block\':\'none\'">';
html+='<div class="meta"><span class="badge badge-india">INDIA</span> <span class="badge">'+a.category.replace(/_/g,' ')+'</span> Sec '+a.article_number+'</div>';
html+='<div class="title">'+a.title+'</div>';
html+='<div class="text">'+a.full_text.substring(0,1500)+'</div>';
html+='</div>';
}
if(arts.length>25)html+='<div style="font-size:.75rem;color:#9CA3AF;padding:.5rem">... and '+(arts.length-25)+' more</div>';
}
document.getElementById('indiaContent').innerHTML=html;
})();

(function(){
let html='';
['nepal','india'].forEach(country=>{
const flag=country==='nepal'?'🇳🇵':'🇮🇳';
html+='<h2 style="font-size:1.1rem;margin:1rem 0 .5rem 0">'+flag+' '+country.charAt(0).toUpperCase()+country.slice(1)+' Legal Guides</h2>';
SUPP.guides[country].forEach(g=>{
html+='<div class="guide-card" onclick="this.querySelector(\'.steps\').style.display=this.querySelector(\'.steps\').style.display===\'none\'?\'block\':\'none\'">';
html+='<h3>'+g.icon+' '+g.title+'</h3>';
html+='<div class="cat">'+g.category+'</div>';
html+='<div class="steps">';
html+='<ol>'+g.steps.map(s=>'<li>'+s+'</li>').join('')+'</ol>';
if(g.important_notes)html+='<div class="notes"><b>⚠️ Important:</b><br>'+g.important_notes.map(n=>'• '+n).join('<br>')+'</div>';
if(g.time_limit)html+='<div class="time"><b>⏰ Time Limit:</b> '+g.time_limit+'</div>';
if(g.documents_needed)html+='<div class="docs"><b>📋 Documents Needed:</b> '+g.documents_needed.join(', ')+'</div>';
html+='</div></div>';
});
});
document.getElementById('guidesContent').innerHTML=html;
})();

(function(){
let html='<p style="color:#6B7280;font-size:.85rem;margin-bottom:1rem">Click a template to view and copy. Fill in [BRACKETED] fields with your information.</p>';
for(const[key,t]of Object.entries(SUPP.templates)){
html+='<div class="template-card">';
html+='<h3>'+t.title+'</h3>';
html+='<div class="nep">'+t.nepal_title+'</div>';
html+='<pre onclick="this.style.display=this.style.display===\'none\'?\'block\':\'none\'" style="cursor:pointer;color:#6366F1;font-size:.8rem;margin-bottom:.5rem">📝 Click to view/copy template</pre>';
html+='<pre>'+t.content+'</pre>';
html+='</div>';
}
document.getElementById('templatesContent').innerHTML=html;
})();

(function(){
let html='';
html+='<h2 style="font-size:1.1rem;margin:1rem 0 .5rem 0">📖 Legal Glossary</h2>';
html+='<table class="glossary-table"><thead><tr><th>Term</th><th>Nepali (नेपाली)</th><th>Hindi (हिन्दी)</th><th>Meaning</th></tr></thead><tbody>';
SUPP.glossary.forEach(g=>{
html+='<tr><td><b>'+g.term+'</b></td><td>'+g.nepal+'</td><td>'+g.hindi+'</td><td>'+g.meaning+'</td></tr>';
});
html+='</tbody></table>';
['nepal','india'].forEach(country=>{
const flag=country==='nepal'?'🇳🇵':'🇮🇳';
html+='<h2 style="font-size:1.1rem;margin:1.5rem 0 .5rem 0">'+flag+' Limitation Periods ('+country.charAt(0).toUpperCase()+country.slice(1)+')</h2>';
html+='<table class="limitation-table"><thead><tr><th>Case Type</th><th>Time Limit</th><th>Law</th></tr></thead><tbody>';
SUPP.limitation_periods[country].forEach(lp=>{
html+='<tr><td><b>'+lp.case_type+'</b></td><td>'+lp.period+'</td><td style="font-size:.75rem;color:#6B7280">'+lp.law+'</td></tr>';
});
html+='</tbody></table>';
});
['nepal','india'].forEach(country=>{
const flag=country==='nepal'?'🇳🇵':'🇮🇳';
html+='<h2 style="font-size:1.1rem;margin:1.5rem 0 .5rem 0">'+flag+' Emergency Contacts ('+country.charAt(0).toUpperCase()+country.slice(1)+')</h2>';
html+='<div class="contact-grid">';
SUPP.emergency_contacts[country].forEach(c=>{
html+='<div class="contact-item"><div class="num">'+c.number+'</div><div class="svc">'+c.service+'</div><div class="note">'+c.note+'</div></div>';
});
html+='</div>';
});
['nepal','india'].forEach(country=>{
const flag=country==='nepal'?'🇳🇵':'🇮🇳';
html+='<h2 style="font-size:1.1rem;margin:1.5rem 0 .5rem 0">'+flag+' Court Hierarchy ('+country.charAt(0).toUpperCase()+country.slice(1)+')</h2>';
html+='<div style="display:flex;flex-direction:column;gap:.5rem">';
SUPP.court_hierarchy[country].forEach((c,i)=>{
const local=c.nepali||c.hindi||'';
html+='<div class="card" style="border-left-color:'+['#6366F1','#8B5CF6','#A855F7','#D946EF','#EC4899','#F43F5E','#EF4444'][i%7]+';cursor:default">';
html+='<div class="meta">Level '+(i+1)+'</div>';
html+='<div class="title">'+c.level+(local?' ('+local+')':'')+'</div>';
html+='<div class="text" style="display:block;font-size:.8rem">'+c.jurisdiction+(c.location?' — '+c.location:'')+'</div>';
html+='</div>';
});
html+='</div>';
});
document.getElementById('referenceContent').innerHTML=html;
})();

(function(){
const saved=localStorage.getItem('kanun_lang')||'en';
document.getElementById('langSelect').value=saved;
switchLang(saved);
checkOnboarding();
})();
</script>
</body>
</html>'''


def main():
    print("Loading minified JSON data...")
    nepal = load_json("_nepal_min.json")
    india = load_json("_india_min.json")
    supp = load_json("_supp_min.json")

    guide_count = len(supp.get("guides", {}))
    print(f"  Nepal: {nepal.get('total_articles', 0)} articles")
    print(f"  India: {india.get('total_articles', 0)} articles")
    print(f"  Supplementary: {guide_count} guide categories")

    print("Building HTML...")
    nepal_str = json.dumps(nepal, ensure_ascii=False, separators=(",", ":"))
    india_str = json.dumps(india, ensure_ascii=False, separators=(",", ":"))
    supp_str = json.dumps(supp, ensure_ascii=False, separators=(",", ":"))

    html = HTML_TEMPLATE
    html = html.replace(NEPAL_JSON, nepal_str)
    html = html.replace(INDIA_JSON, india_str)
    html = html.replace(SUPP_JSON, supp_str)

    print(f"Writing {OUT} ({len(html):,} bytes)...")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Done! Open with: open {OUT}")


if __name__ == "__main__":
    main()
