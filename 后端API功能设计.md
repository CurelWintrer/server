# 后端API功能设计



## 1、用户注册

**请求方法：**POST /api/user/register

**请求参数：**
```json
{
  "name": "用户名",
  "email": "user@example.com",
  "password": "password123",
  "role": 0
}
```

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/user/register \
  -H "Content-Type: application/json" \
  -d '{"name":"test","email":"test@example.com","password":"123456","role":0}'
```

**响应示例（200）：**
```json
{
  "id": 1,
  "name": "test",
  "email": "test@example.com",
  "role": 0,
  "state": 1,
  "createdAt": "2024-05-20T10:00:00Z"
}
```

**错误代码：**
- 400：邮箱已被注册
- 422：参数验证失败
- 500：服务器内部错误



## 2、用户登录

**请求方法：**POST /api/user/login

**请求参数：**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**curl示例（带JWT返回）：**

```bash
curl -X POST http://localhost:3000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'
```

**响应示例（200）：**
```json
{
  "token": "jwt_token_string",
  "user": {
    "id": 1,
    "name": "test",
    "email": "test@example.com",
    "role": 0
  }
}
```

**错误代码：**
- 401：邮箱或密码错误
- 422：参数验证失败
- 500：服务器内部错误



## 3、查看所有用户信息

**请求方法：**GET /api/user/list

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：**
```json
{
  "role": 1
}
```

**curl示例：**
```bash
curl -X GET http://localhost:3000/api/user/list \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json"
```

**响应示例（200）：**
```json
{
  "users": [
    {
      "id": 1,
      "name": "admin",
      "email": "admin@example.com",
      "role": 1,
      "state": 1
    }
  ],
  "total": 1
}
```

**错误代码：**
- 403：权限不足
- 500：服务器内部错误



## 4、修改用户角色

**请求方法：**PUT /api/user/{userID}/role

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：**
```json
{
  "role": 1
}
```

**curl示例：**
```bash
curl -X PUT http://localhost:3000/api/user/2/role \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"role":1}'
```

**响应示例（200）：**
```json
{
  "id": 2,
  "name": "user02",
  "email": "user02@example.com",
  "role": 1,
  "state": 1
}
```

**错误代码：**
- 403：权限不足
- 404：用户不存在
- 422：参数验证失败
- 500：服务器内部错误

## 5、修改用户状态

**请求方法：**PUT /api/user/{userID}/state

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：**
```json
{
  "state": 1
}
```

**curl示例：**
```bash
curl -X PUT http://localhost:3000/api/user/3/state \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"state":0}'
```

**响应示例（200）：**
```json
{
  "id": 3,
  "name": "user03",
  "email": "user03@example.com",
  "role": 0,
  "state": 0
}
```

**错误代码：**
- 403：权限不足
- 404：用户不存在
- 422：参数验证失败
- 500：服务器内部错误



## 6、批量修改用户状态

**请求方法：**PUT /api/user/batch-state

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：**
```json
{
  "userIDs": [1, 2, 3],
  "state": 1
}
```

**curl示例：**
```bash
curl -X PUT http://localhost:3000/api/user/batch-state \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"userIDs":[1,2,3],"state":1}'
```

**响应示例（200）：**
```json
{
  "updatedCount": 3,
  "users": [
    {
      "id": 1,
      "name": "user01",
      "email": "user01@example.com",
      "role": 0,
      "state": 1
    },
    {
      "id": 2,
      "name": "user02",
      "email": "user02@example.com",
      "role": 0,
      "state": 1
    },
    {
      "id": 3,
      "name": "user03",
      "email": "user03@example.com",
      "role": 0,
      "state": 1
    }
  ]
}
```

**错误代码：**
- 400：用户ID列表不能为空
- 403：权限不足
- 422：参数验证失败
- 500：服务器内部错误



## 7、获取单个图片信息

**请求方法：**GET /api/images/{imageID}

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**curl示例：**
```bash
curl -X GET http://localhost:3000/api/images/123 \
  -H "Authorization: Bearer your_jwt_token"
```

**响应示例（200）：**
```json
{
  "id": 123,
  "name": "example.jpg",
  "size": 204800,
  "state": 1,
  "imageListID": 5,
  "createdAt": "2024-05-20T10:00:00Z"
}
```

**错误代码：**
- 403：权限不足
- 404：图片不存在
- 500：服务器内部错误





## 8、拉取检查任务

**请求方法：**POST /api/image-lists

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：**
```json
{
  "image_count": 10
}
```

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/image-lists \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"image_count":10}'
```

**响应示例（200）：**
```json
{
  "id": 5,
  "assignedTo": 1,
  "totalImages": 10,
  "createdAt": "2024-05-20T10:00:00Z",
  "images": [
    {
      "id": 123,
      "name": "example1.jpg",
      "size": 204800
    }
  ]
}
```

**错误代码：**
- 400：可用图片不足
- 403：权限不足
- 500：服务器内部错误



## 9、更新检查任务状态

**请求方法：**PUT /api/image-lists/{imageListID}

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：**
```json
{
  "images": [
    {
      "id": 123,
      "state": 2
    }
  ]
}
```

**curl示例：**
```bash
curl -X PUT http://localhost:3000/api/image-lists/5 \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"images":[{"id":123,"state":2}]}'
```

**响应示例（200）：**
```json
{
  "updatedCount": 1,
  "success": true
}
```

**错误代码：**
- 400：任务状态不匹配
- 403：权限不足
- 404：任务不存在
- 500：服务器内部错误





