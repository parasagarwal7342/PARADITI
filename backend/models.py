"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
from datetime import datetime, timezone
from backend.database import db

def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    """User model for storing user information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    income = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(50), nullable=True)  # General, SC, ST, OBC, etc.
    occupation = db.Column(db.String(100), nullable=True)
    
    # Claim P: Agent Network Identifier
    agent_id = db.Column(db.String(50), nullable=True, unique=True)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    
    # Relationship with user_schemes
    viewed_schemes = db.relationship('UserScheme', backref='user', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='user', lazy=True, cascade='all, delete-orphan')
    
    @property
    def beneficiary_score(self):
        """
        PATENT CLAIM: Universal Beneficiary Score (UBS).
        Quantifies eligibility readiness based on profile data and verified docs.
        """
        score = 0
        from backend.models import Document
        
        # Profile Completeness (Max 50)
        profile_fields = ['age', 'gender', 'state', 'income', 'category', 'occupation']
        completed = sum(1 for f in profile_fields if getattr(self, f))
        score += (completed / len(profile_fields)) * 50
        
        # Document Verification (Max 50)
        docs = Document.query.filter_by(user_id=self.id).all()
        doc_types = {d.document_type.lower() for d in docs}
        
        if 'aadhaar' in doc_types: score += 20
        if 'pan' in doc_types: score += 10
        if 'income' in doc_types: score += 10
        if 'caste' in doc_types: score += 10
        
        return int(min(100, score))

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'state': self.state,
            'income': self.income,
            'category': self.category,
            'occupation': self.occupation,
            'beneficiary_score': self.beneficiary_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class Scheme(db.Model):
    """Government scheme model"""
    __tablename__ = 'schemes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    ministry = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)  # Education, Health, Agriculture, etc.
    state = db.Column(db.String(50), nullable=True)  # 'Central' for central schemes, state name for state schemes
    eligibility_criteria = db.Column(db.Text, nullable=True)
    prerequisites = db.Column(db.Text, nullable=True)  # JSON list of scheme_ids that must be applied to first
    benefits = db.Column(db.Text, nullable=True)
    documents_required = db.Column(db.Text, nullable=True)
    official_link = db.Column(db.String(500), nullable=True)
    min_age = db.Column(db.Integer, nullable=True)
    max_age = db.Column(db.Integer, nullable=True)
    min_income = db.Column(db.Float, nullable=True)
    max_income = db.Column(db.Float, nullable=True)
    gender_specific = db.Column(db.String(20), nullable=True)  # 'Male', 'Female', 'All'
    category_specific = db.Column(db.String(100), nullable=True)  # 'SC', 'ST', 'OBC', 'General', etc.
    occupation_specific = db.Column(db.String(200), nullable=True)
    occupation_specific = db.Column(db.String(200), nullable=True)
    external_id = db.Column(db.String(100), nullable=True, index=True)  # API Setu or external source ID
    source = db.Column(db.String(50), default='local')  # 'local' | 'api_setu'
    link_health_score = db.Column(db.Integer, default=100) # 0-100, patent claim for "Probabilistic Availability"
    
    # Welfare-to-Employment Bridge (Claim M & N)
    graduation_path = db.Column(db.Text, nullable=True) # JSON list of next-step scheme IDs
    projected_salary_increase = db.Column(db.Float, default=0.0) # ROI Metric
    skill_tags = db.Column(db.String(500), nullable=True) # JSON list of skills (e.g. ["Digital Literacy", "Agri-Tech"])
    
    created_at = db.Column(db.DateTime, default=utc_now)
    
    # Relationship with user_schemes
    user_views = db.relationship('UserScheme', backref='scheme', lazy=True, cascade='all, delete-orphan')
    
    # Relationship with user_schemes
    user_views = db.relationship('UserScheme', backref='scheme', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert scheme object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'ministry': self.ministry,
            'description': self.description,
            'category': self.category,
            'state': self.state,
            'eligibility_criteria': self.eligibility_criteria,
            'prerequisites': self.prerequisites,
            'benefits': self.benefits,
            'documents_required': self.documents_required,
            'official_link': self.official_link,
            'min_age': self.min_age,
            'max_age': self.max_age,
            'min_income': self.min_income,
            'max_income': self.max_income,
            'gender_specific': self.gender_specific,
            'category_specific': self.category_specific,
            'occupation_specific': self.occupation_specific,
            'external_id': self.external_id,
            'link_health_score': self.link_health_score,
            'graduation_path': self.graduation_path,
            'projected_salary_increase': self.projected_salary_increase,
            'skill_tags': self.skill_tags,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Scheme {self.name}>'

class UserScheme(db.Model):
    """Track user interactions with schemes"""
    __tablename__ = 'user_schemes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheme_id = db.Column(db.Integer, db.ForeignKey('schemes.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=utc_now)
    applied_at = db.Column(db.DateTime, nullable=True)
    interest_score = db.Column(db.Float, nullable=True)  # ML similarity score
    
    # Unique constraint to prevent duplicate entries
    __table_args__ = (db.UniqueConstraint('user_id', 'scheme_id', name='unique_user_scheme'),)
    
    def to_dict(self):
        """Convert user_scheme object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scheme_id': self.scheme_id,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'interest_score': self.interest_score
        }
    
    def __repr__(self):
        return f'<UserScheme user_id={self.user_id} scheme_id={self.scheme_id}>'

