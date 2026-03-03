import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.services.Database.database import Base 
from app.models import BaseModel
from app import bcrypt
import re

class User(BaseModel, Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    is_admin = Column(Boolean, default=False)
    places = relationship("Place", backref="owner", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, email, password, first_name, last_name, is_admin=False, **kwargs):
        """
        User model

        Parameters are accepted as keywords by the facade/service layer,
        so this constructor supports both positional and keyword usage.
        """
        super().__init__(**kwargs)
        self.email = self.validate_email(email)
        # store hashed password only via hash_password; allow setting raw then hashing
        self.password = None
        self.hash_password(password or '')
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = bool(is_admin)

    @staticmethod
    def validate_email(email):
        """Validate email format and return the normalized value."""
        if not email:
            raise ValueError("Email is required")
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")
        return email

    def to_dict(self):
        """Return a JSON-serializable representation of the user (no password)."""
        return {
            'id': str(self.id),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': bool(self.is_admin),
            'created_at': self.created_at.isoformat() if getattr(self, 'created_at', None) else None,
            'updated_at': self.updated_at.isoformat() if getattr(self, 'updated_at', None) else None
        }

    def hash_password(self, password):
        """Hash and store the password using the app's bcrypt instance."""
        # Ensure password is a string
        pw = '' if password is None else str(password)
        # bcrypt.generate_password_hash returns bytes; decode to str for storage
        self.password = bcrypt.generate_password_hash(pw).decode('utf-8')

    def set_password(self, password):
        """Public helper to change password (hashes before storing)."""
        if not password:
            raise ValueError("Password cannot be empty")
        self.hash_password(password)

    def verify_password(self, password):
        """Verify a plaintext password against the stored hash."""
        if not self.password:
            return False
        try:
            return bcrypt.check_password_hash(self.password, password)
        except Exception:
            return False

    def update(self, data):
        """
        Update allowed user fields in-place.
        This method intentionally excludes password changes; use set_password for that.
        """
        if not isinstance(data, dict):
            return

        if 'first_name' in data:
            self.first_name = data['first_name']
        if 'last_name' in data:
            self.last_name = data['last_name']
        # Do not allow email or password updates here; higher layers enforce that.
        if 'is_admin' in data:
            self.is_admin = bool(data['is_admin'])
        # update timestamps if BaseModel supports it
        if hasattr(self, 'touch'):
            try:
                self.touch()
            except Exception:
                pass
        return self
