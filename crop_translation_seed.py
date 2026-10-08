"""Reviewed Hindi and Marathi translations for the existing crop catalog."""

import re

from psycopg2.extras import execute_values


LANGUAGES = ('hi', 'mr')


NAME_TRANSLATIONS = {
    'Avocado': ('एवोकाडो', 'अ‍ॅव्होकॅडो'), 'Wheat': ('गेहूँ', 'गहू'),
    'Rice': ('धान', 'भात'), 'Cotton': ('कपास', 'कापूस'),
    'Maize': ('मक्का', 'मका'), 'Barley': ('जौ', 'जव'),
    'Sorghum': ('ज्वार', 'ज्वारी'), 'Pearl Millet': ('बाजरा', 'बाजरी'),
    'Finger Millet': ('रागी', 'नाचणी'), 'Chickpea': ('चना', 'हरभरा'),
    'Pigeon Pea': ('अरहर', 'तूर'), 'Green Gram': ('मूंग', 'मूग'),
    'Black Gram': ('उड़द', 'उडीद'), 'Lentil': ('मसूर', 'मसूर'),
    'Field Pea': ('मटर', 'वाटाणा'), 'Cowpea': ('लोबिया', 'चवळी'),
    'Groundnut': ('मूंगफली', 'भुईमूग'), 'Mustard': ('सरसों', 'मोहरी'),
    'Soybean': ('सोयाबीन', 'सोयाबीन'), 'Sunflower': ('सूरजमुखी', 'सूर्यफूल'),
    'Sesame': ('तिल', 'तीळ'), 'Safflower': ('कुसुम', 'करडई'),
    'Linseed': ('अलसी', 'जवस'), 'Castor': ('अरंडी', 'एरंडी'),
    'Sugarcane': ('गन्ना', 'ऊस'), 'Jute': ('जूट', 'ताग'),
    'Tobacco': ('तंबाकू', 'तंबाखू'), 'Tea': ('चाय', 'चहा'),
    'Coffee': ('कॉफी', 'कॉफी'), 'Rubber': ('रबर', 'रबर'),
    'Coconut': ('नारियल', 'नारळ'), 'Arecanut': ('सुपारी', 'सुपारी'),
    'Potato': ('आलू', 'बटाटा'), 'Tomato': ('टमाटर', 'टोमॅटो'),
    'Onion': ('प्याज', 'कांदा'), 'Brinjal': ('बैंगन', 'वांगी'),
    'Okra': ('भिंडी', 'भेंडी'), 'Cabbage': ('पत्तागोभी', 'कोबी'),
    'Cauliflower': ('फूलगोभी', 'फुलकोबी'), 'Carrot': ('गाजर', 'गाजर'),
    'Cucumber': ('खीरा', 'काकडी'), 'Chilli': ('मिर्च', 'मिरची'),
    'Banana': ('केला', 'केळी'), 'Mango': ('आम', 'आंबा'),
    'Guava': ('अमरूद', 'पेरू'), 'Papaya': ('पपीता', 'पपई'),
    'Pomegranate': ('अनार', 'डाळिंब'), 'Orange': ('संतरा', 'संत्रे'),
    'Grapes': ('अंगूर', 'द्राक्षे'), 'Turmeric': ('हल्दी', 'हळद'),
}


CATEGORY_TRANSLATIONS = {
    'Fruit': ('फल', 'फळपीक'), 'Cereal': ('अनाज', 'तृणधान्य'),
    'Cash Crop': ('नकदी फसल', 'नगदी पीक'), 'Pulse': ('दलहन', 'कडधान्य'),
    'Oilseed': ('तिलहन', 'तेलबिया'), 'Fibre Crop': ('रेशा फसल', 'तंतू पीक'),
    'Commercial Crop': ('व्यावसायिक फसल', 'व्यावसायिक पीक'),
    'Plantation Crop': ('बागान फसल', 'लागवड पीक'),
    'Vegetable': ('सब्जी', 'भाजीपाला'),
    'Spice and Vegetable': ('मसाला और सब्जी', 'मसाला व भाजीपाला'),
    'Spice': ('मसाला फसल', 'मसाला पीक'),
}


