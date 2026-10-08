"""Reviewed Hindi and Marathi translations for the existing fertilizer catalog."""

import re

from psycopg2.extras import execute_values


LANGUAGES = ('hi', 'mr')


TYPE_TRANSLATIONS = {
    'Nitrogen': ('नाइट्रोजन उर्वरक', 'नत्र खत'),
    'Phosphatic': ('फॉस्फेटिक उर्वरक', 'स्फुरदयुक्त खत'),
    'Potassic': ('पोटाश उर्वरक', 'पालाशयुक्त खत'),
    'Potassium': ('पोटैशियम उर्वरक', 'पालाशयुक्त खत'),
    'Nitrogen and Sulphur': ('नाइट्रोजन और सल्फर उर्वरक', 'नत्र व गंधकयुक्त खत'),
    'Water-soluble': ('जल में घुलनशील', 'पाण्यात विरघळणारे'),
    'Secondary nutrient': ('द्वितीयक पोषक तत्व', 'दुय्यम अन्नद्रव्य'),
    'Soil amendment': ('मृदा सुधारक', 'मृदा सुधारक'),
    'Sulphur fertilizer': ('सल्फर उर्वरक', 'गंधकयुक्त खत'),
    'Micronutrient': ('सूक्ष्म पोषक तत्व', 'सूक्ष्म अन्नद्रव्य'),
    'Chelated micronutrient': ('कीलेटेड सूक्ष्म पोषक तत्व', 'चिलेटेड सूक्ष्म अन्नद्रव्य'),
    'Compound NPK': ('मिश्रित NPK उर्वरक', 'संयुक्त NPK खत'),
    'Organic manure': ('जैविक खाद', 'सेंद्रिय खत'),
    'Enriched organic manure': ('समृद्ध जैविक खाद', 'समृद्ध सेंद्रिय खत'),
    'Organic soil conditioner': ('जैविक मृदा सुधारक', 'सेंद्रिय मृदा सुधारक'),
    'Oil-cake manure': ('खली खाद', 'पेंड खत'),
    'Organic phosphatic manure': ('जैविक फॉस्फेटिक खाद', 'सेंद्रिय स्फुरदयुक्त खत'),
    'Organic nitrogen fertilizer': ('जैविक नाइट्रोजन उर्वरक', 'सेंद्रिय नत्र खत'),
    'Biostimulant and organic input': ('जैव-उत्तेजक और जैविक इनपुट', 'जैव-उत्तेजक व सेंद्रिय निविष्ठा'),
    'Biostimulant': ('जैव-उत्तेजक', 'जैव-उत्तेजक'),
    'Soil conditioner': ('मृदा सुधारक', 'मृदा सुधारक'),
    'Biofertilizer': ('जैव उर्वरक', 'जैविक खत'),
}


