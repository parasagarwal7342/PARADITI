"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
import os
import numpy as np
from backend.config import Config
from backend.models import Scheme, User
from backend.ml.scheme_matcher import SchemeMatcher

# Optional: use TF-IDF only (set USE_TFIDF=1 to skip sentence-transformers)
USE_TFIDF = os.getenv("USE_TFIDF", "").strip().lower() in ("1", "true", "yes")

try:
    from sentence_transformers import SentenceTransformer
    _HAS_SENTENCE_TRANSFORMERS = True
except Exception:
    _HAS_SENTENCE_TRANSFORMERS = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    pass



class MLRecommendationEngine:
    """ML Engine for recommending government schemes (transformer or TF-IDF)."""
    
    def __init__(self):
        """Initialize the ML model (transformer or TF-IDF fallback)."""
        self.model = None
        self.use_tfidf = USE_TFIDF or not _HAS_SENTENCE_TRANSFORMERS
        self.model_name = Config.ML_MODEL_NAME
        self.similarity_threshold = Config.SIMILARITY_THRESHOLD
        self._vectorizer = None
        self._load_model()
        self.matcher = SchemeMatcher(self)
    
    def _load_model(self):
        """Load sentence transformer or TF-IDF fallback."""
        if self.use_tfidf:
            self._vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")
            print("ML engine: using TF-IDF fallback (no heavy model download).")
            return
        try:
            print(f"Loading ML model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print("ML model loaded successfully!")
        except Exception as e:
            print(f"Sentence transformer failed: {e}. Using TF-IDF fallback.")
            self.use_tfidf = True
            self._vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")
    
    def _create_user_profile_text(self, user):
        """
        Create a text representation of user profile for embedding
        
        Args:
            user (User): User object
            
        Returns:
            str: User profile text
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
        
        # If profile is empty, return a generic profile to still get recommendations
        if not profile_parts:
            return "General user seeking government schemes and benefits"
        
        return ". ".join(profile_parts)
    
    def _create_scheme_text(self, scheme):
        """
        Create a text representation of scheme for embedding
        
        Args:
            scheme (Scheme): Scheme object
            
        Returns:
            str: Scheme text
        """
        scheme_parts = []
        
        scheme_parts.append(f"Scheme: {scheme.name}")
        scheme_parts.append(f"Description: {scheme.description}")
        
        if scheme.ministry:
            scheme_parts.append(f"Ministry: {scheme.ministry}")
        if scheme.state:
            scheme_parts.append(f"State: {scheme.state}")
        
        return ". ".join(scheme_parts)
    
    def _calculate_similarity(self, emb1, emb2):
        """Calculate cosine similarity between two embeddings."""
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    def recommend_schemes(self, user, limit=10):
        """
        Recommend schemes for a user based on ML similarity (transformer or TF-IDF).
        Delegates to SchemeMatcher for advanced filtering and gap analysis.
        """
        if not self.use_tfidf and not self.model:
            raise Exception("ML model not loaded")
        
        all_schemes = Scheme.query.all()
        if not all_schemes:
            return {'eligible': [], 'almost_eligible': []}
            
        # Use SchemeMatcher logic
        return self.matcher.match_schemes(user, all_schemes, limit=limit)
    
    def get_scheme_similarity(self, user, scheme):
        """Get similarity score for a specific scheme."""
        if self.use_tfidf:
            texts = [self._create_user_profile_text(user), self._create_scheme_text(scheme)]
            X = self._vectorizer.fit_transform(texts)
            return float(cosine_similarity(X[0:1], X[1:2])[0][0])
        if not self.model:
            return 0.0
        user_embedding = self.model.encode(self._create_user_profile_text(user), convert_to_numpy=True)
        scheme_embedding = self.model.encode(self._create_scheme_text(scheme), convert_to_numpy=True)
        return self._calculate_similarity(user_embedding, scheme_embedding)

    def get_scheme_to_scheme_similarity(self, scheme1, scheme2):
        """Get similarity score between two schemes."""
        if self.use_tfidf:
            texts = [self._create_scheme_text(scheme1), self._create_scheme_text(scheme2)]
            X = self._vectorizer.fit_transform(texts)
            return float(cosine_similarity(X[0:1], X[1:2])[0][0])
        if not self.model:
            return 0.0
        emb1 = self.model.encode(self._create_scheme_text(scheme1), convert_to_numpy=True)
        emb2 = self.model.encode(self._create_scheme_text(scheme2), convert_to_numpy=True)
        return self._calculate_similarity(emb1, emb2)

# Global ML engine instance
ml_engine = None

def get_ml_engine():
    """Get or create ML engine instance"""
    global ml_engine
    if not ml_engine:
        ml_engine = MLRecommendationEngine()
    return ml_engine
