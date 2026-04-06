"""
P Λ R Λ D I T I - Programmable Benefit Tokenizer (Claim O)
Copyright (c) 2026. All rights reserved.
Patent Pending: Claim O (Instruction-Led Spending Tokens).
"""

import hashlib
import json
import time
import hmac
import base64
import os
from typing import Dict, Optional, List, Union

TOKEN_SECRET = "paraditi-benefit-secret-v1"

class BenefitTokenizer:
    """Implements Claim O: Programmable Benefit Tokenizer."""
    
    def issue_voucher(self, user_id: str, scheme_id: str, amount: float, category: Union[str, List[str]]) -> Dict[str, str]:
        """
        Generate a programmable token/voucher.
        """
        cats = [category] if isinstance(category, str) else category
        
        payload = {
            "uid": user_id,
            "sid": scheme_id,
            "amt": amount,
            "cat": cats,
            "exp": int(time.time()) + (90 * 86400),
            "nonce": base64.b64encode(os.urandom(8)).decode('utf-8')
        }
        
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            TOKEN_SECRET.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        token_data = base64.urlsafe_b64encode(payload_str.encode('utf-8')).decode('utf-8')
        final_token = f"PRDT.{token_data}.{signature}"
        
        return {
            "token": final_token,
            "amount": amount,
            "restricted_to": cats,
            "status": "ISSUED"
        }

# Singleton instance
benefit_tokenizer = BenefitTokenizer()
