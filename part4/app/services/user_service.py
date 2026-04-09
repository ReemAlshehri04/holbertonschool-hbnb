"""User service module"""
from app.models.user import User
from app.persistence.repository import InMemoryRepository

class UserService:
    """Service class for user operations"""
    
    def __init__(self):
        self.repository = InMemoryRepository()
    
    def create_user(self, user_data):
        """Create a new user"""
        # Check if user already exists
        existing_user = self.get_user_by_email(user_data.get('email'))
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user object
        user = User(**user_data)
        
        # Save to repository
        self.repository.save(user)
        return user
    
    def get_user(self, user_id):
        """Get user by ID"""
        return self.repository.get(user_id)
    
    def get_user_by_email(self, email):
        """Get user by email"""
        users = self.repository.get_all()
        for user in users:
            if user.email == email:
                return user
        return None
    
    def get_all_users(self):
        """Get all users"""
        return self.repository.get_all()