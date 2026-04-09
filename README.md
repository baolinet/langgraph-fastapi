# langgraph-fastapi 项目文档

## 📖 项目简介

基于 FastAPI + SQLAlchemy 的用户管理系统，提供双认证机制（JWT + API Key）和完整的用户管理功能。

---

## 🚀 快速开始

### 方式一：使用脚本（推荐）⭐

```bash
# 首次运行添加执行权限
chmod +x run.sh
chmod +x run_tests.sh

# 启动服务器
./run.sh

# 运行所有测试
./run_tests.sh
```

**脚本功能：**
- ✅ `run.sh` - 自动检查环境、端口、初始化数据库并启动服务器
- ✅ `run_tests.sh` - 自动检查服务器状态、初始化测试数据并运行所有测试

### 方式二：手动操作

```bash
# 1. 安装依赖
python -m pip install -r requirements.txt

# 2. 初始化数据库
python tests/init_db.py

# 3. 启动服务器
uv run uvicorn main:app --reload

# 4. 运行测试
python tests/test_auth.py && python tests/test_response_format.py && python tests/test_users.py
```

### 5. 访问 API 文档

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **健康检查**: http://127.0.0.1:8000/health

---

## 🔐 双认证机制

### JWT Token（前端 Web 应用）
- **用途**: 前端 Web/Mobile 应用登录
- **接口**: `POST /login`
- **有效期**: 1 小时
- **使用方式**: `Authorization: Bearer <token>`

### API Key（后端服务调用）
- **用途**: 后端服务、脚本、第三方系统
- **接口**: `POST /api-key`
- **前置条件**: 先通过 `POST /login` 获取 JWT Token
- **有效期**: 24 小时
- **使用方式**: `api-auth-key: <key>`

### 使用示例

#### 1. JWT Token 登录

```bash
# 登录获取 JWT Token
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 响应示例
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "username": "admin",
  "user_id": 1,
  "full_name": "Admin User"
}

# 使用 JWT Token 访问受保护接口
curl -X GET "http://127.0.0.1:8000/api/users/" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### 2. API Key 认证

```bash
# 先登录获取 JWT Token
JWT_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')

# 使用 JWT 创建 API Key
curl -X POST "http://127.0.0.1:8000/api-key" \
  -H "Authorization: Bearer ${JWT_TOKEN}"

# 响应示例
{
  "api_auth_key": "abc123xyz...",
  "created_at": "2024-01-01T00:00:00",
  "expires_at": "2024-01-02T00:00:00"
}

# 使用 API Key 访问受保护接口
curl -X GET "http://127.0.0.1:8000/api/users/" \
  -H "api-auth-key: <your_api_key>"
```

#### 3. 撤销 API Key

```bash
curl -X POST "http://127.0.0.1:8000/api-key/revoke" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -G \
  --data-urlencode "api_auth_key=abc123xyz..."
```

---

## 📋 API 接口清单

### 认证接口

| 方法 | 端点 | 说明 | 认证方式 |
|------|------|------|----------|
| POST | `/login` | 用户登录获取 JWT Token | 无 |
| POST | `/api-key` | 创建 API Key | JWT |
| POST | `/api-key/revoke` | 撤销 API Key | JWT |

### 用户管理接口

| 方法 | 端点 | 说明 | 认证方式 |
|------|------|------|----------|
| GET | `/api/users/` | 获取用户列表（分页） | API Key |
| GET | `/api/users/{username}` | 获取单个用户详情 | API Key |
| GET | `/api/users/search/fullname/{fullname}` | 根据全名模糊查询 | API Key |
| POST | `/api/users/` | 创建新用户 | API Key |
| PUT | `/api/users/{username}` | 更新用户信息 | API Key |
| DELETE | `/api/users/{username}` | 删除用户 | API Key |
| POST | `/api/users/{username}/activate` | 激活用户 | API Key |
| POST | `/api/users/{username}/deactivate` | 禁用用户 | API Key |

### 其他接口

| 方法 | 端点 | 说明 | 认证方式 |
|------|------|------|----------|
| GET | `/health` | 健康检查 | 无 |

---

## 📦 统一响应格式

所有 API 接口返回统一的 JSON 格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... },
  "timestamp": 1775212372
}
```

### 字段说明

- **code**: 状态码（200=成功，其他=错误）
- **message**: 消息描述
- **data**: 数据（可选，成功时包含）
- **timestamp**: 时间戳（可选）

### 成功响应示例

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "username": "admin",
    "user_id": 1,
    "full_name": "Admin User"
  },
  "timestamp": 1775212372
}
```

### 错误响应示例

```json
{
  "code": 404,
  "message": "用户名 admin 不存在",
  "data": null,
  "timestamp": 1775212372
}
```

---

## 🧪 测试指南

### 运行所有测试

```bash
# 1. 确保服务器正在运行
uv run uvicorn main:app --reload

# 2. 初始化测试数据（首次运行）
python tests/init_db.py

# 3. 运行所有测试
python tests/test_auth.py
python tests/test_response_format.py
python tests/test_users.py

