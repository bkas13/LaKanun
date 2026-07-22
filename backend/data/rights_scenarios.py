"""Rights scenarios — curated legal rights information for citizens.

Each scenario maps a real-life situation to the relevant legal provisions
across Nepal and India constitutions and laws.
"""

from pathlib import Path
import json

SCENARIOS = [
    {
        "id": "arrest",
        "icon": "police",
        "category": "criminal",
        "title": {
            "en": "I've Been Arrested",
            "ne": "मलाई गिरफ्तार गरिएको छ",
            "hi": "मुझे गिरफ्तार किया गया है"
        },
        "description": {
            "en": "Know your rights when taken into police custody. Police must follow specific procedures during arrest.",
            "ne": "प्रहरी हिरासतमा लिँदा तपाईंको अधिकार जान्नुहोस्। प्रहरीले गिरफ्तारीको क्रममा विशेष प्रक्रिया पालना गर्नुपर्छ।",
            "hi": "पुलिस हिरासत में आपके अधिकार जानें। गिरफ्तारी के दौरान पुलिस को विशेष प्रक्रिया का पालन करना होगा।"
        },
        "your_rights": {
            "en": [
                "Right to be informed of the reason for arrest immediately",
                "Right to consult a lawyer before questioning",
                "Right to be produced before a magistrate within 24 hours",
                "Right against torture and cruel treatment",
                "Right to remain silent — anything you say can be used against you"
            ],
            "ne": [
                "गिरफ्तारीको कारण तुरुन्तै जान्ने अधिकार",
                "पूछताछ अघि वकीलसँग भेट्ने अधिकार",
                "२४ घण्टाभित्र न्यायाधीशसामु प्रस्तुत गरिने अधिकार",
                "यातना र क्रूर व्यवहार विरुद्धको अधिकार",
                "मौन रहने अधिकार — तपाईंले भनेको केही पनि तपाईंविरुद्ध प्रयोग गर्न सकिन्छ"
            ],
            "hi": [
                "गिरफ्तारी का कारण तुरंत जानने का अधिकार",
                "पूछताछ से पहले वकील से मिलने का अधिकार",
                "24 घंटे के भीतर मजिस्ट्रेट के सामने पेश किए जाने का अधिकार",
                "यातना और क्रूर व्यवहार के खिलाफ अधिकार",
                "चुप रहने का अधिकार — आप जो भी कहेंगे वह आपके खिलाफ इस्तेमाल किया जा सकता है"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Show a warrant (except in case of cognizable offences)",
                "Provide a copy of the arrest memo signed by a witness",
                "Allow one phone call to a family member or lawyer",
                "Not arrest between sunset and sunrise without a magistrate's order"
            ],
            "ne": [
                "वारेन्ट देखाउनुपर्छ (संज्ञेय अपराध बाहेक)",
                "साक्षीको हस्ताक्षर भएको गिरफ्तारी मेमोको प्रतिलिपि दिनुपर्छ",
                "परिवारको सदस्य वा वकीललाई एक फोन कल गर्न दिनुपर्छ",
                "न्यायाधीशको आदेश बिना सूर्यास्त र सूर्योदयबीच गिरफ्तार गर्न हुँदैन"
            ],
            "hi": [
                "वारंट दिखाना होगा (संज्ञेय अपराध को छोड़कर)",
                "गिरफ्तारी ज्ञापन की प्रति गवाह के हस्ताक्षर सहित देनी होगी",
                "परिवार के सदस्य या वकील को एक फोन कॉल करने की अनुमति देनी होगी",
                "मजिस्ट्रेट के आदेश के बिना सूर्यास्त और सूर्योदय के बीच गिरफ्तार नहीं किया जा सकता"
            ]
        },
        "deadlines": {
            "en": "Produced before magistrate within 24 hours (Art. 25 Nepal Constitution / Art. 22 India Constitution)",
            "ne": "२४ घण्टाभित्र न्यायाधीशसामु प्रस्तुत (नेपाल संविधान धारा २५ / भारत संविधान धारा २२)",
            "hi": "24 घंटे के भीतर मजिस्ट्रेट के सामने पेश (नेपाल संविधान धारा 25 / भारत संविधान धारा 22)"
        },
        "where_to_go": {
            "en": "Nearest police station, District Court, or Nepal National Human Rights Commission / National Human Rights Commission (India)",
            "ne": "नजिकको प्रहरी चौकी, जिल्ला अदालत, वा नेपाल मानवअधिकार आयोग",
            "hi": "निकटतम पुलिस स्टेशन, जिला न्यायालय, या राष्ट्रीय मानवाधिकार आयोग"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_25", "title": "Right relating to arrest and detention"},
            {"country": "nepal", "article_id": "nepal_const_art_22", "title": "Right against torture"},
            {"country": "nepal", "article_id": "nepal_const_art_20", "title": "Right relating to free legal aid"},
            {"country": "india", "article_id": "india_const_art_22", "title": "Protection against arrest and detention"},
            {"country": "india", "article_id": "india_const_art_20", "title": "Protection in respect of conviction for offence"},
            {"country": "india", "article_id": "india_const_art_21", "title": "Protection of life and personal liberty"}
        ]
    },
    {
        "id": "domestic_violence",
        "icon": "shield",
        "category": "family",
        "title": {
            "en": "Domestic Violence",
            "ne": "घरेलु हिंसा",
            "hi": "घरेलू हिंसा"
        },
        "description": {
            "en": "If you or someone you know is experiencing domestic violence, you have legal protections and remedies available.",
            "ne": "यदि तपाईं वा तपाईंलाई थाहा भएको कोही घरेलु हिंसा भोगिरहेको छ भने, तपाईंसँग कानूनी सुरक्षा र उपायहरू छन्।",
            "hi": "यदि आप या आपके जानने वाला कोई घरेलू हिंसा झेल रहा है, तो आपके पास कानूनी सुरक्षा और उपाय हैं।"
        },
        "your_rights": {
            "en": [
                "Right to protection from domestic violence",
                "Right to reside in the shared household",
                "Right to monetary relief and compensation",
                "Right to custody of children",
                "Right to free legal aid"
            ],
            "ne": [
                "घरेलु हिंसाबाट सुरक्षाको अधिकार",
                "साझा घरमा बस्ने अधिकार",
                "आर्थिक राहत र क्षतिपूर्तिको अधिकार",
                "बालबालिकाको हिरासतको अधिकार",
                "निःशुल्क कानूनी सहायताको अधिकार"
            ],
            "hi": [
                "घरेलू हिंसा से सुरक्षा का अधिकार",
                "साझा घर में रहने का अधिकार",
                "आर्थिक राहत और मुआवजे का अधिकार",
                "बच्चों की हिरासत का अधिकार",
                "मुफ्त कानूनी सहायता का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Register your complaint (FIR) without delay",
                "Provide protection if there is imminent danger",
                "Refer you to a shelter home if needed",
                "Issue a protection order within 48 hours of application"
            ],
            "ne": [
                "तपाईंको शिकायत (FIR) ढिलाइ नगरी दर्ता गर्नुपर्छ",
                "आसन्न खतरा छ भने सुरक्षा प्रदान गर्नुपर्छ",
                "आवश्यक भएमा आश्रय गृहमा रेफर गर्नुपर्छ",
                "आवेदनपत्र पेश गरेको ४८ घण्टाभित्र सुरक्षा आदेश जारी गर्नुपर्छ"
            ],
            "hi": [
                "आपकी शिकायत (FIR) बिना देरी दर्ज करनी होगी",
                "तत्काल खतरा होने पर सुरक्षा प्रदान करनी होगी",
                "जरूरत पड़ने पर आवास गृह में भेजना होगा",
                "आवेदन के 48 घंटे के भीतर सुरक्षा आदेश जारी करना होगा"
            ]
        },
        "deadlines": {
            "en": "Protection order within 48 hours; FIR must be registered immediately",
            "ne": "४८ घण्टाभित्र सुरक्षा आदेश; FIR तुरुन्तै दर्ता गर्नुपर्छ",
            "hi": "48 घंटे के भीतर सुरक्षा आदेश; FIR तुरंत दर्ज होनी चाहिए"
        },
        "where_to_go": {
            "en": "Nearest police station, Protection Officer, Service Provider, or Magistrate's Court",
            "ne": "नजिकको प्रहरी चौकी, सुरक्षा अधिकारी, सेवा प्रदायक, वा न्यायाधीशको अदालत",
            "hi": "निकटतम पुलिस स्टेशन, सुरक्षा अधिकारी, सेवा प्रदाता, या मजिस्ट्रेट की अदालत"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_38", "title": "Right relating to women"},
            {"country": "nepal", "article_id": "nepal_const_art_39", "title": "Right relating to children"},
            {"country": "nepal", "article_id": "nepal_const_art_16", "title": "Right to live with dignity"},
            {"country": "india", "article_id": "india_const_art_21", "title": "Protection of life and personal liberty"},
            {"country": "india", "article_id": "india_const_art_15", "title": "Prohibition of discrimination"}
        ]
    },
    {
        "id": "property_dispute",
        "icon": "home",
        "category": "property",
        "title": {
            "en": "Property Dispute",
            "ne": "सम्पत्ति विवाद",
            "hi": "सम्पत्ति विवाद"
        },
        "description": {
            "en": "Disputes over land, housing, or inherited property. Know your rights in property matters.",
            "ne": "जमिन, घर, वा उत्तराधिकारमा प्राप्त सम्पत्तिमा विवाद। सम्पत्ति सम्बन्धी कुरामा आफ्नो अधिकार जान्नुहोस्।",
            "hi": "भूमि, घर, या विरासत की सम्पत्ति पर विवाद। सम्पत्ति के मामलों में अपने अधिकार जानें।"
        },
        "your_rights": {
            "en": [
                "Right to own, use, and dispose of property",
                "Right to equal inheritance regardless of gender",
                "Right to residence in shared household",
                "Right to fair compensation if property is acquired by government",
                "Right to challenge illegal eviction"
            ],
            "ne": [
                "सम्पत्ति आफ्नोमा राख्न, प्रयोग गर्न र बेच्ने अधिकार",
                "लिङ्गभेद बिना समान उत्तराधिकारको अधिकार",
                "साझा घरमा बस्ने अधिकार",
                "सरकारले सम्पत्ति अधिग्रहण गरेमा उचित क्षतिपूर्तिको अधिकार",
                "गैरकानूनी निकासीको विरुद्ध चुनौती दिने अधिकार"
            ],
            "hi": [
                "सम्पत्ति का स्वामित्व, उपयोग और बेचने का अधिकार",
                "लिंग की परवाह किए बिना समान विरासत का अधिकार",
                "साझा घर में रहने का अधिकार",
                "सरकार द्वारा सम्पत्ति अधिग्रहण पर उचित मुआवजे का अधिकार",
                "गैरकानूनी बेदखली को चुनौती देने का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Register your property case in the appropriate court",
                "Conduct a hearing within the time limit",
                "Issue orders for property partition if co-owned",
                "Ensure government acquisition provides fair compensation"
            ],
            "ne": [
                "उपयुक्त अदालतमा तपाईंको सम्पत्ति मुद्दा दर्ता गर्नुपर्छ",
                "समयसीमाभित्र सुनुवाई गर्नुपर्छ",
                "सह-स्वामित्वमा भएमा सम्पत्ति विभाजनको आदेश जारी गर्नुपर्छ",
                "सरकारी अधिग्रहणले उचित क्षतिपूर्ति सुनिश्चित गर्नुपर्छ"
            ],
            "hi": [
                "उचित न्यायालय में आपका सम्पत्ति मामला दर्ज करना होगा",
                "समय सीमा के भीतर सुनवाई करनी होगी",
                "सह-स्वामित्व में सम्पत्ति विभाजन का आदेश जारी करना होगा",
                "सरकारी अधिग्रहण में उचित मुआवजा सुनिश्चित करना होगा"
            ]
        },
        "deadlines": {
            "en": "Varies by case type — consult a lawyer for specific timelines",
            "ne": "मुद्दाको प्रकार अनुसार फरक हुन्छ — विशिष्ट समयसीमाको लागि वकीलसँग परामर्श गर्नुहोस्",
            "hi": "मामले के प्रकार के अनुसार अलग-अलग — विशिष्ट समय सीमा के लिए वकील से परामर्श करें"
        },
        "where_to_go": {
            "en": "District Court, Land Revenue Office, or local government body",
            "ne": "जिल्ला अदालत, भूमि राजस्व कार्यालय, वा स्थानीय सरकार",
            "hi": "जिला न्यायालय, भूमि राजस्व कार्यालय, या स्थानीय सरकारी निकाय"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_25", "title": "Right to property"},
            {"country": "nepal", "article_id": "nepal_const_art_35", "title": "Right relating to marriage"},
            {"country": "india", "article_id": "india_const_art_300A", "title": "Right to property"},
            {"country": "india", "article_id": "india_const_art_14", "title": "Equality before law"}
        ]
    },
    {
        "id": "workplace_injury",
        "icon": "briefcase",
        "category": "labor",
        "title": {
            "en": "Workplace Injury or Wrongful Termination",
            "ne": "कार्यस्थलमा चोटपटक वा गलत निकासी",
            "hi": "कार्यस्थल पर चोट या गलत निकासी"
        },
        "description": {
            "en": "If you've been injured at work or fired without cause, labor laws protect you.",
            "ne": "यदि तपाईं काममा घाइते भए वा बिना कारण निकालिए भने, श्रम कानूनले तपाईंलाई सुरक्षा दिन्छ।",
            "hi": "यदि आप काम पर घायल हुए या बिना कारण निकाले गए, तो श्रम कानून आपकी रक्षा करते हैं।"
        },
        "your_rights": {
            "en": [
                "Right to safe working conditions",
                "Right to minimum wages",
                "Right to compensation for work-related injury",
                "Right against arbitrary dismissal",
                "Right to paid leave and holidays"
            ],
            "ne": [
                "सुरक्षित कार्यस्थलको अधिकार",
                "न्यूनतम ज्यालाको अधिकार",
                "कामसँग सम्बन्धित चोटपटकको क्षतिपूर्तिको अधिकार",
                "मनमानो निकासीविरुद्धको अधिकार",
                "तलब रहित बिदा र बिदाको अधिकार"
            ],
            "hi": [
                "सुरक्षित कार्यस्थल का अधिकार",
                "न्यूनतम वेतन का अधिकार",
                "कार्य-संबंधी चोट के लिए मुआवजे का अधिकार",
                "मनमानी निकासी के खिलाफ अधिकार",
                "वेतन सहित छुट्टी और अवकाश का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Employer must provide safe working environment",
                "Employer must pay compensation for work injuries",
                "Employer cannot terminate without notice period",
                "Labour office must investigate complaints",
                "Worker must be registered with social security"
            ],
            "ne": [
                "रोजगारदाताले सुरक्षित कार्यस्थल प्रदान गर्नुपर्छ",
                "रोजगारदाताले कामसँग सम्बन्धित चोटपटको क्षतिपूर्ति दिनुपर्छ",
                "रोजगारदाताले सूचना अवधि बिना निकासी गर्न हुँदैन",
                "श्रम कार्यालयले शिकायतको छानबिन गर्नुपर्छ",
                "श्रमिकलाई सामाजिक सुरक्षामा दर्ता गर्नुपर्छ"
            ],
            "hi": [
                "नियोक्ता को सुरक्षित कार्यस्थल प्रदान करना होगा",
                "नियोक्ता को कार्य-संबंधी चोट के लिए मुआवजा देना होगा",
                "नियोक्ता बिना नोटिस अवधि के निकासी नहीं कर सकता",
                "श्रम कार्यालय को शिकायत की जांच करनी होगी",
                "श्रमिक को सामाजिक सुरक्षा में पंजीकृत करना होगा"
            ]
        },
        "deadlines": {
            "en": "Report injury within 12 months; wrongful termination claim within 1 year",
            "ne": "१२ महिनाभित्र चोटपटक रिपोर्ट गर्नुपर्छ; गलत निकासीको दाबी १ वर्षभित्र",
            "hi": "12 महीने के भीतर चोट की रिपोर्ट करनी होगी; गलत निकासी का दावा 1 साल के भीतर"
        },
        "where_to_go": {
            "en": "Labour Office, District Court, or Workers' Compensation Board",
            "ne": "श्रम कार्यालय, जिल्ला अदालत, वा श्रमिक क्षतिपूर्ति बोर्ड",
            "hi": "श्रम कार्यालय, जिला न्यायालय, या श्रमिक मुआवजा बोर्ड"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_34", "title": "Right relating to labour"},
            {"country": "nepal", "article_id": "nepal_const_art_33", "title": "Right relating to employment"},
            {"country": "india", "article_id": "india_const_art_23", "title": "Prohibition of traffic in human beings and forced labour"},
            {"country": "india", "article_id": "india_const_art_43", "title": "Living wages etc. for workers"}
        ]
    },
    {
        "id": "consumer_complaint",
        "icon": "shopping",
        "category": "consumer",
        "title": {
            "en": "Consumer Complaint",
            "ne": "उपभोक्ता शिकायत",
            "hi": "उपभोक्ता शिकायत"
        },
        "description": {
            "en": "If you've been sold defective goods or received poor service, consumer protection laws give you rights to remedies.",
            "ne": "यदि तपाईंलाई दोषपूर्ण माल बेइएको छ वा सेवा खराब भएको छ भने, उपभोक्ता संरक्षण कानूनले तपाईंलाई उपायको अधिकार दिन्छ।",
            "hi": "यदि आपको दोषपूर्ण माल बेचा गया या खराब सेवा मिली, तो उपभोक्ता संरक्षण कानून आपको उपाय का अधिकार देते हैं।"
        },
        "your_rights": {
            "en": [
                "Right to safety from hazardous goods",
                "Right to be informed about product quality and price",
                "Right to choose among competing products",
                "Right to seek redressal for defective goods or services",
                "Right to consumer education"
            ],
            "ne": [
                "खतरनाक मालबाट सुरक्षाको अधिकार",
                "उत्पादनको गुणस्तर र मूल्यबारे जान्ने अधिकार",
                "प्रतिस्पर्धी उत्पादनबाट छनोट गर्ने अधिकार",
                "दोषपूर्ण माल वा सेवाको लागि न्याय खोज्ने अधिकार",
                "उपभोक्ता शिक्षाको अधिकार"
            ],
            "hi": [
                "खतरनाक माल से सुरक्षा का अधिकार",
                "उत्पादन की गुणवत्ता और मूल्य के बारे में जानने का अधिकार",
                "प्रतिस्पर्धी उत्पादनों में से चुनने का अधिकार",
                "दोषपूर्ण माल या सेवाओं के लिए न्याय खोजने का अधिकार",
                "उपभोक्ता शिक्षा का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Consumer court must hear your complaint",
                "Seller must provide refund, replacement, or compensation",
                "Penalty can be imposed on unfair trade practices",
                "Product recall ordered if safety is at risk"
            ],
            "ne": [
                "उपभोक्ता अदालतले तपाईंको शिकायत सुन्नुपर्छ",
                "विक्रेताले फिर्ता, प्रतिस्थापन, वा क्षतिपूर्ति दिनुपर्छ",
                "अनुचित व्यापारिक व्यवहारमा जरिवाना लगाउन सकिन्छ",
                "सुरक्षा जोखिममा छ भने उत्पादन फिर्तीको आदेश दिइन्छ"
            ],
            "hi": [
                "उपभोक्ता अदालत को आपकी शिकायत सुननी होगी",
                "विक्रेता को रिफंड, प्रतिस्थापन, या मुआवजा देना होगा",
                "अनुचित व्यापारिक प्रथाओं पर जुर्माना लगाया जा सकता है",
                "सुरक्षा जोखिम होने पर उत्पादन वापसी का आदेश दिया जाएगा"
            ]
        },
        "deadlines": {
            "en": "File complaint within 2 years of purchase; no limit for life-threatening defects",
            "ne": "खरिद गरेको २ वर्षभित्र शिकायत दर्ता गर्नुपर्छ; जीवनलाई खतरा हुने दोषको लागि सीमा छैन",
            "hi": "खरीद के 2 साल के भीतर शिकायत दर्ज करनी होगी; जीवन के लिए खतरनाक दोषों के लिए कोई सीमा नहीं"
        },
        "where_to_go": {
            "en": "Consumer Forum / Consumer Disputes Redressal Commission",
            "ne": "उपभोक्ता फोरम / उपभोक्ता विवाद निवारण आयोग",
            "hi": "उपभोक्ता फोरम / उपभोक्ता विवाद निवारण आयोग"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_44", "title": "Right of consumers"},
            {"country": "india", "article_id": "india_const_art_21", "title": "Protection of life and personal liberty"}
        ]
    },
    {
        "id": "child_labor",
        "icon": "child",
        "category": "child",
        "title": {
            "en": "Child Labor or Abuse",
            "ne": "बाल श्रम वा दुर्व्यवहार",
            "hi": "बाल श्रम या दुर्व्यवहार"
        },
        "description": {
            "en": "Child labor is illegal. Every child has the right to education and protection from exploitation.",
            "ne": "बाल श्रम गैरकानूनी छ। प्रत्येक बालबालिकालाई शिक्षा र शोषणबाट सुरक्षाको अधिकार छ।",
            "hi": "बाल श्रम गैरकानूनी है। हर बच्चे को शिक्षा और शोषण से सुरक्षा का अधिकार है।"
        },
        "your_rights": {
            "en": [
                "Right to free and compulsory education (ages 5-14)",
                "Protection from employment in hazardous industries",
                "Right to protection from sexual exploitation",
                "Right to be tried as a juvenile (under 18)",
                "Right to rehabilitation if trafficked or exploited"
            ],
            "ne": [
                "निःशुल्क र अनिवार्य शिक्षाको अधिकार (५-१४ वर्ष)",
                "खतरनाक उद्योगमा रोजगारबाट सुरक्षा",
                "यौन शोषणबाट सुरक्षाको अधिकार",
                "किशोरको रूपमा मुद्दा चल्ने अधिकार (१८ वर्षमुनि)",
                "तस्करी वा शोषण भएमा पुनर्वासको अधिकार"
            ],
            "hi": [
                "मुफ्त और अनिवार्य शिक्षा का अधिकार (5-14 वर्ष)",
                "खतरनाक उद्योगों में रोजगार से सुरक्षा",
                "यौन शोषण से सुरक्षा का अधिकार",
                "किशोर के रूप में मुकदमा चलाने का अधिकार (18 साल से कम)",
                "तस्करी या शोषण की स्थिति में पुनर्वास का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Police must register a case if child labor is reported",
                "Child Welfare Committee must protect the child",
                "Employer faces criminal prosecution",
                "Child must be enrolled in school within 30 days"
            ],
            "ne": [
                "बाल श्रम रिपोर्ट भएमा प्रहरीले मुद्दा दर्ता गर्नुपर्छ",
                "बाल कल्याण समितिले बालबालिकालाई सुरक्षित गर्नुपर्छ",
                "रोजगारदातालाई फौजदारी मुद्दा चलिन्छ",
                "३० दिनभित्र बालबालिकालाई विद्यालयमा भर्ना गर्नुपर्छ"
            ],
            "hi": [
                "बाल श्रम की रिपोर्ट मिलने पर पुलिस को मामला दर्ज करना होगा",
                "बाल कल्याण समिति को बच्चे की रक्षा करनी होगी",
                "नियोक्ता पर आपराधिक मुकदमा चलेगा",
                "30 दिन के भीतर बच्चे का स्कूल में दाखिला होना चाहिए"
            ]
        },
        "deadlines": {
            "en": "Report immediately; no time limit for child abuse cases",
            "ne": "तुरुन्तै रिपोर्ट गर्नुहोस्; बाल दुर्व्यवहारको लागि समय सीमा छैन",
            "hi": "तुरंत रिपोर्ट करें; बाल दुर्व्यवहार के मामलों के लिए कोई समय सीमा नहीं"
        },
        "where_to_go": {
            "en": "Police, Child Welfare Committee, District Administration Office",
            "ne": "प्रहरी, बाल कल्याण समिति, जिल्ला प्रशासन कार्यालय",
            "hi": "पुलिस, बाल कल्याण समिति, जिला प्रशासन कार्यालय"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_39", "title": "Right relating to children"},
            {"country": "nepal", "article_id": "nepal_const_art_31", "title": "Right relating to education"},
            {"country": "india", "article_id": "india_const_art_24", "title": "Prohibition of employment of children in factories"},
            {"country": "india", "article_id": "india_const_art_21A", "title": "Right to education"}
        ]
    },
    {
        "id": "online_fraud",
        "icon": "computer",
        "category": "cyber",
        "title": {
            "en": "Online Fraud or Cybercrime",
            "ne": "अनलाइन धोखाधडी वा साइबर अपराध",
            "hi": "ऑनलाइन धोखाधडी या साइबर अपराध"
        },
        "description": {
            "en": "If you've been a victim of online fraud, hacking, or data theft, cyber laws provide remedies.",
            "ne": "यदि तपाईं अनलाइन धोखाधडी, ह्याकिङ, वा डाटा चोरीको शिकार भएको छ भने, साइबर कानूनले उपाय प्रदान गर्छ।",
            "hi": "यदि आप ऑनलाइन धोखाधडी, हैकिंग, या डेटा चोरी के शिकार हुए हैं, तो साइबर कानून उपाय प्रदान करते हैं।"
        },
        "your_rights": {
            "en": [
                "Right to privacy of personal data",
                "Right to report cybercrime to police",
                "Right to compensation for financial loss",
                "Right to have fraudulent transactions reversed",
                "Right to data protection"
            ],
            "ne": [
                "व्यक्तिगत डाटाको गोपनीयताको अधिकार",
                "साइबर अपराध प्रहरीलाई रिपोर्ट गर्ने अधिकार",
                "आर्थिक क्षतिको क्षतिपूर्तिको अधिकार",
                "धोखाधडी लेनदेन उल्टाउने अधिकार",
                "डाटा संरक्षणको अधिकार"
            ],
            "hi": [
                "व्यक्तिगत डेटा की गोपनीयता का अधिकार",
                "साइबर अपराध की पुलिस में रिपोर्ट करने का अधिकार",
                "वित्तीय नुकसान के लिए मुआवजे का अधिकार",
                "धोखाधडी लेनदेन को उलटने का अधिकार",
                "डेटा संरक्षण का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Police must register FIR for cybercrime",
                "Bank must freeze fraudulent accounts on request",
                "CERT must assist in investigation",
                "Court can order data restoration"
            ],
            "ne": [
                "प्रहरीले साइबर अपराधको FIR दर्ता गर्नुपर्छ",
                "बैंकले अनुरोधमा धोखाधडी खाता फ्रिज गर्नुपर्छ",
                "CERT ले छानबिनमा सहयोग गर्नुपर्छ",
                "अदालतले डाटा पुनर्स्थापनाको आदेश दिन सक्छ"
            ],
            "hi": [
                "पुलिस को साइबर अपराध की FIR दर्ज करनी होगी",
                "बैंक को अनुरोध पर धोखाधडी खाते को फ्रीज करना होगा",
                "CERT को जांच में सहायता करनी होगी",
                "अदालत डेटा पुनर्स्थापना का आदेश दे सकती है"
            ]
        },
        "deadlines": {
            "en": "Report within 24 hours for financial fraud; no limit for data theft",
            "ne": "वित्तीय धोखाधडीको लागि २४ घण्टाभित्र रिपोर्ट गर्नुपर्छ; डाटा चोरीको लागि सीमा छैन",
            "hi": "वित्तीय धोखाधडी के लिए 24 घंटे के भीतर रिपोर्ट करनी होगी; डेटा चोरी के लिए कोई सीमा नहीं"
        },
        "where_to_go": {
            "en": "Cyber Crime Police Station, Bank Fraud Cell, or National CERT",
            "ne": "साइबर अपराध प्रहरी चौकी, बैंक फ्राड सेल, वा राष्ट्रिय CERT",
            "hi": "साइबर क्राइम पुलिस स्टेशन, बैंक फ्रॉड सेल, या राष्ट्रीय CERT"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_30", "title": "Right relating to information technology"},
            {"country": "nepal", "article_id": "nepal_const_art_28", "title": "Right to privacy"},
            {"country": "india", "article_id": "india_const_art_21", "title": "Protection of life and personal liberty"}
        ]
    },
    {
        "id": "inheritance",
        "icon": "family",
        "category": "family",
        "title": {
            "en": "Inheritance & Succession",
            "ne": "उत्तराधिकार र वंशानुक्रम",
            "hi": "विरासत और उत्तराधिकार"
        },
        "description": {
            "en": "When a family member dies, their property is distributed according to succession laws. Know your share.",
            "ne": "परिवारको सदस्यको मृत्यु हुँदा, उनको सम्पत्ति उत्तराधिकार कानून अनुसार वितरण गरिन्छ। आफ्नो हिस्सा जान्नुहोस्।",
            "hi": "परिवार के सदस्य की मृत्यु पर, उनकी सम्पत्ति उत्तराधिकार कानून के अनुसार वितरित होती है। अपना हिस्सा जानें।"
        },
        "your_rights": {
            "en": [
                "Equal share for all children regardless of gender",
                "Widow has equal share in husband's property",
                "Right to maintenance from family property",
                "Right to challenge unfair wills",
                "Right to ancestral property"
            ],
            "ne": [
                "लिङ्गभेद बिना सबै छोराछोरीलाई समान हिस्सा",
                "विधवालाई पतिको सम्पत्तिमा समान हिस्सा",
                "पारिवारिक सम्पत्तिबाट भरणपोषणको अधिकार",
                "अनुचित वसियतनामाको विरुद्ध चुनौती दिने अधिकार",
                "पुस्तैनी सम्पत्तिको अधिकार"
            ],
            "hi": [
                "लिंग की परवाह किए बिना सभी बच्चों को समान हिस्सा",
                "विधवा को पति की सम्पत्ति में समान हिस्सा",
                "पारिवारिक सम्पत्ति से भरण-पोषण का अधिकार",
                "अनुचित वसियतनामा को चुनौती देने का अधिकार",
                "पैतृक सम्पत्ति का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Court must register succession case",
                "All legal heirs must be notified",
                "Property must be divided according to law",
                "Probate must be granted for wills"
            ],
            "ne": [
                "अदालतले उत्तराधिकार मुद्दा दर्ता गर्नुपर्छ",
                "सबै वैध उत्तराधिकारीलाई सूचित गर्नुपर्छ",
                "सम्पत्ति कानून अनुसार विभाजन गर्नुपर्छ",
                "वसियतनामाको लागि प्रोबेट दिनुपर्छ"
            ],
            "hi": [
                "अदालत को उत्तराधिकार मामला दर्ज करना होगा",
                "सभी वैध उत्तराधिकारियों को सूचित करना होगा",
                "सम्पत्ति कानून के अनुसार वितरित करनी होगी",
                "वसियतनामा के लिए प्रोबेट देना होगा"
            ]
        },
        "deadlines": {
            "en": "File succession case within 12 years of death; no limit for minors",
            "ne": "मृत्युको १२ वर्षभित्र उत्तराधिकार मुद्दा दर्ता गर्नुपर्छ; नाबालिगको लागि सीमा छैन",
            "hi": "मृत्यु के 12 साल के भीतर उत्तराधिकार मामला दर्ज करना होगा; नाबालिग के लिए कोई सीमा नहीं"
        },
        "where_to_go": {
            "en": "District Court, Revenue Office, or Sub-Registrar",
            "ne": "जिल्ला अदालत, राजस्व कार्यालय, वा उप-निबन्धक",
            "hi": "जिला न्यायालय, राजस्व कार्यालय, या उप-निबंधक"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_18", "title": "Right to equality"},
            {"country": "nepal", "article_id": "nepal_const_art_35", "title": "Right relating to marriage"},
            {"country": "india", "article_id": "india_const_art_14", "title": "Equality before law"},
            {"country": "india", "article_id": "india_const_art_15", "title": "Prohibition of discrimination"}
        ]
    },
    {
        "id": "free_legal_aid",
        "icon": "scale",
        "category": "constitutional",
        "title": {
            "en": "Free Legal Aid",
            "ne": "निःशुल्क कानूनी सहायता",
            "hi": "मुफ्त कानूनी सहायता"
        },
        "description": {
            "en": "Every citizen has the right to free legal representation if they cannot afford a lawyer.",
            "ne": "प्रत्येक नागरिकलाई वकील भाडा गर्न नसकेमा निःशुल्क कानूनी प्रतिनिधित्वको अधिकार छ।",
            "hi": "हर नागरिक को वकील का खर्च उठाने में असमर्थ होने पर मुफ्त कानूनी प्रतिनिधित्व का अधिकार है।"
        },
        "your_rights": {
            "en": [
                "Right to free legal aid at government expense",
                "Right to a government-appointed lawyer",
                "Right to free legal services at all court levels",
                "Right to legal awareness and education",
                "Cannot be denied justice due to poverty"
            ],
            "ne": [
                "सरकारी खर्चमा निःशुल्क कानूनी सहायताको अधिकार",
                "सरकारद्वारा नियुक्त वकीलको अधिकार",
                "सबै अदालत तहमा निःशुल्क कानूनी सेवाको अधिकार",
                "कानूनी चेतना र शिक्षाको अधिकार",
                "गरिबीका कारण न्यायबाट वञ्चित गर्न सकिँदैन"
            ],
            "hi": [
                "सरकारी खर्च पर मुफ्त कानूनी सहायता का अधिकार",
                "सरकार द्वारा नियुक्त वकील का अधिकार",
                "सभी न्यायालय स्तरों पर मुफ्त कानूनी सेवाओं का अधिकार",
                "कानूनी जागरूकता और शिक्षा का अधिकार",
                "गरीबी के कारण न्याय से वंचित नहीं किया जा सकता"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Legal Aid Commission must provide free lawyers",
                "Court must appoint lawyer if accused cannot afford one",
                "Legal aid offices in every district",
                "No fees for poor litigants"
            ],
            "ne": [
                "कानूनी सहायता आयोगले निःशुल्क वकील प्रदान गर्नुपर्छ",
                "अभियुक्तले भाडा गर्न नसकेमा अदालतले वकील नियुक्त गर्नुपर्छ",
                "प्रत्येक जिल्लामा कानूनी सहायता कार्यालय",
                "गरिब मुद्दाहरूका लागि शुल्क छैन"
            ],
            "hi": [
                "कानूनी सहायता आयोग को मुफ्त वकील प्रदान करने होंगे",
                "अभियुक्त के खर्च उठाने में असमर्थ होने पर अदालत को वकील नियुक्त करना होगा",
                "हर जिले में कानूनी सहायता कार्यालय",
                "गरीब मुद्देदारों के लिए कोई शुल्क नहीं"
            ]
        },
        "deadlines": {
            "en": "Apply anytime — no deadline for legal aid applications",
            "ne": "कुनै पनि बेला आवेदन गर्न सकिन्छ — कानूनी सहायता आवेदनको लागि समय सीमा छैन",
            "hi": "कभी भी आवेदन कर सकते हैं — कानूनी सहायता आवेदन के लिए कोई समय सीमा नहीं"
        },
        "where_to_go": {
            "en": "District Legal Aid Office, Nepal Bar Association, or Legal Aid Commission",
            "ne": "जिल्ला कानूनी सहायता कार्यालय, नेपाल बार एसोसिएसन, वा कानूनी सहायता आयोग",
            "hi": "जिला कानूनी सहायता कार्यालय, नेपाल बार एसोसिएसन, या कानूनी सहायता आयोग"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_20", "title": "Right relating to free legal aid"},
            {"country": "nepal", "article_id": "nepal_const_art_21", "title": "Right to justice"},
            {"country": "india", "article_id": "india_const_art_39A", "title": "Equal justice and free legal aid"},
            {"country": "india", "article_id": "india_const_art_14", "title": "Equality before law"}
        ]
    },
    {
        "id": "police_harassment",
        "icon": "police",
        "category": "criminal",
        "title": {
            "en": "Police Harassment or Bribery Demand",
            "ne": "प्रहरी द्वारा सताउने वा घुस माग्ने",
            "hi": "पुलिस उत्पीड़न या रिश्वत की मांग"
        },
        "description": {
            "en": "Police cannot ask for bribes, threaten you, or mistreat you. You have protections against official misconduct.",
            "ne": "प्रहरीले घुस माग्न, धम्की दिन, वा दुर्व्यवहार गर्न सक्दैन। तपाईंसँग आधिकारिक दुर्व्यवहारविरुद्ध सुरक्षा छ।",
            "hi": "पुलिस रिश्वत नहीं मांग सकती, धमका नहीं सकती, या दुर्व्यवहार नहीं कर सकती। आधिकारिक दुर्व्यवहार के खिलाफ सुरक्षा है।"
        },
        "your_rights": {
            "en": [
                "Right to refuse to pay a bribe — it is a crime for police to ask",
                "Right to record the officer's name and badge number",
                "Right to file a complaint with the Police Commission",
                "Right to refuse a search without a warrant (except in urgent cases)",
                "Right to legal representation if detained"
            ],
            "ne": [
                "घुस दिनबाट इन्कार गर्ने अधिकार — प्रहरीले माग्नु अपराध हो",
                "अधिकारीको नाम र ब्याज नम्बर रेकर्ड गर्ने अधिकार",
                "प्रहरी आयोगमा शिकायत दर्ता गर्ने अधिकार",
                "वारेन्ट बिना खोजबाट इन्कार गर्ने अधिकार (आपतकालीन अवस्था बाहेक)",
                "हिरासतमा भएमा कानूनी प्रतिनिधित्वको अधिकार"
            ],
            "hi": [
                "रिश्वत देने से मना करने का अधिकार — पुलिस का मांगना अपराध है",
                "अधिकारी का नाम और बैज नंबर रिकॉर्ड करने का अधिकार",
                "पुलिस आयोग में शिकायत दर्ज करने का अधिकार",
                "वारंट के बिना तलाशी से मना करने का अधिकार (आपातकालीन स्थिति को छोड़कर)",
                "हिरासत में कानूनी प्रतिनिधित्व का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Police must wear name tags and show ID on request",
                "Must register complaints against fellow officers",
                "Cannot demand money to settle a case",
                "Must provide a written reason for any detention"
            ],
            "ne": [
                "प्रहरीले नाम ट्याग लगाउनुपर्छ र अनुरोधमा आईडी देखाउनुपर्छ",
                "आफ्नै साथीविरुद्ध शिकायत दर्ता गर्नुपर्छ",
                "मुद्दा सेटल गर्न पैसा माग्न हुँदैन",
                "कुनै पनि हिरासतको लागि लिखित कारण दिनुपर्छ"
            ],
            "hi": [
                "पुलिस को नाम टैग लगाना होगा और अनुरोध पर आईडी दिखानी होगी",
                "अपने साथियों के खिलाफ शिकायत दर्ज करनी होगी",
                "मामला सेटल करने के लिए पैसे नहीं मांग सकते",
                "किसी भी हिरासत के लिए लिखित कारण देना होगा"
            ]
        },
        "deadlines": {
            "en": "Complaint can be filed at any time; no time limit for misconduct reports",
            "ne": "कुनै पनि बेला शिकायत दर्ता गर्न सकिन्छ; दुर्व्यवहार रिपोर्टको लागि समय सीमा छैन",
            "hi": "कभी भी शिकायत दर्ज की जा सकती है; दुर्व्यवहार रिपोर्ट के लिए कोई समय सीमा नहीं"
        },
        "where_to_go": {
            "en": "Police Headquarters, National Human Rights Commission, or District Court",
            "ne": "प्रहरी मुख्यालय, मानवअधिकार आयोग, वा जिल्ला अदालत",
            "hi": "पुलिस मुख्यालय, राष्ट्रीय मानवाधिकार आयोग, या जिला न्यायालय"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_22", "title": "Right against torture"},
            {"country": "nepal", "article_id": "nepal_const_art_27", "title": "Right relating to public service"},
            {"country": "nepal", "article_id": "nepal_const_art_16", "title": "Right to live with dignity"},
            {"country": "india", "article_id": "india_const_art_21", "title": "Protection of life and personal liberty"},
            {"country": "india", "article_id": "india_const_art_14", "title": "Equality before law"}
        ]
    },
    {
        "id": "tenant_rights",
        "icon": "home",
        "category": "civil",
        "title": {
            "en": "Tenant Rights - Eviction or Deposit Dispute",
            "ne": "भाडाटिका अधिकार - निकासी वा जम्मा विवाद",
            "hi": "किरायेदार अधिकार - बेदखली या जमा विवाद"
        },
        "description": {
            "en": "Landlords cannot evict you without notice, seize your deposit, or deny basic services. Know your rights as a tenant.",
            "ne": "भाडादाताले सूचना बिना निकासी गर्न, जम्मा खेर्न, वा आधारभूत सेवा रोक्न सक्दैन। भाडाटिकाको रूपमा आफ्नो अधिकार जान्नुहोस्।",
            "hi": "मकान मालिक बिना नोटिस बेदखल नहीं कर सकते, जमा राशि नहीं रख सकते, या बुनियादी सेवाएं नहीं रोक सकते।"
        },
        "your_rights": {
            "en": [
                "Right to receive 30 days written notice before eviction",
                "Right to full return of security deposit with deductions explained",
                "Right to habitable living conditions (water, electricity, sanitation)",
                "Right to a written rental agreement",
                "Right against rent increase without proper notice"
            ],
            "ne": [
                "निकासीअघि ३० दिनको लिखित सूचना पाउने अधिकार",
                "जम्मा पूरा फिर्ता पाउने अधिकार, कटौती स्पष्ट भएको",
                "बस्नयोग्य जीवन स्थितिको अधिकार (पानी, बत्ती, सरसफाइ)",
                "लिखित भाडा सम्झौता पाउने अधिकार",
                "उचित सूचना बिना भाडा वृद्धिविरुद्धको अधिकार"
            ],
            "hi": [
                "बेदखली से पहले 30 दिन का लिखित नोटिस मिलने का अधिकार",
                "सुरक्षा जमा राशि की पूरी वापसी, कटौती स्पष्ट के साथ",
                "रहने योग्य जीवन स्थितियों का अधिकार (पानी, बिजली, स्वच्छता)",
                "लिखित किराया समझौता मिलने का अधिकार",
                "उचित नोटिस के बिना किराया वृद्धि के खिलाफ अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Court must hear tenant before issuing eviction order",
                "Landlord must return deposit within 30 days of move-out",
                "Municipality must enforce housing standards",
                "Police cannot forcibly evict without court order"
            ],
            "ne": [
                "अदालतले निकासी आदेश जारी गर्नुअघि भाडाटिकालाई सुन्नुपर्छ",
                "भाडादाताले बसाइसरेको ३० दिनभित्र जम्मा फिर्ता गर्नुपर्छ",
                "नगरपालिकाले आवास मापदण्ड लागू गर्नुपर्छ",
                "प्रहरीले अदालतको आदेश बिना जबरजस्ती निकासी गर्न हुँदैन"
            ],
            "hi": [
                "अदालत को बेदखली आदेश जारी करने से पहले किरायेदार की सुनवाई करनी होगी",
                "मकान मालिक को शिफ्ट-आउट के 30 दिनों के भीतर जमा राशि लौटानी होगी",
                "नगरपालिका को आवास मानक लागू करने होंगे",
                "पुलिस अदालत के आदेश के बिना जबरन बेदखली नहीं कर सकती"
            ]
        },
        "deadlines": {
            "en": "Deposit return within 30 days; eviction notice of 30 days minimum",
            "ne": "३० दिनभित्र जम्मा फिर्ता; न्यूनतम ३० दिनको निकासी सूचना",
            "hi": "30 दिन के भीतर जमा वापसी; न्यूनतम 30 दिन का बेदखली नोटिस"
        },
        "where_to_go": {
            "en": "District Court, Municipality Office, or Rent Control Board",
            "ne": "जिल्ला अदालत, नगरपालिका कार्यालय, वा भाडा नियन्त्रण बोर्ड",
            "hi": "जिला न्यायालय, नगरपालिका कार्यालय, या किराया नियंत्रण बोर्ड"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_25", "title": "Right to shelter"},
            {"country": "nepal", "article_id": "nepal_const_art_16", "title": "Right to live with dignity"},
            {"country": "india", "article_id": "india_const_art_21", "title": "Protection of life and personal liberty"},
            {"country": "india", "article_id": "india_const_art_19", "title": "Freedom of residence"}
        ]
    },
    {
        "id": "traffic_stop",
        "icon": "police",
        "category": "criminal",
        "title": {
            "en": "Traffic Stop - Know Your Rights",
            "ne": "ट्राफिक रोक - आफ्नो अधिकार जान्नुहोस्",
            "hi": "ट्रैफिक रोक - अपने अधिकार जानें"
        },
        "description": {
            "en": "Whether stopped for a routine check or a violation, you have specific rights during a traffic stop.",
            "ne": "नियमित जाँच वा उल्लंघनका लागि रोकिए पनि, ट्राफिक रोकमा तपाईंका विशेष अधिकार छन्।",
            "hi": "नियमित जांच या उल्लंघन के लिए रोके जाने पर भी, ट्रैफिक रोक में आपके विशेष अधिकार हैं।"
        },
        "your_rights": {
            "en": [
                "Right to ask for the officer's name and ID",
                "Right to know the specific reason for being stopped",
                "Right to refuse a vehicle search without probable cause",
                "Right to remain silent beyond providing license and registration",
                "Right to note down the officer's details for any complaint"
            ],
            "ne": [
                "अधिकारीको नाम र आईडी सोध्ने अधिकार",
                "रोकिनुको विशिष्ट कारण जान्ने अधिकार",
                "सम्भाव्य कारण बिना गाडी खोजबाट इन्कार गर्ने अधिकार",
                "लाइसेन्स र रजिस्ट्रेसन दिने बाहेक मौन रहने अधिकार",
                "शिकायतका लागि अधिकारीको विवरण रेकर्ड गर्ने अधिकार"
            ],
            "hi": [
                "अधिकारी का नाम और आईडी पूछने का अधिकार",
                "रोके जाने का विशिष्ट कारण जानने का अधिकार",
                "संभाव्य कारण के बिना गाड़ी की तलाशी से मना करने का अधिकार",
                "लाइसेंस और रजिस्ट्रेशन देने के अलावा चुप रहने का अधिकार",
                "शिकायत के लिए अधिकारी का विवरण नोट करने का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Officer must state the reason for stopping you",
                "Must show ID and name tag when requested",
                "Cannot search your vehicle without consent or probable cause",
                "Must issue a receipt for any fine imposed"
            ],
            "ne": [
                "अधिकारीले तपाईंलाई रोकेको कारण भन्नुपर्छ",
                "अनुरोधमा आईडी र नाम ट्याग देखाउनुपर्छ",
                "सहमति वा सम्भाव्य कारण बिना गाडी खोज्न हुँदैन",
                "लगाइएको जरिवानाको रसीद दिनुपर्छ"
            ],
            "hi": [
                "अधिकारी को आपको रोकने का कारण बताना होगा",
                "अनुरोध पर आईडी और नाम टैग दिखाना होगा",
                "सहमति या संभाव्य कारण के बिना गाड़ी की तलाशी नहीं ले सकते",
                "लगाए गए जुर्माने की रसीद देनी होगी"
            ]
        },
        "deadlines": {
            "en": "Traffic fines must be challenged in court within 15 days",
            "ne": "ट्राफिक जरिवाना १५ दिनभित्र अदालतमा चुनौती दिनुपर्छ",
            "hi": "ट्रैफिक जुर्माने को अदालत में 15 दिन के भीतर चुनौती देनी होगी"
        },
        "where_to_go": {
            "en": "Traffic Police Office, Transport Management Office, or District Court",
            "ne": "ट्राफिक प्रहरी कार्यालय, यातायात व्यवस्थापन कार्यालय, वा जिल्ला अदालत",
            "hi": "ट्रैफिक पुलिस कार्यालय, परिवहन प्रबंधन कार्यालय, या जिला न्यायालय"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_22", "title": "Right against torture"},
            {"country": "nepal", "article_id": "nepal_const_art_16", "title": "Right to live with dignity"},
            {"country": "india", "article_id": "india_const_art_20", "title": "Protection in respect of conviction"},
            {"country": "india", "article_id": "india_const_art_21", "title": "Protection of life and personal liberty"}
        ]
    },
    {
        "id": "medical_negligence",
        "icon": "scale",
        "category": "consumer",
        "title": {
            "en": "Medical Negligence or Hospital Issues",
            "ne": "चिकित्सा लापरवाही वा अस्पताल समस्या",
            "hi": "चिकित्सा लापरवाही या अस्पताल की समस्या"
        },
        "description": {
            "en": "If you received negligent medical treatment, were overcharged, or denied emergency care, you have legal remedies.",
            "ne": "यदि तपाईंलाई लापरवाह उपचार भएको छ, अत्यधिक शुल्क लगाइएको छ, वा आपतकालीन सेवा बाट वञ्चित गरिएको छ भने, कानूनी उपाय छन्।",
            "hi": "यदि आपको लापरवाह चिकित्सा उपचार मिला है, अधिक शुल्क लगाया गया है, या आपातकालीन देखभाल से वंचित किया गया है, तो कानूनी उपाय हैं।"
        },
        "your_rights": {
            "en": [
                "Right to informed consent before any treatment",
                "Right to access your complete medical records",
                "Right to emergency medical treatment regardless of ability to pay",
                "Right to file a complaint against negligent doctors",
                "Right to compensation for medical malpractice"
            ],
            "ne": [
                "कुनै पनि उपचारअघि सूचित सहमतिको अधिकार",
                "आफ्नो पूर्ण चिकित्सा रेकर्डमा पहुँचको अधिकार",
                "भुक्तानी क्षमताको परवाह नगरी आपतकालीन उपचारको अधिकार",
                "लापरवाह चिकित्सकविरुद्ध शिकायत दर्ता गर्ने अधिकार",
                "चिकित्सा लापरवाहीको क्षतिपूर्तिको अधिकार"
            ],
            "hi": [
                "किसी भी उपचार से पहले सूचित सहमति का अधिकार",
                "अपने पूर्ण चिकित्सा रिकॉर्ड तक पहुंच का अधिकार",
                "भुगतान क्षमता की परवाह किए बिना आपातकालीन चिकित्सा उपचार का अधिकार",
                "लापरवाह डॉक्टरों के खिलाफ शिकायत दर्ज करने का अधिकार",
                "चिकित्सा लापरवाही के लिए मुआवजे का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Hospital must provide treatment in emergencies",
                "Medical council must investigate complaints against doctors",
                "Hospital must maintain and share medical records",
                "Cannot refuse treatment for inability to pay"
            ],
            "ne": [
                "अस्पतालले आपतकालीन अवस्थामा उपचार दिनुपर्छ",
                "चिकित्सा परिषदले चिकित्सकविरुद्ध शिकायतको छानबिन गर्नुपर्छ",
                "अस्पतालले चिकित्सा रेकर्ड मिलाउनुपर्छ",
                "भुक्तानी नगर्नुका कारण उपचार अस्वीकार गर्न हुँदैन"
            ],
            "hi": [
                "अस्पताल को आपातकाल में इलाज देना होगा",
                "चिकित्सा परिषद को डॉक्टरों के खिलाफ शिकायतों की जांच करनी होगी",
                "अस्पताल को चिकित्सा रिकॉर्ड बनाए रखने और साझा करने होंगे",
                "भुगतान न कर पाने के कारण इलाज से इनकार नहीं कर सकते"
            ]
        },
        "deadlines": {
            "en": "File medical negligence claim within 2 years of the incident",
            "ne": "घटनाको २ वर्षभित्र चिकित्सा लापरवाही दाबी दर्ता गर्नुपर्छ",
            "hi": "घटना के 2 साल के भीतर चिकित्सा लापरवाही का दावा दर्ज करना होगा"
        },
        "where_to_go": {
            "en": "District Court, Medical Council, or Consumer Forum",
            "ne": "जिल्ला अदालत, चिकित्सा परिषद, वा उपभोक्ता फोरम",
            "hi": "जिला न्यायालय, चिकित्सा परिषद, या उपभोक्ता फोरम"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_16", "title": "Right to live with dignity"},
            {"country": "nepal", "article_id": "nepal_const_art_44", "title": "Right of consumers"},
            {"country": "india", "article_id": "india_const_art_21", "title": "Protection of life and personal liberty"},
            {"country": "india", "article_id": "india_const_art_32", "title": "Right to constitutional remedies"}
        ]
    },
    {
        "id": "neighbor_dispute",
        "icon": "home",
        "category": "civil",
        "title": {
            "en": "Neighbor Dispute - Noise, Boundary, or Nuisance",
            "ne": "छिमेकी विवाद - शोर, सीमा, वा गाइँ",
            "hi": "पड़ोसी विवाद - शोर, सीमा, या उपद्रव"
        },
        "description": {
            "en": "Issues with neighbors over noise, property boundaries, or disturbance have legal solutions.",
            "ne": "शोर, सम्पत्ति सीमा, अतिक्रमण, वा गाइँका लागि छिमेकीसँगको समस्याको कानूनी समाधान छ।",
            "hi": "शोर, सम्पत्ति की सीमा, अतिक्रमण, या परेशानी के लिए पड़ोसियों के साथ समस्या का कानूनी समाधान है।"
        },
        "your_rights": {
            "en": [
                "Right to quiet enjoyment of your property",
                "Right to seek injunction to stop encroachment",
                "Right to file complaint for structural damage caused by neighbor",
                "Right to action for persistent noise or nuisance",
                "Right to demarcation of property boundaries"
            ],
            "ne": [
                "आफ्नो सम्पत्तिमा शान्तिपूर्वक बस्ने अधिकार",
                "अतिक्रमण रोक्न निषेधाज्ञा खोज्ने अधिकार",
                "छिमेकीले गरेको संरचनात्मक क्षतिको शिकायत दर्ता गर्ने अधिकार",
                "निरन्तर शोर वा गाइँको लागि कारबाही गर्ने अधिकार",
                "सम्पत्ति सीमा निर्धारणको अधिकार"
            ],
            "hi": [
                "अपनी सम्पत्ति में शांतिपूर्वक रहने का अधिकार",
                "अतिक्रमण रोकने के लिए निषेधाज्ञा प्राप्त करने का अधिकार",
                "पड़ोसी द्वारा संरचनात्मक नुकसान की शिकायत दर्ज करने का अधिकार",
                "लगातार शोर या उपद्रव के लिए कार्रवाई का अधिकार",
                "सम्पत्ति सीमा निर्धारण का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Municipality must enforce building and zoning rules",
                "Court can issue noise abatement orders",
                "Police can file FIR for persistent nuisance",
                "Land Revenue Office can help demarcate boundaries"
            ],
            "ne": [
                "नगरपालिकाले भवन र जोनिङ नियम लागू गर्नुपर्छ",
                "अदालतले शोर नियन्त्रण आदेश जारी गर्न सक्छ",
                "प्रहरीले निरन्तर गाइँको लागि FIR दर्ता गर्न सक्छ",
                "भूमि राजस्व कार्यालयले सीमा निर्धारणमा सहयोग गर्न सक्छ"
            ],
            "hi": [
                "नगरपालिका को भवन और ज़ोनिंग नियम लागू करने होंगे",
                "अदालत शोर नियंत्रण आदेश जारी कर सकती है",
                "पुलिस लगातार उपद्रव के लिए FIR दर्ज कर सकती है",
                "भूमि राजस्व कार्यालय सीमा निर्धारण में सहायता कर सकता है"
            ]
        },
        "deadlines": {
            "en": "Civil suit must be filed within 3 years; nuisance complaints can be filed anytime",
            "ne": "दीवानी मुद्दा ३ वर्षभित्र दर्ता गर्नुपर्छ; गाइँको शिकायत कुनै पनि बेला गर्न सकिन्छ",
            "hi": "दीवानी मुकदमा 3 साल के भीतर दर्ज करना होगा; उपद्रव की शिकायत कभी भी की जा सकती है"
        },
        "where_to_go": {
            "en": "Municipality Office, District Court, or Land Revenue Office",
            "ne": "नगरपालिका कार्यालय, जिल्ला अदालत, वा भूमि राजस्व कार्यालय",
            "hi": "नगरपालिका कार्यालय, जिला न्यायालय, या भूमि राजस्व कार्यालय"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_25", "title": "Right to property"},
            {"country": "nepal", "article_id": "nepal_const_art_16", "title": "Right to live with dignity"},
            {"country": "india", "article_id": "india_const_art_21", "title": "Protection of life and personal liberty"},
            {"country": "india", "article_id": "india_const_art_14", "title": "Equality before law"}
        ]
    },
    {
        "id": "marriage_divorce",
        "icon": "family",
        "category": "family",
        "title": {
            "en": "Marriage Registration or Divorce",
            "ne": "विवाह दर्ता वा छुट्टाछुटी",
            "hi": "विवाह पंजीकरण या तलाक"
        },
        "description": {
            "en": "Know your rights about marriage registration, consent, and what happens during separation or divorce.",
            "ne": "विवाह दर्ता, सहमतिका आवश्यकता, र छुट्टाछुटीको क्रममा के हुन्छ भन्नेबारे आफ्नो अधिकार जान्नुहोस्।",
            "hi": "विवाह पंजीकरण, सहमति, और अलगाव या तलाक के दौरान क्या होता है, इसके बारे में अपने अधिकार जानें।"
        },
        "your_rights": {
            "en": [
                "Right to register marriage at local office",
                "Right to consent - forced marriage is illegal",
                "Right to equal property division upon divorce",
                "Right to maintenance and alimony after separation",
                "Right to custody arrangement in child's best interest"
            ],
            "ne": [
                "स्थानीय कार्यालयमा विवाह दर्ता गर्ने अधिकार",
                "सहमतिको अधिकार - जबरजस्ती विवाह गैरकानूनी छ",
                "छुट्टाछुटीमा समान सम्पत्ति विभाजनको अधिकार",
                "अलगावपछि भरणपोषण र गुजारा भत्ताको अधिकार",
                "बालबालिकाको सर्वोत्तम हितमा हिरासत व्यवस्थाको अधिकार"
            ],
            "hi": [
                "स्थानीय कार्यालय में विवाह पंजीकृत करने का अधिकार",
                "सहमति का अधिकार - जबरन विवाह गैरकानूनी है",
                "तलाक पर समान सम्पत्ति विभाजन का अधिकार",
                "अलगाव के बाद भरण-पोषण और गुजारा भत्ते का अधिकार",
                "बच्चे के सर्वोत्तम हित में हिरासत व्यवस्था का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Local government must register marriages",
                "Court must hear both parties in divorce proceedings",
                "Maintenance must be ordered based on financial need",
                "Child custody decided based on welfare of the child"
            ],
            "ne": [
                "स्थानीय सरकारले विवाह दर्ता गर्नुपर्छ",
                "अदालतले छुट्टाछुटी कार्यवाहीमा दुवै पक्षलाई सुन्नुपर्छ",
                "आर्थिक आवश्यकता अनुसार भरणपोषण आदेश गर्नुपर्छ",
                "बालबालिकाको कल्याणमा हिरासत निर्णय गरिन्छ"
            ],
            "hi": [
                "स्थानीय सरकार को विवाह पंजीकृत करने होंगे",
                "अदालत को तलाक की कार्यवाही में दोनों पक्षों की सुनवाई करनी होगी",
                "वित्तीय आवश्यकता के आधार पर भरण-पोषण का आदेश देना होगा",
                "बच्चे के कल्याण के आधार पर हिरासत का निर्णय"
            ]
        },
        "deadlines": {
            "en": "Divorce petition can be filed after 1 year of marriage; maintenance claims have no time limit",
            "ne": "विवाहको १ वर्षपछि छुट्टाछुटी दाबी दर्ता गर्न सकिन्छ; भरणपोषण दाबीको लागि समय सीमा छैन",
            "hi": "विवाह के 1 साल बाद तलाक का दावा दर्ज किया जा सकता है; भरण-पोषण दावे के लिए कोई समय सीमा नहीं"
        },
        "where_to_go": {
            "en": "District Court, Local Municipality, or Family Court",
            "ne": "जिल्ला अदालत, स्थानीय नगरपालिका, वा पारिवारिक अदालत",
            "hi": "जिला न्यायालय, स्थानीय नगरपालिका, या पारिवारिक न्यायालय"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_35", "title": "Right relating to marriage"},
            {"country": "nepal", "article_id": "nepal_const_art_18", "title": "Right to equality"},
            {"country": "india", "article_id": "india_const_art_14", "title": "Equality before law"},
            {"country": "india", "article_id": "india_const_art_15", "title": "Prohibition of discrimination"}
        ]
    },
    {
        "id": "government_service",
        "icon": "scale",
        "category": "constitutional",
        "title": {
            "en": "Government Service Delay or Denial",
            "ne": "सरकारी सेवा ढिलाइ वा अस्वीकार",
            "hi": "सरकारी सेवा में देरी या इनकार"
        },
        "description": {
            "en": "If a government office is delaying your application, demanding bribes, or refusing services you are entitled to, you have legal options.",
            "ne": "यदि सरकारी कार्यालयले तपाईंको आवेदन ढिलाइ गरिरहेको छ, घुस मागिरहेको छ, वा सेवा दिन अस्वीकार गरिरहेको छ भने, कानूनी उपाय छन्।",
            "hi": "यदि कोई सरकारी कार्यालय आपके आवेदन में देरी कर रहा है, रिश्वत मांग रहा है, या सेवाएं देने से इनकार कर रहा है, तो कानूनी विकल्प हैं।"
        },
        "your_rights": {
            "en": [
                "Right to timely delivery of public services",
                "Right to file complaint for delayed services",
                "Right to written reason for denial of service",
                "Right to information about government decisions",
                "Right to compensation for loss caused by government delay"
            ],
            "ne": [
                "सार्वजनिक सेवाको समयमै डेलिभरीको अधिकार",
                "ढिलाइ भएको सेवाको शिकायत दर्ता गर्ने अधिकार",
                "सेवा अस्वीकारको लिखित कारण पाउने अधिकार",
                "सरकारी निर्णयबारे जानकारी पाउने अधिकार",
                "सरकारी ढिलाइले गरेको हानिको क्षतिपूर्तिको अधिकार"
            ],
            "hi": [
                "सार्वजनिक सेवाओं की समय पर डिलीवरी का अधिकार",
                "विलंबित सेवाओं की शिकायत दर्ज करने का अधिकार",
                "सेवा अस्वीकार का लिखित कारण मिलने का अधिकार",
                "सरकारी निर्णयों के बारे में जानकारी का अधिकार",
                "सरकारी विलंब से हुई हानि के मुआवजे का अधिकार"
            ]
        },
        "what_authorities_must_do": {
            "en": [
                "Government must process applications within prescribed time",
                "Must provide written acknowledgment of receipt",
                "Right to Information Act must be enforced",
                "Grievance officer must respond within 15 days"
            ],
            "ne": [
                "सरकारले निर्धारित समयमा आवेदन प्रशोधन गर्नुपर्छ",
                "प्राप्तिको लिखित प्रमाणित दिनुपर्छ",
                "सूचना अधिकार ऐन लागू गर्नुपर्छ",
                "गुनासो अधिकारीले १५ दिनभित्र जवाफ दिनुपर्छ"
            ],
            "hi": [
                "सरकार को निर्धारित समय में आवेदन संसाधित करने होंगे",
                "प्राप्ति का लिखित प्रमाण देना होगा",
                "सूचना अधिकार अधिनियम लागू किया जाना चाहिए",
                "शिकायत अधिकारी को 15 दिनों के भीतर जवाब देना होगा"
            ]
        },
        "deadlines": {
            "en": "RTI application response within 30 days; service complaints within prescribed time",
            "ne": "सूचना अधिकार आवेदनको जवाफ ३० दिनभित्र; सेवा शिकायत निर्धारित समयमा",
            "hi": "सूचना अधिकार आवेदन का जवाब 30 दिन के भीतर; सेवा शिकायतें निर्धारित समय में"
        },
        "where_to_go": {
            "en": "Information Commission, District Administration Office, or Grievance Cell",
            "ne": "सूचना आयोग, जिल्ला प्रशासन कार्यालय, वा गुनासो शाखा",
            "hi": "सूचना आयोग, जिला प्रशासन कार्यालय, या शिकायत प्रकोष्ठ"
        },
        "provisions": [
            {"country": "nepal", "article_id": "nepal_const_art_27", "title": "Right relating to public service"},
            {"country": "nepal", "article_id": "nepal_const_art_24", "title": "Right to information"},
            {"country": "india", "article_id": "india_const_art_19", "title": "Freedom of speech and expression"},
            {"country": "india", "article_id": "india_const_art_32", "title": "Right to constitutional remedies"}
        ]
    }
]


def get_all_scenarios() -> list:
    """Return all rights scenarios."""
    return SCENARIOS


def get_scenario_by_id(scenario_id: str):
    """Return a single scenario by ID."""
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    return None


def get_scenarios_by_category(category: str) -> list:
    """Return scenarios filtered by category."""
    return [s for s in SCENARIOS if s["category"] == category]


def get_categories() -> list:
    """Return unique scenario categories."""
    cats = list(dict.fromkeys(s["category"] for s in SCENARIOS))
    return cats
