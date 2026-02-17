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
        diseases: ['Rust (Leaf, Stem, Stripe)', 'Powdery Mildew', 'Karnal Bunt', 'Loose Smut'],
        practices: [
            'Use certified disease-resistant seeds',
            'Sow at proper depth (4-5 cm)',
            'Apply balanced fertilizers (NPK)',
            'Ensure timely irrigation at critical growth stages',
            'Practice crop rotation'
        ]
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
        diseases: ['Maize Dwarf Mosaic', 'Northern Leaf Blight', 'Stalk Rot', 'Ear Rot'],
        practices: [
            'Plant at 5-7 cm depth with 60-75 cm row spacing',
            'Apply adequate nitrogen for high yields',
            'Irrigate at critical stages: knee-high, tasseling, grain filling',
            'Control weeds in first 40 days',
            'Harvest when moisture content is 20-25%'
        ]
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
        diseases: ['Early Blight', 'Late Blight', 'Bacterial Wilt', 'Tomato Yellow Leaf Curl'],
        practices: [
            'Transplant seedlings 25-30 days old',
            'Maintain spacing of 60x45 cm',
            'Stake plants for support',
            'Apply mulch to conserve moisture',
            'Prune suckers for better yield'
        ]
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
        diseases: ['Rust', 'Yellow Mosaic', 'Charcoal Rot', 'Pod Blight'],
        practices: [
            'Treat seeds with Rhizobium culture',
            'Sow at 3-4 cm depth',
            'Maintain row spacing of 30-45 cm',
            'Avoid waterlogging',
            'Harvest when 95% pods turn brown'
        ]
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
        diseases: ['Red Rot', 'Smut', 'Wilt', 'Mosaic'],
        practices: [
            'Use disease-free seed cane',
            'Plant at proper spacing (90-120 cm)',
            'Ensure adequate irrigation',
            'Apply balanced fertilization',
            'Harvest at proper maturity'
        ]
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
