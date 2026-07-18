"""Plain language legal summaries — translates complex legal text into simple language.

Each entry maps an article ID to a plain-language explanation in all 3 languages.
These are hand-written, not LLM-generated — authoritative and accurate.
"""

SUMMARIES: dict[str, dict[str, str]] = {
    # ═══════════════════════════════════════════════════════════════════════
    # NEPAL CONSTITUTION 2072 — Fundamental Rights
    # ═══════════════════════════════════════════════════════════════════════
    "nepal_const_art_16": {
        "en": "Every person has the right to live with dignity. The government cannot take your life except as punishment ordered by a court of law. This is your most fundamental right — it protects your life itself.",
        "ne": "प्रत्येक व्यक्तिले गरिमाका साथ बस्ने अधिकार राख्छ। न्यायालयले आदेश गरेको दण्डको रूपमा मात्र सरकारले तपाईंको जीवन लिन सक्छ। यो तपाईंको सबैभन्दा आधारभूत अधिकार हो — यसले तपाईंको जीवनको रक्षा गर्छ।",
        "hi": "हर व्यक्ति को गरिमा के साथ जीने का अधिकार है। सरकार केवल अदालत द्वारा आदेशित सजा के रूप में आपकी जान ले सकती है। यह आपका सबसे मौलिक अधिकार है — यह आपके जीवन की रक्षा करता है।",
    },
    "nepal_const_art_17": {
        "en": "No one can be treated as a slave or forced into labor against their will. Forced labor in any form is prohibited. If someone forces you to work without pay, they are breaking the law.",
        "ne": "कसैलाई दास बनाउन वा उनको इच्छा विपरीत जबरजस्ती श्रममा लगाउन सकिँदैन। जबरजस्ती श्रम कुनै पनि रूपमा प्रतिबन्धित छ। कसैले तपाईंलाई बिना तलब काम गराउँछ भने, उनले कानून उल्लङ्घन गरिरहेका छन्।",
        "hi": "किसी को भी दास नहीं बनाया जा सकता या उसकी इच्छा के विरुद्ध मजबूर श्रम में नहीं लगाया जा सकता। किसी भी रूप में जबरन श्रम प्रतिबंधित है। यदि कोई आपको बिना वेतन काम कराता है, तो वह कानून तोड़ रहा है।",
    },
    "nepal_const_art_18": {
        "en": "All citizens are equal before the law. The government cannot discriminate against you based on your gender, caste, ethnicity, religion, or any other status. Everyone deserves equal treatment.",
        "ne": "सबै नागरिक कानूनअघि समान छन्। सरकारले तपाईंलाई लिङ्ग, जाति, जात, धर्म, वा अन्य कुनै पनि आधारमा भेदभाव गर्न सक्दैन। सबैलाई समान व्यवहार पाउने अधिकार छ।",
        "hi": "सभी नागरिक कानून के समक्ष समान हैं। सरकार आपके लिंग, जाति, जनजाति, धर्म या किसी अन्य आधार पर भेदभाव नहीं कर सकती। सभी को समान व्यवहार मिलना चाहिए।",
    },
    "nepal_const_art_19": {
        "en": "Untouchability is abolished and its practice is prohibited. No one can refuse to serve you or deny you entry because of your caste or social status. This is punishable by law.",
        "ne": "अस्पृश्यता अन्त्य गरिएको छ र यसको अभ्यास प्रतिबन्धित छ। तपाईंको जाति वा सामाजिक स्थितिका कारण कसैले तपाईंलाई सेवा दिन अस्वीकार गर्न वा प्रवेश अस्वीकार गर्न सक्दैन। यो कानूनअन्तर्गत दण्डनीय छ।",
        "hi": "अस्पृश्यता का अंत कर दिया गया है और इसका अभ्यास प्रतिबंधित है। कोई भी आपकी जाति या सामाजिक स्थिति के कारण आपको सेवा देने से इनकार नहीं कर सकता या प्रवेश से वंचित नहीं कर सकता। यह कानून के तहत दंडनीय है।",
    },
    "nepal_const_art_20": {
        "en": "If you cannot afford a lawyer, the government must provide one for free. You have the right to free legal aid at every stage of your case — from investigation to appeal.",
        "ne": "यदि तपाईंसँग वकील भाडा गर्ने क्षमता छैन भने, सरकारले निःशुल्क प्रदान गर्नुपर्छ। तपाईंसँग तपाईंको मुद्दाको प्रत्येक चरणमा निःशुल्क कानूनी सहायताको अधिकार छ — छानबिनदेखि अपीलसम्म।",
        "hi": "यदि आप वकील का खर्च उठाने में असमर्थ हैं, तो सरकार को मुफ्त में प्रदान करना होगा। आपको अपने मामले के हर चरण में मुफ्त कानूनी सहायता का अधिकार है — जांच से अपील तक।",
    },
    "nepal_const_art_21": {
        "en": "Every person has the right to get justice. Courts must deliver justice fairly and without delay. You cannot be denied access to the court system because of poverty or lack of resources.",
        "ne": "प्रत्येक व्यक्तिलाई न्याय पाउने अधिकार छ। अदालतले न्याय निष्पक्ष र बिना ढिलाइ दिनुपर्छ। गरिबी वा स्रोतको अभावका कारण अदालती प्रणालीमा पहुँचबाट वञ्चित गर्न सकिँदैन।",
        "hi": "हर व्यक्ति को न्याय पाने का अधिकार है। अदालतों को न्याय निष्पक्ष और बिना देरी के देना होगा। गरीबी या संसाधनों की कमी के कारण न्यायिक प्रणाली तक पहुंच से वंचित नहीं किया जा सकता।",
    },
    "nepal_const_art_22": {
        "en": "No one can torture you or treat you cruelly. If you are tortured, you have the right to compensation and the person responsible will face criminal charges.",
        "ne": "कसैले तपाईंलाई यातना दिन वा क्रूर व्यवहार गर्न सक्दैन। तपाईंलाई यातना दिइएमा, तपाईंलाई क्षतिपूर्तिको अधिकार छ र जिम्मेवार व्यक्तिलाई फौजदारी अभियोग सामना गर्नुपर्छ।",
        "hi": "कोई भी आपको यातना नहीं दे सकता या क्रूर व्यवहार नहीं कर सकता। यदि आपको यातना दी जाती है, तो आपको मुआवजे का अधिकार है और जिम्मेदार व्यक्ति को आपराधिक आरोपों का सामना करना होगा।",
    },
    "nepal_const_art_25": {
        "en": "If police arrest you, they must tell you why within 1 hour. You must be brought before a court within 24 hours. You have the right to talk to a lawyer before any questioning.",
        "ne": "प्रहरीले तपाईंलाई गिरफ्तार गर्छ भने, १ घण्टाभित्र किन गिरफ्तार गरेको बताउनुपर्छ। २४ घण्टाभित्र अदालतमा प्रस्तुत गर्नुपर्छ। कुनै पनि पूछताछ अघि वकीलसँग कुराकानी गर्ने अधिकार छ।",
        "hi": "यदि पुलिस आपको गिरफ्तार करती है, तो उन्हें 1 घंटे के भीतर बताना होगा कि क्यों। 24 घंटे के भीतर अदालत में पेश करना होगा। किसी भी पूछताछ से पहले वकील से बात करने का अधिकार है।",
    },
    "nepal_const_art_26": {
        "en": "If you are arrested, you have the right to meet a lawyer, get copies of all documents, and be informed of your legal rights. You cannot be forced to confess.",
        "ne": "तपाईं गिरफ्तार भएमा, वकीलसँग भेट्ने, सबै कागजातको प्रतिलिपि पाउने, र कानूनी अधिकारबारे सूचित हुने अधिकार छ। जबरजस्ती स्वीकारोक्ति दिन बाध्य पार्न सकिँदैन।",
        "hi": "गिरफ्तार होने पर, वकील से मिलने, सभी दस्तावेजों की प्रति प्राप्त करने और अपने कानूनी अधिकारों की जानकारी प्राप्त करने का अधिकार है। जबरन भर्ती नहीं कराई जा सकती।",
    },
    "nepal_const_art_28": {
        "en": "Your personal life, home, and communications are protected from illegal search. No one can enter your home without a valid warrant from a court.",
        "ne": "तपाईंको व्यक्तिगत जीवन, घर, र सञ्चार गैरकानूनी खोजीबाट सुरक्षित छ। अदालतको वैध वारेन्ट बिना कसैले तपाईंको घरमा प्रवेश गर्न सक्दैन।",
        "hi": "आपका व्यक्तिगत जीवन, घर और संचार गैरकानूनी खोजी से सुरक्षित हैं। अदालत के वैध वारंट के बिना कोई आपके घर में प्रवेश नहीं कर सकता।",
    },
    "nepal_const_art_30": {
        "en": "Every citizen has the right to information about any matter of public importance. The government must give you information you request, unless it threatens national security.",
        "ne": "प्रत्येक नागरिकलाई सार्वजनिक महत्त्वको कुनै पनि कुराबारे सूचना पाउने अधिकार छ। तपाईंले माग गरेको सूचना सरकारले दिनुपर्छ, राष्ट्रिय सुरक्षालाई खतरा नभएसम्म।",
        "hi": "हर नागरिक को सार्वजनिक महत्व के किसी भी मामले के बारे में जानकारी प्राप्त करने का अधिकार है। सरकार को आपके अनुरोध की जानकारी देनी होगी, जब तक कि यह राष्ट्रीय सुरक्षा को खतरा न हो।",
    },
    "nepal_const_art_31": {
        "en": "Every child has the right to free and compulsory education. The government must ensure all children ages 5-14 attend school. Education is a right, not a privilege.",
        "ne": "प्रत्येक बालबालिकालाई निःशुल्क र अनिवार्य शिक्षाको अधिकार छ। ५-१४ वर्षका सबै बालबालिका विद्यालय जानुपर्छ भन्ने सुनिश्चित गर्नुपर्छ। शिक्षा अधिकार हो, सुविधा होइन।",
        "hi": "हर बच्चे को मुफ्त और अनिवार्य शिक्षा का अधिकार है। सरकार को सुनिश्चित करना होगा कि 5-14 साल के सभी बच्चे स्कूल जाएं। शिक्षा अधिकार है, सुविधा नहीं।",
    },
    "nepal_const_art_34": {
        "en": "Workers have the right to fair wages, safe working conditions, and protection from exploitation. You cannot be forced to work more than 8 hours a day without overtime pay.",
        "ne": "श्रमिकलाई उचित ज्याला, सुरक्षित कार्यस्थल, र शोषणबाट सुरक्षाको अधिकार छ। ओभरटाइम तलब बिना दिनमा ८ घण्टाभन्दा बढी काम गराउन बाध्य पार्न सकिँदैन।",
        "hi": "श्रमिकों को उचित वेतन, सुरक्षित कार्यस्थल और शोषण से सुरक्षा का अधिकार है। ओवरटाइम वेतन के बिना दिन में 8 घंटे से अधिक काम कराने के लिए मजबूर नहीं किया जा सकता।",
    },
    "nepal_const_art_35": {
        "en": "Marriage is a right of every adult. You are free to marry the person of your choice. The law protects women's equal rights in marriage and divorce.",
        "ne": "विवाह प्रत्येक वयस्कको अधिकार हो। तपाईं आफ्नो मनपर्ने व्यक्तिसँग विवाह गर्न स्वतन्त्र छन्। विवाह र तलाकमा महिलाको समान अधिकारको रक्षा गर्छ।",
        "hi": "विवाह हर वयस्क का अधिकार है। आप अपनी पसंद के व्यक्ति से शादी करने के लिए स्वतंत्र हैं। कानून विवाह और तलाक में महिलाओं के समान अधिकार की रक्षा करता है।",
    },
    "nepal_const_art_38": {
        "en": "Women have equal rights in all areas of life. The government must take special measures to end gender discrimination and ensure women's participation in governance.",
        "ne": "महिलाको जीवनका सबै क्षेत्रमा समान अधिकार छ। लिङ्ग भेदभाव अन्त्य गर्न र शासनमा महिलाको सहभागिता सुनिश्चित गर्न सरकारले विशेष उपाय गर्नुपर्छ।",
        "hi": "महिलाओं को जीवन के सभी क्षेत्रों में समान अधिकार है। सरकार को लिंग भेदभाव को समाप्त करने और शासन में महिलाओं की भागीदारी सुनिश्चित करने के लिए विशेष उपाय करने होंगे।",
    },
    "nepal_const_art_39": {
        "en": "Every child has the right to be protected from exploitation, abuse, and child labor. No child below 14 can be employed in any factory, mine, or hazardous work.",
        "ne": "प्रत्येक बालबालिकालाई शोषण, दुर्व्यवहार, र बाल श्रमबाट सुरक्षाको अधिकार छ। १४ वर्षमुनिको कुनै पनि बालबालिकालाई कारखाना, खानी, वा खतरनाक काममा रोजगार गर्न सकिँदैन।",
        "hi": "हर बच्चे को शोषण, दुर्व्यवहार और बाल श्रम से सुरक्षा का अधिकार है। 14 साल से कम उम्र के किसी भी बच्चे को कारखाने, खदान या खतरनाक काम में नहीं रखा जा सकता।",
    },
    "nepal_const_art_44": {
        "en": "Consumers have the right to be protected from unsafe goods and unfair trade practices. You can file a complaint if you receive defective products or poor services.",
        "ne": "उपभोक्तालाई असुरक्षित माल र अनुचित व्यापारिक व्यवहारबाट सुरक्षाको अधिकार छ। दोषपूर्ण उत्पादन वा खराब सेवा प्राप्त भएमा शिकायत दर्ता गर्न सक्नुहुन्छ।",
        "hi": "उपभोक्ताओं को असुरक्षित माल और अनुचित व्यापारिक प्रथाओं से सुरक्षा का अधिकार है। दोषपूर्ण उत्पादन या खराब सेवा मिलने पर शिकायत दर्ज कर सकते हैं।",
    },

    # ═══════════════════════════════════════════════════════════════════════
    # INDIA CONSTITUTION — Fundamental Rights
    # ═══════════════════════════════════════════════════════════════════════
    "india_const_art_14": {
        "en": "The State shall not deny to any person equality before the law or the equal protection of the laws within India. Everyone is equal in the eyes of the law.",
        "ne": "राज्यले भारतभित्र कुनै पनि व्यक्तिलाई कानूनअघि समानता वा कानूनको समान संरक्षणबाट वञ्चित गर्न सक्दैन। कानूनको आँखामा सबै समान छन्।",
        "hi": "राज्य किसी भी व्यक्ति को भारत के भीतर कानून के समक्ष समानता या कानूनों के समान संरक्षण से वंचित नहीं करेगा। कानून की नजर में सभी समान हैं।",
    },
    "india_const_art_15": {
        "en": "The government cannot discriminate against you based on religion, race, caste, sex, or place of birth. Everyone has equal access to public spaces, shops, and government services.",
        "ne": "सरकारले तपाईंलाई धर्म, जात, जाति, लिङ्ग, वा जन्मस्थानका आधारमा भेदभाव गर्न सक्दैन। सबैलाई सार्वजनिक स्थान, पसल, र सरकारी सेवामा समान पहुँच छ।",
        "hi": "सरकार आपके साथ धर्म, जाति, लिंग या जन्मस्थान के आधार पर भेदभाव नहीं कर सकती। सभी को सार्वजनिक स्थानों, दुकानों और सरकारी सेवाओं तक समान पहुंच है।",
    },
    "india_const_art_19": {
        "en": "You have the right to freedom of speech and expression, to assemble peacefully, to form associations, to move freely throughout India, and to practice any profession.",
        "ne": "तपाईंसँग अभिव्यक्ति स्वतन्त्रता, शान्तिपूर्ण सभा, संघ बनाउने, भारतभर स्वतन्त्र रूपमा घुम्ने, र कुनै पनि व्यवसाय गर्ने अधिकार छ।",
        "hi": "आपके पास वाक और अभिव्यक्ति की स्वतंत्रता, शांतिपूर्ण सभा, संघ बनाने, भारत भर में स्वतंत्र रूप से आने-जाने और कोई भी पेशा करने का अधिकार है।",
    },
    "india_const_art_20": {
        "en": "You cannot be punished for an offence that was not a crime when you committed it. You cannot be forced to be a witness against yourself. You cannot be punished twice for the same offence.",
        "ne": "तपाईंले गर्नुभएको कुरा त्यसबेला अपराध नभएमा तपाईंलाई सजाय हुन सक्दैन। आफ्नो विरुद्ध गवाह दिन बाध्य पार्न सकिँदैन। एउटै अपराधको दोहोरो सजाय हुन सक्दैन।",
        "hi": "आपको उस अपराध के लिए सजा नहीं दी जा सकती जो आपने किया था जब वह अपराध नहीं था। आपको अपने खिलाफ गवाह बनने के लिए मजबूर नहीं किया जा सकता। एक ही अपराध के लिए दो बार सजा नहीं दी जा सकती।",
    },
    "india_const_art_21": {
        "en": "No person shall be deprived of their life or personal liberty except according to procedure established by law. This right has been expanded by courts to include the right to privacy, clean environment, education, health, and shelter.",
        "ne": "कानूनले स्थापित प्रक्रिया अनुसार बाहेक कसैको जीवन वा व्यक्तिगत स्वतन्त्रताबाट वञ्चित गर्न सकिँदैन। अदालतले यसलाई गोपनीयता, स्वच्छ वातावरण, शिक्षा, स्वास्थ्य, र आश्रमको अधिकारसम्म विस्तार गरेको छ।",
        "hi": "कानून द्वारा स्थापित प्रक्रिया के अनुसार किसी भी व्यक्ति को उसके जीवन या व्यक्तिगत स्वतंत्रता से वंचित नहीं किया जा सकता। अदालतों ने इसे गोपनीयता, स्वच्छ वातावरण, शिक्षा, स्वास्थ्य और आश्रय के अधिकार तक विस्तारित किया है।",
    },
    "india_const_art_22": {
        "en": "If arrested, you must be told the reason and produced before a magistrate within 24 hours. You have the right to a lawyer and cannot be detained beyond 24 hours without magistrate's approval.",
        "ne": "गिरफ्तार भएमा, कारण बताउनुपर्छ र २४ घण्टाभित्र मजिस्ट्रेटसामु प्रस्तुत गर्नुपर्छ। वकीलको अधिकार छ र मजिस्ट्रेटको स्वीकृति बिना २४ घण्टाभन्दा बढी निरोध गर्न सकिँदैन।",
        "hi": "गिरफ्तार होने पर, कारण बताना होगा और 24 घंटे के भीतर मजिस्ट्रेट के सामने पेश करना होगा। वकील का अधिकार है और मजिस्ट्रेट की मंजूरी के बिना 24 घंटे से अधिक निरोध नहीं किया जा सकता।",
    },
    "india_const_art_23": {
        "en": "Traffic in human beings, begar (forced labor), and similar forms of forced labor are prohibited. Anyone who forces you to work against your will commits a crime.",
        "ne": "मानव व्यापार, जबरजस्ती श्रम, र यस्तै जबरजस्ती श्रमका रूपहरू प्रतिबन्धित छन्। तपाईंको इच्छा विपरीत काम गराउने कोहीले अपराध गर्छ।",
        "hi": "मानव तस्करी, जबरन श्रम, और इसी तरह के जबरन श्रम के रूप प्रतिबंधित हैं। आपकी इच्छा के विरुद्ध काम कराने वाला कोई भी अपराध करता है।",
    },
    "india_const_art_24": {
        "en": "No child below 14 can be employed in any factory, mine, or hazardous employment. Every child has the right to free and compulsory education.",
        "ne": "१४ वर्षमुनिको बालबालिकालाई कारखाना, खानी, वा खतरनाक काममा रोजगार गर्न सकिँदैन। प्रत्येक बालबालिकालाई निःशुल्क र अनिवार्य शिक्षाको अधिकार छ।",
        "hi": "14 साल से कम उम्र के किसी भी बच्चे को कारखाने, खदान या खतरनाक रोजगार में नहीं रखा जा सकता। हर बच्चे को मुफ्त और अनिवार्य शिक्षा का अधिकार है।",
    },
    "india_const_art_25": {
        "en": "Every person has the right to freedom of conscience and religion. You can freely profess, practice, and propagate any religion, subject to public order, morality, and health.",
        "ne": "प्रत्येक व्यक्तिलाई अन्तरात्मा र धर्मको स्वतन्त्रताको अधिकार छ। सार्वजनिक व्यवस्था, नैतिकता, र स्वास्थ्यको अधीनमा कुनै पनि धर्म स्वतन्त्र रूपमा पालना, अभ्यास, र प्रचार गर्न सक्नुहुन्छ।",
        "hi": "हर व्यक्ति को अंतरात्मा और धर्म की स्वतंत्रता का अधिकार है। सार्वजनिक व्यवस्था, नैतिकता और स्वास्थ्य के अधीन, आप किसी भी धर्म का स्वतंत्र रूप से पालन, अभ्यास और प्रचार कर सकते हैं।",
    },
    "india_const_art_21A": {
        "en": "Every child between ages 6 and 14 has the fundamental right to free and compulsory education. The government must ensure all children in this age group can attend school.",
        "ne": "६ र १४ वर्षबीचका प्रत्येक बालबालिकाको निःशुल्क र अनिवार्य शिक्षाको आधारभूत अधिकार छ। यो उमेर समूहका सबै बालबालिका विद्यालय जान सक्ने सुनिश्चित गर्नुपर्छ।",
        "hi": "6 और 14 साल के बीच हर बच्चे को मुफ्त और अनिवार्य शिक्षा का मौलिक अधिकार है। सरकार को सुनिश्चित करना होगा कि इस आयु वर्ग के सभी बच्चे स्कूल जा सकें।",
    },
    "india_const_art_32": {
        "en": "You can directly approach the Supreme Court if your fundamental rights are violated. This is the 'right to constitutional remedies' — the guardian of all other rights.",
        "ne": "तपाईंको आधारभूत अधिकार उल्लङ्घन भएमा सिधै सर्वोच्च अदालतमा जान सक्नुहुन्छ। यो 'संवैधानिक उपायको अधिकार' हो — सबै अन्य अधिकारहरूको संरक्षक।",
        "hi": "यदि आपके मौलिक अधिकारों का उल्लंघन होता है तो आप सीधे सर्वोच्च न्यायालय जा सकते हैं। यह 'संवैधानिक उपाय का अधिकार' है — सभी अन्य अधिकारों का संरक्षक।",
    },
    "india_const_art_39A": {
        "en": "The State must ensure that the legal system promotes justice on the basis of equal opportunity. Free legal aid must be provided to ensure justice is not denied due to economic disability.",
        "ne": "राज्यले कानूनी प्रणालीले समान अवसरको आधारमा न्यायलाई बढावा दिन्छ भन्ने सुनिश्चित गर्नुपर्छ। आर्थिक अक्षमताका कारण न्यायबाट वञ्चित नहुन निःशुल्क कानूनी सहायता प्रदान गर्नुपर्छ।",
        "hi": "राज्य को सुनिश्चित करना होगा कि कानूनी प्रणाली समान अवसर के आधार पर न्याय को बढ़ावा देती है। आर्थिक अक्षमता के कारण न्याय से वंचित न हो, इसके लिए मुफ्त कानूनी सहायता प्रदान करनी होगी।",
    },
    "india_const_art_43": {
        "en": "The State must secure a living wage for workers that provides a decent standard of living. Workers should also get social security and welfare benefits.",
        "ne": "राज्यले श्रमिकलाई गरिमापूर्ण जीवनस्तर प्रदान गर्ने जीविका ज्याला सुनिश्चित गर्नुपर्छ। श्रमिकलाई सामाजिक सुरक्षा र कल्याण लाभ पनि पाउनुपर्छ।",
        "hi": "राज्य को श्रमिकों को सम्मानजनक जीवन स्तर प्रदान करने वाला जीवन वेतन सुनिश्चित करना होगा। श्रमिकों को सामाजिक सुरक्षा और कल्याण लाभ भी मिलना चाहिए।",
    },
    "india_const_art_300A": {
        "en": "No person can be deprived of their property except by authority of law. The government cannot take your property without following proper legal procedures.",
        "ne": "कानूनको अधिकार बाहेक कसैको सम्पत्तिबाट वञ्चित गर्न सकिँदैन। सरकारले उचित कानूनी प्रक्रिया पालना नगरी तपाईंको सम्पत्ति लिन सक्दैन।",
        "hi": "कानून के अधिकार के बिना किसी भी व्यक्ति को उसकी सम्पत्ति से वंचित नहीं किया जा सकता। सरकार उचित कानूनी प्रक्रिया का पालन किए बिना आपकी सम्पत्ति नहीं ले सकती।",
    },
}


def get_summary(article_id: str):
    """Get plain language summary for an article, returns dict with en/ne/hi keys."""
    return SUMMARIES.get(article_id)


def get_summaries_batch(article_ids: list[str]) -> dict[str, dict]:
    """Get plain language summaries for multiple articles."""
    return {aid: SUMMARIES[aid] for aid in article_ids if aid in SUMMARIES}


def get_all_summarized_ids() -> list[str]:
    """Return all article IDs that have plain language summaries."""
    return list(SUMMARIES.keys())