SEASON_TRANSLATIONS = {
    'All year (mainly summer)': ('पूरे वर्ष (मुख्यतः गर्मी)', 'वर्षभर (मुख्यतः उन्हाळा)'),
    'Rabi': ('रबी', 'रब्बी'), 'Kharif': ('खरीफ', 'खरीप'),
    'Kharif and suitable-region rabi': ('खरीफ तथा उपयुक्त क्षेत्रों में रबी', 'खरीप आणि योग्य प्रदेशात रब्बी'),
    'Kharif or peninsular rabi': ('खरीफ या प्रायद्वीपीय रबी', 'खरीप किंवा द्वीपकल्पीय रब्बी'),
    'Kharif, summer or spring': ('खरीफ, गर्मी या वसंत', 'खरीप, उन्हाळा किंवा वसंत'),
    'Kharif or irrigated summer': ('खरीफ या सिंचित गर्मी', 'खरीप किंवा बागायती उन्हाळा'),
    'Kharif or summer': ('खरीफ या गर्मी', 'खरीप किंवा उन्हाळा'),
    'Kharif, rabi or spring': ('खरीफ, रबी या वसंत', 'खरीप, रब्बी किंवा वसंत'),
    'Spring or autumn planting': ('वसंत या शरद ऋतु में रोपण', 'वसंत किंवा शरद ऋतूतील लागवड'),
    'Varies by tobacco type and region': ('तंबाकू के प्रकार और क्षेत्र के अनुसार', 'तंबाखूचा प्रकार व प्रदेशानुसार'),
    'Perennial; rainy-season planting': ('बहुवर्षीय; वर्षा ऋतु में रोपण', 'बहुवर्षीय; पावसाळी लागवड'),
    'Perennial; monsoon planting': ('बहुवर्षीय; मानसून में रोपण', 'बहुवर्षीय; पावसाळी लागवड'),
    'Rabi plains or summer hills': ('मैदानी रबी या पहाड़ी गर्मी', 'मैदानी रब्बी किंवा डोंगराळ उन्हाळा'),
    'Multiple seasons by region': ('क्षेत्र के अनुसार कई मौसम', 'प्रदेशानुसार अनेक हंगाम'),
    'Kharif, late kharif or rabi': ('खरीफ, पछेती खरीफ या रबी', 'खरीप, उशिरा खरीप किंवा रब्बी'),
    'Year-round where frost-free': ('पाला-मुक्त क्षेत्रों में वर्षभर', 'दवमुक्त प्रदेशात वर्षभर'),
    'Kharif and summer': ('खरीफ और गर्मी', 'खरीप आणि उन्हाळा'),
    'Rabi plains or cool-season hills': ('मैदानी रबी या पहाड़ी ठंडा मौसम', 'मैदानी रब्बी किंवा डोंगराळ थंड हंगाम'),
    'Cool season; maturity group varies': ('ठंडा मौसम; परिपक्वता समूह अलग होता है', 'थंड हंगाम; पक्वता गट बदलतो'),
    'Rabi plains or cool season': ('मैदानी रबी या ठंडा मौसम', 'मैदानी रब्बी किंवा थंड हंगाम'),
    'Spring-summer and kharif': ('वसंत-गर्मी और खरीफ', 'वसंत-उन्हाळा आणि खरीप'),
    'Kharif, rabi or summer': ('खरीफ, रबी या गर्मी', 'खरीप, रब्बी किंवा उन्हाळा'),
    'Year-round; monsoon planting common': ('वर्षभर; मानसून रोपण सामान्य', 'वर्षभर; पावसाळी लागवड सामान्य'),
    'Perennial; monsoon or spring planting': ('बहुवर्षीय; मानसून या वसंत रोपण', 'बहुवर्षीय; पावसाळी किंवा वसंत लागवड'),
    'Year-round in frost-free areas': ('पाला-मुक्त क्षेत्रों में वर्षभर', 'दवमुक्त प्रदेशात वर्षभर'),
    'Perennial; regional bahar selection': ('बहुवर्षीय; क्षेत्रानुसार बहार चयन', 'बहुवर्षीय; प्रदेशानुसार बहार निवड'),
    'Perennial; pruning season varies': ('बहुवर्षीय; छँटाई का मौसम अलग होता है', 'बहुवर्षीय; छाटणीचा हंगाम बदलतो'),
    'Kharif or monsoon planting': ('खरीफ या मानसून रोपण', 'खरीप किंवा पावसाळी लागवड'),
}


