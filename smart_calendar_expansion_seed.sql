-- Additional verified Smart Calendar profiles.
-- Guidance is non-prescriptive: local soil tests, labels and extension advice take priority.

INSERT INTO crop_calendar_profiles
    (crop_id, sowing_months, duration_days, harvest_window_days, region,
     source_name, source_url, last_verified)
SELECT c.crop_id, v.sowing_months, v.duration_days, v.harvest_window_days,
       v.region, v.source_name, v.source_url, DATE '2026-10-08'
FROM crops c
JOIN (VALUES
    ('maize', ARRAY[6,7]::SMALLINT[], 105, 14, 'India - kharif maize general reference',
     'TNAU - Maize water management',
     'https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_maize.html'),
    ('chickpea', ARRAY[10,11]::SMALLINT[], 110, 14, 'India - rabi chickpea general reference',
     'TNAU - Bengal gram crop production',
     'https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_bengalgram.html'),
    ('soybean', ARRAY[6,7]::SMALLINT[], 105, 14, 'India - kharif soybean general reference',
     'TNAU - Soybean crop production',
     'https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_soybean.html'),
    ('groundnut', ARRAY[6,7]::SMALLINT[], 110, 14, 'India - kharif groundnut general reference',
     'TNAU - Groundnut crop production',
     'https://www.agritech.tnau.ac.in/agriculture/CropProduction/Oilseeds/oilseeds_groundnut01.html'),
    ('potato', ARRAY[10,11]::SMALLINT[], 100, 14, 'India - rabi plains potato general reference',
     'TNAU - Potato crop production',
     'https://agritech.tnau.ac.in/horticulture/horti_vegetables_potato.html'),
    ('tomato', ARRAY[6]::SMALLINT[], 120, 21, 'India - monsoon tomato general reference',
     'TNAU - Tomato water management',
     'https://www.agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_irrigation.html'),
    ('onion', ARRAY[10,11]::SMALLINT[], 135, 14, 'India - rabi onion general reference',
     'TNAU - Bellary onion crop production',
     'https://agritech.tnau.ac.in/horticulture/horti_vegetables_bellaryonion.html')
) AS v(crop_name, sowing_months, duration_days, harvest_window_days,
       region, source_name, source_url)
  ON LOWER(TRIM(c.name)) = v.crop_name
ON CONFLICT (crop_id) DO UPDATE SET
    sowing_months = EXCLUDED.sowing_months,
    duration_days = EXCLUDED.duration_days,
    harvest_window_days = EXCLUDED.harvest_window_days,
    region = EXCLUDED.region,
    source_name = EXCLUDED.source_name,
    source_url = EXCLUDED.source_url,
    last_verified = EXCLUDED.last_verified,
    is_active = TRUE;

INSERT INTO farming_activities
    (profile_id, activity_type, growth_stage, start_day, end_day, title,
     guidance, priority, source_name, source_url)
SELECT p.profile_id, v.activity_type, v.growth_stage, v.start_day, v.end_day,
       v.title, v.guidance, v.priority, v.source_name, v.source_url