NAME_TRANSLATIONS = {
    'Urea': ('यूरिया', 'युरिया'),
    'DAP': ('डीएपी', 'डीएपी'),
    'MOP': ('एमओपी', 'एमओपी'),
    'Ammonium Sulphate': ('अमोनियम सल्फेट', 'अमोनियम सल्फेट'),
    'Calcium Ammonium Nitrate': ('कैल्शियम अमोनियम नाइट्रेट', 'कॅल्शियम अमोनियम नायट्रेट'),
    'Ammonium Chloride': ('अमोनियम क्लोराइड', 'अमोनियम क्लोराइड'),
    'Single Super Phosphate': ('सिंगल सुपर फॉस्फेट', 'सिंगल सुपर फॉस्फेट'),
    'Triple Super Phosphate': ('ट्रिपल सुपर फॉस्फेट', 'ट्रिपल सुपर फॉस्फेट'),
    'Reactive Rock Phosphate': ('प्रतिक्रियाशील रॉक फॉस्फेट', 'प्रतिक्रियाशील रॉक फॉस्फेट'),
    'Sulphate of Potash': ('पोटाश सल्फेट', 'पोटॅश सल्फेट'),
    'Potassium Nitrate': ('पोटैशियम नाइट्रेट', 'पोटॅशियम नायट्रेट'),
    'Monoammonium Phosphate': ('मोनोअमोनियम फॉस्फेट', 'मोनोअमोनियम फॉस्फेट'),
    'Monopotassium Phosphate': ('मोनोपोटैशियम फॉस्फेट', 'मोनोपोटॅशियम फॉस्फेट'),
    'Calcium Nitrate': ('कैल्शियम नाइट्रेट', 'कॅल्शियम नायट्रेट'),
    'Magnesium Sulphate': ('मैग्नीशियम सल्फेट', 'मॅग्नेशियम सल्फेट'),
    'Kieserite': ('कीसेराइट', 'कीझेराइट'),
    'Agricultural Dolomite': ('कृषि डोलोमाइट', 'कृषी डोलोमाइट'),
    'Agricultural Lime': ('कृषि चूना', 'कृषी चुना'),
    'Agricultural Gypsum': ('कृषि जिप्सम', 'कृषी जिप्सम'),
    'Bentonite Sulphur': ('बेंटोनाइट सल्फर', 'बेंटोनाइट गंधक'),
    'Zinc Sulphate Heptahydrate': ('जिंक सल्फेट हेप्टाहाइड्रेट', 'झिंक सल्फेट हेप्टाहायड्रेट'),
    'Zinc Sulphate Monohydrate': ('जिंक सल्फेट मोनोहाइड्रेट', 'झिंक सल्फेट मोनोहायड्रेट'),
    'Ferrous Sulphate': ('फेरस सल्फेट', 'फेरस सल्फेट'),
    'Copper Sulphate': ('कॉपर सल्फेट', 'कॉपर सल्फेट'),
    'Manganese Sulphate': ('मैंगनीज सल्फेट', 'मॅंगनीज सल्फेट'),
    'Borax': ('बोरेक्स', 'बोरॅक्स'),
    'Boric Acid': ('बोरिक अम्ल', 'बोरिक आम्ल'),
    'Sodium Molybdate': ('सोडियम मोलिब्डेट', 'सोडियम मॉलिब्डेट'),
    'Ammonium Molybdate': ('अमोनियम मोलिब्डेट', 'अमोनियम मॉलिब्डेट'),
    'Zinc EDTA Chelate': ('जिंक EDTA कीलेट', 'झिंक EDTA चिलेट'),
    'Iron EDTA Chelate': ('आयरन EDTA कीलेट', 'लोह EDTA चिलेट'),
    'Manganese EDTA Chelate': ('मैंगनीज EDTA कीलेट', 'मॅंगनीज EDTA चिलेट'),
    'Copper EDTA Chelate': ('कॉपर EDTA कीलेट', 'कॉपर EDTA चिलेट'),
    'Farmyard Manure': ('गोबर की खाद', 'शेणखत'),
    'Vermicompost': ('केंचुआ खाद', 'गांडूळ खत'),
    'Enriched Vermicompost': ('समृद्ध केंचुआ खाद', 'समृद्ध गांडूळ खत'),
    'City Compost': ('शहरी कंपोस्ट', 'शहरी कंपोस्ट'),
    'Phosphocompost': ('फॉस्फोकंपोस्ट', 'फॉस्फोकंपोस्ट'),
    'Press Mud Compost': ('प्रेसमड कंपोस्ट', 'प्रेसमड कंपोस्ट'),
    'Coir Pith Compost': ('नारियल रेशा कंपोस्ट', 'नारळ काथ्या कंपोस्ट'),
    'Poultry Manure Compost': ('मुर्गी खाद कंपोस्ट', 'कुक्कुट खत कंपोस्ट'),
    'Sheep and Goat Manure Compost': ('भेड़-बकरी खाद कंपोस्ट', 'मेंढी-शेळी खत कंपोस्ट'),
    'Neem Cake': ('नीम खली', 'निंबोळी पेंड'),
    'Groundnut Cake': ('मूंगफली खली', 'भुईमूग पेंड'),
    'Castor Cake': ('अरंडी खली', 'एरंडी पेंड'),
    'Mustard Cake': ('सरसों खली', 'मोहरी पेंड'),
    'Karanja Cake': ('करंज खली', 'करंज पेंड'),
    'Steamed Bone Meal': ('भाप-उपचारित हड्डी चूर्ण', 'वाफ-प्रक्रियायुक्त हाडांची भुकटी'),
    'Fish Meal Fertilizer': ('मछली चूर्ण उर्वरक', 'मत्स्यचूर्ण खत'),
    'Blood Meal Fertilizer': ('रक्त चूर्ण उर्वरक', 'रक्तचूर्ण खत'),
    'Horn and Hoof Meal': ('सींग और खुर चूर्ण', 'शिंग व खूर भुकटी'),
    'Seaweed Granules': ('समुद्री शैवाल दाने', 'समुद्री शेवाळ कण'),
    'Seaweed Liquid Extract': ('समुद्री शैवाल तरल अर्क', 'समुद्री शेवाळ द्रव अर्क'),
    'Humic Acid Granules': ('ह्यूमिक अम्ल दाने', 'ह्युमिक आम्ल कण'),
    'Fulvic Acid Concentrate': ('फुल्विक अम्ल सांद्र', 'फुल्विक आम्ल सांद्र'),
    'Rhizobium Inoculant': ('राइजोबियम संवर्धक', 'रायझोबियम संवर्धक'),
    'Azotobacter Inoculant': ('एजोटोबैक्टर संवर्धक', 'अ‍ॅझोटोबॅक्टर संवर्धक'),
    'Azospirillum Inoculant': ('एजोस्पिरिलम संवर्धक', 'अ‍ॅझोस्पिरिलम संवर्धक'),
    'Phosphate Solubilizing Bacteria': ('फॉस्फेट घुलनशील जीवाणु', 'स्फुरद विरघळवणारे जिवाणू'),
    'Potassium Mobilizing Bacteria': ('पोटैशियम सक्रिय करने वाले जीवाणु', 'पालाश उपलब्ध करणारे जिवाणू'),
    'Zinc Solubilizing Bacteria': ('जिंक घुलनशील जीवाणु', 'झिंक विरघळवणारे जिवाणू'),
    'Acetobacter diazotrophicus Inoculant': ('एसीटोबैक्टर डायजोट्रोफिकस संवर्धक', 'अ‍ॅसिटोबॅक्टर डायझोट्रोफिकस संवर्धक'),
    'Blue Green Algae Biofertilizer': ('नील-हरित शैवाल जैव उर्वरक', 'निळे-हिरवे शेवाळ जैविक खत'),
    'Azolla Biofertilizer': ('एजोला जैव उर्वरक', 'अ‍ॅझोला जैविक खत'),
    'Arbuscular Mycorrhizal Fungi': ('आर्बस्कुलर माइकोराइजल कवक', 'आर्बस्क्युलर मायकोरायझल बुरशी'),
    'Microbial Biofertilizer Consortium': ('सूक्ष्मजीवी जैव उर्वरक मिश्रण', 'सूक्ष्मजीव जैविक खत समूह'),
    'Trichoderma-enriched Organic Manure': ('ट्राइकोडर्मा-समृद्ध जैविक खाद', 'ट्रायकोडर्मा-समृद्ध सेंद्रिय खत'),
    'Sulphur Oxidizing Bacteria': ('सल्फर ऑक्सीकरण जीवाणु', 'गंधक ऑक्सिडीकरण जिवाणू'),
    'Silicate Solubilizing Bacteria': ('सिलिकेट घुलनशील जीवाणु', 'सिलिकेट विरघळवणारे जिवाणू'),
    'Liquid Biofertilizer Consortium': ('तरल जैव उर्वरक मिश्रण', 'द्रव जैविक खत समूह'),
}