SOIL_TRANSLATIONS = {
    'Well-drained loamy soil': ('अच्छी जल निकासी वाली दोमट मिट्टी', 'उत्तम निचऱ्याची पोयट्याची माती'),
    'Loamy Soil': ('दोमट मिट्टी', 'पोयट्याची माती'), 'Clay Soil': ('चिकनी मिट्टी', 'चिकण माती'),
    'Black Soil': ('काली मिट्टी', 'काळी माती'),
    'Well-drained loam to clay loam': ('अच्छी जल निकासी वाली दोमट से चिकनी दोमट मिट्टी', 'उत्तम निचऱ्याची पोयट्याची ते चिकण पोयट्याची माती'),
    'Well-drained loam or sandy loam': ('अच्छी जल निकासी वाली दोमट या बलुई दोमट मिट्टी', 'उत्तम निचऱ्याची पोयट्याची किंवा वालुकामय पोयट्याची माती'),
    'Loam to medium black soil': ('दोमट से मध्यम काली मिट्टी', 'पोयट्याची ते मध्यम काळी माती'),
    'Light sandy loam to loam': ('हल्की बलुई दोमट से दोमट मिट्टी', 'हलकी वालुकामय पोयट्याची ते पोयट्याची माती'),
    'Red loam, sandy loam or lateritic soil': ('लाल दोमट, बलुई दोमट या लैटेराइट मिट्टी', 'लाल पोयट्याची, वालुकामय पोयट्याची किंवा जांभी माती'),
    'Loam rich in organic matter': ('जैविक पदार्थ से भरपूर दोमट मिट्टी', 'सेंद्रिय पदार्थयुक्त पोयट्याची माती'),
    'Sandy loam to loam': ('बलुई दोमट से दोमट मिट्टी', 'वालुकामय पोयट्याची ते पोयट्याची माती'),
    'Well-drained sandy loam': ('अच्छी जल निकासी वाली बलुई दोमट मिट्टी', 'उत्तम निचऱ्याची वालुकामय पोयट्याची माती'),
    'Well-drained loam': ('अच्छी जल निकासी वाली दोमट मिट्टी', 'उत्तम निचऱ्याची पोयट्याची माती'),
    'Deep black soil or loam': ('गहरी काली या दोमट मिट्टी', 'खोल काळी किंवा पोयट्याची माती'),
    'Deep loam to sandy loam': ('गहरी दोमट से बलुई दोमट मिट्टी', 'खोल पोयट्याची ते वालुकामय पोयट्याची माती'),
    'Deep fertile loam to clay loam': ('गहरी उपजाऊ दोमट से चिकनी दोमट मिट्टी', 'खोल सुपीक पोयट्याची ते चिकण पोयट्याची माती'),
    'Fertile alluvial loam': ('उपजाऊ जलोढ़ दोमट मिट्टी', 'सुपीक गाळाची पोयट्याची माती'),
    'Well-drained sandy loam to loam': ('अच्छी जल निकासी वाली बलुई दोमट से दोमट मिट्टी', 'उत्तम निचऱ्याची वालुकामय पोयट्याची ते पोयट्याची माती'),
    'Acidic loam rich in organic matter': ('जैविक पदार्थ से भरपूर अम्लीय दोमट मिट्टी', 'सेंद्रिय पदार्थयुक्त आम्लधर्मी पोयट्याची माती'),
    'Deep loam rich in organic matter': ('जैविक पदार्थ से भरपूर गहरी दोमट मिट्टी', 'सेंद्रिय पदार्थयुक्त खोल पोयट्याची माती'),
    'Deep well-drained lateritic loam': ('गहरी, अच्छी जल निकासी वाली लैटेराइट दोमट मिट्टी', 'खोल, उत्तम निचऱ्याची जांभी पोयट्याची माती'),
    'Sandy loam, laterite or alluvial soil': ('बलुई दोमट, लैटेराइट या जलोढ़ मिट्टी', 'वालुकामय पोयट्याची, जांभी किंवा गाळाची माती'),
    'Loose well-drained sandy loam': ('भुरभुरी, अच्छी जल निकासी वाली बलुई दोमट मिट्टी', 'भुसभुशीत, उत्तम निचऱ्याची वालुकामय पोयट्याची माती'),
    'Well-drained friable loam': ('अच्छी जल निकासी वाली भुरभुरी दोमट मिट्टी', 'उत्तम निचऱ्याची भुसभुशीत पोयट्याची माती'),
    'Well-drained fertile loam': ('अच्छी जल निकासी वाली उपजाऊ दोमट मिट्टी', 'उत्तम निचऱ्याची सुपीक पोयट्याची माती'),
    'Fertile well-drained loam': ('उपजाऊ, अच्छी जल निकासी वाली दोमट मिट्टी', 'सुपीक, उत्तम निचऱ्याची पोयट्याची माती'),
    'Loose deep sandy loam': ('भुरभुरी गहरी बलुई दोमट मिट्टी', 'भुसभुशीत खोल वालुकामय पोयट्याची माती'),
    'Sandy loam rich in organic matter': ('जैविक पदार्थ से भरपूर बलुई दोमट मिट्टी', 'सेंद्रिय पदार्थयुक्त वालुकामय पोयट्याची माती'),
    'Deep fertile well-drained loam': ('गहरी उपजाऊ, अच्छी जल निकासी वाली दोमट मिट्टी', 'खोल सुपीक, उत्तम निचऱ्याची पोयट्याची माती'),
    'Deep well-drained loam': ('गहरी, अच्छी जल निकासी वाली दोमट मिट्टी', 'खोल, उत्तम निचऱ्याची पोयट्याची माती'),
    'Fertile loam rich in organic matter': ('जैविक पदार्थ से भरपूर उपजाऊ दोमट मिट्टी', 'सेंद्रिय पदार्थयुक्त सुपीक पोयट्याची माती'),
}


