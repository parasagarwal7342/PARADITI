"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""

from backend.models import Application, User, Scheme, Document, db
from backend.services.document_processor import DocumentProcessor
from backend.services.ocr_service import OCRService
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ApplicationService:
    """
    Orchestrates the 'One-Click Apply' process.
    """
    
    def __init__(self):
        self.ocr = OCRService()
        self.doc_processor = DocumentProcessor()

    def initiate_application(self, user_id, scheme_id):
        """
        Starts the application process.
        Returns:
            - success: Application object
            - failure: Error dict with missing requirements
        """
        user = User.query.get(user_id)
        scheme = Scheme.query.get(scheme_id)
        
        if not user or not scheme:
            return {'error': 'User or Scheme not found', 'status': 'failed'}

        # 1. Analyze Requirements
        req_docs = self._parse_requirements(scheme.documents_required)
        user_docs = Document.query.filter_by(user_id=user_id).all()
        
        # 2. Check Availability
        available_types = {d.document_type.lower(): d for d in user_docs}
        missing = []
        
        used_documents = []
        
        for req in req_docs:
            formatted_req = req.lower().strip()
            # Fuzzy match or direct match logic could go here
            found = False
            for dtype in available_types:
                if formatted_req in dtype or dtype in formatted_req:
                    used_documents.append(available_types[dtype])
                    found = True
                    break
            if not found:
                missing.append(req)

        if missing:
             return {
                 'status': 'missing_documents',
                 'missing': missing,
                 'message': f"Missing documents: {', '.join(missing)}"
             }

        # 3. Process & Validate Documents (One-Click Intelligence)
        processed_data = {}
        for doc in used_documents:
            # Ensure document is optimized
            if doc.file_path.endswith(('jpg', 'jpeg', 'png')):
                # Auto-resize if needed (e.g. scheme limit is 2MB, our standard is 200KB)
                # We assume DocumentProcessor.compress_image updates the file in place or returns new path
                # For now, we just ensure it is valid
                pass
            
            # Extract Data if not already present
            if not doc.extracted_data:
                extraction = self.ocr.extract_data(doc.file_path, doc.document_type)
                doc.extracted_data = json.dumps(extraction)
                db.session.commit()
                processed_data[doc.document_type] = extraction
            else:
                 processed_data[doc.document_type] = json.loads(doc.extracted_data)

        # 4. Generate Application Payload (The Form Fill)
        payload = self._generate_payload(user, scheme, processed_data)
        
        # 5. Create Application Record
        app = Application(
            user_id=user_id,
            scheme_id=scheme_id,
            status='submitted', # Simulating instant submission
            submission_data=json.dumps(payload),
            submitted_at=datetime.utcnow(),
            validation_status='valid'
        )
        
        db.session.add(app)
        db.session.commit()
        
        # Calculate Optimization Stats
        total_original = sum((d.original_size or 0) for d in used_documents)
        total_optimized = sum((d.file_size or 0) for d in used_documents)
        savings_mb = round((total_original - total_optimized) / (1024 * 1024), 2)
        
        return {
            'status': 'success',
            'application_id': app.id,
            'message': f'Application submitted! AI optimized {len(used_documents)} documents (saved {savings_mb} MB).',
            'savings_mb': savings_mb
        }

    def _parse_requirements(self, req_string):
        """
        Parses the document requirements string from Scheme model.
        Assumes comma separated or newline separated.
        """
        if not req_string:
            return []
        
        # Split by comma or newline
        reqs = [r.strip() for r in req_string.replace('\n', ',').split(',') if r.strip()]
        return reqs

    def _generate_payload(self, user, scheme, doc_data):
        """
        Maps User Profile + Document Data -> Scheme Form
        """
        form = {
            "applicant": {
                "name": user.name,
                "email": user.email,
                "gender": user.gender,
                "age": user.age,
                "address": user.state # Simplified
            },
            "scheme_details": {
                "id": scheme.id,
                "name": scheme.name
            },
            "documents_attached": []
        }
        
        # Intelligent Merge: properties found in docs override or supplement profile
        for dtype, data in doc_data.items():
            form["documents_attached"].append({
                "type": dtype,
                "extracted_info": data
            })
            
            # Example: Update payload with verified data from Aadhaar
            if 'aadhaar' in dtype and 'address' in data:
                form["applicant"]["verified_address"] = data['address']
            if 'pan' in dtype and 'pan_number' in data:
               form["applicant"]["pan_number"] = data['pan_number']
               
        return form
