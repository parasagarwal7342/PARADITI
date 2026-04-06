import pytest
import json
from datetime import datetime
from backend.app import create_app
from backend.models import User, Scheme, db

@pytest.fixture
def client():
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed minimal data for testing
            s1 = Scheme(
                id=4, 
                name="Post Matric Scholarships Scheme for Minorities",
                ministry="Ministry of Minority Affairs",
                description="Scholarship for minorities",
                max_income=200000.0,
                category_specific="Minority"
            )
            s2 = Scheme(
                id=5,
                name="Sukanya Samriddhi Yojana",
                ministry="Ministry of Finance",
                description="Savings scheme for girl child",
                min_age=0,
                max_age=10,
                gender_specific="Female"
            )
            db.session.add(s1)
            db.session.add(s2)
            db.session.commit()
            
            yield client
            
            db.session.remove()
            db.drop_all()

def test_income_gap_analysis(client):
    # Register user with income slightly above limit
    timestamp = int(datetime.now().timestamp())
    email = f"gap_test_{timestamp}@example.com"
    password = "Password123"
    
    resp = client.post('/api/register', json={
        'name': 'Gap Tester',
        'email': email,
        'password': password,
        'state': 'Delhi',
        'age': 25,
        'gender': 'Male',
        'income': 220000, # 20k above 200k limit (10%)
        'category': 'Minority'
    })
    assert resp.status_code == 201
    token = resp.json['token']
    
    # Get recommendations
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.get('/api/schemes/recommended?limit=10', headers=headers)
    assert resp.status_code == 200
    
    data = resp.json
    almost_eligible = data['almost_eligible']
    
    # Check if Scheme 4 is in almost_eligible
    found = False
    for item in almost_eligible:
        if item['id'] == 4:
            found = True
            assert "Income is ₹20000.0 above the limit" in item['gap_reason']
            break
    assert found

def test_income_gap_too_high(client):
    # Register user with income way above limit
    timestamp = int(datetime.now().timestamp())
    email = f"gap_high_{timestamp}@example.com"
    password = "Password123"
    
    resp = client.post('/api/register', json={
        'name': 'Gap Tester',
        'email': email,
        'password': password,
        'state': 'Delhi',
        'age': 25,
        'gender': 'Male',
        'income': 300000, # 100k above 200k limit (50% > 30%)
        'category': 'Minority'
    })
    assert resp.status_code == 201
    token = resp.json['token']
    
    # Get recommendations
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.get('/api/schemes/recommended?limit=10', headers=headers)
    assert resp.status_code == 200
    
    data = resp.json
    almost_eligible = data['almost_eligible']
    
    # Check if Scheme 4 is NOT in almost_eligible
    found = False
    for item in almost_eligible:
        if item['id'] == 4:
            found = True
            break
    assert not found

def test_age_gap_analysis(client):
    # Register user with age slightly above limit
    timestamp = int(datetime.now().timestamp())
    email = f"gap_age_{timestamp}@example.com"
    password = "Password123"
    
    resp = client.post('/api/register', json={
        'name': 'Gap Tester',
        'email': email,
        'password': password,
        'state': 'Delhi',
        'age': 11, # 1 year above 10 limit
        'gender': 'Female',
        'income': 100000,
        'category': 'General'
    })
    assert resp.status_code == 201
    token = resp.json['token']
    
    # Get recommendations
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.get('/api/schemes/recommended?limit=10', headers=headers)
    assert resp.status_code == 200
    
    data = resp.json
    almost_eligible = data['almost_eligible']
    
    # Check if Scheme 5 is in almost_eligible
    found = False
    for item in almost_eligible:
        if item['id'] == 5:
            found = True
            assert "exceeded the age limit by 1 years" in item['gap_reason']
            break
    assert found
