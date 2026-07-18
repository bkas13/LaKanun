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
