// AgriHelper - Data Store

const CropData = [
    {
        id: 'wheat',
        name: 'Wheat',
        icon: '🌾',
        category: 'Cereal',
        description: 'Wheat is one of the world\'s most important staple crops grown in cool seasons.',
        fullDescription: 'Wheat is one of the world\'s most important staple crops. It is primarily grown in cool seasons and is a major source of carbohydrates and protein for millions of people.',
        season: 'Rabi (Winter)',
        water: '450-650 mm',
        soil: 'Well-drained loamy or clay loam soil',
        duration: '100-150 days',
        yield: '2-5 tonnes/hectare',
        temperature: '15-25°C (optimal)',
        rainfall: '75-100 cm annually',
        pH: '6.0-7.5',
        diseases: ['Rust (Leaf, Stem, Stripe)', 'Powdery Mildew', 'Karnal Bunt', 'Loose Smut'],
        practices: [
            'Use certified disease-resistant seeds',
            'Sow at proper depth (4-5 cm)',
            'Apply balanced fertilizers (NPK)',
            'Ensure timely irrigation at critical growth stages',
            'Practice crop rotation'
        ],
        fertilizers: {
            basal: 'Apply 60 kg N, 30 kg P2O5, 20 kg K2O per hectare at sowing',
            topDressing: 'Apply remaining 60 kg N in two splits - at crown root initiation and flowering'
        },
        irrigation: [
            'Crown Root Initiation (CRI) stage - 20-25 days after sowing',
            'Tillering stage - 40-45 days after sowing',
            'Jointing stage - 60-65 days after sowing',
            'Flowering stage - 80-85 days after sowing',
            'Milk stage - 100-105 days after sowing',
            'Dough stage - 115-120 days after sowing'
        ],
        harvesting: 'Harvest when grains are hard and moisture content is 20-25%. Use combine harvester or manual sickle.',
        storage: 'Dry grains to 12% moisture. Store in clean, dry, pest-free warehouses. Use proper fumigation.',
        marketPrice: '₹2,000-2,500 per quintal (varies by region and quality)',
        nutritionalValue: 'Rich in carbohydrates (71%), protein (12%), fiber, vitamins B and E, minerals like iron and zinc'
    },
    {
        id: 'maize',
        name: 'Maize',
        icon: '🌽',
        category: 'Cereal',
        description: 'Maize is a versatile crop used for food, feed, and industrial products.',
        fullDescription: 'Maize, also known as corn, is a versatile crop used for food, animal feed, and industrial purposes. It is rich in carbohydrates and provides essential vitamins.',
        season: 'Kharif & Rabi',
        water: '500-800 mm',
        soil: 'Well-drained sandy loam',
        duration: '80-110 days',
        yield: '5-8 tonnes/hectare',
        temperature: '21-27°C (optimal)',
        rainfall: '50-75 cm',
        pH: '5.5-7.0',
        diseases: ['Maize Dwarf Mosaic', 'Northern Leaf Blight', 'Stalk Rot', 'Ear Rot'],
        practices: [
            'Plant at 5-7 cm depth with 60-75 cm row spacing',
            'Apply adequate nitrogen for high yields',
            'Irrigate at critical stages: knee-high, tasseling, grain filling',
            'Control weeds in first 40 days',
            'Harvest when moisture content is 20-25%'
        ],
        fertilizers: {
            basal: 'Apply 60 kg N, 60 kg P2O5, 40 kg K2O per hectare at sowing',
            topDressing: 'Apply 60 kg N at knee-high stage (30-35 days) and 60 kg N at tasseling stage'
        },
        irrigation: [
            'Knee-high stage - 20-25 days after sowing (critical)',
            'Tasseling stage - 50-55 days after sowing (most critical)',
            'Silking stage - 60-65 days after sowing (critical)',
            'Grain filling stage - 75-80 days after sowing',
            'Dough stage - 90-95 days after sowing'
        ],
        harvesting: 'Harvest when kernels are hard and moisture is 20-25%. Cobs should be dry with brown husks.',
        storage: 'Dry to 12-14% moisture. Store in well-ventilated areas. Protect from rodents and insects.',
        marketPrice: '₹1,800-2,200 per quintal',
        nutritionalValue: 'High in carbohydrates (74%), moderate protein (9%), rich in vitamins A, B, E, and minerals'
    },
    {
        id: 'tomato',
        name: 'Tomato',
        icon: '🍅',
        category: 'Vegetable',
        description: 'Tomatoes are widely cultivated and used in various cuisines worldwide.',
        fullDescription: 'Tomatoes are one of the most popular vegetables grown worldwide. They are rich in vitamins A and C, and lycopene, making them highly nutritious.',
        season: 'Year-round (with protection)',
        water: '400-600 mm',
        soil: 'Sandy loam to clay loam',
        duration: '60-90 days',
        yield: '25-40 tonnes/hectare',
        temperature: '20-25°C (optimal)',
        rainfall: '60-150 cm',
        pH: '6.0-7.0',
        diseases: ['Early Blight', 'Late Blight', 'Bacterial Wilt', 'Tomato Yellow Leaf Curl'],
        practices: [
            'Transplant seedlings 25-30 days old',
            'Maintain spacing of 60x45 cm',
            'Stake plants for support',
            'Apply mulch to conserve moisture',
            'Prune suckers for better yield'
        ],
        fertilizers: {
            basal: 'Apply 25 tonnes FYM, 50 kg N, 50 kg P2O5, 50 kg K2O per hectare before transplanting',
            topDressing: 'Apply 50 kg N and 50 kg K2O in 2-3 splits at 30, 45, and 60 days after transplanting'
        },
        irrigation: [
            'Immediately after transplanting',
            'Light irrigation every 3-4 days for first 2 weeks',
            'Every 5-7 days during vegetative growth',
            'Every 7-10 days during flowering and fruiting',
            'Reduce irrigation 10 days before final harvest'
        ],
        harvesting: 'Harvest when fruits are firm and fully colored. Pick every 3-4 days. Handle carefully to avoid bruising.',
        storage: 'Store at 10-15°C with 85-90% humidity. Ripe tomatoes last 7-10 days. Green tomatoes can be ripened gradually.',
        marketPrice: '₹800-2,000 per quintal (highly variable by season)',
        nutritionalValue: 'Rich in lycopene, vitamins A and C, potassium, folate. Low in calories (18 kcal per 100g)'
    },
    {
        id: 'soybean',
        name: 'Soybean',
        icon: '🌱',
        category: 'Pulse',
        description: 'Soybean is a high-protein crop used for oil and animal feed.',
        fullDescription: 'Soybean is a high-protein legume that enriches soil nitrogen. It is used for oil extraction, animal feed, and various food products like tofu and soy milk.',
        season: 'Kharif',
        water: '450-700 mm',
        soil: 'Well-drained loamy soil',
        duration: '85-120 days',
        yield: '2-3 tonnes/hectare',
        temperature: '20-30°C (optimal)',
        rainfall: '50-75 cm',
        pH: '6.0-7.5',
        diseases: ['Rust', 'Yellow Mosaic', 'Charcoal Rot', 'Pod Blight'],
        practices: [
            'Treat seeds with Rhizobium culture',
            'Sow at 3-4 cm depth',
            'Maintain row spacing of 30-45 cm',
            'Avoid waterlogging',
            'Harvest when 95% pods turn brown'
        ],
        fertilizers: {
            basal: 'Apply 20 kg N, 60 kg P2O5, 40 kg K2O per hectare at sowing. Inoculate seeds with Rhizobium culture',
            topDressing: 'Generally not required due to nitrogen fixation. Apply 20 kg N if plants show deficiency'
        },
        irrigation: [
            'Pre-sowing irrigation for good germination',
            'Flowering stage - 35-40 days after sowing (critical)',
            'Pod formation stage - 55-60 days after sowing (critical)',
            'Pod filling stage - 70-75 days after sowing',
            'Stop irrigation 10-15 days before harvest'
        ],
        harvesting: 'Harvest when 95% pods turn brown and leaves fall. Moisture should be 12-14%. Use combine harvester or manual methods.',
        storage: 'Dry to 9-10% moisture. Store in cool, dry place. Use hermetic storage to prevent pest damage.',
        marketPrice: '₹3,500-4,500 per quintal',
        nutritionalValue: 'Highest protein content (40%), oil (20%), rich in calcium, iron, vitamins B and E'
    },
    {
        id: 'sugarcane',
        name: 'Sugarcane',
        icon: '🎋',
        category: 'Cash Crop',
        description: 'Sugarcane is a tropical crop used for sugar and ethanol production.',
        fullDescription: 'Sugarcane is a tropical perennial crop widely cultivated for sugar production. It is also used to produce jaggery, ethanol, and animal feed. India is one of the largest producers of sugarcane in the world.',
        season: 'Year-round',
        water: '1500-2500 mm',
        soil: 'Deep, fertile, well-drained loamy soil',
        duration: '10-18 months',
        yield: '60-80 tonnes/hectare',
        temperature: '20-35°C (optimal)',
        rainfall: '150-250 cm',
        pH: '6.5-7.5',
        diseases: ['Red Rot', 'Smut', 'Wilt', 'Mosaic'],
        practices: [
            'Use disease-free seed cane',
            'Plant at proper spacing (90-120 cm)',
            'Ensure adequate irrigation',
            'Apply balanced fertilization',
            'Harvest at proper maturity'
        ],
        fertilizers: {
            basal: 'Apply 150 kg N, 60 kg P2O5, 60 kg K2O per hectare at planting',
            topDressing: 'Apply 150 kg N in 2-3 splits at 30, 60, and 90 days. Apply 60 kg K2O at 120 days'
        },
        irrigation: [
            'Immediately after planting',
            'Every 7-10 days during germination (first 45 days)',
            'Every 10-15 days during tillering phase',
            'Every 12-15 days during grand growth phase',
            'Stop irrigation 15-20 days before harvest for better sugar content'
        ],
        harvesting: 'Harvest at 10-12 months for early varieties, 12-18 months for main crop. Cut close to ground level. Process within 24 hours.',
        storage: 'Sugarcane should be processed immediately after harvest. Delay reduces sugar content. Store cut cane in shade if processing is delayed.',
        marketPrice: '₹280-350 per quintal (government FRP)',
        nutritionalValue: 'High in sucrose (15-20%), contains vitamins B and C, calcium, iron, magnesium, phosphorus'
    }
];

