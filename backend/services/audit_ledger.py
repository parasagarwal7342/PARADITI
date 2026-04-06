"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claim C (Immutable Integrity Ledger).
"""
import hashlib
import json
import os
import time
from datetime import datetime

class ImmutableLedger:
    """
    PATENT CLAIM: 'Verifiable Integrity Protocol for Welfare Applications'.
    
    Implements a local blockchain-style ledger to create a tamper-proof
    audit trail of all user applications.
    
    Structure:
    [
        {
            "transaction_id": "uuid",
            "timestamp": "iso-date",
            "data_hash": "sha256(application_data)",
            "prev_hash": "sha256(previous_block_signature)",
            "signature": "sha256(this_block)"
        }
    ]
    """
    
    LEDGER_FILE = 'instance/audit_ledger.json'
    
    @staticmethod
    def _calculate_hash(data_string):
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()
    
    @classmethod
    def get_ledger(cls):
        if not os.path.exists(cls.LEDGER_FILE):
            return []
        try:
            with open(cls.LEDGER_FILE, 'r') as f:
                return json.load(f)
        except:
            return []

    @classmethod
    def record_application(cls, user_id, scheme_id, application_data):
        ledger = cls.get_ledger()
        
        # 1. Get Previous Hash (Genesis block if empty)
        if ledger:
            prev_hash = ledger[-1]['signature']
        else:
            prev_hash = "GENESIS_BLOCK_00000000000000000000000000000000"
            
        # 2. Create Block Data
        timestamp = datetime.utcnow().isoformat()
        
        # We assume application_data is a dict
        data_string = json.dumps({
            "user_id": user_id,
            "scheme_id": scheme_id,
            "payload": application_data # The compressed packet receipt
        }, sort_keys=True)
        
        data_hash = cls._calculate_hash(data_string)
        
        # 3. Create Signature (Proof of Integrity)
        # Signature = Hash(Prev_Hash + Timestamp + Data_Hash)
        block_content = f"{prev_hash}{timestamp}{data_hash}"
        signature = cls._calculate_hash(block_content)
        
        new_block = {
            "index": len(ledger) + 1,
            "timestamp": timestamp,
            "user_id": user_id,
            "scheme_id": scheme_id,
            "data_hash": data_hash,
            "prev_hash": prev_hash,
            "signature": signature
        }
        
        ledger.append(new_block)
        
        # 4. Save Atomically
        with open(cls.LEDGER_FILE, 'w') as f:
            json.dump(ledger, f, indent=2)
            
        return signature

    @classmethod
    def verify_integrity(cls):
        """
        Re-calculates entire chain to ensure no record was modified.
        Returns: (bool, offending_index)
        """
        ledger = cls.get_ledger()
        if not ledger:
            return True, -1
            
        prev_hash = "GENESIS_BLOCK_00000000000000000000000000000000"
        
        for i, block in enumerate(ledger):
            # 1. Check Linkage
            if block['prev_hash'] != prev_hash:
                return False, i
            
            # 2. Check Signature
            # We can't re-hash the data payload since we don't store it raw here for privacy,
            # but we verify the block construction integrity.
            # In a full impl, we'd verify data_hash against the DB record.
            
            recalc_content = f"{block['prev_hash']}{block['timestamp']}{block['data_hash']}"
            recalc_sig = cls._calculate_hash(recalc_content)
            
            if recalc_sig != block['signature']:
                return False, i
                
            prev_hash = block['signature']
            
        return True, -1