def _pick(mapping, key, language):
    value = mapping[key]
    return value[0] if language == 'hi' else value[1]


def translate_duration(value, language):
    special = {
        '3-4 years (bearing)': ('3-4 वर्षों में फल देना', '3-4 वर्षांनी उत्पादन'),
        'Bearing from 3-4 years': ('3-4 वर्षों में फल देना शुरू', '3-4 वर्षांनी उत्पादन सुरू'),
        'Tapping from 6-7 years': ('6-7 वर्षों में दोहन शुरू', '6-7 वर्षांनी टॅपिंग सुरू'),
        'Bearing from 4-7 years': ('4-7 वर्षों में फल देना शुरू', '4-7 वर्षांनी उत्पादन सुरू'),
        'Bearing from 5-7 years': ('5-7 वर्षों में फल देना शुरू', '5-7 वर्षांनी उत्पादन सुरू'),
        'Bearing from 3-6 years': ('3-6 वर्षों में फल देना शुरू', '3-6 वर्षांनी उत्पादन सुरू'),
        'Bearing from 2-3 years': ('2-3 वर्षों में फल देना शुरू', '2-3 वर्षांनी उत्पादन सुरू'),
        'First harvest in 9-12 months': ('पहली कटाई 9-12 महीनों में', 'पहिली काढणी 9-12 महिन्यांत'),
        'Bearing from 3-5 years': ('3-5 वर्षों में फल देना शुरू', '3-5 वर्षांनी उत्पादन सुरू'),
        'Harvest from 2-3 years': ('2-3 वर्षों में कटाई शुरू', '2-3 वर्षांनी काढणी सुरू'),
    }
    if value in special:
        return _pick(special, value, language)
    translated = value
    units = {
        ' days': ' दिन' if language == 'hi' else ' दिवस',
        ' months': ' महीने' if language == 'hi' else ' महिने',
        ' years': ' वर्ष' if language == 'hi' else ' वर्षे',
    }
    for source, target in units.items():
        translated = translated.replace(source, target)
    return translated


