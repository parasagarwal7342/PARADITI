import pytest
from unittest.mock import MagicMock
from backend.ml_engine import MLRecommendationEngine

from unittest.mock import MagicMock, patch
from sklearn.feature_extraction.text import TfidfVectorizer

class MockScheme:
    def __init__(self, id, name, description, category="", state="", eligibility_criteria="", benefits="", category_specific="", occupation_specific="", gender_specific="", min_age=None, max_age=None, min_income=None, max_income=None):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.state = state
        self.eligibility_criteria = eligibility_criteria
        self.benefits = benefits
        self.category_specific = category_specific
        self.occupation_specific = occupation_specific
        self.gender_specific = gender_specific
        self.min_age = min_age
        self.max_age = max_age
        self.min_income = min_income
        self.max_income = max_income

class MockUser:
    def __init__(self, name="Test User", age=25, gender="Male", state="Maharashtra", income=50000, category="General", occupation="Farmer"):
        self.name = name
        self.age = age
        self.gender = gender
        self.state = state
        self.income = income
        self.category = category
        self.occupation = occupation

@pytest.fixture
def ml_engine():
    # Initialize engine (might load transformer if installed)
    engine = MLRecommendationEngine()
    
    # Force switch to TF-IDF for consistent testing logic
    engine.use_tfidf = True
    engine.model = None
    engine._vectorizer = TfidfVectorizer(stop_words="english")
    
    return engine

def test_profile_text_generation(ml_engine):
    user = MockUser(name="Rahul", age=30, gender="Male")
    text = ml_engine._create_user_profile_text(user)
    assert "Name: Rahul" in text
    assert "Age: 30 years" in text
    assert "Gender: Male" in text

def test_scheme_text_generation(ml_engine):
    scheme = MockScheme(1, "PM Kisan", "Financial support for farmers", "Agriculture")
    text = ml_engine._create_scheme_text(scheme)
    assert "Scheme: PM Kisan" in text
    assert "Description: Financial support for farmers" in text
    assert "Category: Agriculture" in text

def test_recommendation_ranking(ml_engine):
    # Create user with specific profile to match Farmer scheme
    user = MockUser(occupation="Farmer", name="", age=None, gender="", state="", income=None, category="")
    schemes = [
        MockScheme(1, "Health Scheme", "Insurance for all citizens", "Health"),
        MockScheme(2, "Farmer Subsidy", "Direct benefit for farmers and agricultural workers", "Agriculture"),
        MockScheme(3, "Education Grant", "Scholarship for students", "Education")
    ]
    
    # Patch Scheme in backend.ml_engine, not backend.models
    with patch('backend.ml_engine.Scheme') as MockSchemeModel:
        MockSchemeModel.query.all.return_value = schemes
        
        # Fit vectorizer manually since we bypassed init
        # We need to ensure the vocabulary covers our terms
        user_text = ml_engine._create_user_profile_text(user)
        scheme_texts = [ml_engine._create_scheme_text(s) for s in schemes]
        print(f"User text: {user_text}")
        for i, st in enumerate(scheme_texts):
            print(f"Scheme {i+1} text: {st}")
            
        ml_engine._vectorizer.fit(scheme_texts + [user_text])
        
        recommendations = ml_engine.recommend_schemes(user)
        
        assert len(recommendations) > 0
        # The farmer-related scheme should be ranked highest due to keyword matching
        # recommendations is a list of (scheme, score) tuples
        top_scheme = recommendations[0][0]
        
        # Print for debugging if needed (will show in pytest output on failure)
        for s, score in recommendations:
            print(f"Scheme: {s.name}, Score: {score}")
        
        assert top_scheme.id == 2
        assert recommendations[0][1] > 0
