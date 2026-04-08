from app import db
import uuid
from datetime import datetime

class BaseModel(db.Model):
    __abstract__ = True 

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def update(self, data):
        """
        Update model attributes from a dict-like object.

        - Only sets attributes that already exist on the model.
        - Skips protected fields: id and created_at.
        - Returns self for chaining.
        """
        protected = {'id', 'created_at'}
        for key, value in data.items():
            if key in protected:
                continue
            if hasattr(self, key):
                setattr(self, key, value)
        return self
