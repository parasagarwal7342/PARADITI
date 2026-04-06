"""
P Λ R Λ D I T I (परादिति) - WhatsApp/SMS Benefit Hub (Claim J)
(C) 2026 Founder: PARAS AGRAWAL
Patent Pending: Low-bandwidth asynchronous application platform.
"""

import logging
from datetime import datetime

class WhatsAppHub:
    """
    Allows citizens to discover and apply for benefits via simple 
    WhatsApp/SMS messaging, bridging the digital divide.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Mock Templates
        self.templates = {
            "WELCOME": "Namaste! Welcome to SAHAJ. Reply with your State to find schemes.",
            "SCHEME_LIST": "We found {count} schemes for you:\n{schemes}\nReply with Scheme ID to apply.",
            "STATUS_UPDATE": "Your application {app_id} is now {status}."
        }

    def handle_incoming_message(self, phone_number, message_body):
        """
        Parses incoming WhatsApp/SMS messages and routes to intent handlers.
        """
        msg = message_body.lower().strip()
        
        if "hi" in msg or "hello" in msg or "start" in msg:
            return self._send_response(phone_number, self.templates["WELCOME"])
            
        elif "apply" in msg:
            # Mock Application flow
            scheme_id = msg.split(" ")[-1] if " " in msg else "UNKNOWN"
            return self._send_response(phone_number, f"Application initiated for Scheme {scheme_id}. Please upload your Aadhaar photo here.")
            
        else:
            return self._send_response(phone_number, "I didn't understand. Type 'Hi' to start or 'Status' to check applications.")

    def send_status_alert(self, user_phone, application_id, new_status):
        """
        Push notification for application status change.
        """
        msg = self.templates["STATUS_UPDATE"].format(app_id=application_id, status=new_status)
        # In production, this would call Twilio/WhatsApp API
        self.logger.info(f"Sending SMS to {user_phone}: {msg}")
        return {"sent": True, "recipient": user_phone, "content": msg}

    def _send_response(self, phone, text):
        """
        Mock sender.
        """
        return {
            "recipient": phone,
            "message": text,
            "platform": "WHATSAPP_BUSINESS_API",
            "timestamp": datetime.now().isoformat()
        }

# Global singleton
whatsapp_hub = WhatsAppHub()
