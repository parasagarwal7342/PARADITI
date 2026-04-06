"""
P Λ R Λ D I T I (परादिति) - Universal Beneficiary Score (UBS) (Claim F)
(C) 2026 Founder: PARAS AGRAWAL
Patent Pending: The 'CIBIL Score' for social welfare readiness.
"""

import logging
from datetime import datetime

class UniversalBeneficiaryScore:
    """
    Quantifies a citizen's readiness for benefits using a multi-variate analysis 
    of profile completeness and document authenticity.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_score(self, user_profile, verified_documents):
        """
        Calculates the UBS (0-900) based on 'Claim F' algorithm.
        """
        base_score = 300 # Starting score
        
        # Factor 1: Profile Completeness (Max 300)
        profile_score = 0
        fields = ['name', 'dob', 'gender', 'address', 'income', 'caste']
        for field in fields:
            if user_profile.get(field):
                profile_score += 50
        
        # Factor 2: Document Authenticity (Max 300)
        doc_score = 0
        required_docs = ['aadhaar', 'pan', 'income_certificate', 'caste_certificate']
        for doc in verified_documents:
            if doc.get('type') in required_docs and doc.get('verified'):
                doc_score += 75
                
        # Calculate Final Score
        final_score = base_score + profile_score + doc_score
        final_score = min(900, final_score)
        
        # Determine Readiness Level
        readiness = "LOW"
        if final_score > 750:
            readiness = "INSTANT_APPROVAL_LIKELY"
        elif final_score > 600:
            readiness = "HIGH"
        elif final_score > 450:
            readiness = "MODERATE"
            
        return {
            "ubs_score": final_score,
            "readiness_level": readiness,
            "breakdown": {
                "base": base_score,
                "profile": profile_score,
                "documents": doc_score
            },
            "timestamp": datetime.now().isoformat()
        }

# Global singleton
ubs_service = UniversalBeneficiaryScore()
