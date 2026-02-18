#!/usr/bin/python3
import uuid
import re


class User:
    def __init__(self, first_name, last_name, email, password):
        self.id = str(uuid.uuid4())
        self.first_name = self.validate_string(first_name, "first_name")
        self.last_name = self.validate_string(last_name, "last_name")
        self.email = self.validate_email(email)
        self.password = self.validate_string(password, "password")

    def validate_string(self, value, field_name):
        if not value or not isinstance(value, str):
            raise ValueError(f"{field_name} is required and must be a string")
        return value

    def validate_email(self, email):
        regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(regex, email):
            raise ValueError("Invalid email format")
        return email

    def to_dict(self):
        """Serialize without password"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email
        }
