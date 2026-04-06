"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026. All rights reserved.
Seed Script for Government Schemes Data.
"""
import sys
import os
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.models import Scheme, User
    from backend.database import db
except ImportError:
    # Handle direct script execution vs app import
    pass

def seed_db(app):
    """Seed database with government schemes and a test user"""
    from backend.models import Scheme, User
    from backend.database import db
    
    with app.app_context():
        # 1. Create Tables
        db.create_all()
        
        # 2. Seed Test User
        if User.query.filter_by(email='admin@paraditi.in').first() is None:
            admin = User(
                username='admin',
                email='admin@paraditi.in',
                password_hash=generate_password_hash('paraditi2026'),
                role='citizen'
            )
            db.session.add(admin)
            print("Admin user created: admin@paraditi.in / paraditi2026")

        # 3. Seed Schemes
        if Scheme.query.count() == 0:
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
                    'name': 'Ayushman Bharat - PM-JAY',
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
                    'eligibility_criteria': 'Non-corporate, non-farm small/micro enterprises.',
                    'benefits': 'Loans up to Rs. 10 lakh without collateral.',
                    'documents_required': 'Aadhaar card, Business proof, Bank account details',
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
                    'benefits': 'Cash benefit of Rs. 5000 in three installments.',
                    'documents_required': 'Aadhaar card, MCP card, Bank account details',
                    'official_link': 'https://wcd.nic.in/',
                    'min_age': 19,
                    'gender_specific': 'Female'
                },
                {
                    'name': 'Beti Bachao Beti Padhao',
                    'description': 'Scheme to prevent gender-biased sex selection and promote education of girl child.',
                    'category': 'Education',
                    'state': 'Central',
                    'eligibility_criteria': 'Families with girl child.',
                    'benefits': 'Financial incentives for girl child education.',
                    'documents_required': 'Aadhaar card, Birth certificate',
                    'official_link': 'https://wcd.nic.in/',
                    'gender_specific': 'Female'
                },
                {
                    'name': 'Delhi Arogya Kosh',
                    'description': 'Health insurance scheme for residents of Delhi providing cashless treatment.',
                    'category': 'Health',
                    'state': 'Delhi',
                    'eligibility_criteria': 'Residents of Delhi. Annual family income less than Rs. 3 lakh.',
                    'benefits': 'Cashless treatment up to Rs. 5 lakh per family per year.',
                    'documents_required': 'Aadhaar card, Delhi residence proof, Income certificate',
                    'official_link': 'https://www.delhi.gov.in/',
                    'min_income': 0,
                    'max_income': 300000
                }
            ]
            
            for scheme_data in schemes_data:
                scheme = Scheme(**scheme_data)
                db.session.add(scheme)
            
            db.session.commit()
            print(f"Successfully seeded {len(schemes_data)} government schemes!")

if __name__ == '__main__':
    from backend.app import create_app
    app = create_app()
    seed_db(app)