# 或一次性运行所有
python tests/test_auth.py && python tests/test_response_format.py && python tests/test_users.py
```

### 测试文件说明

| 文件 | 说明 | 覆盖接口 |
|------|------|----------|
| `tests/test_auth.py` | 双认证机制测试 | 登录、API Key、未授权访问 |
| `tests/test_response_format.py` | 统一响应格式测试 | 成功/错误响应格式验证 |
| `tests/test_users.py` | 用户管理接口完整测试 | 用户 CRUD、状态管理、模糊查询 |
| `tests/init_db.py` | 数据库初始化脚本 | 创建测试数据 |

### 测试覆盖率

**接口总数**: 12 个  
**已测试接口**: 12 个  
**测试覆盖率**: **100%** ✅

详细报告请查看：[测试覆盖率报告](#测试覆盖率报告)

---

## 🗄️ 数据库设计

### User 表（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String | 用户名（唯一） |
| email | String | 邮箱（唯一） |
| password_hash | String | 密码哈希 |
| full_name | String | 全名 |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### AuthToken 表（API Key）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户 ID（逻辑关联） |
| api_auth_key | String | API Key（唯一） |
| created_at | DateTime | 创建时间 |
| expires_at | DateTime | 过期时间 |

**注意**: 两个表之间没有 ForeignKey 约束，采用逻辑关联。

---

## 🔧 配置说明

### 环境变量（可选）

通过 `.env` 文件或环境变量配置：

```env
# 数据库
DATABASE_URL=sqlite:///./app.db

# JWT 配置
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRE_MINUTES=60

# 其他配置
DEBUG=True
```

---

## 📊 测试覆盖率报告

### 接口覆盖率

| 接口类别 | 接口数 | 已测试 | 覆盖率 |
|----------|--------|--------|--------|
| 认证接口 | 3 | 3 | 100% |
| 用户管理接口 | 8 | 8 | 100% |
| 其他接口 | 1 | 1 | 100% |
| **总计** | **12** | **12** | **100%** |

### 测试场景覆盖

#### 成功场景
- ✅ JWT Token 登录成功
- ✅ API Key 创建和使用成功
- ✅ 用户 CRUD 操作成功
- ✅ 用户状态变更成功
- ✅ 模糊查询匹配成功

#### 错误场景
- ✅ 401 未授权访问（缺少/无效 API Key）
- ✅ 404 资源不存在（用户、API Key）
- ✅ 400 业务错误（重复用户名/邮箱）
- ✅ 422 验证错误（缺少字段、格式错误）

#### 边界场景
- ✅ 重复数据检测
- ✅ 删除后验证不存在
- ✅ 撤销后 API Key 失效验证
- ✅ 分页参数测试

---

## 🛠️ 常见问题

### 1. 端口被占用

**错误**: `ERROR: [Errno 48] Address already in use`

**解决**:
```bash
# 杀死占用 8000 端口的进程
lsof -ti:8000 | xargs kill -9

# 等待 2 秒后重启
sleep 2 && uv run uvicorn main:app --reload
```

### 2. 数据库不存在

**错误**: `sqlite3.OperationalError: no such table: users`

**解决**:
```bash
python tests/init_db.py
```

### 3. 测试失败：无法获取 API Key

**原因**: 测试用户不存在或密码错误

**解决**:
```bash
# 重新初始化测试数据
python tests/init_db.py

# 或先登录再创建 API Key
JWT_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.data.access_token')

curl -X POST http://127.0.0.1:8000/api-key \
  -H "Authorization: Bearer ${JWT_TOKEN}"
```

---

## 📚 技术栈

- **FastAPI** 0.104.1 - Web 框架
- **SQLAlchemy** 2.0.23 - ORM
- **Pydantic** 2.5.0 - 数据验证
- **SQLite** - 数据库
- **PyJWT** - JWT 认证
- **python-multipart** - 表单支持
- **uvicorn** - ASGI 服务器

---

## 📝 开发笔记

### 1. 为什么创建接口使用 201 而不是 200？

根据 RESTful API 规范，创建资源应返回 `201 Created`，表示新资源已成功创建。这比通用的 `200 OK` 语义更明确，便于客户端区分不同类型的成功操作。

### 2. 为什么移除 ForeignKey 约束？

采用逻辑关联而非数据库级 ForeignKey，可以：
- 提高灵活性（如用户删除后保留 API Key 记录）
- 减少数据库耦合
- 便于水平扩展

### 3. 为什么使用 username 而不是 user_id？

- 更用户友好（易读易记）
- 避免暴露内部 ID
- 符合 RESTful 资源命名最佳实践

---

## 🎯 最佳实践

1. **统一响应格式**: 所有接口使用 `success_response()` 和 `error_response()`
2. **服务层封装**: 业务逻辑放在 `services/` 目录
3. **依赖注入**: 使用 FastAPI 的 Depends 机制
4. **类型注解**: 所有函数使用 Python type hints
5. **错误处理**: 使用 try-except 捕获业务异常
6. **时间戳**: 使用 timezone-aware 的 datetime
7. **测试覆盖**: 所有新功能必须包含测试用例

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- **项目地址**: `/Users/bao.li001/gitcode/langgraph-fastapi`
- **文档版本**: v1.0
- **最后更新**: 2026 年 4 月 3 日

---

## 📋 目录结构

```
langgraph-fastapi/
├── main.py                 # 应用入口
├── database.py             # 数据库配置
├── config.py               # 配置管理
├── requirements.txt        # 依赖列表
├── README.md               # 本文档
├── models/                 # 数据模型
│   ├── user.py
│   └── auth.py
├── schemas/                # Pydantic 模型
│   ├── user.py
│   └── auth.py
├── services/               # 业务服务层
│   ├── user_service.py
│   └── auth_service.py
├── routers/                # API 路由
│   ├── users.py
│   └── auth.py
├── utils/                  # 工具函数
│   ├── response.py         # 统一响应格式
│   └── exceptions.py       # 异常处理
└── tests/                  # 测试文件
    ├── test_auth.py
    ├── test_response_format.py
    ├── test_users.py
    ├── init_db.py
    └── init_test_data.py
```

---

**🎉 感谢使用 langgraph-fastapi！**
