import uuid
import re
from app import db, bcrypt
from .basemodel import BaseModel
from sqlalchemy.orm import validates

class User(BaseModel):
    __tablename__ = "users"

    # Use db.Column to stay within the Flask-SQLAlchemy context
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Task 8: Relationships
    # Using string references "Place" and "Review" prevents circular imports
    places = db.relationship("Place", backref="owner", cascade="all, delete-orphan")
    reviews = db.relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, email, password, first_name, last_name, is_admin=False, **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.hash_password(password or '')
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = bool(is_admin)

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email is required")
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")
        return email

    def hash_password(self, password):
        pw = '' if password is None else str(password)
        self.password = bcrypt.generate_password_hash(pw).decode('utf-8')

    def verify_password(self, password):
        if not self.password:
            return False
        try:
            return bcrypt.check_password_hash(self.password, password)
        except Exception:
            return False

    def to_dict(self):
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': bool(self.is_admin),
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None
        }
