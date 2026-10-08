"""Reviewed Hindi and Marathi translations for the existing loan/scheme catalog."""

from psycopg2.extras import execute_values


LANGUAGES = ('hi', 'mr')


NAME_TRANSLATIONS = {
    'Pradhan Mantri Kisan Credit Card': ('प्रधानमंत्री किसान क्रेडिट कार्ड', 'प्रधानमंत्री किसान क्रेडिट कार्ड'),
    'Agriculture Infrastructure Fund': ('कृषि अवसंरचना कोष', 'कृषी पायाभूत सुविधा निधी'),
    'NABARD Farm Loan': ('नाबार्ड कृषि ऋण', 'नाबार्ड कृषी कर्ज'),
    'Pradhan Mantri Fasal Bima Yojana': ('प्रधानमंत्री फसल बीमा योजना', 'प्रधानमंत्री पीक विमा योजना'),
    'Pradhan Mantri Kisan Samman Nidhi': ('प्रधानमंत्री किसान सम्मान निधि', 'प्रधानमंत्री किसान सन्मान निधी'),
    'Pradhan Mantri Kisan Maandhan Yojana': ('प्रधानमंत्री किसान मानधन योजना', 'प्रधानमंत्री किसान मानधन योजना'),
    'Pradhan Mantri Krishi Sinchayee Yojana': ('प्रधानमंत्री कृषि सिंचाई योजना', 'प्रधानमंत्री कृषी सिंचन योजना'),
    'Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan': ('प्रधानमंत्री किसान ऊर्जा सुरक्षा एवं उत्थान महाभियान', 'प्रधानमंत्री किसान ऊर्जा सुरक्षा एवं उत्थान महाभियान'),
    'Sub-Mission on Agricultural Mechanization': ('कृषि मशीनीकरण उप-मिशन', 'कृषी यांत्रिकीकरण उप-अभियान'),
    'Mission for Integrated Development of Horticulture': ('एकीकृत बागवानी विकास मिशन', 'एकात्मिक फलोत्पादन विकास अभियान'),
    'National Mission for Sustainable Agriculture': ('राष्ट्रीय सतत कृषि मिशन', 'राष्ट्रीय शाश्वत कृषी अभियान'),
    'National Food Security Mission': ('राष्ट्रीय खाद्य सुरक्षा मिशन', 'राष्ट्रीय अन्न सुरक्षा अभियान'),
    'Rashtriya Krishi Vikas Yojana': ('राष्ट्रीय कृषि विकास योजना', 'राष्ट्रीय कृषी विकास योजना'),
    'Formation and Promotion of 10,000 Farmer Producer Organizations': ('10,000 किसान उत्पादक संगठनों का गठन और संवर्धन', '10,000 शेतकरी उत्पादक संस्थांची स्थापना व प्रोत्साहन'),
    'Agricultural Marketing Infrastructure': ('कृषि विपणन अवसंरचना', 'कृषी विपणन पायाभूत सुविधा'),
    'Animal Husbandry Infrastructure Development Fund': ('पशुपालन अवसंरचना विकास कोष', 'पशुसंवर्धन पायाभूत सुविधा विकास निधी'),
    'Pradhan Mantri Matsya Sampada Yojana': ('प्रधानमंत्री मत्स्य संपदा योजना', 'प्रधानमंत्री मत्स्य संपदा योजना'),
}


TYPE_TRANSLATIONS = {
    'Agriculture': ('कृषि ऋण', 'कृषी कर्ज'),
    'Infrastructure': ('अवसंरचना', 'पायाभूत सुविधा'),
    'Crop Insurance Scheme': ('फसल बीमा योजना', 'पीक विमा योजना'),
    'Income Support Scheme': ('आय सहायता योजना', 'उत्पन्न सहाय्य योजना'),
    'Contributory Pension Scheme': ('अंशदायी पेंशन योजना', 'अंशदायी निवृत्तीवेतन योजना'),
    'Irrigation Support Scheme': ('सिंचाई सहायता योजना', 'सिंचन सहाय्य योजना'),
    'Solar Energy Support Scheme': ('सौर ऊर्जा सहायता योजना', 'सौर ऊर्जा सहाय्य योजना'),
    'Farm Mechanization Scheme': ('कृषि मशीनीकरण योजना', 'कृषी यांत्रिकीकरण योजना'),
    'Horticulture Support Scheme': ('बागवानी सहायता योजना', 'फलोत्पादन सहाय्य योजना'),
    'Sustainable Agriculture Scheme': ('सतत कृषि योजना', 'शाश्वत कृषी योजना'),
    'Crop Development Scheme': ('फसल विकास योजना', 'पीक विकास योजना'),
    'Agricultural Development Scheme': ('कृषि विकास योजना', 'कृषी विकास योजना'),
    'Farmer Collective Scheme': ('किसान सामूहिक योजना', 'शेतकरी सामूहिक योजना'),
    'Credit-linked Subsidy Scheme': ('ऋण-संबद्ध सब्सिडी योजना', 'कर्ज-संलग्न अनुदान योजना'),
    'Infrastructure Finance Scheme': ('अवसंरचना वित्त योजना', 'पायाभूत सुविधा वित्त योजना'),
    'Fisheries Development Scheme': ('मत्स्य विकास योजना', 'मत्स्यव्यवसाय विकास योजना'),
}