NUTRIENT_TRANSLATIONS = {
    'Natural phosphate; grade varies': ('प्राकृतिक फॉस्फेट; ग्रेड अलग हो सकता है', 'नैसर्गिक स्फुरद; दर्जा बदलू शकतो'),
    'Magnesium and sulphur; grade varies': ('मैग्नीशियम और सल्फर; ग्रेड अलग हो सकता है', 'मॅग्नेशियम व गंधक; दर्जा बदलू शकतो'),
    'Calcium and magnesium carbonates': ('कैल्शियम और मैग्नीशियम कार्बोनेट', 'कॅल्शियम व मॅग्नेशियम कार्बोनेट'),
    'Calcium carbonate equivalent varies': ('कैल्शियम कार्बोनेट समतुल्य मात्रा अलग हो सकती है', 'कॅल्शियम कार्बोनेट समतुल्य मात्रा बदलू शकते'),
    'Calcium and sulphur': ('कैल्शियम और सल्फर', 'कॅल्शियम व गंधक'),
    'Elemental sulphur; grade varies': ('तत्वीय सल्फर; ग्रेड अलग हो सकता है', 'मूलद्रव्य गंधक; दर्जा बदलू शकतो'),
    'Iron and sulphur; grade varies': ('लोहा और सल्फर; ग्रेड अलग हो सकता है', 'लोह व गंधक; दर्जा बदलू शकतो'),
    'Copper and sulphur; grade varies': ('तांबा और सल्फर; ग्रेड अलग हो सकता है', 'तांबे व गंधक; दर्जा बदलू शकतो'),
    'Manganese and sulphur; grade varies': ('मैंगनीज और सल्फर; ग्रेड अलग हो सकता है', 'मॅंगनीज व गंधक; दर्जा बदलू शकतो'),
    'Molybdenum; grade varies': ('मोलिब्डेनम; ग्रेड अलग हो सकता है', 'मॉलिब्डेनम; दर्जा बदलू शकतो'),
    'Copper in chelated form; grade varies': ('कीलेटेड रूप में तांबा; ग्रेड अलग हो सकता है', 'चिलेटेड स्वरूपातील तांबे; दर्जा बदलू शकतो'),
    'Variable organic matter and low N-P-K': ('परिवर्तनशील जैविक पदार्थ और कम N-P-K', 'बदलते सेंद्रिय पदार्थ व कमी N-P-K'),
    'Organic matter; variable N-P-K and micronutrients': ('जैविक पदार्थ; परिवर्तनशील N-P-K और सूक्ष्म पोषक तत्व', 'सेंद्रिय पदार्थ; बदलते N-P-K व सूक्ष्म अन्नद्रव्ये'),
    'Organic matter with declared enrichment': ('घोषित संवर्धन वाला जैविक पदार्थ', 'घोषित संवर्धन असलेले सेंद्रिय पदार्थ'),
    'Stabilized organic matter; nutrients vary': ('स्थिर जैविक पदार्थ; पोषक तत्व अलग हो सकते हैं', 'स्थिर सेंद्रिय पदार्थ; अन्नद्रव्ये बदलू शकतात'),
    'Organic matter with enriched phosphorus': ('फॉस्फोरस-समृद्ध जैविक पदार्थ', 'स्फुरद-समृद्ध सेंद्रिय पदार्थ'),
    'Organic matter; variable N-P-K, Ca and S': ('जैविक पदार्थ; परिवर्तनशील N-P-K, Ca और S', 'सेंद्रिय पदार्थ; बदलते N-P-K, Ca व S'),
    'Organic matter; low nutrient concentration': ('जैविक पदार्थ; पोषक तत्वों की कम सांद्रता', 'सेंद्रिय पदार्थ; अन्नद्रव्यांची कमी सांद्रता'),
    'Organic N-P-K; analysis varies': ('जैविक N-P-K; विश्लेषण अलग हो सकता है', 'सेंद्रिय N-P-K; विश्लेषण बदलू शकते'),
    'Organic N with smaller P and K amounts': ('जैविक N तथा कम मात्रा में P और K', 'सेंद्रिय N आणि कमी प्रमाणात P व K'),
    'Organic nitrogen; analysis varies': ('जैविक नाइट्रोजन; विश्लेषण अलग हो सकता है', 'सेंद्रिय नत्र; विश्लेषण बदलू शकते'),
    'Organic nitrogen and sulphur; analysis varies': ('जैविक नाइट्रोजन और सल्फर; विश्लेषण अलग हो सकता है', 'सेंद्रिय नत्र व गंधक; विश्लेषण बदलू शकते'),
    'Slow-release phosphorus and calcium': ('धीरे उपलब्ध होने वाला फॉस्फोरस और कैल्शियम', 'हळूहळू उपलब्ध होणारे स्फुरद व कॅल्शियम'),
    'Organic nitrogen and phosphorus; analysis varies': ('जैविक नाइट्रोजन और फॉस्फोरस; विश्लेषण अलग हो सकता है', 'सेंद्रिय नत्र व स्फुरद; विश्लेषण बदलू शकते'),
    'Concentrated organic nitrogen; analysis varies': ('सांद्र जैविक नाइट्रोजन; विश्लेषण अलग हो सकता है', 'सांद्र सेंद्रिय नत्र; विश्लेषण बदलू शकते'),
    'Slow-release organic nitrogen': ('धीरे उपलब्ध होने वाला जैविक नाइट्रोजन', 'हळूहळू उपलब्ध होणारे सेंद्रिय नत्र'),
    'Seaweed compounds and trace minerals; low N-P-K': ('समुद्री शैवाल यौगिक और सूक्ष्म खनिज; कम N-P-K', 'समुद्री शेवाळ संयुगे व सूक्ष्म खनिजे; कमी N-P-K'),
    'Humic substances; not complete N-P-K': ('ह्यूमिक पदार्थ; संपूर्ण N-P-K नहीं', 'ह्युमिक पदार्थ; संपूर्ण N-P-K नाही'),
    'Fulvic substances; not complete N-P-K': ('फुल्विक पदार्थ; संपूर्ण N-P-K नहीं', 'फुल्विक पदार्थ; संपूर्ण N-P-K नाही'),
    'Crop-specific nitrogen-fixing bacteria': ('फसल-विशिष्ट नाइट्रोजन स्थिरीकरण जीवाणु', 'पीक-विशिष्ट नत्र स्थिरीकरण जिवाणू'),
    'Free-living nitrogen-fixing bacteria': ('स्वतंत्र नाइट्रोजन स्थिरीकरण जीवाणु', 'स्वतंत्र नत्र स्थिरीकरण जिवाणू'),
    'Associative nitrogen-fixing bacteria': ('सहजीवी नाइट्रोजन स्थिरीकरण जीवाणु', 'सहचारी नत्र स्थिरीकरण जिवाणू'),
    'Phosphate-solubilizing microorganisms': ('फॉस्फेट घुलनशील सूक्ष्मजीव', 'स्फुरद विरघळवणारे सूक्ष्मजीव'),
    'Potassium-mobilizing microorganisms': ('पोटैशियम उपलब्ध कराने वाले सूक्ष्मजीव', 'पालाश उपलब्ध करणारे सूक्ष्मजीव'),
    'Zinc-solubilizing microorganisms': ('जिंक घुलनशील सूक्ष्मजीव', 'झिंक विरघळवणारे सूक्ष्मजीव'),
    'Nitrogen-fixing Acetobacter diazotrophicus': ('नाइट्रोजन स्थिरीकरण एसीटोबैक्टर डायजोट्रोफिकस', 'नत्र स्थिरीकरण अ‍ॅसिटोबॅक्टर डायझोट्रोफिकस'),
    'Nitrogen-fixing cyanobacteria': ('नाइट्रोजन स्थिरीकरण सायनोबैक्टीरिया', 'नत्र स्थिरीकरण सायनोबॅक्टेरिया'),
    'Azolla-Anabaena biological nitrogen source': ('एजोला-एनाबीना जैविक नाइट्रोजन स्रोत', 'अ‍ॅझोला-अ‍ॅनाबेना जैविक नत्र स्रोत'),
    'Beneficial mycorrhizal fungal propagules': ('लाभकारी माइकोराइजल कवक प्रवर्धक', 'उपयुक्त मायकोरायझल बुरशी प्रवर्धके'),
    'Multiple compatible beneficial microorganisms': ('अनेक संगत लाभकारी सूक्ष्मजीव', 'अनेक सुसंगत उपयुक्त सूक्ष्मजीव'),
    'Organic matter enriched with Trichoderma': ('ट्राइकोडर्मा-समृद्ध जैविक पदार्थ', 'ट्रायकोडर्मा-समृद्ध सेंद्रिय पदार्थ'),
    'Sulphur-oxidizing microorganisms': ('सल्फर ऑक्सीकरण सूक्ष्मजीव', 'गंधक ऑक्सिडीकरण सूक्ष्मजीव'),
    'Silicate-solubilizing microorganisms': ('सिलिकेट घुलनशील सूक्ष्मजीव', 'सिलिकेट विरघळवणारे सूक्ष्मजीव'),
    'Nitrogen-fixing and nutrient-mobilizing microbes': ('नाइट्रोजन स्थिरीकरण और पोषक तत्व उपलब्ध कराने वाले सूक्ष्मजीव', 'नत्र स्थिरीकरण व अन्नद्रव्ये उपलब्ध करणारे सूक्ष्मजीव'),
}


