-- Verified starter profiles for crops already present in AgriHelper.
-- Guidance is deliberately non-prescriptive; local soil tests and extension advice win.

INSERT INTO crop_calendar_profiles
    (crop_id, sowing_months, duration_days, harvest_window_days, region,
     source_name, source_url, last_verified)
SELECT crop_id, ARRAY[10,11], 120, 14, 'North and Central India - general reference',
       'ICAR - Wheat variety HD 3226 agronomic practices',
       'https://www.icar.gov.in/node/12081', DATE '2026-10-08'
FROM crops WHERE LOWER(TRIM(name)) = 'wheat'
ORDER BY crop_id LIMIT 1
ON CONFLICT (crop_id) DO UPDATE SET
    sowing_months = EXCLUDED.sowing_months,
    duration_days = EXCLUDED.duration_days,
    harvest_window_days = EXCLUDED.harvest_window_days,
    region = EXCLUDED.region,
    source_name = EXCLUDED.source_name,
    source_url = EXCLUDED.source_url,
    last_verified = EXCLUDED.last_verified,
    is_active = TRUE;

INSERT INTO crop_calendar_profiles
    (crop_id, sowing_months, duration_days, harvest_window_days, region,
     source_name, source_url, last_verified)
SELECT crop_id, ARRAY[6,7], 150, 14, 'India - monsoon rice general reference',
       'Tamil Nadu Agricultural University - Rice crop production',
       'https://www.agritech.tnau.ac.in/agriculture/agri_irrigationmgt_cereals_rice.html',
       DATE '2026-10-08'
FROM crops WHERE LOWER(TRIM(name)) = 'rice'
ORDER BY crop_id LIMIT 1
ON CONFLICT (crop_id) DO UPDATE SET
    sowing_months = EXCLUDED.sowing_months,
    duration_days = EXCLUDED.duration_days,
    harvest_window_days = EXCLUDED.harvest_window_days,
    region = EXCLUDED.region,
    source_name = EXCLUDED.source_name,
    source_url = EXCLUDED.source_url,
    last_verified = EXCLUDED.last_verified,
    is_active = TRUE;

INSERT INTO crop_calendar_profiles
    (crop_id, sowing_months, duration_days, harvest_window_days, region,
     source_name, source_url, last_verified)
SELECT crop_id, ARRAY[5,6], 180, 21, 'India - kharif cotton general reference',
       'Tamil Nadu Agricultural University - Cotton crop production',
       'https://agritech.tnau.ac.in/CropProduction/Fibre%20crops/fibrecrops_cotton.html',
       DATE '2026-10-08'
FROM crops WHERE LOWER(TRIM(name)) = 'cotton'
ORDER BY crop_id LIMIT 1
ON CONFLICT (crop_id) DO UPDATE SET
    sowing_months = EXCLUDED.sowing_months,
    duration_days = EXCLUDED.duration_days,
    harvest_window_days = EXCLUDED.harvest_window_days,
    region = EXCLUDED.region,
    source_name = EXCLUDED.source_name,
    source_url = EXCLUDED.source_url,
    last_verified = EXCLUDED.last_verified,
    is_active = TRUE;

-- Wheat activities
INSERT INTO farming_activities
    (profile_id, activity_type, growth_stage, start_day, end_day, title, guidance,
     priority, source_name, source_url)
SELECT p.profile_id, v.activity_type, v.growth_stage, v.start_day, v.end_day,
       v.title, v.guidance, v.priority,
       'ICAR - Wheat variety HD 3226 agronomic practices',
       'https://www.icar.gov.in/node/12081'
FROM crop_calendar_profiles p
JOIN crops c ON c.crop_id = p.crop_id
CROSS JOIN (VALUES
    ('planning','Pre-sowing',-14,-1,'Prepare field and check soil','Prepare a suitable seedbed and use a current soil test to decide nutrient inputs.','high'),
    ('sowing','Establishment',0,3,'Sow in the recommended window','Use a locally recommended variety and seed rate suitable for the field and irrigation system.','high'),
    ('fertilizer','Establishment',0,7,'Apply basal nutrients by soil test','Apply phosphorus, potash and the basal nitrogen portion only according to local soil-test recommendations.','high'),
    ('irrigation','Crown-root initiation',20,23,'Prioritise first irrigation','Check soil moisture; crown-root initiation is a critical irrigation stage for timely-sown irrigated wheat.','high'),
    ('weed','Early vegetative',27,35,'Inspect and manage weeds','Scout the whole field and use locally approved mechanical or labelled control methods when needed.','normal'),
    ('irrigation','Jointing',45,50,'Check moisture at jointing','Maintain adequate soil moisture; adjust irrigation for rainfall, soil type and local advice.','normal'),
    ('irrigation','Flowering',65,70,'Protect flowering from moisture stress','Check soil moisture and irrigate when required; avoid waterlogging.','high'),
    ('harvest','Maturity',105,120,'Check maturity and prepare harvest','Confirm grain and straw maturity, arrange clean storage, and harvest in dry conditions when possible.','high')
) AS v(activity_type,growth_stage,start_day,end_day,title,guidance,priority)
WHERE LOWER(TRIM(c.name)) = 'wheat'
ON CONFLICT (profile_id, activity_type, start_day, title) DO NOTHING;

