"""
Data Processing Utilities
Handles preprocessing and transformation of user and scheme data
"""
from typing import Dict, Any, Optional
from backend.models import User, Scheme


class DataProcessor:
    """Handles data preprocessing for ML models"""
    
    @staticmethod
    def create_user_profile_text(user: User) -> str:
        """
        Create a text representation of user profile for embedding
        
        Args:
            user: User object
            
        Returns:
            User profile text string
        """
        profile_parts = []
        
        if user.name:
            profile_parts.append(f"Name: {user.name}")
        if user.age:
            profile_parts.append(f"Age: {user.age} years")
        if user.gender:
            profile_parts.append(f"Gender: {user.gender}")
        if user.state:
            profile_parts.append(f"State: {user.state}")
        if user.income:
            profile_parts.append(f"Income: Rs. {user.income} per month")
        if user.category:
            profile_parts.append(f"Category: {user.category}")
        if user.occupation:
            profile_parts.append(f"Occupation: {user.occupation}")
        
        return ". ".join(profile_parts) if profile_parts else "User profile"
    
    @staticmethod
    def create_scheme_text(scheme: Scheme) -> str:
        """
        Create a text representation of scheme for embedding
        
        Args:
            scheme: Scheme object
            
        Returns:
            Scheme text string
        """
        scheme_parts = []
        
        scheme_parts.append(f"Scheme: {scheme.name}")
        scheme_parts.append(f"Description: {scheme.description}")
        
        if scheme.category:
            scheme_parts.append(f"Category: {scheme.category}")
        if scheme.state:
            scheme_parts.append(f"Applicable in: {scheme.state}")
        if scheme.eligibility_criteria:
            scheme_parts.append(f"Eligibility: {scheme.eligibility_criteria}")
        if scheme.benefits:
            scheme_parts.append(f"Benefits: {scheme.benefits}")
        if scheme.category_specific:
            scheme_parts.append(f"For category: {scheme.category_specific}")
        if scheme.occupation_specific:
            scheme_parts.append(f"For occupation: {scheme.occupation_specific}")
        if scheme.gender_specific:
            scheme_parts.append(f"For gender: {scheme.gender_specific}")
        
        return ". ".join(scheme_parts)
    
    @staticmethod
    def normalize_user_data(user: User) -> Dict[str, Any]:
        """
        Normalize user data for processing
        
        Args:
            user: User object
            
        Returns:
            Normalized user data dictionary
        """
        return {
            'id': user.id,
            'name': user.name or '',
            'age': user.age or 0,
            'gender': user.gender or '',
            'state': user.state or '',
            'income': user.income or 0,
            'category': user.category or '',
            'occupation': user.occupation or ''
        }
    
    @staticmethod
    def normalize_scheme_data(scheme: Scheme) -> Dict[str, Any]:
        """
        Normalize scheme data for processing
        
        Args:
            scheme: Scheme object
            
        Returns:
            Normalized scheme data dictionary
        """
        return {
            'id': scheme.id,
            'name': scheme.name or '',
            'description': scheme.description or '',
            'category': scheme.category or '',
            'state': scheme.state or 'Central',
            'eligibility_criteria': scheme.eligibility_criteria or '',
            'benefits': scheme.benefits or '',
            'min_age': scheme.min_age,
            'max_age': scheme.max_age,
            'min_income': scheme.min_income,
            'max_income': scheme.max_income,
            'gender_specific': scheme.gender_specific or 'All',
            'category_specific': scheme.category_specific or '',
            'occupation_specific': scheme.occupation_specific or ''
        }
    
    @staticmethod
    def extract_keywords(text: str) -> list:
        """
        Extract keywords from text (simple implementation)
        
        Args:
            text: Input text
            
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return list(set(keywords))  # Remove duplicates
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """
        Calculate simple text similarity based on common words
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        keywords1 = set(DataProcessor.extract_keywords(text1))
        keywords2 = set(DataProcessor.extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    @staticmethod
    def validate_user_profile(user: User) -> tuple:
        """
        Validate user profile completeness
        
        Args:
            user: User object
            
        Returns:
            Tuple of (is_valid, list_of_missing_fields)
        """
        missing_fields = []
        
        if not user.name:
            missing_fields.append('name')
        if not user.email:
            missing_fields.append('email')
        if not user.age:
            missing_fields.append('age')
        if not user.state:
            missing_fields.append('state')
        
        return len(missing_fields) == 0, missing_fields
    
    @staticmethod
    def enrich_scheme_data(scheme: Scheme) -> Dict[str, Any]:
        """
        Enrich scheme data with computed fields
        
        Args:
            scheme: Scheme object
            
        Returns:
            Enriched scheme data
        """
        data = DataProcessor.normalize_scheme_data(scheme)
        
        # Add computed fields
        data['is_central'] = scheme.state == 'Central' or scheme.state is None
        data['has_age_limit'] = scheme.min_age is not None or scheme.max_age is not None
        data['has_income_limit'] = scheme.min_income is not None or scheme.max_income is not None
        data['is_gender_specific'] = scheme.gender_specific and scheme.gender_specific != 'All'
        data['is_category_specific'] = bool(scheme.category_specific)
        data['is_occupation_specific'] = bool(scheme.occupation_specific)
        
        # Calculate eligibility complexity (higher = more restrictive)
        complexity = 0
        if data['has_age_limit']:
            complexity += 1
        if data['has_income_limit']:
            complexity += 1
        if data['is_gender_specific']:
            complexity += 1
        if data['is_category_specific']:
            complexity += 1
        if data['is_occupation_specific']:
            complexity += 1
        
        data['eligibility_complexity'] = complexity
        
        return data