FROM crop_calendar_profiles p
JOIN crops c ON c.crop_id=p.crop_id
JOIN (VALUES
    ('maize','planning','Pre-sowing',-14,-1,'Prepare a drained seedbed','Review the soil test, break compacted clods and provide drainage before monsoon sowing.','high','TNAU - Maize water management','https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_maize.html'),
    ('maize','sowing','Establishment',0,5,'Sow maize in suitable moisture','Use a locally recommended hybrid or variety and inspect emergence and field drainage.','high','TNAU - Maize water management','https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_maize.html'),
    ('maize','weed','Early vegetative',15,30,'Control early weed competition','Scout rows and use locally approved mechanical or labelled weed management before competition becomes severe.','normal','TNAU - Maize water management','https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_maize.html'),
    ('maize','fertilizer','Vegetative',20,35,'Review crop nutrition','Use crop appearance and the soil-test plan to time split nutrients; avoid unnecessary nitrogen.','normal','TNAU - Maize water management','https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_maize.html'),
    ('maize','irrigation','Flowering',40,65,'Protect the critical moisture period','Maize is sensitive to both moisture stress and excess water; check moisture frequently during flowering.','high','TNAU - Maize water management','https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_maize.html'),
    ('maize','harvest','Maturity',90,110,'Check cob maturity','Confirm grain maturity and dry weather before harvest, then dry produce safely for storage.','high','TNAU - Maize water management','https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_maize.html'),

    ('chickpea','planning','Pre-sowing',-14,-1,'Prepare fine, well-drained soil','Prepare a fine seedbed, review soil-test needs and avoid fields likely to remain waterlogged.','high','TNAU - Bengal gram crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_bengalgram.html'),
    ('chickpea','sowing','Establishment',0,5,'Sow chickpea in the rabi window','Use healthy seed of a locally recommended variety and sow into suitable residual moisture.','high','TNAU - Bengal gram crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_bengalgram.html'),
    ('chickpea','monitoring','Seedling',7,25,'Inspect crop establishment','Check gaps, seedling health and patches of drooping plants; avoid standing water.','high','TNAU - Bengal gram crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_bengalgram.html'),
    ('chickpea','weed','Vegetative',20,35,'Manage early weeds','Remove competing weeds early with a locally suitable method while protecting roots.','normal','TNAU - Bengal gram crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_bengalgram.html'),
    ('chickpea','irrigation','Flowering to pod filling',35,80,'Avoid moisture stress and waterlogging','Check soil moisture at flowering and pod development; irrigate only when locally required.','high','TNAU - Bengal gram crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_bengalgram.html'),
    ('chickpea','harvest','Maturity',95,115,'Harvest dry mature plants','Wait for pods and plants to mature and dry, then harvest and store clean grain safely.','high','TNAU - Bengal gram crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_bengalgram.html'),

    ('soybean','planning','Pre-sowing',-14,-1,'Prepare drainage for soybean','Use raised-bed or broad-bed-and-furrow planting where locally suitable and review the soil test.','high','TNAU - Soybean crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_soybean.html'),
    ('soybean','sowing','Establishment',0,5,'Sow healthy soybean seed','Use a locally recommended variety, suitable spacing and seed with verified germination.','high','TNAU - Soybean crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_soybean.html'),
    ('soybean','monitoring','Seedling',7,25,'Check emergence and drainage','Inspect plant stand, stem damage and water movement after rainfall.','normal','TNAU - Soybean crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_soybean.html'),
    ('soybean','weed','Vegetative',15,35,'Manage weeds early','Control weeds before canopy closure using locally approved mechanical or labelled methods.','high','TNAU - Soybean crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_soybean.html'),
    ('soybean','monitoring','Flowering and pod formation',30,85,'Scout leaves, flowers and pods','Inspect representative plants weekly for yellowing, defoliation, stem damage and pod injury.','high','TNAU - Soybean crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_soybean.html'),
    ('soybean','harvest','Maturity',90,110,'Harvest at pod maturity','Harvest after most pods mature and before avoidable shattering; dry seed safely.','high','TNAU - Soybean crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Pulses/pulses_soybean.html'),

    ('groundnut','planning','Pre-sowing',-14,-1,'Prepare a fine, drained field','Break clods, correct hard-pan issues where present and use the current soil test for inputs.','high','TNAU - Groundnut crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Oilseeds/oilseeds_groundnut01.html'),
    ('groundnut','sowing','Establishment',0,5,'Sow healthy groundnut seed','Use a locally recommended variety and spacing in suitable soil moisture.','high','TNAU - Groundnut crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Oilseeds/oilseeds_groundnut01.html'),
    ('groundnut','weed','Vegetative',15,35,'Keep the early crop weed free','Manage weeds before pegging and avoid disturbing the crop after pegs enter the soil.','high','TNAU - Groundnut crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Oilseeds/oilseeds_groundnut01.html'),
    ('groundnut','irrigation','Flowering and pegging',25,60,'Protect flowering and pegging','Check soil moisture frequently, avoid waterlogging and prevent severe stress during pegging.','high','TNAU - Groundnut crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Oilseeds/oilseeds_groundnut01.html'),
    ('groundnut','monitoring','Pod development',55,95,'Inspect foliage and pod development','Scout representative areas for leaf spots, rust-like pustules and premature leaf fall.','high','TNAU - Groundnut crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Oilseeds/oilseeds_groundnut01.html'),
    ('groundnut','harvest','Maturity',95,115,'Check pods before lifting','Confirm internal pod maturity, lift in suitable soil conditions and dry pods safely.','high','TNAU - Groundnut crop production','https://www.agritech.tnau.ac.in/agriculture/CropProduction/Oilseeds/oilseeds_groundnut01.html'),

    ('potato','planning','Pre-planting',-14,-1,'Prepare ridges and healthy seed tubers','Use clean seed tubers, a current soil test and a loose, drained seedbed.','high','TNAU - Potato crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_potato.html'),
    ('potato','planting','Establishment',0,5,'Plant potato at suitable depth','Use locally recommended seed tubers and spacing; avoid bruising and waterlogged soil.','high','TNAU - Potato crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_potato.html'),
    ('potato','fieldwork','Vegetative',15,35,'Check emergence and earth up','Fill gaps only when appropriate, control early weeds and earth up without damaging roots.','normal','TNAU - Potato crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_potato.html'),
    ('potato','irrigation','Tuber initiation',25,70,'Maintain even soil moisture','Avoid alternating drought and excess water during tuber initiation and bulking.','high','TNAU - Potato crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_potato.html'),
    ('potato','monitoring','Tuber bulking',30,85,'Scout foliage for blight symptoms','Inspect lower and upper leaves after cool humid weather and confirm suspicious symptoms promptly.','high','TNAU - Potato crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_potato.html'),
    ('potato','harvest','Maturity',85,105,'Prepare for careful harvest','Allow skins to set, harvest in suitable soil conditions and avoid bruising tubers.','high','TNAU - Potato crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_potato.html'),

    ('tomato','planning','Nursery preparation',-14,-1,'Prepare a clean raised nursery','Use healthy seed and a well-drained nursery; plan the main-field water supply and drainage.','high','TNAU - Tomato water management','https://www.agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_irrigation.html'),
    ('tomato','sowing','Nursery',0,7,'Sow tomato nursery','Sow a locally suitable variety and maintain even moisture without saturating the nursery.','high','TNAU - Tomato water management','https://www.agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_irrigation.html'),
    ('tomato','transplanting','Establishment',25,35,'Transplant healthy seedlings','Transplant sturdy healthy seedlings, water them in and replace failed plants promptly.','high','TNAU - Tomato water management','https://www.agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_irrigation.html'),
    ('tomato','fieldwork','Vegetative to flowering',35,65,'Support plants and manage weeds','Stake where appropriate, control weeds and maintain airflow around plants.','normal','TNAU - Tomato water management','https://www.agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_irrigation.html'),
    ('tomato','irrigation','Flowering and fruit set',45,100,'Keep water supply even','Avoid drought followed by heavy irrigation because uneven moisture can damage fruit quality.','high','TNAU - Tomato water management','https://www.agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_irrigation.html'),
    ('tomato','harvest','Fruit maturity',90,130,'Harvest at the required maturity','Pick carefully at the maturity needed for the target market and remove damaged fruit.','high','TNAU - Tomato water management','https://www.agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_irrigation.html'),

    ('onion','planning','Nursery preparation',-14,-1,'Prepare raised nursery beds','Use healthy seed, fine soil and drainage; plan transplanting and main-field irrigation.','high','TNAU - Bellary onion crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_bellaryonion.html'),
    ('onion','sowing','Nursery',0,7,'Sow onion nursery','Sow thinly in lines and maintain uniform nursery moisture without waterlogging.','high','TNAU - Bellary onion crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_bellaryonion.html'),
    ('onion','transplanting','Establishment',42,56,'Transplant suitable seedlings','Move healthy seedlings into a well-prepared field and irrigate for uniform establishment.','high','TNAU - Bellary onion crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_bellaryonion.html'),
    ('onion','weed','Vegetative',55,80,'Manage weeds and inspect leaves','Control weeds carefully and check representative plants for thrips or leaf lesions.','normal','TNAU - Bellary onion crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_bellaryonion.html'),
    ('onion','irrigation','Bulb development',60,115,'Maintain uniform bulb-stage moisture','Adjust irrigation to soil and weather, avoiding both prolonged dryness and waterlogging.','high','TNAU - Bellary onion crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_bellaryonion.html'),
    ('onion','harvest','Top fall and maturity',120,140,'Stop irrigation and prepare harvest','Follow local advice on withholding irrigation, harvest near top fall and cure bulbs in shade.','high','TNAU - Bellary onion crop production','https://agritech.tnau.ac.in/horticulture/horti_vegetables_bellaryonion.html')
) AS v(crop_name, activity_type, growth_stage, start_day, end_day, title,
       guidance, priority, source_name, source_url)
  ON LOWER(TRIM(c.name))=v.crop_name