-- Rice activities
INSERT INTO farming_activities
    (profile_id, activity_type, growth_stage, start_day, end_day, title, guidance,
     priority, source_name, source_url)
SELECT p.profile_id, v.activity_type, v.growth_stage, v.start_day, v.end_day,
       v.title, v.guidance, v.priority,
       'Tamil Nadu Agricultural University - Rice crop production',
       'https://www.agritech.tnau.ac.in/agriculture/agri_irrigationmgt_cereals_rice.html'
FROM crop_calendar_profiles p
JOIN crops c ON c.crop_id = p.crop_id
CROSS JOIN (VALUES
    ('planning','Pre-sowing',-21,-1,'Prepare seed and field plan','Choose a locally recommended variety and prepare drainage, nursery or direct-sowing arrangements.','high'),
    ('sowing','Establishment',0,7,'Establish the rice crop','Avoid deep standing water during early establishment and inspect emergence regularly.','high'),
    ('fieldwork','Early establishment',14,25,'Check establishment or transplanting','Replace gaps and keep only shallow water where the selected establishment method requires it.','high'),
    ('weed','Tillering',18,35,'Manage early weeds','Scout early and use locally recommended mechanical or labelled methods before weeds compete strongly.','normal'),
    ('fertilizer','Vegetative growth',20,45,'Review crop colour and nutrients','Use soil-test or site-specific nutrient guidance; avoid unnecessary or excessive nitrogen.','high'),
    ('irrigation','Tillering to flowering',30,105,'Manage water and drainage','Check field moisture frequently, prevent prolonged deep flooding, and drain excess rainfall promptly.','high'),
    ('monitoring','Panicle initiation to flowering',75,115,'Protect critical reproductive stages','Avoid moisture stress at panicle initiation, booting, heading and flowering; monitor lodging and disease.','high'),
    ('harvest','Maturity',135,150,'Prepare for harvest','Plan the final irrigation and harvest only after checking crop maturity and local weather.','high')
) AS v(activity_type,growth_stage,start_day,end_day,title,guidance,priority)
WHERE LOWER(TRIM(c.name)) = 'rice'
ON CONFLICT (profile_id, activity_type, start_day, title) DO NOTHING;

-- Cotton activities
INSERT INTO farming_activities
    (profile_id, activity_type, growth_stage, start_day, end_day, title, guidance,
     priority, source_name, source_url)
SELECT p.profile_id, v.activity_type, v.growth_stage, v.start_day, v.end_day,
       v.title, v.guidance, v.priority,
       'Tamil Nadu Agricultural University - Cotton crop production',
       'https://agritech.tnau.ac.in/CropProduction/Fibre%20crops/fibrecrops_cotton.html'
FROM crop_calendar_profiles p
JOIN crops c ON c.crop_id = p.crop_id
CROSS JOIN (VALUES
    ('planning','Pre-sowing',-14,-1,'Prepare field and drainage','Use a soil test, prepare drainage and select a locally recommended cotton variety or hybrid.','high'),
    ('sowing','Establishment',0,5,'Sow and check emergence','Sow in suitable soil moisture and inspect emergence; provide life-saving irrigation only when required.','high'),
    ('fieldwork','Vegetative',16,30,'Thin gaps and inspect plant stand','Maintain the recommended stand and look for early sucking-pest or nutrient symptoms.','normal'),
    ('weed','Vegetative',20,45,'Control early weed competition','Hoe or use locally approved labelled control while protecting young roots.','normal'),
    ('fertilizer','Vegetative to square formation',25,50,'Apply nutrients by soil test','Split nutrients according to soil test, variety and local recommendations; avoid excess nitrogen.','high'),
    ('irrigation','Square and flowering',45,100,'Protect square and flowering stages','Check moisture more often during reproductive growth and regulate irrigation for rainfall and soil type.','high'),
    ('monitoring','Flowering and boll formation',60,150,'Scout flowers and bolls every week','Inspect representative plants and use traps or local thresholds before considering control measures.','high'),
    ('harvest','Boll opening',150,180,'Plan clean cotton picking','Pick only well-opened dry bolls, keep produce clean, and separate damaged cotton.','high')
) AS v(activity_type,growth_stage,start_day,end_day,title,guidance,priority)
WHERE LOWER(TRIM(c.name)) = 'cotton'
ON CONFLICT (profile_id, activity_type, start_day, title) DO NOTHING;

