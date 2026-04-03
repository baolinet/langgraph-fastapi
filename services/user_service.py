from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from typing import Optional, List
import hashlib

class UserService:
    """用户业务服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """密码哈希（实际项目用 bcrypt）"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def search_users_by_fullname(self, fullname: str) -> List[User]:
        """根据全名进行左侧模糊匹配查询（LIKE 'fullname%'）"""
        return self.db.query(User).filter(User.full_name.like(f"{fullname}%")).all()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, user_create: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否存在
        if self.get_user_by_username(user_create.username):
            raise ValueError(f"用户名 {user_create.username} 已存在")
        
        # 检查邮箱是否存在
        if self.get_user_by_email(user_create.email):
            raise ValueError(f"邮箱 {user_create.email} 已存在")
        
        # 创建新用户
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            password_hash=self._hash_password(user_create.password)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # 检查邮箱是否被其他用户占用
        if user_update.email and user_update.email != user.email:
            existing = self.get_user_by_email(user_update.email)
            if existing:
                raise ValueError(f"邮箱 {user_update.email} 已被使用")
            user.email = user_update.email
        
        if user_update.full_name:
            user.full_name = user_update.full_name
        
        if user_update.password:
            user.password_hash = self._hash_password(user_update.password)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def activate_user(self, user_id: int) -> Optional[User]:
        """激活用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """禁用用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user_by_username(self, username: str, user_update: UserUpdate) -> Optional[User]:
        """根据用户名更新用户信息"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        # 检查邮箱是否被其他用户占用
        if user_update.email and user_update.email != user.email:
            existing = self.get_user_by_email(user_update.email)
            if existing:
                raise ValueError(f"邮箱 {user_update.email} 已被使用")
            user.email = user_update.email
        
        if user_update.full_name:
            user.full_name = user_update.full_name
        
        if user_update.password:
            user.password_hash = self._hash_password(user_update.password)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user_by_username(self, username: str) -> bool:
        """根据用户名删除用户"""
        user = self.get_user_by_username(username)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def activate_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名激活用户"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def deactivate_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名禁用用户"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user