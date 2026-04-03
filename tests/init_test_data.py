#!/usr/bin/env python3
"""
初始化测试数据脚本
创建测试用户用于接口测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def create_test_user():
    """创建测试用户"""
    print("📝 创建测试用户...")
    
    # 尝试直接创建（不需要认证）
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
        try:
            # 先尝试直接创建（可能失败）
            response = requests.post(f"{BASE_URL}/api/users/", json=user_data)
            
            if response.status_code == 401:
                # 如果需要认证，尝试使用一个临时的方式
                print(f"⚠️  需要认证才能创建用户 {user_data['username']}")
                print(f"   请手动创建测试用户，或提供一个有效的 API Key")
                return False
            elif response.status_code == 201:
                print(f"✅ 创建成功：{user_data['username']}")
            elif response.status_code == 400:
                print(f"ℹ️  用户已存在：{user_data['username']}")
            else:
                print(f"❌ 创建失败 {user_data['username']}: {response.status_code}")
                print(f"   {response.json()}")
        except Exception as e:
            print(f"❌ 异常：{e}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 初始化测试数据")
    print("=" * 60)
    
    success = create_test_user()
    
    if success:
        print("\n✅ 测试数据初始化完成")
        print("\n测试账号：")
        print("  - admin / admin123")
        print("  - testuser / test123")
        print("  - user1 / password123")
        print("  - user2 / password123")
    else:
        print("\n❌ 测试数据初始化失败")
        print("\n请手动创建测试用户或使用以下命令：")
        print("  1. 先通过 /login 获取 JWT Token")
        print("  2. 使用 Token 创建测试用户")