DESCRIPTION_TRANSLATIONS = {
    'Loan for farmers for crop production': ('फसल उत्पादन के लिए किसानों को ऋण।', 'पीक उत्पादनासाठी शेतकऱ्यांना कर्ज.'),
    'Supports post-harvest management': ('कटाई के बाद के प्रबंधन में सहायता करता है।', 'काढणीनंतरच्या व्यवस्थापनासाठी सहाय्य करते.'),
    'Financial support for rural farmers': ('ग्रामीण किसानों के लिए वित्तीय सहायता।', 'ग्रामीण शेतकऱ्यांसाठी आर्थिक सहाय्य.'),
    'Government crop-insurance scheme for notified crops and areas against specified production risks.': ('अधिसूचित फसलों और क्षेत्रों को निर्धारित उत्पादन जोखिमों से सुरक्षा देने वाली सरकारी फसल बीमा योजना।', 'अधिसूचित पिके व क्षेत्रांना ठरावीक उत्पादन जोखमींपासून संरक्षण देणारी शासकीय पीक विमा योजना.'),
    'Central income-support scheme for eligible landholding farmer families.': ('पात्र भूमिधारक किसान परिवारों के लिए केंद्रीय आय सहायता योजना।', 'पात्र जमीनधारक शेतकरी कुटुंबांसाठी केंद्रीय उत्पन्न सहाय्य योजना.'),
    'Voluntary contributory pension scheme for eligible small and marginal farmers.': ('पात्र लघु और सीमांत किसानों के लिए स्वैच्छिक अंशदायी पेंशन योजना।', 'पात्र लहान व सीमांत शेतकऱ्यांसाठी ऐच्छिक अंशदायी निवृत्तीवेतन योजना.'),
    'Umbrella program supporting irrigation access, water efficiency and watershed development.': ('सिंचाई की पहुँच, जल दक्षता और जलागम विकास में सहायता देने वाला व्यापक कार्यक्रम।', 'सिंचन उपलब्धता, जल कार्यक्षमता व पाणलोट विकासाला सहाय्य करणारा व्यापक कार्यक्रम.'),
    'Scheme supporting solar pumps, pump or feeder solarisation and decentralized renewable energy.': ('सौर पंप, पंप या फीडर सौरकरण तथा विकेंद्रीकृत नवीकरणीय ऊर्जा में सहायता देने वाली योजना।', 'सौर पंप, पंप किंवा फीडर सौरिकीकरण आणि विकेंद्रित अक्षय ऊर्जेला सहाय्य करणारी योजना.'),
    'Program supporting access to tested farm machinery, equipment and custom-hiring services.': ('परीक्षित कृषि मशीनरी, उपकरण और कस्टम-हायरिंग सेवाओं तक पहुँच में सहायता देने वाला कार्यक्रम।', 'तपासलेली कृषी यंत्रे, उपकरणे व कस्टम-हायरिंग सेवांची उपलब्धता वाढवणारा कार्यक्रम.'),
    'Mission supporting holistic development of fruits, vegetables, spices and other horticulture.': ('फल, सब्जी, मसाले और अन्य बागवानी के समग्र विकास में सहायता देने वाला मिशन।', 'फळे, भाजीपाला, मसाले व इतर फलोत्पादनाच्या सर्वांगीण विकासाला सहाय्य करणारे अभियान.'),
    'Mission promoting resilient farming and improved soil, water and natural-resource management.': ('जलवायु-सहनीय खेती तथा बेहतर मिट्टी, जल और प्राकृतिक-संसाधन प्रबंधन को बढ़ावा देने वाला मिशन।', 'हवामान-सक्षम शेती तसेच सुधारित माती, पाणी व नैसर्गिक-संसाधन व्यवस्थापनाला प्रोत्साहन देणारे अभियान.'),
    'Mission supporting production and productivity improvement for notified food crops.': ('अधिसूचित खाद्य फसलों के उत्पादन और उत्पादकता में सुधार हेतु सहायता देने वाला मिशन।', 'अधिसूचित अन्नपिकांचे उत्पादन व उत्पादकता सुधारण्यासाठी सहाय्य करणारे अभियान.'),
    'Framework supporting approved state agriculture, allied-sector, infrastructure and innovation projects.': ('स्वीकृत राज्य कृषि, संबद्ध क्षेत्र, अवसंरचना और नवाचार परियोजनाओं को सहायता देने वाला ढाँचा।', 'मंजूर राज्य कृषी, संलग्न क्षेत्र, पायाभूत सुविधा व नवकल्पना प्रकल्पांना सहाय्य करणारी चौकट.'),
    'Central scheme for formation and professional support of eligible Farmer Producer Organizations.': ('पात्र किसान उत्पादक संगठनों के गठन और व्यावसायिक सहायता के लिए केंद्रीय योजना।', 'पात्र शेतकरी उत्पादक संस्थांची स्थापना व व्यावसायिक सहाय्यासाठी केंद्रीय योजना.'),
    'Sub-scheme supporting eligible storage and agricultural marketing infrastructure projects.': ('पात्र भंडारण और कृषि विपणन अवसंरचना परियोजनाओं को सहायता देने वाली उप-योजना।', 'पात्र साठवण व कृषी विपणन पायाभूत सुविधा प्रकल्पांना सहाय्य करणारी उप-योजना.'),
    'Credit-linked support for eligible dairy, meat, feed and animal-husbandry infrastructure.': ('पात्र डेयरी, मांस, चारा और पशुपालन अवसंरचना के लिए ऋण-संबद्ध सहायता।', 'पात्र दुग्धव्यवसाय, मांस, पशुखाद्य व पशुसंवर्धन पायाभूत सुविधांसाठी कर्ज-संलग्न सहाय्य.'),
    'Fisheries program supporting eligible production, infrastructure, value-chain and welfare activities.': ('पात्र उत्पादन, अवसंरचना, मूल्य-श्रृंखला और कल्याण गतिविधियों को सहायता देने वाला मत्स्य कार्यक्रम।', 'पात्र उत्पादन, पायाभूत सुविधा, मूल्यसाखळी व कल्याणकारी उपक्रमांना सहाय्य करणारा मत्स्यव्यवसाय कार्यक्रम.'),
}