def translate_yield(value, language):
    replacements = (
        ('quintals green fruit/acre', 'क्विंटल हरे फल/एकड़' if language == 'hi' else 'क्विंटल हिरवी फळे/एकर'),
        ('quintals/acre bearing orchard', 'क्विंटल/एकड़ फलदार बाग' if language == 'hi' else 'क्विंटल/एकर उत्पादनक्षम बाग'),
        ('kg made tea/acre/year', 'किग्रा तैयार चाय/एकड़/वर्ष' if language == 'hi' else 'किलो तयार चहा/एकर/वर्ष'),
        ('kg clean beans/acre/year', 'किग्रा साफ बीज/एकड़/वर्ष' if language == 'hi' else 'किलो स्वच्छ बिया/एकर/वर्ष'),
        ('kg dry rubber/acre/year', 'किग्रा सूखा रबर/एकड़/वर्ष' if language == 'hi' else 'किलो कोरडे रबर/एकर/वर्ष'),
        ('kg dry kernels/acre/year', 'किग्रा सूखी गिरी/एकड़/वर्ष' if language == 'hi' else 'किलो सुक्या गाभ्या/एकर/वर्ष'),
        ('nuts/acre/year', 'फल/एकड़/वर्ष' if language == 'hi' else 'नारळ/एकर/वर्ष'),
        ('quintals cured leaf/acre', 'क्विंटल उपचारित पत्ती/एकड़' if language == 'hi' else 'क्विंटल प्रक्रिया केलेली पाने/एकर'),
        ('quintals fibre/acre', 'क्विंटल रेशा/एकड़' if language == 'hi' else 'क्विंटल तंतू/एकर'),
        ('quintals cane/acre', 'क्विंटल गन्ना/एकड़' if language == 'hi' else 'क्विंटल ऊस/एकर'),
        ('quintals grain/acre', 'क्विंटल अनाज/एकड़' if language == 'hi' else 'क्विंटल धान्य/एकर'),
        ('quintals pods/acre', 'क्विंटल फलियाँ/एकड़' if language == 'hi' else 'क्विंटल शेंगा/एकर'),
        ('quintals fresh/acre', 'क्विंटल ताजा/एकड़' if language == 'hi' else 'क्विंटल ताजे/एकर'),
        ('quintals/acre', 'क्विंटल/एकड़' if language == 'hi' else 'क्विंटल/एकर'),
        ('quintals', 'क्विंटल'), ('tons', 'टन'),
    )
    translated = value
    for source, target in replacements:
        translated = translated.replace(source, target)
    return translated


def translate_market_price(value, language):
    if value == 'Varies; check current local mandi price':
        return 'बदलता रहता है; वर्तमान स्थानीय मंडी भाव देखें' if language == 'hi' else 'बदलते; सध्याचा स्थानिक बाजारभाव तपासा'
    translated = value.replace(' per kg', ' प्रति किग्रा' if language == 'hi' else ' प्रति किलो')
    translated = translated.replace('/quintal', '/क्विंटल')
    return translated


def translate_profit(value, language):
    if value == 'Varies with yield, costs and sale price':
        return 'उपज, लागत और बिक्री मूल्य के अनुसार बदलता है' if language == 'hi' else 'उत्पादन, खर्च आणि विक्रीभावानुसार बदलतो'
    if 'lakh per acre' in value:
        return value.replace('lakh per acre', 'लाख प्रति एकड़' if language == 'hi' else 'लाख प्रति एकर')
    return value


def seed_crop_translations(cursor):
    cursor.execute("SELECT COUNT(*) FROM content_translations WHERE entity_type='crop'")
    existing_count = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT crop_id, name, category, season, duration, soil, ph_range,
               temperature, rainfall, yield_per_acre, market_price,
               estimated_profit
        FROM crops ORDER BY crop_id
        """
    )
    records = cursor.fetchall()
    values = []
    for record in records:
        (crop_id, name, category, season, duration, soil, ph_range,
         temperature, rainfall, crop_yield, market_price, profit) = record
        for language in LANGUAGES:
            translated_fields = {
                'name': _pick(NAME_TRANSLATIONS, name, language),
                'category': _pick(CATEGORY_TRANSLATIONS, category, language),
                'season': _pick(SEASON_TRANSLATIONS, season, language),
                'duration': translate_duration(duration, language),
                'soil': _pick(SOIL_TRANSLATIONS, soil, language),
                'ph_range': ph_range,
                'temperature': temperature,
                'rainfall': rainfall,
                'yield_per_acre': translate_yield(crop_yield, language),
                'market_price': translate_market_price(market_price, language),
                'estimated_profit': translate_profit(profit, language),
            }
            values.extend(
                ('crop', crop_id, field_name, language, translated_text, True)
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
    cursor.execute("SELECT COUNT(*) FROM content_translations WHERE entity_type='crop'")
    final_count = cursor.fetchone()[0]
    return len(records), len(values), final_count - existing_count