DOSAGE_TRANSLATIONS = {
    '50 kg/acre': ('50 किग्रा/एकड़', '50 किलो/एकर'),
    '25 kg/acre': ('25 किग्रा/एकड़', '25 किलो/एकर'),
    '20 kg/acre': ('20 किग्रा/एकड़', '20 किलो/एकर'),
    'Use soil test, crop need, product label and local agricultural guidance.': (
        'मिट्टी जाँच, फसल की आवश्यकता, उत्पाद लेबल और स्थानीय कृषि मार्गदर्शन के अनुसार उपयोग करें।',
        'माती परीक्षण, पिकाची गरज, उत्पादनाचे लेबल आणि स्थानिक कृषी मार्गदर्शनानुसार वापरा.',
    ),
    'Use only after testing; follow label and local advice.': (
        'केवल जाँच के बाद उपयोग करें; उत्पाद लेबल और स्थानीय सलाह मानें।',
        'फक्त तपासणीनंतर वापरा; उत्पादनाचे लेबल आणि स्थानिक सल्ला पाळा.',
    ),
    'Base use on nutrient analysis, crop need and local organic-input guidance.': (
        'पोषक विश्लेषण, फसल की आवश्यकता और स्थानीय जैविक इनपुट मार्गदर्शन के आधार पर उपयोग करें।',
        'अन्नद्रव्य विश्लेषण, पिकाची गरज आणि स्थानिक सेंद्रिय निविष्ठा मार्गदर्शनानुसार वापरा.',
    ),
    'Use the registered crop label; protect inoculant from heat and incompatible chemicals.': (
        'पंजीकृत फसल लेबल के अनुसार उपयोग करें; संवर्धक को गर्मी और असंगत रसायनों से बचाएँ।',
        'नोंदणीकृत पीक लेबलनुसार वापरा; संवर्धकाचे उष्णता व विसंगत रसायनांपासून संरक्षण करा.',
    ),
}


