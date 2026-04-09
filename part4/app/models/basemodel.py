from datetime import datetime
import uuid
from app.extensions import db  # ✅ استيراد db من extensions فقط

class BaseModel(db.Model):
    __abstract__ = True  # هذا يعني أنه لا يتم إنشاء جدول له مباشرة

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

    def to_dict(self):
        """
        Convert model instance to dictionary, useful for API responses.
        """
        return {
            'id': str(self.id),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }