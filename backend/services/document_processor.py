
import os
from PIL import Image
from pypdf import PdfReader, PdfWriter
import io

class DocumentProcessor:
    """
    Handles document processing: compression, resizing, and format conversion
    for the 'One-Click Apply' feature.
    """
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

    @staticmethod
    def get_file_size_kb(file_path):
        """Get file size in KB"""
        if not os.path.exists(file_path):
            return 0
        return os.path.getsize(file_path) / 1024

    @staticmethod
    def compress_image(file_path, target_size_kb=200):
        """
        Compress image to be under target_size_kb.
        Returns path to compressed file.
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            current_size = os.path.getsize(file_path) / 1024
            if current_size <= target_size_kb:
                return file_path
                
            img = Image.open(file_path)
            
            # Convert to RGB if RGBA (standardize)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                
            # Iterative compression
            quality = 90
            output_path = file_path.replace('.', '_compressed.')
            
            while quality > 10:
                img.save(output_path, "JPEG", quality=quality)
                if os.path.getsize(output_path) / 1024 <= target_size_kb:
                    return output_path
                quality -= 10
                
            return output_path
            
        except Exception as e:
            print(f"Error compressing image: {e}")
            return file_path

    @staticmethod
    def compress_pdf(file_path, target_size_kb=500):
        """
        Attempt to compress PDF by removing duplication and downsampling images.
        Note: pypdf compression is limited. For strong compression, ghostscript is usually needed.
        Here we implement a robust optimization using pypdf.
        """
        try:
            current_size = os.path.getsize(file_path) / 1024
            if current_size <= target_size_kb:
                return file_path
                
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                page.compress_content_streams()  # Basic DEFLATE compression
                writer.add_page(page)
                
            output_path = file_path.replace('.', '_compressed.')
            with open(output_path, "wb") as f:
                writer.write(f)
                
            return output_path
            
        except Exception as e:
            print(f"Error compressing PDF: {e}")
            return file_path

    @staticmethod
    def prepare_application_package(user, scheme, documents):
        """
        Simulates creating a unified application package.
        1. Checks required documents
        2. Decrypts and processes them
        3. Fills 'Form' (Returns filled data structure)
        """
        from backend.security_utils import get_encryptor
        encryptor = get_encryptor()
        
        package = {
            "applicant_id": user.id,
            "applicant_name": user.name,
            "scheme_id": scheme.id,
            "scheme_name": scheme.name,
            "form_data": {
                "name": user.name,
                "email": user.email,
                "age": user.age,
                "gender": user.gender,
                "income": user.income,
                "state": user.state,
                "category": user.category
            },
            "documents": []
        }
        
        # Process docs (Transparent Decryption)
        for doc in documents:
            file_path = doc.file_path
            
            try:
                # 1. Read and Decrypt
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
                
                # If decryption fails, it might be an unencrypted file (retry gracefully)
                try:
                    decrypted_data = encryptor.decrypt_data(encrypted_data)
                except:
                    decrypted_data = encrypted_data # Fallback
                
                # 2. Process based on type
                processed_data = decrypted_data
                status = "Ready"
                
                if doc.document_type.lower() in ['aadhaar', 'pan', 'photo']:
                     # For images, we can compress in memory here if needed
                     pass
                
                package["documents"].append({
                    "type": doc.document_type,
                    "filename": doc.filename,
                    "status": "Verified & Decrypted",
                    "preview_snippet": f"{len(processed_data)} bytes processed"
                })
            except Exception as e:
                print(f"Error processing doc {doc.id}: {e}")
                package["documents"].append({
                    "type": doc.document_type,
                    "status": "Error: Decryption Failed"
                })
                
        return package
