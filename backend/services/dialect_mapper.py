"""
P Λ R Λ D I T I (परादिति) - Dialect-Adaptive Intent Mapper (Claim I)
(C) 2026 Founder: PARAS AGRAWAL
Patent Pending: NLP layer that bridges regional dialects to welfare intents.
"""

import re
import logging

class DialectMapper:
    """
    Standardizes regional dialect queries into high-fidelity welfare intents.
    Supports Bharat-specific speech patterns (Bhojpuri, Magahi, rural Hindi).
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Multilingual Lexicon: Global Languages + Indian Languages
        self.lexicon = {
            # Education / Student
            r"education|study|school|college|scholarship|student|university|padhai|likhai|vidyarthi|chatravritti|baji|shiksha|porashona|kalvi|vidyabhyasam|shikshan|padipu|chaduvu|patha|padanam|taleem|educación|école|bildung|schule|تعليم|学校|교육|школа|ensino": "education",
            
            # Women / Girl Child
            r"girl|daughter|woman|female|lady|beti|bitiya|chhori|larki|mahila|aurat|bahini|nari|mey|penn|ammayi|hudugi|stree|baiko|mulgi|jhio|penkutty|mujer|niña|femme|fille|frau|tochter|امرأة|女|여자|женщина|mulher": "women",
            
            # Agriculture / Farmer
            r"farmer|agriculture|farming|crop|seed|fertilizer|kisan|kheti|fasal|beej|khad|anndata|Krishi|krishak|vivasayi|vivasayam|rythu|raitha|shatkari|chasa|karshakan|khedut|chash|aagrahihunu|agricultor|granja|agriculture|ferme|landwirtschaft|bauer|زراعة|农业|농업|фермер|agricultura|ziraea": "agriculture",
            
            # Health / Medical
            r"health|hospital|medical|treatment|medicine|doctor|swasthya|ilaj|dawayi|aspataal|bimari|rog|aarogya|chikitsa|maruthuvam|vaidyam|oushadham|rogo|salud|médico|santé|hôpital|gesundheit|arzt|صحة|健康|건강|здоровье|saúde": "health",
            
            # Business / Loan / Employment
            r"business|loan|startup|store|shop|money|fund|credit|dhandha|karja|rin|udhar|dukaan|naukri|rojgar|kam|vyapar|kadan|appu|sala|ulaga|vyavsaya|taka|paisa|dhandho|thozhil|shuru|joie|negocio|préstamo|entreprise|prêt|geschäft|kredit|عمل|生意|사업|бизнес|negócio|daikuan": "business_employment",
            
            # Pension / Elderly
            r"pension|old|elderly|senior|retired|budhapa|bridhavastha|vridha|siyaan|boyoshko|mudhi|vayasaana|hiriyar|vయోvruddhalu|vridh|pensión|anciano|retraite|rente|senioren|تقاعد|养老金|연금|пенсия|aposentadoria": "pension",
            
            # Housing
            r"home|house|flat|roof|shelter|ghar|makan|awas|chhat|niw|bari|veedu|illu|mane|kudil|vasati|casa|hogar|maison|haus|heim|بيت|家|집|дом|жильем": "housing"
        }
        
        # Intent to specific scheme mapping (Heuristic for demo)
        self.intent_scheme_map = {
            "women_education": ["Sukanya Samriddhi Yojana", "CBSE Udaan", "Begum Hazrat Mahal Scholarship"],
            "women_business": ["Mudra Loan", "Stand Up India", "Mahila E-Haat"],
            "agriculture_loan": ["Kisan Credit Card", "PM Kisan Samman Nidhi"],
            "health_insurance": ["Ayushman Bharat", "PM Jan Arogya Yojana"],
            "business_loan": ["PM Mudra Yojana", "PMEGP"],
            "pension": ["Atal Pension Yojana", "PM Vaya Vandana Yojana"]
        }

    def map_speech_to_intent(self, transcript):
        """
        Processes a raw STT transcript (voice-converted text) and extracts intents.
        Example: "humra laiki ke padhai khatir paisa chai" -> ['women', 'education', 'business_employment'] -> "women_education"
        """
        detected_tokens = set()
        cleaned_input = transcript.lower().strip()

        # 1. Detect Keywords
        for pattern, token in self.lexicon.items():
            if re.search(pattern, cleaned_input):
                detected_tokens.add(token)

        # 2. Construct Composite Intent
        final_intent = "general_discovery"
        search_query = transcript # Default fallback
        scheme_hints = []

        if "women" in detected_tokens and "education" in detected_tokens:
            final_intent = "women_education"
            search_query = "girl child education scholarship"
        elif "women" in detected_tokens and "business_employment" in detected_tokens:
            final_intent = "women_business"
            search_query = "women business loan startup"
        elif "agriculture" in detected_tokens and "business_employment" in detected_tokens:
            final_intent = "agriculture_loan"
            search_query = "kisan credit card farmer loan"
        elif "health" in detected_tokens:
            final_intent = "health_insurance"
            search_query = "health insurance medical aid"
        elif "business_employment" in detected_tokens:
            final_intent = "business_loan"
            search_query = "small business loan mudra"
        elif "pension" in detected_tokens:
            final_intent = "pension"
            search_query = "old age pension"
        elif "housing" in detected_tokens:
            final_intent = "housing"
            search_query = "housing scheme awas yojana"
        elif "education" in detected_tokens:
             final_intent = "education"
             search_query = "student scholarship"

        # 3. Get Specific Scheme Hints
        if final_intent in self.intent_scheme_map:
            scheme_hints = self.intent_scheme_map[final_intent]
        
        return {
            "original_transcript": transcript,
            "detected_keywords": list(detected_tokens),
            "mapped_intent": final_intent,
            "search_query": search_query,
            "scheme_hints": scheme_hints,
            "confidence": 0.95 if detected_tokens else 0.3
        }

    def get_greeting_for_dialect(self, user_region="UP_BIHAR"):
        """Returns a localized greeting to build trust."""
        greetings = {
            # Indian Languages
            "UP_BIHAR": "प्रणाम! हम आदिति हईं। रउआ के कइसे मदद करीं?", # Bhojpuri
            "HARYANA": "राम राम! मैं आदिति हूँ। के सेवा कर सकूँ थारी?", # Haryanvi
            "MAHARASHTRA": "नमस्ते! मी आदिति आहे. मी तुम्हाला कशी मदत करू शकते?", # Marathi
            "WEST_BENGAL": "Namaskar! Ami Aditi. Ami apnake kivabe sahajyo korte pari?", # Bengali
            "TAMIL_NADU": "Vanakkam! Naan Aditi. Ungaluku epadi udhava mudiyum?", # Tamil
            "ANDHRA_TELANGANA": "Namaskaram! Nenu Aditi. Meeku ela sahayam cheyagalanu?", # Telugu
            "KARNATAKA": "Namaskara! Naanu Aditi. Nigu hege sahaya madali?", # Kannada
            "KERALA": "Namaskaram! Njan Aditi. Ningale engane sahabhikkam?", # Malayalam
            "GUJARAT": "Namaste! Hu Aditi chu. Hu tamari evi rite madad kari shaku?", # Gujarati
            "PUNJAB": "Sat Sri Akal! Main Aditi haan. Main tuhadi kiwen madad kar sakdi haan?", # Punjabi
            "ODISHA": "Namaskar! Mu Aditi. Mu apananku kemiti sahajya karipari?", # Odia
            "SOUTH": "Vanakkam! I am Aditi. How can I help you regarding government schemes?", # General South
            
            # Global Languages
            "GLOBAL_ES": "¡Hola! Soy Aditi AI. ¿Cómo puedo ayudarte hoy?", # Spanish
            "GLOBAL_FR": "Bonjour! Je suis Aditi AI. Comment puis-je vous aider?", # French
            "GLOBAL_DE": "Hallo! Ich bin Aditi AI. Wie kann ich Ihnen helfen?", # German
            "GLOBAL_CN": "你好! 我是 Aditi AI。我能为你做些什么?", # Mandarin
            "GLOBAL_AR": "مرحبًا! أنا Aditi AI. كيف يمكنني مساعدتك؟", # Arabic
            "GLOBAL_RU": "Здравствуйте! Я Aditi AI. Чем могу помочь?", # Russian
            "GLOBAL_PT": "Olá! Sou a Aditi AI. Como posso ajudar?", # Portuguese
            "GLOBAL_JP": "こんにちは！Aditi AIです。どのようにお手伝いできますか？", # Japanese
             
            "GENERAL": "Namaste! I am Aditi AI. Tell me about your needs (Education, Loan, Health)?" # Standard
        }
        return greetings.get(user_region, greetings["GENERAL"])

# Global singleton
dialect_mapper = DialectMapper()