INTEREST_TRANSLATIONS = {
    '4%': ('4%', '4%'), '3%': ('3%', '3%'), '5%': ('5%', '5%'),
    'Premium; not loan interest': ('प्रीमियम; ऋण ब्याज नहीं', 'विमा हप्ता; कर्जाचे व्याज नाही'),
    'Not applicable': ('लागू नहीं', 'लागू नाही'),
    'Varies by lender/component': ('ऋणदाता/घटक के अनुसार', 'कर्जदाता/घटकानुसार बदलते'),
    'Lender rate applies': ('ऋणदाता की दर लागू', 'कर्जदात्याचा दर लागू'),
    'Lender rate; 3% subvention': ('ऋणदाता की दर; 3% ब्याज सहायता', 'कर्जदात्याचा दर; 3% व्याज सवलत'),
    'Varies by assistance type': ('सहायता के प्रकार के अनुसार', 'सहाय्याच्या प्रकारानुसार बदलते'),
}


AMOUNT_TRANSLATIONS = {
    '3 lakh': ('3 लाख', '3 लाख'), '2 crore': ('2 करोड़', '2 कोटी'),
    '5 lakh': ('5 लाख', '5 लाख'),
    'Notified crop sum insured': ('अधिसूचित फसल की बीमित राशि', 'अधिसूचित पिकाची विमा रक्कम'),
    'Rs 6,000 yearly if eligible': ('पात्र होने पर ₹6,000 प्रति वर्ष', 'पात्र असल्यास ₹6,000 प्रति वर्ष'),
    'Rs 3,000 monthly pension': ('₹3,000 मासिक पेंशन', '₹3,000 मासिक निवृत्तीवेतन'),
    'As per component rules': ('घटक के नियमों के अनुसार', 'घटकाच्या नियमांनुसार'),
    'As per state guidelines': ('राज्य के दिशा-निर्देशों के अनुसार', 'राज्याच्या मार्गदर्शक सूचनांनुसार'),
    'As per crop/state program': ('फसल/राज्य कार्यक्रम के अनुसार', 'पीक/राज्य कार्यक्रमानुसार'),
    'As per approved project': ('स्वीकृत परियोजना के अनुसार', 'मंजूर प्रकल्पानुसार'),
    'As per FPO guidelines': ('FPO दिशा-निर्देशों के अनुसार', 'FPO मार्गदर्शक सूचनांनुसार'),
    'As per AMI project norms': ('AMI परियोजना मानदंडों के अनुसार', 'AMI प्रकल्प निकषांनुसार'),
    'Up to 90% eligible cost': ('पात्र लागत का 90% तक', 'पात्र खर्चाच्या 90% पर्यंत'),
    'As per activity guidelines': ('गतिविधि दिशा-निर्देशों के अनुसार', 'उपक्रमाच्या मार्गदर्शक सूचनांनुसार'),
}


