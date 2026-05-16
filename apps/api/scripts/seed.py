from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import User
Base.metadata.create_all(bind=engine)
db=SessionLocal()
try:
    if not db.query(User).filter(User.username=='admin').first():
        db.add(User(username='admin', email='admin@example.local', password_hash=hash_password('password123'), role='ADMIN', enabled=True))
        db.commit(); print('Created admin user: admin / password123')
    else: print('Admin already exists')
finally: db.close()
