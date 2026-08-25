import asyncio
from database import SessionLocal, engine
import models
from auth import hash_password

def seed_db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(models.User).count() == 0:
        # Create initial users
        admin = models.User(
            username="admin",
            email="admin@landrecord.gov.in",
            full_name="System Administrator",
            hashed_password=hash_password("admin123"),
            role="admin"
        )
        
        officer1 = models.User(
            username="officer_ramesh",
            email="ramesh@landrecord.gov.in",
            full_name="Ramesh Kumar (Verification Officer)",
            hashed_password=hash_password("officer123"),
            role="officer"
        )

        db.add_all([admin, officer1])
        db.commit()
        print("Initial users created.")
    else:
        print("Database already seeded.")
        
    db.close()

if __name__ == "__main__":
    seed_db()