const LoanData = [
    {
        name: 'Kisan Credit Card Scheme',
        shortName: 'KCC',
        type: 'Crop Loan',
        region: 'National',
        description: 'Provides affordable credit to farmers for crop production and allied activities.',
        interest: '4%',
        maxAmount: '₹3,00,000',
        benefits: ['Low interest rate', 'Flexible repayment']
    },
    {
        name: 'PM Fasal Bima Yojana',
        shortName: 'PMFBY',
        type: 'Subsidy',
        region: 'State',
        description: 'Crop insurance scheme providing financial support to farmers in case of crop loss.',
        interest: '2%',
        maxAmount: '₹2,00,000',
        benefits: ['Insurance coverage', 'Risk protection']
    },
    {
        name: 'PM-KISAN Scheme',
        shortName: 'PM-KISAN',
        type: 'Subsidy',
        region: 'National',
        description: 'Direct income support of ₹6,000 per year to all farmer families.',
        interest: '0%',
        maxAmount: '₹6,000/year',
        benefits: ['Direct bank transfer', 'Three installments']
    },
    {
        name: 'Agricultural Term Loan',
        shortName: 'ATL',
        type: 'Crop Loan',
        region: 'State',
        description: 'Long-term loans for farm equipment, irrigation, and land development.',
        interest: '7%',
        maxAmount: '₹10,00,000',
        benefits: ['Long repayment period', 'Equipment financing']
    }
];
