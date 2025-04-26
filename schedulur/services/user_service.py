import json
import os
from typing import List, Optional
import uuid

from schedulur.models.user import User

class UserService:
    """Service for managing users"""
    
    def __init__(self, data_file: str = None):
        self.data_file = data_file or os.path.join(os.path.dirname(__file__), "../data/users.json")
        self.users = {}
        self.load_users()
    
    def load_users(self) -> None:
        """Load users from data file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    user_data = json.load(f)
                
                for user_id, user_dict in user_data.items():
                    self.users[user_id] = User(**user_dict)
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = {}
    
    def save_users(self) -> None:
        """Save users to data file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            user_data = {}
            for user_id, user in self.users.items():
                user_data[user_id] = user.dict()
            
            with open(self.data_file, 'w') as f:
                json.dump(user_data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def create_user(self, user: User) -> Optional[User]:
        """Create a new user"""
        if not user.id:
            user.id = str(uuid.uuid4())
        
        self.users[user.id] = user
        self.save_users()
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, user: User) -> Optional[User]:
        """Update a user"""
        if user_id in self.users:
            user.id = user_id
            self.users[user_id] = user
            self.save_users()
            return user
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        if user_id in self.users:
            del self.users[user_id]
            self.save_users()
            return True
        return False
    
    def list_users(self) -> List[User]:
        """List all users"""
        return list(self.users.values())