WHERE p.is_active=TRUE
ON CONFLICT (profile_id, activity_type, start_day, title) DO NOTHING;

INSERT INTO crop_disease_risks
    (profile_id, disease_name, start_day, end_day, risk_level,
     trigger_conditions, symptoms, precautions, monitoring_frequency,
     source_name, source_url)
SELECT p.profile_id, v.disease_name, v.start_day, v.end_day, 'monitor',
       v.trigger_conditions, v.symptoms, v.precautions, v.monitoring_frequency,
       v.source_name, v.source_url
FROM crop_calendar_profiles p
JOIN crops c ON c.crop_id=p.crop_id
JOIN (VALUES
    ('maize','Downy mildew monitoring',10,50,
     'Warm humid weather, high relative humidity and continued drizzle can favour disease.',
     'Look for chlorotic streaks, white downy growth, stunting or abnormal upper growth.',
     ARRAY['Use healthy locally recommended seed','Keep drainage open','Remove suspicious plants only after expert confirmation','Seek local advice before treatment'],
     'Inspect seedlings weekly and after prolonged humid or drizzly weather',
     'TNAU - Maize downy mildew','https://agritech.tnau.ac.in/crop_protection/maize_disease_new/maize_1.html'),
    ('chickpea','Fusarium wilt monitoring',15,105,
     'The disease can appear from seedling to adult stages and often develops in patches.',
     'Look for collapsed seedlings, drooping leaves, whole-plant wilt or dark internal stem tissue.',
     ARRAY['Use healthy seed and locally recommended resistant varieties','Maintain field sanitation and crop rotation','Avoid waterlogging','Confirm wilt before treatment'],
     'Inspect representative rows weekly and investigate wilt patches promptly',
     'TNAU - Chickpea Fusarium wilt','https://agritech.tnau.ac.in/crop_protection/chickpea_disease/chickpea_6.html'),
    ('soybean','Yellow mosaic monitoring',10,65,
     'Whitefly activity and nearby infected host plants can increase virus risk.',
     'Look for bright yellow mottling, yellow bands along major veins or rusty necrotic spots.',
     ARRAY['Use healthy seed of a locally recommended variety','Inspect field borders and young plants','Remove confirmed infected plants early where locally advised','Confirm symptoms with an expert'],
     'Inspect plants weekly during early vegetative growth',
     'TNAU - Soybean yellow mosaic','https://agritech.tnau.ac.in/crop_protection/soyabean_disease/soybean_d10.html'),
    ('groundnut','Leaf spot and rust monitoring',30,100,
     'Humid weather and persistent leaf wetness can favour foliar leaf spots and rust.',
     'Look for circular dark spots, yellow halos, lower-leaf pustules or premature leaf fall.',
     ARRAY['Use locally recommended tolerant varieties','Rotate with non-host crops','Remove volunteer plants and manage residues','Confirm symptoms before treatment'],
     'Inspect lower and middle canopy leaves weekly from flowering onward',
     'TNAU - Groundnut disease guidance','https://agritech.tnau.ac.in/govt_schemes_services/aas/groundnut_ex1.html'),
    ('potato','Late blight monitoring',15,90,
     'Cool humid weather, high relative humidity and rain alternating with moist periods increase risk.',
     'Look for water-soaked leaf spots turning brown or black, white growth below leaves, or brown tuber lesions.',
     ARRAY['Use healthy seed tubers','Improve drainage and airflow','Avoid moving through wet foliage','Confirm symptoms promptly with a local expert'],
     'Inspect foliage at least weekly and more often during cool humid weather',
     'TNAU - Potato late blight','https://agritech.tnau.ac.in/crop_protection/potato_phdiseases_4.html'),
    ('tomato','Early blight monitoring',35,120,
     'Warm humid rainy weather and prolonged leaf wetness can favour early blight.',
     'Look for brown spots with concentric rings and yellow margins on leaves, stems or fruit.',
     ARRAY['Use healthy seed and seedlings','Remove badly affected debris','Maintain airflow and even irrigation','Confirm symptoms before treatment'],
     'Inspect lower leaves weekly from establishment through harvest',
     'TNAU - Tomato early blight','https://agritech.tnau.ac.in/crop_protection/tomato_diseases_2.html'),
    ('onion','Purple blotch monitoring',45,125,
     'Humid or wet weather and persistent leaf moisture can favour purple blotch.',
     'Look for small pale spots that develop into elongated lesions with dark concentric rings.',
     ARRAY['Use healthy planting material','Keep the field well drained','Avoid unnecessary leaf wetness','Confirm symptoms before treatment'],
     'Inspect leaves weekly after establishment, especially during humid weather',
     'TNAU - Onion purple blotch','https://agritech.tnau.ac.in/crop_protection/onion_diseases_7.html')
) AS v(crop_name, disease_name, start_day, end_day, trigger_conditions,
       symptoms, precautions, monitoring_frequency, source_name, source_url)
  ON LOWER(TRIM(c.name))=v.crop_name
WHERE p.is_active=TRUE
ON CONFLICT (profile_id, disease_name, start_day) DO NOTHING;