BENEFIT_TRANSLATIONS = {
    'Low interest and easy repayment': ('कम ब्याज और आसान पुनर्भुगतान।', 'कमी व्याज आणि सुलभ परतफेड.'),
    'Interest subsidy and long tenure': ('ब्याज सहायता और लंबी अवधि।', 'व्याज सवलत आणि दीर्घ मुदत.'),
    'Flexible repayment options': ('लचीले पुनर्भुगतान विकल्प।', 'लवचिक परतफेड पर्याय.'),
    'Subsidized crop-insurance protection subject to notification, enrolment dates and scheme rules.': ('अधिसूचना, नामांकन तिथियों और योजना नियमों के अधीन सब्सिडी वाला फसल बीमा संरक्षण।', 'अधिसूचना, नोंदणीच्या तारखा व योजनेच्या नियमांच्या अधीन अनुदानित पीक विमा संरक्षण.'),
    'Direct benefit transfer in three instalments, subject to current eligibility and verification.': ('वर्तमान पात्रता और सत्यापन के अधीन तीन किस्तों में प्रत्यक्ष लाभ अंतरण।', 'सध्याची पात्रता व पडताळणीच्या अधीन तीन हप्त्यांत थेट लाभ हस्तांतरण.'),
    'Old-age protection after age 60, subject to entry-age, contribution and eligibility rules.': ('प्रवेश आयु, अंशदान और पात्रता नियमों के अधीन 60 वर्ष की आयु के बाद वृद्धावस्था सुरक्षा।', 'प्रवेश वय, योगदान व पात्रता नियमांच्या अधीन 60 वर्षांनंतर वृद्धापकाळ संरक्षण.'),
    'Support for approved irrigation, watershed and water-efficiency interventions.': ('स्वीकृत सिंचाई, जलागम और जल-दक्षता उपायों के लिए सहायता।', 'मंजूर सिंचन, पाणलोट व जल-कार्यक्षमता उपायांसाठी सहाय्य.'),
    'Solar-energy support for eligible farmers under current central and state implementation rules.': ('वर्तमान केंद्र और राज्य कार्यान्वयन नियमों के अंतर्गत पात्र किसानों के लिए सौर-ऊर्जा सहायता।', 'सध्याच्या केंद्र व राज्य अंमलबजावणी नियमांनुसार पात्र शेतकऱ्यांसाठी सौर-ऊर्जा सहाय्य.'),
    'Eligible mechanization assistance under applicable beneficiary and state implementation rules.': ('लागू लाभार्थी और राज्य कार्यान्वयन नियमों के अंतर्गत पात्र मशीनीकरण सहायता।', 'लागू लाभार्थी व राज्य अंमलबजावणी नियमांनुसार पात्र यांत्रिकीकरण सहाय्य.'),
    'Eligible support for horticulture production, post-harvest management and infrastructure.': ('बागवानी उत्पादन, कटाई-पश्चात प्रबंधन और अवसंरचना के लिए पात्र सहायता।', 'फलोत्पादन, काढणीनंतरचे व्यवस्थापन व पायाभूत सुविधांसाठी पात्र सहाय्य.'),
    'Support for approved sustainable-agriculture and resource-management interventions.': ('स्वीकृत सतत-कृषि और संसाधन-प्रबंधन उपायों के लिए सहायता।', 'मंजूर शाश्वत-कृषी व संसाधन-व्यवस्थापन उपायांसाठी सहाय्य.'),
    'Eligible demonstrations, seed, machinery or conservation support through implementing agencies.': ('कार्यान्वयन एजेंसियों के माध्यम से पात्र प्रदर्शन, बीज, मशीनरी या संरक्षण सहायता।', 'अंमलबजावणी संस्थांमार्फत पात्र प्रात्यक्षिके, बियाणे, यंत्रसामग्री किंवा संवर्धन सहाय्य.'),
    'Support for approved state projects and eligible agripreneurship or innovation components.': ('स्वीकृत राज्य परियोजनाओं और पात्र कृषि-उद्यमिता या नवाचार घटकों के लिए सहायता।', 'मंजूर राज्य प्रकल्प व पात्र कृषी-उद्योजकता किंवा नवकल्पना घटकांसाठी सहाय्य.'),
    'Handholding, capacity building and eligible financial support for participating FPOs.': ('भाग लेने वाले FPO के लिए मार्गदर्शन, क्षमता निर्माण और पात्र वित्तीय सहायता।', 'सहभागी FPO साठी मार्गदर्शन, क्षमता बांधणी व पात्र आर्थिक सहाय्य.'),
    'Credit-linked back-ended subsidy for eligible storage, processing and marketing infrastructure.': ('पात्र भंडारण, प्रसंस्करण और विपणन अवसंरचना के लिए ऋण-संबद्ध बैक-एंड सब्सिडी।', 'पात्र साठवण, प्रक्रिया व विपणन पायाभूत सुविधांसाठी कर्ज-संलग्न पश्च-अनुदान.'),
    'Interest subvention and possible credit-guarantee support for eligible viable projects.': ('पात्र व्यवहार्य परियोजनाओं के लिए ब्याज सहायता और संभावित ऋण-गारंटी सहयोग।', 'पात्र व्यवहार्य प्रकल्पांसाठी व्याज सवलत व संभाव्य कर्ज-हमी सहाय्य.'),
    'Financial, technical or infrastructure support for approved fisheries and aquaculture activities.': ('स्वीकृत मत्स्य पालन और जलीय कृषि गतिविधियों के लिए वित्तीय, तकनीकी या अवसंरचना सहायता।', 'मंजूर मत्स्यव्यवसाय व मत्स्यशेती उपक्रमांसाठी आर्थिक, तांत्रिक किंवा पायाभूत सहाय्य.'),
}


