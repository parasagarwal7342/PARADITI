"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026. All rights reserved.
Seed Script for Government Schemes Data.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db
from backend.models import Scheme

def seed_schemes():
    """Seed database with government schemes"""
    app = create_app()
    
    with app.app_context():
        # Check if schemes already exist
        if Scheme.query.count() > 0:
            print("Schemes already exist in database. Skipping seed.")
            return
        
        schemes_data = [
            {
                'name': 'Pradhan Mantri Awas Yojana (PMAY)',
                'description': 'Housing for All by 2022 - Provides affordable housing to urban and rural poor.',
                'category': 'Housing',
                'state': 'Central',
                'eligibility_criteria': 'Family income should be less than Rs. 3 lakh per annum. Should not own a pucca house.',
                'benefits': 'Financial assistance up to Rs. 2.67 lakh for construction of house. Interest subsidy on home loans.',
                'documents_required': 'Aadhaar card, Income certificate, Bank account details, Land documents',
                'official_link': 'https://pmaymis.gov.in/',
                'min_income': 0,
                'max_income': 300000,
                'category_specific': 'General'
            },
            {
                'name': 'Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)',
                'description': 'Direct income support scheme for farmers. Provides Rs. 6000 per year in three installments.',
                'category': 'Agriculture',
                'state': 'Central',
                'eligibility_criteria': 'Must be a farmer owning cultivable land. Should be registered in land records.',
                'benefits': 'Rs. 2000 per installment, total Rs. 6000 per year directly to bank account.',
                'documents_required': 'Aadhaar card, Bank account details, Land ownership documents',
                'official_link': 'https://pmkisan.gov.in/',
                'min_income': 0,
                'max_income': None,
                'occupation_specific': 'Farmer'
            },
            {
                'name': 'Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)',
                'description': 'World\'s largest health insurance scheme providing coverage of Rs. 5 lakh per family per year.',
                'category': 'Health',
                'state': 'Central',
                'eligibility_criteria': 'Families listed in SECC database. No age or income limit for beneficiaries.',
                'benefits': 'Health insurance coverage of Rs. 5 lakh per family per year for secondary and tertiary care.',
                'documents_required': 'Aadhaar card, Ration card, Income certificate',
                'official_link': 'https://pmjay.gov.in/',
                'min_income': 0,
                'max_income': None
            },
            {
                'name': 'Pradhan Mantri Ujjwala Yojana (PMUY)',
                'description': 'Free LPG connection to women from below poverty line families.',
                'category': 'Energy',
                'state': 'Central',
                'eligibility_criteria': 'Women above 18 years from BPL families. Should not already have LPG connection.',
                'benefits': 'Free LPG connection with first refill. Financial assistance for connection.',
                'documents_required': 'Aadhaar card, BPL certificate, Bank account details',
                'official_link': 'https://www.pmuy.gov.in/',
                'min_income': 0,
                'max_income': 100000,
                'gender_specific': 'Female'
            },
            {
                'name': 'Pradhan Mantri Mudra Yojana (PMMY)',
                'description': 'Micro finance scheme providing loans up to Rs. 10 lakh to small businesses.',
                'category': 'Finance',
                'state': 'Central',
                'eligibility_criteria': 'Non-corporate, non-farm small/micro enterprises. Business should be engaged in manufacturing, trading or services.',
                'benefits': 'Loans up to Rs. 10 lakh without collateral. Three categories: Shishu (up to Rs. 50,000), Kishore (Rs. 50,001 to Rs. 5 lakh), Tarun (Rs. 5,00,001 to Rs. 10 lakh).',
                'documents_required': 'Aadhaar card, Business proof, Bank account details, Identity proof',
                'official_link': 'https://www.mudra.org.in/',
                'min_income': 0,
                'max_income': None
            },
            {
                'name': 'Pradhan Mantri Matru Vandana Yojana (PMMVY)',
                'description': 'Maternity benefit program providing financial assistance to pregnant and lactating mothers.',
                'category': 'Women Welfare',
                'state': 'Central',
                'eligibility_criteria': 'Pregnant and lactating mothers above 19 years. First living child only.',
                'benefits': 'Cash benefit of Rs. 5000 in three installments during pregnancy and after delivery.',
                'documents_required': 'Aadhaar card, MCP card, Bank account details, Pregnancy certificate',
                'official_link': 'https://wcd.nic.in/schemes/pradhan-mantri-matru-vandana-yojana',
                'min_age': 19,
                'max_age': None,
                'gender_specific': 'Female'
            },
            {
                'name': 'Pradhan Mantri Shram Yogi Maan-Dhan (PM-SYM)',
                'description': 'Pension scheme for unorganized workers providing monthly pension after 60 years.',
                'category': 'Pension',
                'state': 'Central',
                'eligibility_criteria': 'Unorganized workers between 18-40 years. Monthly income should be less than Rs. 15,000.',
                'benefits': 'Monthly pension of Rs. 3000 after 60 years. Government contributes equal amount.',
                'documents_required': 'Aadhaar card, Bank account details, Income certificate, Age proof',
                'official_link': 'https://maandhan.in/',
                'min_age': 18,
                'max_age': 40,
                'min_income': 0,
                'max_income': 15000
            },
            {
                'name': 'Pradhan Mantri Kisan Maan-Dhan Yojana (PM-KMY)',
                'description': 'Pension scheme for small and marginal farmers providing monthly pension after 60 years.',
                'category': 'Pension',
                'state': 'Central',
                'eligibility_criteria': 'Small and marginal farmers between 18-40 years. Landholding up to 2 hectares.',
                'benefits': 'Monthly pension of Rs. 3000 after 60 years. Government contributes equal amount.',
                'documents_required': 'Aadhaar card, Bank account details, Land ownership documents, Age proof',
                'official_link': 'https://maandhan.in/',
                'min_age': 18,
                'max_age': 40,
                'occupation_specific': 'Farmer'
            },
            {
                'name': 'Beti Bachao Beti Padhao',
                'description': 'Scheme to prevent gender-biased sex selection and promote education of girl child.',
                'category': 'Education',
                'state': 'Central',
                'eligibility_criteria': 'Families with girl child. Focus on districts with low child sex ratio.',
                'benefits': 'Financial incentives for girl child education. Awareness programs and support services.',
                'documents_required': 'Aadhaar card, Birth certificate, School enrollment proof',
                'official_link': 'https://wcd.nic.in/bbbp-schemes',
                'gender_specific': 'Female',
                'min_age': 0,
                'max_age': 18
            },
            {
                'name': 'Pradhan Mantri Gramin Digital Saksharta Abhiyan (PMGDISHA)',
                'description': 'Digital literacy program to make citizens digitally literate.',
                'category': 'Education',
                'state': 'Central',
                'eligibility_criteria': 'Age 14-60 years. Should not be digitally literate. Preference to SC/ST/BPL/women/minorities.',
                'benefits': 'Free digital literacy training. Certificate after completion. Access to digital services.',
                'documents_required': 'Aadhaar card, Age proof, Category certificate (if applicable)',
                'official_link': 'https://www.pmgdisha.in/',
                'min_age': 14,
                'max_age': 60
            },
            {
                'name': 'Pradhan Mantri Suraksha Bima Yojana (PMSBY)',
                'description': 'Accidental insurance scheme providing coverage of Rs. 2 lakh at premium of Rs. 12 per year.',
                'category': 'Insurance',
                'state': 'Central',
                'eligibility_criteria': 'Age 18-70 years. Should have bank account. Aadhaar linked bank account preferred.',
                'benefits': 'Accidental death and disability coverage of Rs. 2 lakh. Premium only Rs. 12 per year.',
                'documents_required': 'Aadhaar card, Bank account details',
                'official_link': 'https://www.jansuraksha.gov.in/',
                'min_age': 18,
                'max_age': 70
            },
            {
                'name': 'Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)',
                'description': 'Life insurance scheme providing coverage of Rs. 2 lakh at premium of Rs. 436 per year.',
                'category': 'Insurance',
                'state': 'Central',
                'eligibility_criteria': 'Age 18-50 years. Should have bank account. Aadhaar linked bank account preferred.',
                'benefits': 'Life insurance coverage of Rs. 2 lakh. Premium only Rs. 436 per year.',
                'documents_required': 'Aadhaar card, Bank account details, Age proof',
                'official_link': 'https://www.jansuraksha.gov.in/',
                'min_age': 18,
                'max_age': 50
            },
            {
                'name': 'Stand Up India Scheme',
                'description': 'Bank loan scheme for SC/ST and women entrepreneurs to promote entrepreneurship.',
                'category': 'Finance',
                'state': 'Central',
                'eligibility_criteria': 'SC/ST or women entrepreneurs. Age above 18 years. Greenfield project (first time venture).',
                'benefits': 'Bank loans from Rs. 10 lakh to Rs. 1 crore for setting up new enterprise.',
                'documents_required': 'Aadhaar card, Caste certificate (for SC/ST), Business plan, Bank account details',
                'official_link': 'https://www.standupmitra.in/',
                'min_age': 18,
                'category_specific': 'SC,ST',
                'gender_specific': 'Female'
            },
            {
                'name': 'Pradhan Mantri Vaya Vandana Yojana (PMVVY)',
                'description': 'Pension scheme for senior citizens providing guaranteed pension.',
                'category': 'Pension',
                'state': 'Central',
                'eligibility_criteria': 'Age 60 years and above. Maximum investment Rs. 15 lakh.',
                'benefits': 'Guaranteed pension of 8% per annum. Pension payable monthly/quarterly/half-yearly/yearly.',
                'documents_required': 'Aadhaar card, Age proof, Bank account details',
                'official_link': 'https://www.licindia.in/',
                'min_age': 60,
                'max_age': None
            },
            {
                'name': 'Pradhan Mantri Garib Kalyan Anna Yojana (PMGKAY)',
                'description': 'Free food grains scheme providing 5 kg rice/wheat per person per month.',
                'category': 'Food Security',
                'state': 'Central',
                'eligibility_criteria': 'All beneficiaries under National Food Security Act (NFSA). Priority and Antyodaya households.',
                'benefits': 'Free 5 kg food grains (rice/wheat) per person per month in addition to regular entitlement.',
                'documents_required': 'Ration card, Aadhaar card',
                'official_link': 'https://nfsa.gov.in/',
                'min_income': 0,
                'max_income': None
            },
            {
                'name': 'Delhi Arogya Kosh',
                'description': 'Health insurance scheme for residents of Delhi providing cashless treatment.',
                'category': 'Health',
                'state': 'Delhi',
                'eligibility_criteria': 'Residents of Delhi. Annual family income less than Rs. 3 lakh.',
                'benefits': 'Cashless treatment up to Rs. 5 lakh per family per year in empaneled hospitals.',
                'documents_required': 'Aadhaar card, Delhi residence proof, Income certificate, Ration card',
                'official_link': 'https://www.delhi.gov.in/',
                'min_income': 0,
                'max_income': 300000
            },
            {
                'name': 'Mukhyamantri Teerth Yatra Yojana (Delhi)',
                'description': 'Free pilgrimage scheme for senior citizens of Delhi to visit religious places.',
                'category': 'Welfare',
                'state': 'Delhi',
                'eligibility_criteria': 'Senior citizens (60+) of Delhi. Annual family income less than Rs. 3 lakh.',
                'benefits': 'Free travel, accommodation and food for pilgrimage to various religious places.',
                'documents_required': 'Aadhaar card, Age proof, Income certificate, Delhi residence proof',
                'official_link': 'https://www.delhi.gov.in/',
                'min_age': 60,
                'max_income': 300000
            },
            {
                'name': 'Ladli Scheme (Delhi)',
                'description': 'Financial assistance scheme for girl child education and welfare in Delhi.',
                'category': 'Education',
                'state': 'Delhi',
                'eligibility_criteria': 'Girl child born in Delhi. Parents should be residents of Delhi for at least 3 years.',
                'benefits': 'Financial assistance of Rs. 11,000 at birth and additional amounts at various stages of education.',
                'documents_required': 'Birth certificate, Aadhaar card, Delhi residence proof, Bank account details',
                'official_link': 'https://www.delhi.gov.in/',
                'gender_specific': 'Female',
                'min_age': 0,
                'max_age': 18
            },
            {
                'name': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
                'description': 'Crop insurance scheme providing financial support to farmers in case of crop loss.',
                'category': 'Agriculture',
                'state': 'Central',
                'eligibility_criteria': 'All farmers growing notified crops in notified areas. Should have insurable interest in the crop.',
                'benefits': 'Premium subsidy by government. Comprehensive coverage for yield losses. Quick claim settlement.',
                'documents_required': 'Aadhaar card, Land ownership documents, Bank account details, Crop details',
                'official_link': 'https://pmfby.gov.in/',
                'occupation_specific': 'Farmer'
            },
            {
                'name': 'Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan (PM-KUSUM)',
                'description': 'Scheme for farmers to set up solar power plants and solar pumps.',
                'category': 'Energy',
                'state': 'Central',
                'eligibility_criteria': 'Farmers with agricultural land. Should have valid land documents.',
                'benefits': 'Subsidy up to 60% for solar pumps. Opportunity to earn by selling surplus solar power.',
                'documents_required': 'Aadhaar card, Land ownership documents, Bank account details',
                'official_link': 'https://mnre.gov.in/',
                'occupation_specific': 'Farmer'
            }
        ]
        
        # Add schemes to database
        for scheme_data in schemes_data:
            scheme = Scheme(**scheme_data)
            db.session.add(scheme)
        
        db.session.commit()
        
        print(f"Successfully seeded {len(schemes_data)} government schemes!")
        print("Schemes include Central and State government schemes across various categories.")

if __name__ == '__main__':
    seed_schemes()
