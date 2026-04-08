#!/usr/bin/env python3
"""
数据库初始化脚本
创建测试用户数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models import Base, User
import hashlib

def init_db():
    """初始化数据库并创建测试用户"""
    print("📝 创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")
    
    # 创建测试用户
    print("\n📝 创建测试用户...")
    
    db = SessionLocal()
    
    test_users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "Admin User"
        },
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123",
            "full_name": "Test User"
        },
        {
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123",
            "full_name": "User One"
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
            "full_name": "User Two"
        }
    ]
    
    for user_data in test_users:
        # 检查用户是否已存在
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            print(f"ℹ️  用户已存在：{user_data['username']}")
            continue
        
        # 创建新用户
        password_hash = hashlib.sha256(user_data["password"].encode()).hexdigest()
        db_user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            password_hash=password_hash
        )
        db.add(db_user)
        db.commit()
        print(f"✅ 创建用户：{user_data['username']}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("✅ 数据库初始化完成")
    print("=" * 60)
    print("\n测试账号：")
    print("  - admin / admin123")
    print("  - testuser / test123")
    print("  - user1 / password123")
    print("  - user2 / password123")
    print("\n现在可以运行测试：")
    print("  python tests/test_auth.py")
    print("  python tests/test_response_format.py")
    print("  python tests/test_users.py")
    print("  python tests/test_agents.py")

if __name__ == "__main__":
    init_db()
