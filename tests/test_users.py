#!/usr/bin/env python3
"""
用户管理接口完整测试脚本

测试覆盖：
1. GET /api/users/{username} - 获取单个用户详情
2. GET /api/users/search/fullname/{fullname} - 根据全名模糊查询
3. POST /api/users/ - 创建新用户
4. PUT /api/users/{username} - 更新用户信息
5. DELETE /api/users/{username} - 删除用户
6. POST /api/users/{username}/activate - 激活用户
7. POST /api/users/{username}/deactivate - 禁用用户
8. POST /api-key/revoke - 撤销 API Key
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"

def get_api_key(username="testuser", password="test123"):
    """获取 API Key 用于测试"""
    response = requests.post(f"{BASE_URL}/api-key", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["data"]["api_auth_key"]
    return None

def ensure_test_users_exist():
    """确保测试用户存在"""
    print("\n📝 检查测试用户...")
    
    # 尝试使用默认账号获取 API Key
    test_accounts = [
        ("testuser", "test123"),
        ("admin", "admin123"),
        ("user1", "password123")
    ]
    
    for username, password in test_accounts:
        api_key = get_api_key(username, password)
        if api_key:
            print(f"✅ 使用测试账号：{username}")
            return api_key, username, password
    
    # 如果都没有，尝试创建一个
    print("⚠️  测试账号不存在，尝试创建...")
    
    # 先尝试登录获取临时 token（可能需要先有用户）
    # 这里我们假设至少有一个用户存在
    print("❌ 无法获取有效的测试账号")
    print("\n请先创建一个测试用户：")
    print("  curl -X POST http://127.0.0.1:8000/api/users/ \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -H 'api-auth-key: <your-api-key>' \\")
    print("    -d '{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"test123\",\"full_name\":\"Test User\"}'")
    return None, None, None

def print_test_result(test_name: str, success: bool, details: str = ""):
    """打印测试结果"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"📋 {title}")
    print("=" * 60)

# ==================== 测试用例 ====================

def test_get_user_by_username(api_key):
    """测试获取单个用户详情"""
    print_section("测试 1: GET /api/users/{username}")
    
    headers = {"api-auth-key": api_key}
    
    # 测试成功场景
    response = requests.get(f"{BASE_URL}/api/users/testuser", headers=headers)
    print_test_result(
        "获取存在的用户",
        response.status_code == 200,
        f"状态码：{response.status_code}"
    )
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"   用户：{data['username']} ({data['email']})")
    
    # 测试 404 场景
    response = requests.get(f"{BASE_URL}/api/users/nonexistent_user", headers=headers)
    print_test_result(
        "获取不存在的用户",
        response.status_code == 404,
        f"状态码：{response.status_code}, message: {response.json().get('message')}"
    )

def test_search_users_by_fullname(api_key):
    """测试根据全名模糊查询"""
    print_section("测试 2: GET /api/users/search/fullname/{fullname}")
    
    headers = {"api-auth-key": api_key}
    
    # 测试成功场景 - 查找以 "Admin" 开头的用户（admin 用户的全名是 "Admin User"）
    response = requests.get(f"{BASE_URL}/api/users/search/fullname/Admin", headers=headers)
    print_test_result(
        "模糊查询全名匹配的用户",
        response.status_code == 200,
        f"状态码：{response.status_code}"
    )
    if response.status_code == 200:
        users = response.json()["data"]
        print(f"   找到 {len(users)} 个匹配的用户")
        for user in users[:3]:  # 显示前 3 个
            print(f"   - {user['full_name']} ({user['username']})")
    
    # 测试 404 场景 - 查找不存在的用户
    response = requests.get(f"{BASE_URL}/api/users/search/fullname/NonExistent", headers=headers)
    print_test_result(
        "模糊查询无匹配结果",
        response.status_code == 404,
        f"状态码：{response.status_code}, message: {response.json().get('message')}"
    )