def _pick(mapping, key, language):
    value = mapping[key]
    return value[0] if language == 'hi' else value[1]


def translate_name(name, language):
    if name.startswith('NPK '):
        return name
    return _pick(NAME_TRANSLATIONS, name, language)


def translate_nutrients(text, language):
    if text in NUTRIENT_TRANSLATIONS:
        return _pick(NUTRIENT_TRANSLATIONS, text, language)

    replacements = (
        ('About ', 'लगभग ' if language == 'hi' else 'सुमारे '),
        ('about ', 'लगभग ' if language == 'hi' else 'सुमारे '),
        ('Typically ', 'सामान्यतः '),
        ('Nitrogen', 'नाइट्रोजन' if language == 'hi' else 'नत्र'),
        ('Phosphorus', 'फॉस्फोरस' if language == 'hi' else 'स्फुरद'),
        ('Potassium', 'पोटैशियम' if language == 'hi' else 'पालाश'),
        ('with calcium', 'कैल्शियम सहित' if language == 'hi' else 'कॅल्शियमसह'),
        ('contains chloride', 'क्लोराइड युक्त' if language == 'hi' else 'क्लोराइडयुक्त'),
        ('calcium and sulphur', 'कैल्शियम और सल्फर' if language == 'hi' else 'कॅल्शियम व गंधक'),
        ('sulphur', 'सल्फर' if language == 'hi' else 'गंधक'),
        ('grade varies', 'ग्रेड अलग हो सकता है' if language == 'hi' else 'दर्जा बदलू शकतो'),
    )
    translated = text
    for source, target in replacements:
        translated = translated.replace(source, target)
    return translated