def _pick(mapping, key, language):
    value = mapping[key]
    return value[0] if language == 'hi' else value[1]


def seed_loan_translations(cursor):
    cursor.execute("SELECT COUNT(*) FROM content_translations WHERE entity_type='loan'")
    existing_count = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT loan_id, name, short_name, type, region, description,
               interest, max_amount, benefits
        FROM loans ORDER BY loan_id
        """
    )
    records = cursor.fetchall()
    values = []
    for record in records:
        (loan_id, name, short_name, loan_type, region, description,
         interest, max_amount, benefits) = record
        for language in LANGUAGES:
            translated_fields = {
                'name': _pick(NAME_TRANSLATIONS, name, language),
                'short_name': short_name,
                'type': _pick(TYPE_TRANSLATIONS, loan_type, language),
                'region': 'भारत',
                'description': _pick(DESCRIPTION_TRANSLATIONS, description, language),
                'interest': _pick(INTEREST_TRANSLATIONS, interest, language),
                'max_amount': _pick(AMOUNT_TRANSLATIONS, max_amount, language),
                'benefits': _pick(BENEFIT_TRANSLATIONS, benefits, language),
            }
            values.extend(
                ('loan', loan_id, field_name, language, translated_text, True)
                for field_name, translated_text in translated_fields.items()
            )

    execute_values(
        cursor,
        """
        INSERT INTO content_translations
            (entity_type, entity_id, field_name, language_code,
             translated_text, reviewed)
        VALUES %s
        ON CONFLICT (entity_type, entity_id, field_name, language_code)
        DO NOTHING
        """,
        values,
    )
    cursor.execute("SELECT COUNT(*) FROM content_translations WHERE entity_type='loan'")
    final_count = cursor.fetchone()[0]
    return len(records), len(values), final_count - existing_count
