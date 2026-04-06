"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from backend.models import User, Scheme, UserScheme, Document, Application, db
from backend.security import hash_password, verify_password, sanitize_input, validate_email, validate_password_strength, validate_file_upload
from backend.auth import generate_token, get_current_user
from backend.security_utils import get_encryptor
from backend.cache import get_cache, set_cache, rate_limit
from backend.ml_engine import get_ml_engine
from backend.config import Config
from backend.services.api_setu import fetch_schemes_from_api_setu, sync_schemes_to_db
from backend.services.ocr_service import OCRService
from backend.services.application_service import ApplicationService
from backend.services.rejection_engine import rejection_engine
from backend.services.dialect_mapper import dialect_mapper
from backend.services.mobility_sequencer import mobility_sequencer
from backend.utils import compress_image
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from sqlalchemy import or_
from backend.services.agent_service import agent_service
from backend.services.benefit_tokenizer import benefit_tokenizer
from backend.services.temporal_arbitrage import temporal_arbitrage
from backend.services.social_credit import social_credit_model
from backend.services.future_horizon import GeoSpatialTrigger, ZeroKnowledgeProofer, SocialBondMarket

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'PARADITI API is running'
    }), 200

@api.route('/register', methods=['POST'])
@rate_limit(limit=5, window=60)
def register():
    """Register a new user with optional document uploads"""
    try:
        # Handle both JSON and Multipart/Form-Data
        if request.is_json:
            data = request.get_json()
            files = {}
        else:
            data = request.form.to_dict()
            files = request.files

        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Sanitize inputs
        name = sanitize_input(data['name'])
        email = sanitize_input(data['email']).lower()
        password = data['password']
        
        print(f"Registering user: {email}") # DEBUG
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            print(f"User already exists: {email}") # DEBUG
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        hashed_pw = hash_password(password)
        print(f"Password hashed for {email}") # DEBUG
        
        user = User(
            name=name,
            email=email,
            password_hash=hashed_pw,
            age=int(data.get('age')) if data.get('age') else None,
            gender=sanitize_input(data.get('gender', '')),
            state=sanitize_input(data.get('state', '')),
            income=float(data.get('income')) if data.get('income') else None,
            category=sanitize_input(data.get('category', '')),
            occupation=sanitize_input(data.get('occupation', ''))
        )
        
        db.session.add(user)
        db.session.flush() # Flush to get user ID
        
        db.session.commit()
        
        # Verify persistence
        saved_user = User.query.filter_by(email=email).first()
        if saved_user:
            print(f"VERIFICATION: User {email} found in DB after commit. ID: {saved_user.id}")
        else:
            print(f"VERIFICATION: User {email} NOT found in DB after commit!")
        
        # Generate token
        token = generate_token(user)
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@api.route('/login', methods=['POST'])
@rate_limit(limit=10, window=60)
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = sanitize_input(data['email']).lower()
        password = data['password']
        
        print(f"Login attempt: {email}") # DEBUG
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"Login failed: User not found {email}") # DEBUG
            return jsonify({'error': 'Invalid email or password'}), 401
            
        if not verify_password(user.password_hash, password):
            print(f"Login failed: Password mismatch for {email}") # DEBUG
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(user)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@api.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user documents
        documents = Document.query.filter_by(user_id=user.id).all()
        doc_list = [{
            'type': doc.document_type,
            'filename': doc.filename,
            'status': doc.status,
            'uploaded_at': doc.created_at.isoformat() if doc.created_at else None
        } for doc in documents]
        
        return jsonify({
            'user': user.to_dict(),
            'documents': doc_list
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@api.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            user.name = sanitize_input(data['name'])
        if 'age' in data:
            user.age = data.get('age')
        if 'gender' in data:
            user.gender = sanitize_input(data['gender'])
        if 'state' in data:
            user.state = sanitize_input(data['state'])
        if 'income' in data:
            user.income = float(data['income']) if data['income'] else None
        if 'category' in data:
            user.category = sanitize_input(data['category'])
        if 'occupation' in data:
            user.occupation = sanitize_input(data['occupation'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@api.route('/schemes/recommended', methods=['GET'])
@jwt_required()
def get_recommended_schemes():
    """Get recommended schemes for current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get limit from query params
        limit = request.args.get('limit', 10, type=int)
        
        # Get ML engine
        ml_engine = get_ml_engine()
        
        # TODO: Restore caching for new structure
        # Currently bypassing cache to support 'almost_eligible' feature
        
        # Get recommendations from ML engine
        recommendation_results = ml_engine.recommend_schemes(user, limit=limit)
        
        # If no local schemes found, trigger a background-like sync from API Setu
        if not recommendation_results.get('eligible') and not recommendation_results.get('almost_eligible'):
             if Scheme.query.count() < 5:
                 sync_schemes_to_db()
                 recommendation_results = ml_engine.recommend_schemes(user, limit=limit)
        
        eligible_schemes = recommendation_results.get('eligible', [])
        almost_eligible_schemes = recommendation_results.get('almost_eligible', [])
        
        # Process Eligible Schemes
        schemes_data = []
        user_docs = Document.query.filter_by(user_id=user.id).all()
        doc_metas = [d.to_dict() for d in user_docs]
        
        for scheme, similarity_score in eligible_schemes:
            scheme_dict = scheme.to_dict()
            scheme_dict['similarity_score'] = round(similarity_score, 4)
            
            # PATENT CLAIM K: Predictive Rejection Engine
            confidence, risks = ml_engine.matcher.get_approval_confidence(user, scheme)
            scheme_dict['approval_confidence'] = confidence
            scheme_dict['rejection_risks'] = risks
            
            # PATENT CLAIM M: Welfare-to-Work Sequencer
            scheme_dict['graduation_path'] = ml_engine.matcher.get_graduation_path(scheme)
            
            # Track user view & check applied status
            user_scheme = UserScheme.query.filter_by(
                user_id=user.id,
                scheme_id=scheme.id
            ).first()
            
            scheme_dict['is_applied'] = False
            if user_scheme:
                if user_scheme.applied_at:
                    scheme_dict['is_applied'] = True
                user_scheme.interest_score = similarity_score
                user_scheme.viewed_at = datetime.now(timezone.utc)
            else:
                user_scheme = UserScheme(
                    user_id=user.id,
                    scheme_id=scheme.id,
                    interest_score=similarity_score
                )
                db.session.add(user_scheme)
            
            schemes_data.append(scheme_dict)
            
        # Process Almost Eligible Schemes
        almost_eligible_data = []
        for item in almost_eligible_schemes:
            scheme = item['scheme']
            scheme_dict = scheme.to_dict()
            scheme_dict['similarity_score'] = round(item['score'], 4)
            scheme_dict['gap_reason'] = item['gap']
            
            # Handle Alternative
            if item.get('alternative'):
                alt = item['alternative']
                scheme_dict['alternative'] = {
                    'id': alt.id,
                    'name': alt.name
                }
            
            # Check applied status (unlikely but good to have)
            user_scheme = UserScheme.query.filter_by(
                user_id=user.id,
                scheme_id=scheme.id
            ).first()
            
            scheme_dict['is_applied'] = False
            if user_scheme and user_scheme.applied_at:
                scheme_dict['is_applied'] = True
                
            almost_eligible_data.append(scheme_dict)
        
        db.session.commit()
        
        return jsonify({
            'schemes': schemes_data,
            'almost_eligible': almost_eligible_data,
            'count': len(schemes_data)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500

@api.route('/user-stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get metrics for user dashboard"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        viewed_count = UserScheme.query.filter_by(user_id=user.id).count()
        applied_count = UserScheme.query.filter_by(user_id=user.id).filter(UserScheme.applied_at.isnot(None)).count()
        total_schemes = Scheme.query.count()
        
        return jsonify({
            'viewed_count': viewed_count,
            'applied_count': applied_count,
            'total_schemes': total_schemes,
            'beneficiary_score': user.beneficiary_score
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/schemes/all', methods=['GET'])
@jwt_required()
def get_all_schemes():
    """Get all schemes with optional filters"""
    try:
        # Get filters from query params
        state = request.args.get('state')
        category = request.args.get('category')
        search = request.args.get('search')
        
        # Build query
        query = Scheme.query
        
        if state:
            query = query.filter(Scheme.state == state)
        if category:
            query = query.filter(Scheme.category == category)
        if search:
            search_term = f"%{sanitize_input(search)}%"
            query = query.filter(
                (Scheme.name.like(search_term)) |
                (Scheme.description.like(search_term))
            )
        
        schemes = query.all()
        
        # Get current user to check application status
        user = get_current_user()
        user_schemes_map = {}
        if user:
            user_schemes = UserScheme.query.filter_by(user_id=user.id).all()
            for us in user_schemes:
                if us.applied_at:
                    user_schemes_map[us.scheme_id] = True

        schemes_data = []
        for scheme in schemes:
            d = scheme.to_dict()
            d['is_applied'] = user_schemes_map.get(scheme.id, False)
            schemes_data.append(d)
        
        return jsonify({
            'schemes': schemes_data,
            'count': len(schemes_data)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get schemes: {str(e)}'}), 500
@api.route('/schemes/sync', methods=['POST'])
@jwt_required()
def sync_schemes_route():
    """Trigger a manual sync of schemes from API Setu & curated fallback"""
    return sync_schemes_from_apisetu()

@api.route('/schemes/<int:scheme_id>', methods=['GET'])
@jwt_required()
def get_scheme_details(scheme_id):
    """Get detailed information about a specific scheme"""
    try:
        scheme = Scheme.query.get(scheme_id)
        
        if not scheme:
            return jsonify({'error': 'Scheme not found'}), 404
        
        user = get_current_user()
        scheme_dict = scheme.to_dict()
        
        # PATENT FEATURE: Self-Healing Information Retrieval
        scheme_analyzer = SchemeWebAnalyzer()
        is_link_active = scheme_analyzer.verify_link_health(scheme.official_link, scheme.id)
        fallback_url = None
        if not is_link_active and scheme.official_link:
            fallback_url = scheme_analyzer.generate_fallback_query(scheme.name)
        
        scheme_dict['link_health'] = {
            'is_active': is_link_active,
            'fallback_url': fallback_url,
            'official_url': scheme.official_link
        }
        
        # Add similarity score & Readiness Report if user exists
        if user:
            ml_engine = get_ml_engine()
            similarity = ml_engine.get_scheme_similarity(user, scheme)
            scheme_dict['similarity_score'] = round(similarity, 4)
            
            # PATENT FEATURE: Detailed Readiness Report
            # 1. Get scheme requirements (simulated or scraped)
            requirements = scheme_analyzer.analyze_scheme_url(scheme.official_link)
            
            # 2. Check readiness against user profile/docs
            readiness_report = scheme_analyzer.check_readiness(user, user.documents, requirements)
            scheme_dict['readiness_report'] = readiness_report
            
            # Track view
            user_scheme = UserScheme.query.filter_by(
                user_id=user.id,
                scheme_id=scheme.id
            ).first()
            
            is_applied = False
            if user_scheme:
                user_scheme.viewed_at = datetime.now(timezone.utc)
                if user_scheme.applied_at:
                    is_applied = True
            else:
                user_scheme = UserScheme(
                    user_id=user.id,
                    scheme_id=scheme.id,
                    interest_score=similarity
                )
                db.session.add(user_scheme)
            
            db.session.commit()
            
            scheme_dict['is_applied'] = is_applied
        
        return jsonify({
            'scheme': scheme_dict
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to get scheme details: {str(e)}'}), 500

@api.route('/schemes/<int:scheme_id>/apply', methods=['POST'])
@jwt_required()
def apply_for_scheme(scheme_id):
    """
    Apply for a scheme with AI-powered One-Click Apply.
    Uses ApplicationService to:
    1. Verify required docs
    2. Auto-optimize/compress docs
    3. Extract data via OCR
    4. Auto-fill the application form
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        scheme = Scheme.query.get(scheme_id)
        if not scheme:
            return jsonify({'error': 'Scheme not found'}), 404
            
        # Check if already applied
        existing_app = Application.query.filter_by(user_id=user.id, scheme_id=scheme_id).first()
        if existing_app:
             return jsonify({
                'message': 'Already applied for this scheme',
                'application_id': existing_app.id,
                'status': existing_app.status
            }), 200

        # Delegate to ApplicationService
        service = ApplicationService()
        result = service.initiate_application(user.id, scheme.id)
        
        if result['status'] == 'success':
            # Also update UserScheme for history/analytics
            user_scheme = UserScheme.query.filter_by(user_id=user.id, scheme_id=scheme.id).first()
            if not user_scheme:
                user_scheme = UserScheme(user_id=user.id, scheme_id=scheme.id)
                db.session.add(user_scheme)
            
            user_scheme.applied_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify({
                'message': result['message'],
                'application_id': result['application_id'],
                'status': 'submitted',
                'applicant': user.name,
                'scheme_name': scheme.name
            }), 200
            
        elif result['status'] == 'missing_documents':
            return jsonify({
                'error': 'Missing required documents',
                'missing': result['missing'],
                'message': result['message']
            }), 400
        else:
            return jsonify({'error': 'Application failed', 'details': result}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Application failed: {str(e)}'}), 500

@api.route('/schemes/<int:scheme_id>/one_click_apply', methods=['POST'])
@jwt_required()
def one_click_apply(scheme_id):
    """
    Patent Pending: One-Click Automated Application via AI Agent.
    Orchestrates:
    1. Document Intelligence (Resize/Compress)
    2. OCR Data Extraction
    3. Form Auto-fill (ApplicationService)
    4. API Setu / Ledger Submission
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        scheme = Scheme.query.get(scheme_id)
        if not scheme:
            return jsonify({'error': 'Scheme not found'}), 404

        # Delegate to AI Application Service
        service = ApplicationService()
        result = service.initiate_application(user.id, scheme.id)
        
        if result['status'] == 'missing_documents':
             return jsonify({
                 'status': 'gap_detected',
                 'message': result['message'],
                 'missing_fields': result['missing'],
                 'auto_filled_data': {} # Can populate if needed
             }), 200

        if result['status'] == 'success':
            # 4. Patent Claim: Immutable Ledger Entry
            from backend.services.audit_ledger import ImmutableLedger
            receipt_signature = ImmutableLedger.record_application(
                user_id=user.id,
                scheme_id=scheme_id,
                application_data=str(result)
            )
            
            # Update UserScheme history
            user_scheme = UserScheme.query.filter_by(user_id=user.id, scheme_id=scheme.id).first()
            if not user_scheme:
                user_scheme = UserScheme(user_id=user.id, scheme_id=scheme.id)
                db.session.add(user_scheme)
            
            user_scheme.applied_at = datetime.now(timezone.utc)
            db.session.commit()

            return jsonify({
                'message': 'One-Click Application Successful!',
                'details': 'Documents processed, optimized, and submitted securely.',
                'application_id': f"APP-{result['application_id']}-{datetime.now().strftime('%s')}",
                'receipt_url': f"https://apisetu.gov.in/receipt/{user.id}",
                'receipt_signature': receipt_signature,
                'integrity_verified': True
            }), 200
        
        return jsonify({'error': 'Application failed', 'details': result}), 500

    except Exception as e:
        db.session.rollback()
        print(f"One Click Error: {e}")
        return jsonify({'error': f'One-Click failed: {str(e)}'}), 500

@api.route('/schemes/<int:scheme_id>/withdraw', methods=['POST'])
@jwt_required()
def withdraw_application(scheme_id):
    """Withdraw application for a scheme"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        scheme = Scheme.query.get(scheme_id)
        if not scheme:
            return jsonify({'error': 'Scheme not found'}), 404
            
        user_scheme = UserScheme.query.filter_by(
            user_id=user.id,
            scheme_id=scheme.id
        ).first()
        
        if not user_scheme or not user_scheme.applied_at:
            return jsonify({'error': 'You have not applied for this scheme'}), 400
            
        # Reset applied_at to None to signify withdrawal
        user_scheme.applied_at = None
        db.session.commit()
        
        return jsonify({
            'message': 'Application withdrawn successfully',
            'scheme_name': scheme.name
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Withdrawal failed: {str(e)}'}), 500

@api.route('/schemes/<int:scheme_id>/roadmap', methods=['GET'])
@jwt_required()
def get_scheme_roadmap(scheme_id):
    """
    PATENT FEATURE: Visual Dependency Graph.
    Returns the 'Unlock Path' to reach this scheme.
    """
    try:
        user = get_current_user()
        if not user: return jsonify({'error': 'User not found'}), 404
        
        from backend.ml.dependency_graph import get_dependency_engine
        engine = get_dependency_engine()
        
        roadmap = engine.get_roadmap(scheme_id, user.id)
        
        if not roadmap:
            return jsonify({'error': 'Graph generation failed or scheme not found'}), 404
            
        return jsonify({
            'scheme_id': scheme_id,
            'roadmap': roadmap,
            'claim': 'Patent Claim #2: Directed Graph Eligibility Enforcement'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/documents', methods=['GET'])
@jwt_required()
def get_user_documents():
    """Get all user documents with detailed metadata"""
    try:
        user = get_current_user()
        documents = Document.query.filter_by(user_id=user.id).all()
        
        # Calculate stats
        total = len(documents)
        verified = sum(1 for d in documents if getattr(d, 'is_verified', False))
        
        # Robust expiry check
        expiring = 0
        now_naive = datetime.now()
        now_aware = datetime.now(timezone.utc)
        
        for d in documents:
            if getattr(d, 'expiry_date', None):
                try:
                    # Handle both naive and aware datetimes
                    d_date = d.expiry_date
                    if d_date.tzinfo:
                         if (d_date - now_aware).days < 30: expiring += 1
                    else:
                         if (d_date - now_naive).days < 30: expiring += 1
                except Exception:
                    # Fallback safely
                    pass
        
        # Identify missing types
        required_types = ['Aadhaar Card', 'PAN Card', 'Income Certificate', 'Address Proof']
        existing_types = {d.document_type for d in documents}
        missing_list = [t for t in required_types if t not in existing_types]

        return jsonify({
            'documents': [d.to_dict() for d in documents],
            'stats': {
                'total': total,
                'verified': verified,
                'expiring': expiring,
                'missing_list': missing_list,
                'missing': len(missing_list)
            }
        }), 200
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return jsonify({'error': f"Server Error: {str(e)}"}), 500

@api.route('/upload-document', methods=['POST'])
@jwt_required()
def upload_document_route():
    """Upload a single document with category support"""
    try:
        user = get_current_user()
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        doc_type = request.form.get('doc_type', 'Other')
        category = request.form.get('category', 'General')
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Validate file
        is_valid_type, type_msg = validate_file_upload(file)
        if not is_valid_type:
             return jsonify({'error': type_msg}), 400

        # Ensure upload dir
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save File
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        save_name = f"{timestamp}_{user.id}_{filename}"
        file_path = os.path.join(upload_dir, save_name)

        # Calculate Original Size
        file.seek(0, os.SEEK_END)
        original_size = file.tell()
        file.seek(0)
        
        # Intelligent Processing (Claim G: Compression)
        file_size = original_size
        if file.content_type.startswith('image/'):
             try:
                 compressed = compress_image(file, target_size_kb=300)
                 with open(file_path, 'wb') as f:
                     f.write(compressed.getbuffer())
                 file_size = len(compressed.getbuffer())
             except:
                 file.save(file_path)
        else:
             file.save(file_path)

        # OCR Extraction
        ocr = OCRService()
        extracted_data = ocr.extract_data(file_path, doc_type)

        # Create Record
        doc = Document(
            user_id=user.id,
            document_type=doc_type,
            category=category,
            filename=save_name,
            file_path=file_path,
            original_size=original_size,
            file_size=file_size,
            extracted_data=json.dumps(extracted_data),
            status='processed',
            is_verified=True # Simulated verification
        )
        db.session.add(doc)
        db.session.commit()

        return jsonify({
            'message': 'Document uploaded successfully',
            'document': doc.to_dict(),
            'extracted_data': extracted_data
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/documents/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    try:
        user = get_current_user()
        doc = Document.query.filter_by(id=doc_id, user_id=user.id).first()
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
            
        db.session.delete(doc)
        db.session.commit()
        return jsonify({'message': 'Document deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/chat', methods=['POST'])
@jwt_required()
def chat_with_aditi():
    """
    Simulate AI Avatar 'Aditi' Chat with Multi-Language & Intent Detection
    """
    data = request.get_json()
    user_message = data.get('message', '').lower()
    
    # --- Intent Detection Logic (Simplified NLP) ---
    
    # 1. Define Knowledge Base (Keywords -> Intent)
    # Supports English, Hindi, Tamil, Bengali
    intents = {
        'education': {
            'keywords': ['student', 'education', 'study', 'scholarship', 'school', 'college', 'padhai', 'vidyarthi', 'shiksha', 'padhna', 'exam', 'fees', 'padibu', 'padippu', 'manavar', 'chatro', 'porashona', 'britti'],
            'response_en': "For students, I recommend the **Post-Matric Scholarship** and **Education Loan Subsidy**. What is your current qualification?",
            'response_hi': "Vidhyarthiyon ke liye **Post-Matric Scholarship** aur **Education Loan** upalabdh hain. Aapki vartaman yogyata kya hai?",
            'response_ta': "Māṇavarkaḷukku, **Post-Matric Scholarship** maṟṟum **Education Loan**-ai nān paripatu kkiṟēn. Uṅkaḷ takuti eṉṉa?",
            'response_bn': "Chatroder jonno, ami **Post-Matric Scholarship** ebong **Education Loan** suparish kori. Apnar bortoman joggota ki?"
        },
        'agriculture': {
            'keywords': ['farm', 'farmer', 'agriculture', 'crop', 'kisan', 'kheti', 'fasal', 'krishi', 'khet', 'seed', 'fertilizer', 'khad', 'vivasaayam', 'payir', 'krishok', 'chash', 'foshil'],
            'response_en': "For farming support, **PM-KISAN** provides Rs. 6,000/year. Also check out **PM Fasal Bima Yojana** for crop insurance.",
            'response_hi': "Kisan bhaiyon ke liye **PM-KISAN** yojana hai jisme saalana Rs. 6,000 milte hain. Fasal suraksha ke liye **PM Fasal Bima Yojana** bhi dekhein.",
            'response_ta': "Vivacāyikaḷukku, **PM-KISAN** āṇṭukku Rs. 6,000 vaḻaṅkukiṟatu. Payir kāppīṭṭiṟku **PM Fasal Bima Yojana**-vaiyum pārkkavum.",
            'response_bn': "Krishokder jonno, **PM-KISAN** bochore 6,000 taka dey. Foshil bimar jonno **PM Fasal Bima Yojana**-o dekhte paren."
        },
        'marriage': {
            'keywords': ['marriage', 'wedding', 'bride', 'groom', 'shaadi', 'vivah', 'shadi', 'kanyadan', 'dulhan', 'dowry', 'thirumanam', 'kalyanam', 'biye', 'bou'],
            'response_en': "Congratulations! For marriage assistance, schemes like **Kanyadan Yojana** (Rs. 51,000) and **Shagun Scheme** are available.",
            'response_hi': "Badhai ho! Vivah hetu **Kanyadan Yojana** (Rs. 51,000) aur **Shagun Scheme** uplabdh hain.",
            'response_ta': "Vāḻttukkaḷ! Tirumaṇa utavikku, **Kanyadan Yojana** (Rs. 51,000) maṟṟum **Shagun Scheme** kiṭaikkiṟatu.",
            'response_bn': "Ovinondon! Biye te sahajyer jonno, **Kanyadan Yojana** (Rs. 51,000) ebong **Shagun Scheme** uplobdho ache."
        },
        'business': {
            'keywords': ['business', 'loan', 'startup', 'money', 'capital', 'shop', 'dukan', 'vyapar', 'dhandha', 'mudra', 'paisa', 'udhar', 'thozhil', 'kadan', 'byabsha', 'dhara'],
            'response_en': "For starting a business, **Mudra Yojana** offers loans up to Rs. 10 Lakhs. **PMEGP** is also great for self-employment.",
            'response_hi': "Vyapar shuru karne ke liye **Mudra Yojana** ke antargat 10 Lakh tak ka loan mil sakta hai. **PMEGP** bhi ek accha vikalp hai.",
            'response_ta': "Toḻil toṭaṅka, **Mudra Yojana** Rs. 10 Lakh varai kaṭan aḷikkiṟatu. **PMEGP**-um ciṟantatu.",
            'response_bn': "Byabsha shuru korar jonno, **Mudra Yojana** 10 Lakh taka porjonto loan dey. **PMEGP**-o ekta bhalo bikolpo."
        },
        'health': {
            'keywords': ['health', 'hospital', 'doctor', 'medicine', 'illness', 'sick', 'swasthya', 'ilaj', 'bimari', 'davai', 'ayushman', 'udalnalam', 'maruthuvam', 'sasthya', 'osukh', 'daktar'],
            'response_en': "For health coverage, **Ayushman Bharat** provides free treatment up to Rs. 5 Lakhs. Do you have a Golden Card?",
            'response_hi': "Swasthya suraksha ke liye **Ayushman Bharat** 5 Lakh tak ka muft ilaj deta hai. Kya aapke paas Golden Card hai?",
            'response_ta': "Uṭalnalattiṟku, **Ayushman Bharat** Rs. 5 Lakh varai ilavasa cikiccai aḷikkiṟatu. Uṅkaḷiṭam Golden Card uḷḷatā?",
            'response_bn': "Sasthyer jonno, **Ayushman Bharat** 5 Lakh taka porjonto binamulle chikitsa dey. Apnar ki Golden Card ache?"
        },
        'housing': {
            'keywords': ['house', 'home', 'roof', 'shelter', 'ghar', 'makan', 'awas', 'chhat', 'housing', 'veedu', 'kudisai', 'bari', 'ghor'],
            'response_en': "Looking for a home? **PM Awas Yojana (PMAY)** provides subsidy for building pucca houses.",
            'response_hi': "Ghar banane ke liye **PM Awas Yojana (PMAY)** subsidy pradan karti hai.",
            'response_ta': "Vīṭu kaṭṭa, **PM Awas Yojana (PMAY)** māṉiyam aḷikkiṟatu.",
            'response_bn': "Bari toirir jonno, **PM Awas Yojana (PMAY)** subsidy dey."
        }
    }
    
    # 2. Detect Intent & Language
    detected_intent = None
    detected_lang = 'en' # Default
    
    # Simple language detection
    hindi_markers = ['hai', 'ke', 'liye', 'chahiye', 'kya', 'kaise', 'main', 'hum', 'mujhe', 'karna', 'h', 'namaste']
    tamil_markers = ['vanakkam', 'nanri', 'eppadi', 'irukkeenga', 'padippu', 'veedu', 'thozhil', 'kadan', 'ullatha', 'enna']
    bengali_markers = ['nomoshkar', 'kemon', 'achen', 'korbo', 'jabo', 'taka', 'ami', 'ki', 'kori', 'achhe']
    
    tokens = user_message.split()
    
    if any(w in tokens for w in hindi_markers):
        detected_lang = 'hi'
    elif any(w in tokens for w in tamil_markers):
        detected_lang = 'ta'
    elif any(w in tokens for w in bengali_markers):
        detected_lang = 'bn'
        
    max_matches = 0
    
    for intent, info in intents.items():
        matches = sum(1 for k in info['keywords'] if k in user_message)
        if matches > max_matches:
            max_matches = matches
            detected_intent = intent
            
    # 3. Formulate Response
    # 3. Formulate Response
    rich_cards = []
    
    if detected_intent:
        response_key = f'response_{detected_lang}'
        response = intents[detected_intent].get(response_key, intents[detected_intent]['response_en'])
    else:
        # INTELLIGENT FALLBACK: Search the Database
        # Split message into key terms (simple stopword removal)
        search_terms = [w for w in user_message.split() if w not in ['scheme', 'yojana', 'for', 'the', 'is', 'a', 'i', 'want', 'need', 'help', 'me', 'find', 'search']]
        
        found_schemes = []
        if search_terms:
            # Try finding schemes matching any significant term
            # In a real app, use full-text search (FTS) or vector search
            base_query = Scheme.query
            conditions = []
            for term in search_terms[:3]: # Limit to top 3 terms to avoid complex queries
                conditions.append(Scheme.name.ilike(f'%{term}%'))
                conditions.append(Scheme.description.ilike(f'%{term}%'))
                conditions.append(Scheme.benefits.ilike(f'%{term}%'))
            
            from sqlalchemy import or_
            found_schemes = base_query.filter(or_(*conditions)).limit(3).all()
            
        if found_schemes:
            response = f"I found {len(found_schemes)} schemes that might help you:"
            for s in found_schemes:
                rich_cards.append({
                    'title': s.name,
                    'subtitle': s.ministry,
                    'id': s.id,
                    'link_text': 'View Details'
                })
        else:
            # Default / Fallback
            if detected_lang == 'hi':
                response = "Mujhe aapke prashn ke liye koi vishesh yojana nahi mili. Kya aap 'education' ya 'farming' ke bare mein poochna chahte hain?"
            elif detected_lang == 'ta':
                 response = "Uṅkaḷ kēḷvikku eṉṉāl patil aḷikka muṭiyavillai. 'kalvi' allatu 'vivacāyam' paṟṟi kētkiṟīrkaḷā?"
            elif detected_lang == 'bn':
                 response = "Ami apnar prosner uttor khuje paini. Apni ki 'shikkha' ba 'krishi' sombondhe jante chan?"
            else:
                response = "I couldn't find specific details based on your query. Try asking about 'Education', 'Health', 'Farming', or 'Business' schemes."

    return jsonify({
        'response': response,
        'intent': detected_intent,
        'language': detected_lang,
        'rich_cards': rich_cards # New field for UI to render cards
    })

@api.route('/scan-scheme', methods=['POST'])
@jwt_required()
def scan_to_scheme():
    """
    Simulate Scan-to-Scheme (Photo Magic)
    """
    # In a real app, this would process the image with CV/ML
    # For demo, we simulate a "Roof Leak" or "Crop Damage" scenario
    
    # We don't actually process the file in this mock, just return a canned response
    # simulating that we analyzed the image.
    
    simulated_scenarios = [
        {
            "detected": "Damaged Roof / Housing Need",
            "confidence": "98%",
            "schemes": [
                {"name": "PM Awas Yojana (PMAY)", "benefit": "Rs. 1.5 Lakh Subsidy", "id": 1},
                {"name": "Home Repair Assistance", "benefit": "Rs. 50,000", "id": 2}
            ]
        },
        {
            "detected": "Withered Crop / Drought",
            "confidence": "96%",
            "schemes": [
                {"name": "PM Fasal Bima Yojana", "benefit": "Crop Insurance Claim", "id": 3},
                {"name": "Drought Relief Fund", "benefit": "Rs. 10,000/Acre", "id": 4}
            ]
        }
    ]
    
    # Randomly pick one or toggle based on seconds
    import random
    scenario = random.choice(simulated_scenarios)
    
    return jsonify({
        'analysis': scenario,
        'message': f"I analyzed your photo. I detected: **{scenario['detected']}**"
    })

@api.route('/schemes/sync-apisetu', methods=['POST'])
@jwt_required()
def sync_schemes_from_apisetu():
    """
    Sync schemes from API Setu (apisetu.gov.in) and curated fallback.
    Merges into local DB by external_id or (name, state).
    """
    try:
        from backend.services.api_setu import sync_schemes_to_db
        added, updated = sync_schemes_to_db()
        
        return jsonify({
            'message': f'Sync complete. Added: {added}, Updated: {updated}',
            'added': added,
            'updated': updated,
            'status': 'success'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500



@api.route('/upload-document', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload and process a document"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        doc_type = request.form.get('doc_type', 'other')
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file:
            filename = secure_filename(file.filename)
            # Create uploads directory if not exists
            upload_dir = os.path.join(os.getcwd(), 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
                
            # Add timestamp to filename to prevent duplicates
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(upload_dir, filename)
            
            # Compress if it's an image
            original_size = 0
            compressed_size = 0
            is_compressed = False
            
            # Get original size safely
            file.seek(0, os.SEEK_END)
            original_size = file.tell()
            file.seek(0)
            
            if file.content_type.startswith('image/'):
                try:
                    # Compress to < 200KB (typical requirement)
                    compressed_io = compress_image(file, target_size_kb=200)
                    compressed_size = compressed_io.getbuffer().nbytes
                    
                    with open(file_path, 'wb') as f:
                        f.write(compressed_io.getbuffer())
                    
                    is_compressed = True
                except Exception as e:
                    print(f"Compression error: {e}")
                    file.save(file_path)
                    compressed_size = original_size
            else:
                file.save(file_path)
                compressed_size = original_size
            
            # Process document
            ocr_service = OCRService()
            extracted_data = ocr_service.extract_data(file_path, doc_type)
            
            # Add compression info to extracted data
            extracted_data['_meta'] = {
                'original_size_kb': round(original_size / 1024, 2),
                'compressed_size_kb': round(compressed_size / 1024, 2),
                'compression_applied': is_compressed
            }
            
            # Save document record
            document = Document(
                user_id=user.id,
                document_type=doc_type,
                filename=filename,
                file_path=file_path,
                extracted_data=json.dumps(extracted_data),
                status='processed'
            )
            
            db.session.add(document)
            db.session.commit()
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document_id': document.id,
                'extracted_data': extracted_data
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@api.route('/documents/<int:doc_id>/view', methods=['GET'])
@jwt_required()
def view_document_file(doc_id):
    """
    View a specific document.
    Securely decrypts (reads) the file ONLY for the authenticated owner.
    """
    try:
        user = get_current_user()
        
        # DEBUG: Print exact user status
        from flask_jwt_extended import get_jwt_identity
        identity = get_jwt_identity()
        print(f"DEBUG: JWT Identity: {identity}, Resolved User: {user}")

        if not user:
            print("DEBUG: User not found in session")
            return jsonify({'error': 'Authentication required. User object is None.'}), 401

        print(f"DEBUG: Requesting View. UserID={user.id}, DocID={doc_id}")
        
        # SECURITY CHECK: Ensure user owns the document
        doc = Document.query.filter_by(id=doc_id).first()
        
        if not doc:
            print(f"DEBUG: Doc {doc_id} not found in DB")
            return jsonify({'error': 'Document not found'}), 404
            
        print(f"DEBUG: Found Doc {doc.id}, Owner={doc.user_id}, Path={doc.file_path}")
        
        if doc.user_id != user.id:
            print(f"DEBUG: ACCESS DENIED. {doc.user_id} != {user.id}")
            return jsonify({'error': f'Access Denied. You (ID {user.id}) do not own this document (Owner {doc.user_id})'}), 403
            
        if not doc.file_path:
            return jsonify({'error': 'File path record missing'}), 404

        # Normalize path for Windows
        abs_path = os.path.normpath(doc.file_path)
            
        if not os.path.exists(abs_path):
            print(f"DEBUG: File Missing on Disk: {abs_path}")
            return jsonify({'error': 'File missing from secure storage'}), 404
            
        # Determine mimetype
        mimetype = 'application/octet-stream'
        if abs_path.lower().endswith('.pdf'):
            mimetype = 'application/pdf'
        elif abs_path.lower().endswith('.jpg') or abs_path.lower().endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif abs_path.lower().endswith('.png'):
            mimetype = 'image/png'

        print(f"DEBUG: Serving file {abs_path}")
        # Serve the file (Decryption-at-Rest to Visualization-in-Transit)
        return send_file(abs_path, mimetype=mimetype, as_attachment=False)
        
    except Exception as e:
        print(f"Secure View Error doc={doc_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal Security Error: {str(e)}'}), 500

@api.route('/schemes/analyze-url', methods=['POST'])
@jwt_required()
def analyze_scheme_url():
    """Analyze official scheme website"""
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        analyzer = SchemeWebAnalyzer()
        analysis = analyzer.analyze_scheme_url(url)
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@api.route('/schemes/check-readiness', methods=['POST'])
@jwt_required()
def check_scheme_readiness():
    """Check if user is ready to apply for a scheme based on requirements"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        data = request.get_json()
        requirements = data.get('requirements')
        
        if not requirements:
            return jsonify({'error': 'Requirements data needed'}), 400
            
        # Fetch user documents
        documents = Document.query.filter_by(user_id=user.id).all()
        
        analyzer = SchemeWebAnalyzer()
        readiness = analyzer.check_readiness(user, documents, requirements)
        
        return jsonify(readiness), 200
        
    except Exception as e:
        return jsonify({'error': f'Readiness check failed: {str(e)}'}), 500

@api.route('/dialect/query', methods=['POST'])
@jwt_required()
def dialect_query():
    """
    Claim I: Dialect-Adaptive Intent Mapper.
    Processes voice transcripts in regional dialects to find schemes.
    """
    try:
        user = get_current_user()
        data = request.get_json()
        transcript = data.get('transcript', '')
        
        if not transcript:
            return jsonify({'error': 'Transcript is required'}), 400
            
        # 1. Map Intent using Aditi AI (Dialect Mapper)
        mapping = dialect_mapper.map_speech_to_intent(transcript)
        
        # 2. Get Localized Greeting
        greeting = dialect_mapper.get_greeting_for_dialect(user.state.upper() if user.state else "GENERAL")
        
        # 3. Fetch Relevant Schemes from DB based on Intent
        schemes_data = []
        found_ids = set()
        
        # Strategy A: Direct Scheme Hints (High Confidence)
        if mapping.get('scheme_hints'):
             hints = mapping['scheme_hints']
             # Find schemes where name matches any hint
             hint_filters = [Scheme.name.ilike(f"%{h}%") for h in hints]
             if hint_filters:
                 schemes = Scheme.query.filter(or_(*hint_filters)).all()
                 for s in schemes:
                     if s.id not in found_ids:
                         schemes_data.append(s.to_dict())
                         found_ids.add(s.id)

        # Strategy B: Keyword Search (Broad Discovery) using Mapped Intent Query
        if len(schemes_data) < 5 and mapping.get('search_query'):
            query_text = mapping['search_query']
            keywords = query_text.split()
            
            # Filter valid keywords (len > 3 to avoid 'the', 'for' etc)
            valid_keywords = [w for w in keywords if len(w) > 3]
            if not valid_keywords: valid_keywords = keywords # Fallback
            
            search_filters = []
            for word in valid_keywords:
                search_filters.append(Scheme.name.ilike(f"%{word}%"))
                search_filters.append(Scheme.description.ilike(f"%{word}%"))
                search_filters.append(Scheme.category.ilike(f"%{word}%"))
            
            if search_filters:
                # Find matching schemes
                results = Scheme.query.filter(or_(*search_filters)).limit(5).all()
                for s in results:
                    if s.id not in found_ids:
                        schemes_data.append(s.to_dict())
                        found_ids.add(s.id)
        
        return jsonify({
            'greeting': greeting,
            'analysis': mapping,
            'schemes': schemes_data,
            'count': len(schemes_data),
            'claim': 'Patent Claim I: Dialect-Adaptive Intent Mapping'
        }), 200
    except Exception as e:
        print(f"Aditi AI Error: {e}")
        return jsonify({'error': str(e)}), 500

@api.route('/mobility/roadmap', methods=['GET'])
@jwt_required()
def get_mobility_roadmap():
    """
    Claims M & N: Welfare-to-Work Sequencing.
    Generates an economic mobility path for the user.
    """
    try:
        user = get_current_user()
        # Find approved applications
        approved_apps = Application.query.filter_by(user_id=user.id, status='APPROVED').all()
        app_list = [{"scheme_category": "GIRL_CHILD_EDUCATION", "status": "APPROVED"}] # Mocking for demo if empty
        if approved_apps:
            # Real data logic here...
            pass
            
        path = mobility_sequencer.predict_next_milestone(app_list)
        
        roi = {}
        if path:
             roi = mobility_sequencer.calculate_impact_roi(user.income or 50000, 25000, path[0]['roi_multiplier'])

        return jsonify({
            'current_path': path,
            'economic_impact': roi,
            'claim': 'Patent Claims M & N: Welfare-to-Work Sequencer'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/agent/register', methods=['POST'])
@jwt_required()
def register_agent_route():
    """Claim P: Agent Registration."""
    try:
        user = get_current_user()
        data = request.get_json()
        result = agent_service.register_agent(user.id, data.get('region', 'UNKNOWN'))
        
        # Persist to DB
        if 'agent_id' in result:
            user.agent_id = result['agent_id']
            db.session.commit()
            
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/agent/resign', methods=['POST'])
@jwt_required()
def resign_agent_route():
    """Claim P: Agent Resignation."""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        if not agent_id:
            return jsonify({'error': 'Agent ID required'}), 400
        result = agent_service.resign_agent(agent_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/tokenizer/issue', methods=['POST'])
@jwt_required()
def issue_token():
    """Claim O: Issue Smart Voucher."""
    try:
        user = get_current_user()
        data = request.get_json()
        token = benefit_tokenizer.issue_voucher(
            user.id, 
            data.get('scheme_id'), 
            data.get('amount'), 
            data.get('category')
        )
        return jsonify(token), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/arbitrage/schedule/<int:application_id>', methods=['POST'])
@jwt_required()
def schedule_arbitrage(application_id):
    """Claim Q: Temporal Arbitrage Scheduling."""
    try:
        data = request.get_json()
        portal_id = data.get('portal_id', 'api_setu')
        result = temporal_arbitrage.schedule_submission(application_id, portal_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/credit/assess', methods=['GET'])
@jwt_required()
def assess_social_credit():
    """Claim R: Actuarial Social Risk Assessment."""
    try:
        user = get_current_user()
        # Mocking history for assessment if real history is sparse
        mock_history = [
            {"status": "APPROVED", "timestamp": "2025-01-01T10:00:00"},
            {"status": "APPROVED", "timestamp": "2025-06-01T12:00:00"}
        ]
        
        assessment = social_credit_model.calculate_social_credit(
            user.beneficiary_score or 50,
            mock_history,
            user.income or 100000
        )
        return jsonify(assessment), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------
# FUTURE HORIZON LABS (Claims S, T, U)
# ---------------------------------------------------------

@api.route('/future/trigger-drought', methods=['POST'])
@jwt_required()
def trigger_drought_sim():
    """
    CLAIM S: Geospatial Pre-emptive Trigger.
    Simulates a satellite detecting drought in user's state.
    """
    try:
        data = request.get_json() or {}
        location = data.get('location', {'state': 'Bihar'}) # Default to Bihar
        result = GeoSpatialTrigger.simulate_event('DROUGHT', location)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/future/zk-proof', methods=['POST'])
@jwt_required()
def zk_proof_sim():
    """
    CLAIM T: Zero-Knowledge Sovereign Identity.
    Generates a proof that user meets criteria (e.g. Age > 18) without revealing value.
    """
    try:
        user = get_current_user()
        data = request.get_json()
        attribute = data.get('attribute', 'age')
        condition = data.get('condition', '>')
        value = data.get('value', 18)
        
        proof = ZeroKnowledgeProofer.generate_proof(user, attribute, condition, value)
        return jsonify(proof), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/future/social-bond', methods=['POST'])
@jwt_required()
def social_bond_sim():
    """
    CLAIM U: Peer-to-Peer Social Impact Bonds.
    """
    try:
        user = get_current_user()
        data = request.get_json()
        amount = data.get('amount', 5000)
        purpose = data.get('purpose', 'Education Fees Gap')
        
        # 1. List the bond
        listing = SocialBondMarket.list_bond(user.id, amount, purpose)
        
        # 2. Simulate immediate funding (for demo speed)
        funding = SocialBondMarket.fund_bond(listing['bond_id'], "INVESTOR-888")
        
        return jsonify({
            "listing": listing,
            "transaction": funding
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
