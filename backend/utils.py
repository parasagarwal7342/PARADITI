"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
import os
import io
from PIL import Image

def compress_image(file_storage, target_size_kb=200):
    """
    Compress image to be under target_size_kb.
    Args:
        file_storage: Flask FileStorage object or bytes
        target_size_kb: Target size in KB (default 200KB)
    Returns:
        BytesIO object containing the compressed image data
    """
    target_size_bytes = target_size_kb * 1024
    
    # Read image
    if hasattr(file_storage, 'read'):
        file_storage.seek(0)
        img_data = file_storage.read()
        file_storage.seek(0) # Reset for other uses if needed
    else:
        img_data = file_storage
        
    # Check if already small enough
    if len(img_data) <= target_size_bytes:
        return io.BytesIO(img_data)
        
    try:
        img = Image.open(io.BytesIO(img_data))
        
        # Convert to RGB if RGBA (to save as JPEG)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
            
        # Start compression loop
        quality = 95
        output = io.BytesIO()
        
        # First attempt: just save as JPEG with high quality
        img.save(output, format='JPEG', quality=quality)
        
        # Binary search-ish approach or iterative reduction
        while output.tell() > target_size_bytes and quality > 10:
            output = io.BytesIO()
            quality -= 10
            img.save(output, format='JPEG', quality=quality)
            
        # If still too big, resize
        if output.tell() > target_size_bytes:
            scale = 0.8
            while output.tell() > target_size_bytes and scale > 0.1:
                output = io.BytesIO()
                new_size = (int(img.width * scale), int(img.height * scale))
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                resized_img.save(output, format='JPEG', quality=quality)
                scale -= 0.1
                
        output.seek(0)
        return output
        
    except Exception as e:
        # If compression fails, return original
        print(f"Compression failed: {e}")
        return io.BytesIO(img_data)
