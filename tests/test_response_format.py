import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_response(title: str, response: requests.Response):
    """打印响应信息"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"状态码：{response.status_code}")
    print(f"URL: {response.url}")
    print(f"\n响应 JSON:")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 检查响应结构
        if "code" in data and "message" in data:
            print(f"\n✅ 统一响应格式：code={data['code']}, message='{data['message']}'")
            if "data" in data:
                print(f"   包含 data 字段")
            if "timestamp" in data:
                print(f"   包含 timestamp 字段")
        else:
            print(f"\n⚠️  非统一响应格式")
    except:
        print(f"原始响应：{response.text}")

def test_success_response():
    """测试成功响应"""
    print("\n" + "="*60)
    print("测试成功响应格式")
    print("="*60)
    
    # 测试登录成功
    response = requests.post(f"{BASE_URL}/login", json={
        "username": "admin",
        "password": "admin123"
    })
    print_response("1. 登录成功", response)
    
    # 保存 JWT Token 用于后续测试
    jwt_token = None
    if response.status_code == 200 and response.json().get("data"):
        jwt_token = response.json()["data"]["access_token"]
    
    # 测试健康检查
    response = requests.get(f"{BASE_URL}/health")
    print_response("2. 健康检查", response)
    
    return jwt_token

def test_error_response(jwt_token):
    """测试错误响应"""
    print("\n" + "="*60)
    print("测试错误响应格式")
    print("="*60)
    
    # 测试登录失败
    response = requests.post(f"{BASE_URL}/login", json={
        "username": "wronguser",
        "password": "wrongpass"
    })
    print_response("3. 登录失败（错误密码）", response)
    
    # 测试缺少 API Key
    response = requests.get(f"{BASE_URL}/api/users/")
    print_response("4. 缺少 API Key", response)
    
    # 测试无效 API Key
    response = requests.get(
        f"{BASE_URL}/api/users/",
        headers={"api-auth-key": "invalid-key"}
    )
    print_response("5. 无效 API Key", response)
    
    # 测试用户不存在
    api_key = generate_api_key()
    if api_key:
        response = requests.get(
            f"{BASE_URL}/api/users/999",
            headers={"api-auth-key": api_key}
        )
        print_response("6. 用户不存在 (404)", response)
    
    # 测试使用 JWT Token 访问（应该成功）
    if jwt_token:
        response = requests.get(
            f"{BASE_URL}/api/users/",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        print_response("7. JWT Token 访问用户列表", response)

def generate_api_key():
    """生成 API Key 用于测试"""
    response = requests.post(f"{BASE_URL}/api-key", json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        data = response.json()
        if "data" in data and "api_auth_key" in data["data"]:
            return data["data"]["api_auth_key"]
    return None

def test_validation_error():
    """测试验证错误"""
    print("\n" + "="*60)
    print("测试验证错误响应格式")
    print("="*60)
    
    # 测试缺少必填字段
    response = requests.post(f"{BASE_URL}/login", json={
        "username": "testuser"
        # 缺少 password
    })
    print_response("8. 验证错误（缺少字段）", response)

if __name__ == "__main__":
    print("="*60)
    print("统一响应格式测试")
    print("="*60)
    
    jwt_token = test_success_response()
    test_error_response(jwt_token)
    test_validation_error()
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n所有响应都应该包含以下字段：")
    print("- code: 状态码（200=成功，其他=错误）")
    print("- message: 消息描述")
    print("- data: 数据（可选，成功时包含）")
    print("- timestamp: 时间戳（可选）")