def translate_description(record_id, name, nutrients, language):
    translated_name = translate_name(name, language)
    translated_nutrients = translate_nutrients(nutrients, language)

    if record_id == 2:
        return 'पत्तियों की वृद्धि बढ़ाता है।' if language == 'hi' else 'पानांची वाढ सुधारते.'
    if record_id == 3:
        return 'जड़ों के विकास के लिए उपयोगी।' if language == 'hi' else 'मुळांच्या विकासासाठी उपयुक्त.'
    if record_id == 4:
        return 'रोग प्रतिरोधक क्षमता सुधारता है।' if language == 'hi' else 'रोगप्रतिकारक क्षमता सुधारते.'
    if 5 <= record_id <= 34:
        if language == 'hi':
            return f'{translated_name} से {translated_nutrients} मिलता है; चयन जाँची गई फसल और मिट्टी की आवश्यकता के अनुसार होना चाहिए।'
        return f'{translated_name} मधून {translated_nutrients} मिळते; निवड तपासलेल्या पीक व मातीच्या गरजेनुसार असावी.'
    if 35 <= record_id <= 64:
        ratio = re.search(r'NPK\s+([0-9-]+)', name).group(1)
        if language == 'hi':
            return f'यह {ratio} अनुपात वाला NPK ग्रेड है; इसे तभी चुनें जब यह फसल की पोषक योजना से मेल खाता हो।'
        return f'हा {ratio} गुणोत्तराचा NPK दर्जा आहे; तो पिकाच्या अन्नद्रव्य योजनेशी जुळत असेल तरच निवडा.'
    if 65 <= record_id <= 86:
        if language == 'hi':
            return f'{translated_name} एक जैविक इनपुट है; इसका पोषक योगदान गुणवत्ता और प्रयोगशाला विश्लेषण पर निर्भर करता है।'
        return f'{translated_name} ही सेंद्रिय निविष्ठा आहे; तिचे अन्नद्रव्य योगदान गुणवत्ता व प्रयोगशाळा विश्लेषणावर अवलंबून असते.'
    if language == 'hi':
        return f'{translated_name} संगत फसलों के लिए जीवित सूक्ष्मजीवी इनपुट है और संतुलित पोषक योजना का विकल्प नहीं है।'
    return f'{translated_name} ही सुसंगत पिकांसाठी जिवंत सूक्ष्मजीव निविष्ठा आहे आणि संतुलित अन्नद्रव्य योजनेचा पर्याय नाही.'


def seed_fertilizer_translations(cursor):
    cursor.execute(
        "SELECT COUNT(*) FROM content_translations WHERE entity_type='fertilizer'"
    )
    existing_count = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT fertilizer_id, name, type, nutrients, dosage
        FROM fertilizers
        ORDER BY fertilizer_id
        """
    )
    records = cursor.fetchall()
    values = []
    for record_id, name, fertilizer_type, nutrients, dosage in records:
        for language in LANGUAGES:
            translated_fields = {
                'name': translate_name(name, language),
                'type': _pick(TYPE_TRANSLATIONS, fertilizer_type, language),
                'nutrients': translate_nutrients(nutrients, language),
                'dosage': _pick(DOSAGE_TRANSLATIONS, dosage, language),
                'description': translate_description(record_id, name, nutrients, language),
            }
            values.extend(
                (
                    'fertilizer', record_id, field_name, language,
                    translated_text, True,
                )
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
    cursor.execute(
        "SELECT COUNT(*) FROM content_translations WHERE entity_type='fertilizer'"
    )
    final_count = cursor.fetchone()[0]
    return len(records), len(values), final_count - existing_count