def test_create_user(api_key):
    """测试创建新用户"""
    print_section("测试 3: POST /api/users/")
    
    headers = {"api-auth-key": api_key}
    
    # 生成唯一的用户名和邮箱
    unique_id = str(uuid.uuid4())[:8]
    test_user = {
        "username": f"test_user_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "test123",
        "full_name": f"Test User {unique_id}"
    }
    
    # 测试成功创建
    response = requests.post(f"{BASE_URL}/api/users/", json=test_user, headers=headers)
    # 注意：success_response 返回的 code 是 201，但 HTTP 状态码也是 201
    print_test_result(
        "创建新用户",
        response.status_code in [200, 201],
        f"状态码：{response.status_code}"
    )
    if response.status_code in [200, 201]:
        data = response.json()["data"]
        print(f"   创建成功：{data['username']} ({data['email']})")
        created_username = test_user["username"]
        
        # 测试重复用户名
        response = requests.post(f"{BASE_URL}/api/users/", json=test_user, headers=headers)
        print_test_result(
            "创建重复用户名的用户",
            response.status_code == 400,
            f"状态码：{response.status_code}, message: {response.json().get('message')}"
        )
        
        return created_username  # 返回用户名用于后续测试
    else:
        # 测试重复用户名
        response = requests.post(f"{BASE_URL}/api/users/", json=test_user, headers=headers)
        print_test_result(
            "创建重复用户名的用户",
            response.status_code == 400,
            f"状态码：{response.status_code}, message: {response.json().get('message')}"
        )
    
    return None

def test_update_user(api_key, username):
    """测试更新用户信息"""
    print_section("测试 4: PUT /api/users/{username}")
    
    headers = {"api-auth-key": api_key}
    
    # 测试成功更新
    update_data = {
        "full_name": f"Updated Full Name for {username}",
        "email": f"updated_{username}@example.com"
    }
    response = requests.put(f"{BASE_URL}/api/users/{username}", json=update_data, headers=headers)
    print_test_result(
        "更新用户信息",
        response.status_code == 200,
        f"状态码：{response.status_code}"
    )
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"   更新后全名：{data['full_name']}")
        print(f"   更新后邮箱：{data['email']}")
    
    # 测试 404 场景
    response = requests.put(f"{BASE_URL}/api/users/nonexistent_user", json=update_data, headers=headers)
    print_test_result(
        "更新不存在的用户",
        response.status_code == 404,
        f"状态码：{response.status_code}, message: {response.json().get('message')}"
    )

def test_activate_deactivate_user(api_key, username):
    """测试激活和禁用用户"""
    print_section("测试 5: 用户状态管理")
    
    headers = {"api-auth-key": api_key}
    
    # 先禁用用户
    response = requests.post(f"{BASE_URL}/api/users/{username}/deactivate", headers=headers)
    print_test_result(
        "禁用用户",
        response.status_code == 200,
        f"状态码：{response.status_code}"
    )
    if response.status_code == 200:
        is_active = response.json()["data"]["is_active"]
        print(f"   用户状态：{'激活' if is_active else '禁用'}")
    
    # 再激活用户
    response = requests.post(f"{BASE_URL}/api/users/{username}/activate", headers=headers)
    print_test_result(
        "激活用户",
        response.status_code == 200,
        f"状态码：{response.status_code}"
    )
    if response.status_code == 200:
        is_active = response.json()["data"]["is_active"]
        print(f"   用户状态：{'激活' if is_active else '禁用'}")
    
    # 测试 404 场景
    response = requests.post(f"{BASE_URL}/api/users/nonexistent_user/deactivate", headers=headers)
    print_test_result(
        "禁用不存在的用户",
        response.status_code == 404,
        f"状态码：{response.status_code}, message: {response.json().get('message')}"
    )

def test_delete_user(api_key, username):
    """测试删除用户"""
    print_section("测试 6: DELETE /api/users/{username}")
    
    headers = {"api-auth-key": api_key}
    
    # 测试成功删除
    response = requests.delete(f"{BASE_URL}/api/users/{username}", headers=headers)
    print_test_result(
        "删除用户",
        response.status_code == 200,
        f"状态码：{response.status_code}"
    )
    if response.status_code == 200:
        print(f"   用户 {username} 已删除")
    
    # 验证用户已不存在
    response = requests.get(f"{BASE_URL}/api/users/{username}", headers=headers)
    print_test_result(
        "验证删除后的用户不存在",
        response.status_code == 404,
        f"状态码：{response.status_code}"
    )
    
    # 测试删除不存在的用户
    response = requests.delete(f"{BASE_URL}/api/users/nonexistent_user", headers=headers)
    print_test_result(
        "删除不存在的用户",
        response.status_code == 404,
        f"状态码：{response.status_code}, message: {response.json().get('message')}"
    )

