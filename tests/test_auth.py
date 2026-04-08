#!/usr/bin/env python3
"""
双认证机制测试脚本

测试场景：
1. JWT Token - 前端 Web 应用登录
2. API Key - 后端服务调用
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_jwt_login():
    """测试 JWT Token 登录"""
    print("=" * 60)
    print("📱 测试场景 1：前端 Web 应用使用 JWT Token")
    print("=" * 60)
    
    # 1. 登录获取 JWT Token
    print("\n1️⃣  登录获取 JWT Token...")
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if response.status_code == 200:
        result = response.json()
        data = result.get('data', {})
        print(f"✅ 登录成功！")
        print(f"   - JWT Token: {data['access_token'][:50]}...")
        print(f"   - 用户 ID: {data['user_id']}")
        print(f"   - 用户名：{data['username']}")
        print(f"   - 全名：{data.get('full_name', 'N/A')}")
        print(f"   - 过期时间：{data['expires_in']}秒")
        return data['access_token']
    else:
        print(f"❌ 登录失败：{response.json()}")
        return None

def test_api_key():
    """测试 API Key 认证"""
    print("\n" + "=" * 60)
    print("🖥️  测试场景 2：后端服务使用 API Key")
    print("=" * 60)
    
    # 1. 先登录获取 JWT Token
    jwt_token = test_jwt_login()
    if not jwt_token:
        print("❌ 获取 JWT Token 失败，无法继续创建 API Key")
        return None

    # 2. 使用 JWT Token 获取 API Key
    print("\n1️⃣  获取 API Key...")
    response = requests.post(
        f"{BASE_URL}/api-key",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        data = result.get('data', {})
        api_key = data['api_auth_key']
        print(f"✅ 获取 API Key 成功！")
        print(f"   - API Key: {api_key}")
        print(f"   - 创建时间：{data['created_at']}")
        print(f"   - 过期时间：{data['expires_at']}")
        
        # 3. 使用 API Key 访问受保护接口
        print("\n2️⃣  使用 API Key 访问 /api/users/ 接口...")
        headers = {"api-auth-key": api_key}
        response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
        
        if response.status_code == 200:
            users_result = response.json()
            users = users_result.get('data', [])
            print(f"✅ 访问成功！获取到 {len(users)} 个用户")
            if users:
                print(f"   - 第一个用户：{users[0]['username']} ({users[0]['email']})")
        else:
            print(f"❌ 访问失败：{response.json()}")
        
        return api_key
    else:
        print(f"❌ 获取 API Key 失败：{response.json()}")
        return None

def test_unauthorized_access():
    """测试未授权访问"""
    print("\n" + "=" * 60)
    print("🔒 测试场景 3：未授权访问（应该失败）")
    print("=" * 60)
    
    print("\n尝试直接访问 /api/users/（不带认证）...")
    response = requests.get(f"{BASE_URL}/api/users/")
    
    if response.status_code == 401:
        print(f"✅ 正确拒绝未授权访问！")
        print(f"   - 错误信息：{response.json()['message']}")
    else:
        print(f"❌ 未授权访问未被拒绝：{response.status_code}")

def main():
    """主测试流程"""
    print("\n🚀 开始测试双认证机制\n")
    
    # 测试 JWT Token
    jwt_token = test_jwt_login()
    
    # 测试 API Key
    api_key = test_api_key()
    
    # 测试未授权访问
    test_unauthorized_access()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print("\n✅ JWT Token 认证：用于前端 Web 应用")
    print("   - 登录接口：POST /login")
    print("   - 返回包含用户信息的 JWT Token")
    print("   - 有效期：1 小时")
    print("\n✅ API Key 认证：用于后端服务调用")
    print("   - 获取接口：POST /api-key")
    print("   - 需要请求头：Authorization: Bearer <jwt_token>")
    print("   - 返回长期有效的 API Key")
    print("   - 有效期：24 小时")
    print("   - 访问 /api/** 接口需要：api-auth-key 请求头")
    print("\n🎯 使用建议：")
    print("   - 前端 Web/Mobile 应用 → 使用 JWT Token")
    print("   - 后端服务/脚本/第三方系统 → 使用 API Key")
    print()

if __name__ == "__main__":
    main()
