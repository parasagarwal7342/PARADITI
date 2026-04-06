"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Automated Seeding Service for Production/Demo Environments.
"""
from backend.models import Scheme, User
from backend.database import db

def seed_production_data():
    """Seed database with essential government schemes for the live demo."""
    # Check if already seeded
    if Scheme.query.count() > 0:
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
            'name': 'Ayushman Bharat (PM-JAY)',
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
            'name': 'Pradhan Mantri Mudra Yojana (PMMY)',
            'description': 'Micro finance scheme providing loans up to Rs. 10 lakh to small businesses.',
            'category': 'Finance',
            'state': 'Central',
            'benefits': 'Loans up to Rs. 10 lakh without collateral. Shishu, Kishore, and Tarun categories.',
            'documents_required': 'Aadhaar card, Business proof, Bank account details',
            'official_link': 'https://www.mudra.org.in/',
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
            'documents_required': 'Aadhaar card, Delhi residence proof, Income certificate',
            'official_link': 'https://www.delhi.gov.in/',
            'min_income': 0,
            'max_income': 300000
        }
    ]
    
    for data in schemes_data:
        scheme = Scheme(**data)
        db.session.add(scheme)
    
    db.session.commit()
    print("Production seeding complete.")