class Document(db.Model):
    """User uploaded documents"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # Aadhaar, PAN, Income, etc.
    category = db.Column(db.String(50), nullable=True) # Identity, Income, Address, etc.
    
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    
    # Size & Compression
    file_size = db.Column(db.Integer, nullable=True) # Current Size (Optimized)
    original_size = db.Column(db.Integer, nullable=True) # Original upload size
    mime_type = db.Column(db.String(100), nullable=True) # e.g. 'image/jpeg'
    
    # Intelligence
    extracted_data = db.Column(db.Text, nullable=True)  # JSON string of extracted fields
    expiry_date = db.Column(db.DateTime, nullable=True) # For alerts
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, processed, failed
    is_verified = db.Column(db.Boolean, default=False) # AI or Manual verification
    
    created_at = db.Column(db.DateTime, default=utc_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_type': self.document_type,
            'category': self.category,
            'filename': self.filename,
            'file_size': self.file_size,
            'original_size': self.original_size,
            'status': self.status,
            'is_verified': self.is_verified,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Application(db.Model):
    """
    Tracks the full lifecycle of a scheme application.
    Supports the 'One-Click Apply' feature.
    """
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scheme_id = db.Column(db.Integer, db.ForeignKey('schemes.id'), nullable=False)
    status = db.Column(db.String(50), default='draft') # draft, processing, submitted, approved, rejected
    submission_data = db.Column(db.Text, nullable=True) # JSON payload sent to scheme portal
    submitted_at = db.Column(db.DateTime, nullable=True)
    
    # Application Success Guarantee (Claim K & L)
    approval_confidence = db.Column(db.Float, default=0.0) # 0-100 percentage
    rejection_reasons = db.Column(db.Text, nullable=True) # JSON list of detected risks
    appeal_letter_draft = db.Column(db.Text, nullable=True) # AI Generated Appeal
    appeal_status = db.Column(db.String(50), default='none') # none, drafted, filed, won, lost
    
    created_at = db.Column(db.DateTime, default=utc_now)
    
    # Validation results
    validation_status = db.Column(db.String(20), default='pending') # valid, invalid
    missing_fields = db.Column(db.Text, nullable=True) # JSON list of missing requirements
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scheme_id': self.scheme_id,
            'status': self.status,
            'submission_data': self.submission_data,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'validation_status': self.validation_status,
            'approval_confidence': self.approval_confidence,
            'rejection_reasons': self.rejection_reasons,
            'appeal_letter_draft': self.appeal_letter_draft,
            'appeal_status': self.appeal_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