-- Conditional monitoring risks. These are not diagnoses or spray prescriptions.
INSERT INTO crop_disease_risks
    (profile_id, disease_name, start_day, end_day, risk_level, trigger_conditions,
     symptoms, precautions, monitoring_frequency, source_name, source_url)
SELECT p.profile_id, 'Rust and foliar blight monitoring', 45, 100, 'monitor',
       'Cool or humid periods and persistent leaf wetness can favour foliar disease.',
       'Look for unusual yellow, orange or brown pustules, spots, or expanding leaf damage.',
       ARRAY['Use locally recommended resistant varieties when available','Avoid unnecessary late nitrogen','Confirm symptoms before treatment'],
       'Inspect representative field areas weekly and after prolonged humid weather',
       'ICAR crop guidance', 'https://www.icar.gov.in/node/12081'
FROM crop_calendar_profiles p JOIN crops c ON c.crop_id=p.crop_id
WHERE LOWER(TRIM(c.name))='wheat'
ON CONFLICT (profile_id, disease_name, start_day) DO NOTHING;

INSERT INTO crop_disease_risks
    (profile_id, disease_name, start_day, end_day, risk_level, trigger_conditions,
     symptoms, precautions, monitoring_frequency, source_name, source_url)
SELECT p.profile_id, 'Rice blast monitoring', 20, 120, 'monitor',
       'Moist weather and prolonged leaf wetness can favour blast development.',
       'Look for spindle-shaped leaf lesions with grey centres and dark margins, or neck lesions.',
       ARRAY['Use a locally recommended resistant variety','Avoid excessive nitrogen','Improve field observation after wet weather','Confirm symptoms before treatment'],
       'Inspect weekly from seedlings through heading, especially after moist weather',
       'TNAU - Rice blast', 'https://agritech.tnau.ac.in/crop_protection/rice_diseases/rice_1.html'
FROM crop_calendar_profiles p JOIN crops c ON c.crop_id=p.crop_id
WHERE LOWER(TRIM(c.name))='rice'
ON CONFLICT (profile_id, disease_name, start_day) DO NOTHING;

INSERT INTO crop_disease_risks
    (profile_id, disease_name, start_day, end_day, risk_level, trigger_conditions,
     symptoms, precautions, monitoring_frequency, source_name, source_url)
SELECT p.profile_id, 'Bacterial leaf blight monitoring', 15, 115, 'monitor',
       'Heavy rain, flooding, strong wind, deep irrigation and excessive nitrogen can increase risk.',
       'Look for water-soaked leaf-margin lesions that expand and turn yellow or straw coloured.',
       ARRAY['Use locally recommended resistant varieties','Avoid clipping seedling tips','Drain excess water','Avoid excessive late nitrogen','Confirm symptoms before treatment'],
       'Inspect weekly and after storms or flooding',
       'TNAU - Rice bacterial leaf blight', 'https://www.agritech.tnau.ac.in/crop_protection/rice_diseases/rice_23.html'
FROM crop_calendar_profiles p JOIN crops c ON c.crop_id=p.crop_id
WHERE LOWER(TRIM(c.name))='rice'
ON CONFLICT (profile_id, disease_name, start_day) DO NOTHING;

INSERT INTO crop_disease_risks
    (profile_id, disease_name, start_day, end_day, risk_level, trigger_conditions,
     symptoms, precautions, monitoring_frequency, source_name, source_url)
SELECT p.profile_id, 'Pink bollworm monitoring', 60, 165, 'monitor',
       'Risk requires field scouting during flowering and boll formation; calendar timing alone cannot confirm presence.',
       'Look for rosette flowers, entry holes, damaged seeds or larvae inside sampled green bolls.',
       ARRAY['Use pheromone traps for monitoring where locally recommended','Inspect flowers and sampled green bolls','Remove crop residues after final picking','Act only on local economic thresholds and expert advice'],
       'Inspect representative plants weekly during flowering and boll formation',
       'TNAU - IPM package for cotton', 'https://agritech.tnau.ac.in/crop_protection/crop_pdf/cotton.pdf'
FROM crop_calendar_profiles p JOIN crops c ON c.crop_id=p.crop_id
WHERE LOWER(TRIM(c.name))='cotton'
ON CONFLICT (profile_id, disease_name, start_day) DO NOTHING;
