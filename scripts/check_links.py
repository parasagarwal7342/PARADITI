
from backend.app import create_app
from backend.models import db, Scheme

def check_links():
    app = create_app('development')
    with app.app_context():
        # Check for empty or None links
        missing_links = Scheme.query.filter((Scheme.official_link == None) | (Scheme.official_link == '')).count()
        print(f"Schemes with missing links: {missing_links}")
        
        # Check for placeholder links
        generic_links = Scheme.query.filter(Scheme.official_link.like('%agricoop.nic.in%')).count()
        print(f"Schemes with generic agricoop links: {generic_links}")
        
        schemes = Scheme.query.limit(20).all()
        print(f"\n{'Scheme Name':<50} | {'Official Link'}")
        print("-" * 100)
        for s in schemes:
            print(f"{s.name[:47] + '...' :<50} | {s.official_link}")

if __name__ == "__main__":
    check_links()
