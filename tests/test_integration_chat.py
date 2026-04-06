import pytest
from datetime import datetime
from backend.app import create_app
from backend.models import User, db

@pytest.fixture
def client():
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_chat_multilanguage_intent(client):
    # Register and Login
    email = "chat_test@example.com"
    password = "Password123"
    
    client.post('/api/register', json={
        'name': 'Chat Tester',
        'email': email,
        'password': password,
        'age': 25
    })
    
    resp = client.post('/api/login', json={'email': email, 'password': password})
    token = resp.json['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    test_cases = [
        {
            "message": "I am a student looking for scholarship",
            "expected_intent": "education",
            "expected_lang": "en",
            "keyword_in_response": "Post-Matric Scholarship"
        },
        {
            "message": "Mujhe kheti ke liye scheme chahiye",
            "expected_intent": "agriculture",
            "expected_lang": "hi",
            "keyword_in_response": "PM-KISAN"
        },
        {
            "message": "Main business shuru karna chahta hu, mujhe loan chahiye",
            "expected_intent": "business",
            "expected_lang": "hi", # Hinglish detected as Hindi due to markers
            "keyword_in_response": "Mudra Yojana"
        },
        {
            "message": "Vanakkam enaku veedu kattavum",
            "expected_intent": "housing",
            "expected_lang": "ta",
            "keyword_in_response": "PMAY" # Response is in Tamil script but checks logic
        },
        {
            "message": "Nomoshkar ami byabsha shuru korbo",
            "expected_intent": "business",
            "expected_lang": "bn",
            "keyword_in_response": "Mudra Yojana"
        },
        {
            "message": "Hello Asha",
            "expected_intent": None,
            "expected_lang": "en",
            "keyword_in_response": "I couldn't find specific details"
        }
    ]
    
    for case in test_cases:
        resp = client.post('/api/chat', json={'message': case['message']}, headers=headers)
        assert resp.status_code == 200
        data = resp.json
        
        assert data['intent'] == case['expected_intent'], f"Failed for: {case['message']}"
        assert data['language'] == case['expected_lang'], f"Failed for: {case['message']}"
        
        # Check response content (basic check)
        if case.get('keyword_in_response'):
            # Note: Tamil/Bengali responses are in native script, so keyword check might be tricky if we check English keywords.
            # But the response definitions use **Bold** keywords which are often English or transliterated.
            # For Tamil: "PM Awas Yojana (PMAY)" is used.
            # For Bengali: "Mudra Yojana" is used.
            assert case['keyword_in_response'] in data['response'] or case['keyword_in_response'] in data['response'].replace('**', ''), f"Keyword missing in: {data['response']}"