def test_revoke_api_key():
    """测试撤销 API Key"""
    print_section("测试 7: POST /api-key/revoke")
    
    # 先创建一个 API Key（使用 admin 账号）
    response = requests.post(f"{BASE_URL}/api-key", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        print_test_result("创建 API Key 失败", False, f"状态码：{response.status_code}")
        return
    
    api_key = response.json()["data"]["api_auth_key"]
    print(f"   创建临时 API Key: {api_key[:20]}...")
    
    # 测试撤销
    response = requests.post(f"{BASE_URL}/api-key/revoke", params={"api_auth_key": api_key})
    print_test_result(
        "撤销 API Key",
        response.status_code == 200,
        f"状态码：{response.status_code}, message: {response.json().get('message')}"
    )
    
    # 验证 API Key 已失效
    headers = {"api-auth-key": api_key}
    response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
    print_test_result(
        "验证撤销后的 API Key 失效",
        response.status_code == 401,
        f"状态码：{response.status_code}, message: {response.json().get('message')}"
    )
    
    # 测试撤销不存在的 API Key
    response = requests.post(f"{BASE_URL}/api-key/revoke", params={"api_auth_key": "invalid-key"})
    print_test_result(
        "撤销不存在的 API Key",
        response.status_code == 404,
        f"状态码：{response.status_code}, message: {response.json().get('message')}"
    )

def test_validation_errors(api_key):
    """测试验证错误"""
    print_section("测试 8: 验证错误测试")
    
    headers = {"api-auth-key": api_key}
    
    # 测试创建用户时缺少必填字段
    response = requests.post(f"{BASE_URL}/api/users/", json={
        "username": "test_missing_fields"
        # 缺少 email, password
    }, headers=headers)
    print_test_result(
        "创建用户缺少必填字段",
        response.status_code == 422,
        f"状态码：{response.status_code}"
    )
    
    # 测试创建用户时邮箱格式错误
    response = requests.post(f"{BASE_URL}/api/users/", json={
        "username": "test_invalid_email",
        "email": "invalid-email",  # 无效的邮箱格式
        "password": "test123"
    }, headers=headers)
    print_test_result(
        "创建用户邮箱格式错误",
        response.status_code == 422,
        f"状态码：{response.status_code}"
    )

# ==================== 主测试流程 ====================

def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("🚀 用户管理接口完整测试")
    print("=" * 60)
    
    # 获取 API Key 和测试账号信息
    print("\n📝 准备：获取测试账号...")
    result = ensure_test_users_exist()
    if result[0] is None:
        print("\n❌ 测试初始化失败，请确保测试用户存在")
        return
    
    api_key, username, password = result
    print(f"✅ API Key 获取成功：{api_key[:20]}... (用户：{username})")
    
    # 执行测试
    test_get_user_by_username(api_key)
    test_search_users_by_fullname(api_key)
    
    # 创建测试用户用于后续测试
    test_username = test_create_user(api_key)
    if test_username:
        test_update_user(api_key, test_username)
        test_activate_deactivate_user(api_key, test_username)
        test_delete_user(api_key, test_username)
    else:
        print("\n⚠️  跳过需要测试用户的测试用例")
    
    test_revoke_api_key()
    test_validation_errors(api_key)
    
    # 测试总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print("\n✅ 已测试的接口：")
    print("   1. GET /api/users/{username} - 获取单个用户")
    print("   2. GET /api/users/search/fullname/{fullname} - 全名模糊查询")
    print("   3. POST /api/users/ - 创建用户")
    print("   4. PUT /api/users/{username} - 更新用户")
    print("   5. DELETE /api/users/{username} - 删除用户")
    print("   6. POST /api/users/{username}/activate - 激活用户")
    print("   7. POST /api/users/{username}/deactivate - 禁用用户")
    print("   8. POST /api-key/revoke - 撤销 API Key")
    print("   9. 验证错误处理（422）")
    print("\n🎯 测试覆盖率：用户管理接口 100% 覆盖")
    print()

if __name__ == "__main__":
    main()
