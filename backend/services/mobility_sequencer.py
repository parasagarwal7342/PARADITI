"""
P Λ R Λ D I T I (परादिति) - Welfare-to-Work Sequencer (Claim M)
(C) 2026 Founder: PARAS AGRAWAL
Patent Pending: AI logic to sequence welfare into income-generating pathways.
"""

import logging

class MobilitySequencer:
    """
    Orchestrates the 'Benefit Graduation Path' to transform beneficiaries into earners.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Sequence Map: Current Successful Category -> Recommended Next 'Growth' Step
        self.graduation_paths = {
            "GIRL_CHILD_EDUCATION": {
                "next_step": "NSDC_SKILL_DEVELOPMENT",
                "goal": "Professional Certification",
                "roi_multiplier": 2.5
            },
            "FARMER_SUBSIDY": {
                "next_step": "MUDRA_MICRO_LOAN",
                "goal": "Agri-Business Startup",
                "roi_multiplier": 4.0
            },
            "UNEMPLOYMENT_DOLA": {
                "next_step": "PM_KAUSHAL_VIKAS",
                "goal": "Job Placement",
                "roi_multiplier": 5.2
            }
        }

    def predict_next_milestone(self, active_applications):
        """
        Analyzes current approved schemes and predicts the optimal next career/economic step.
        """
        recommendations = []
        
        for app in active_applications:
            if app.get('status') == 'APPROVED':
                category = app.get('scheme_category')
                if category in self.graduation_paths:
                    recommendations.append(self.graduation_paths[category])
        
        return recommendations

    def calculate_impact_roi(self, user_current_income, grant_amount, path_multiplier):
        """
        Claim N: Impact ROI Calculator.
        Estimates the projected income increase based on the welfare-to-work path.
        """
        projected_earnings_increase = grant_amount * path_multiplier
        total_projected_income = user_current_income + projected_earnings_increase
        
        return {
            "current_income": user_current_income,
            "social_investment": grant_amount,
            "projected_annual_growth": projected_earnings_increase,
            "roi_percentage": f"{((projected_earnings_increase / grant_amount) * 100):.1f}%",
            "narrative": f"This grant is projected to increase your annual earning potential by ₹{projected_earnings_increase:,.0f} through upskilling."
        }

# Global singleton
mobility_sequencer = MobilitySequencer()
