from schedulur.models.user import User
from typing import List, Optional
import uuid

# In-memory storage for demo
users = {}

class UserService:
    @staticmethod
    def create_user(user: User) -> User:
        if not user.id:
            user.id = str(uuid.uuid4())
        users[user.id] = user
        return user
    
    @staticmethod
    def get_user(user_id: str) -> Optional[User]:
        return users.get(user_id)
    
    @staticmethod
    def update_user(user_id: str, updated_user: User) -> Optional[User]:
        if user_id in users:
            updated_user.id = user_id
            users[user_id] = updated_user
            return updated_user
        return None
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        if user_id in users:
            del users[user_id]
            return True
        return False
    
    @staticmethod
    def list_users() -> List[User]:
        return list(users.values())