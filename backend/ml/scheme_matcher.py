"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import json
from backend.models import User, Scheme, UserScheme


class SchemeMatcher:
    """Handles scheme matching logic"""
    
    def __init__(self, ml_engine):
        """
        Initialize scheme matcher
        
        Args:
            ml_engine: MLRecommendationEngine instance
        """
        self.ml_engine = ml_engine
    
    def match_schemes(self, user: User, schemes: List[Scheme], limit: int = 10) -> Dict[str, List[Any]]:
        """
        Match user to schemes using ML similarity
        
        Args:
            user: User object
            schemes: List of Scheme objects
            limit: Maximum number of recommendations
            
        Returns:
            Dict containing 'eligible' and 'almost_eligible' lists
        """
        if not schemes:
            return {'eligible': [], 'almost_eligible': []}
        
        # Filter schemes by hard criteria first
        filtered_schemes = []
        almost_eligible_schemes = []
        
        for scheme in schemes:
            is_eligible, failure_reason = self._check_eligibility(user, scheme)
            
            if is_eligible:
                filtered_schemes.append(scheme)
            elif failure_reason:
                # Calculate similarity for almost eligible too
                similarity = self.ml_engine.get_scheme_similarity(user, scheme)
                if similarity >= (self.ml_engine.similarity_threshold * 0.8): # Lower threshold for almost eligible
                    almost_eligible_schemes.append({
                        'scheme': scheme,
                        'score': similarity,
                        'gap': failure_reason
                    })
        
        # Calculate similarities for eligible
        eligible_results = []
        for scheme in filtered_schemes:
            similarity = self.ml_engine.get_scheme_similarity(user, scheme)
            # PATENT CLAIM: Hybrid Filtering
            # If scheme passed hard filters (is_eligible=True), we include it regardless of ML score.
            # ML score is used purely for ranking/sorting.
            eligible_results.append((scheme, similarity))
        
        # Sort
        eligible_results.sort(key=lambda x: x[1], reverse=True)
        almost_eligible_schemes.sort(key=lambda x: x['score'], reverse=True)
        
        # Find alternatives for almost eligible schemes
        top_eligible_schemes = [s for s, score in eligible_results[:10]] # Use top 10 eligible as candidate pool
        
        for item in almost_eligible_schemes:
            best_alternative = None
            best_score = -1.0
            
            for eligible_scheme in top_eligible_schemes:
                # Calculate similarity between schemes
                try:
                    sim = self.ml_engine.get_scheme_to_scheme_similarity(item['scheme'], eligible_scheme)
                    if sim > best_score:
                        best_score = sim
                        best_alternative = eligible_scheme
                except Exception:
                    continue
            
            if best_alternative and best_score > 0.3: # Low threshold as schemes might be different but related
                item['alternative'] = best_alternative
            else:
                item['alternative'] = None

        return {
            'eligible': eligible_results[:limit],
            'almost_eligible': almost_eligible_schemes[:5] # Limit almost eligible
        }
    
    def get_approval_confidence(self, user: User, scheme: Scheme) -> Tuple[float, List[str]]:
        """
        PATENT CLAIM K: Predictive Rejection Engine.
        Analyzes profile and documents to identify rejection risks before submission.
        """
        risks = []
        score = 95.0 # Base confidence
        
        # 1. Document Readiness Check
        required_docs = []
        if scheme.documents_required:
            try:
                required_docs = json.loads(scheme.documents_required)
            except:
                required_docs = [d.strip() for d in scheme.documents_required.split(',')]
        
        user_docs = {d.document_type.lower() for d in user.documents}
        verified_docs = {d.document_type.lower() for d in user.documents if d.is_verified}
        
        for req in required_docs:
            req_l = req.lower()
            if req_l not in user_docs:
                score -= 25
                risks.append(f"Missing critical document: {req}")
            elif req_l not in verified_docs:
                score -= 10
                risks.append(f"Document uploaded but not AI-verified: {req}")
        
        # 2. Demographic Data Consistency
        if scheme.min_age and user.age:
            if user.age == scheme.min_age:
                score -= 5 # Edge case risk
                risks.append("Age is exactly at minimum limit; proof must be highly accurate")
        
        if scheme.max_income and user.income:
            if user.income > (scheme.max_income * 0.9):
                score -= 15
                risks.append("Income is close to the ceiling; risk of rejection on audit")
                
        return max(0, score), risks

    def get_graduation_path(self, scheme: Scheme) -> List[Dict[str, Any]]:
        """
        PATENT CLAIM M: Welfare-to-Work Sequencer.
        Identifies the next logical steps for economic mobility.
        """
        if not scheme.graduation_path:
            return []
            
        try:
            next_ids = json.loads(scheme.graduation_path)
            next_schemes = Scheme.query.filter(Scheme.id.in_(next_ids)).all()
            return [
                {
                    'id': s.id,
                    'name': s.name,
                    'roi': s.projected_salary_increase,
                    'skills': json.loads(s.skill_tags) if s.skill_tags else []
                } for s in next_schemes
            ]
        except:
            return []
    
    def _check_eligibility(self, user: User, scheme: Scheme) -> Tuple[bool, Optional[str]]:
        """
        Check hard and soft eligibility criteria.
        Returns (is_eligible, failure_reason)
        """
        # --- HARD CRITERIA ---
        
        # 1. State Check
        if scheme.state and scheme.state.lower() != 'central':
            # If user hasn't provided state, we allow it for broad discovery
            if user.state and scheme.state.strip().lower() != user.state.strip().lower():
                return False, None
        
        # 2. Gender Check
        if scheme.gender_specific and scheme.gender_specific.lower() != 'all':
            if user.gender:
                scheme_gender = scheme.gender_specific.strip().lower()
                user_gender = user.gender.strip().lower()
                # Handle cases like "Female", "Women", "Girl"
                women_synonyms = ['female', 'women', 'woman', 'girl']
                men_synonyms = ['male', 'men', 'man', 'boy']
                
                is_match = False
                if scheme_gender in women_synonyms and user_gender in women_synonyms:
                    is_match = True
                elif scheme_gender in men_synonyms and user_gender in men_synonyms:
                    is_match = True
                elif scheme_gender == user_gender:
                    is_match = True
                
                if not is_match:
                    return False, None
                
        # 3. Category Check (SC/ST/OBC/General)
        if scheme.category_specific:
            if user.category:
                scheme_cats = [c.strip().lower() for c in scheme.category_specific.replace('/', ',').split(',')]
                user_cat = user.category.strip().lower()
                
                # If scheme is for everyone or contains 'general' or 'all'
                if 'all' in scheme_cats or 'any' in scheme_cats:
                    pass
                elif user_cat not in scheme_cats:
                    # Special check: If user is General but scheme is reserved
                    return False, None

        # 4. Occupation Check
        if scheme.occupation_specific:
            if user.occupation:
                scheme_occs = [o.strip().lower() for o in scheme.occupation_specific.replace('/', ',').split(',')]
                user_occ = user.occupation.strip().lower()
                
                if 'all' not in scheme_occs and 'any' not in scheme_occs:
                    match_found = False
                    for occ in scheme_occs:
                        # Simple fuzzy matching: "farmer" matches "agri/farmer"
                        if user_occ in occ or occ in user_occ:
                            match_found = True
                            break
                    
                    if not match_found:
                        return False, None

        # Soft exclusions (Age, Income) - Can be "Almost"
        gap_reason = None
        failures = 0
        
        # Age Check
        if user.age:
            if scheme.min_age and user.age < scheme.min_age:
                if (scheme.min_age - user.age) <= 2: # Within 2 years
                    gap_reason = f"You will be eligible in {scheme.min_age - user.age} years"
                    failures += 1
                else:
                    return False, None
            elif scheme.max_age and user.age > scheme.max_age:
                if (user.age - scheme.max_age) <= 2: # Missed by 2 years
                    gap_reason = f"You exceeded the age limit by {user.age - scheme.max_age} years"
                    failures += 1
                else:
                    return False, None

        # Dependency Check (Patent Claim: Scheme Dependency Analysis)
        if scheme.prerequisites:
            try:
                prereqs = json.loads(scheme.prerequisites)
                if prereqs and isinstance(prereqs, list):
                    # Check if user has applied to all prereqs
                    for pid in prereqs:
                        # Find if user has applied to this scheme ID
                        has_applied = UserScheme.query.filter_by(
                            user_id=user.id, 
                            scheme_id=int(pid)
                        ).filter(UserScheme.applied_at.isnot(None)).first()
                        
                        if not has_applied:
                            # Fetch name for better error message
                            p_scheme = Scheme.query.get(int(pid))
                            p_name = p_scheme.name if p_scheme else f"ID {pid}"
                            return False, f"Prerequisite not met: Must apply to '{p_name}' first"
                            
            except Exception as e:
                print(f"Dependency check failed: {e}")
                # Fail safe? or Fail closed? Let's ignore error for now but log it
                pass

        # Income Check
        if user.income:
            if scheme.max_income and user.income > scheme.max_income:
                diff = user.income - scheme.max_income
                if diff <= (scheme.max_income * 0.3): # Within 30%
                    gap_reason = f"Income is ₹{diff} above the limit"
                    failures += 1
                else:
                    return False, None
        
        if failures == 0:
            return True, None
        elif failures == 1:
            return False, gap_reason
        else:
            return False, None # Too many failures
            
    def _filter_by_criteria(self, user: User, schemes: List[Scheme]) -> List[Scheme]:
        """Legacy wrapper for compatibility if needed"""
        return [s for s in schemes if self._check_eligibility(user, s)[0]]
