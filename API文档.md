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



## 7、拉取检查任务

**请求方法：**POST /api/check-tasks

**请求头：**

```
Authorization: Bearer <jwt_token>
```

**请求参数：**

```json
{
  "First": "一级标题（可选）",
  "Second": "二级标题（可选）",
  "Third": "三级标题（可选）",
  "Fourth": "四级标题（可选）",
  "Fifth": "五级标题（可选）",
  "count": 10
}
```

**curl示例：**

```bash
curl -X POST http://localhost:3000/api/check-tasks \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"First":"历史故事","Second":"政治与军事故事","Third":"政治谋略","count":10}'
```

**响应示例（201）：**

```json
{
  "checkImageListID": 1,
  "userID": 2,
  "imageCount": 10,
  "assignedImages": 10
}
```

**注意：**至少需要提供一个标题参数（First/Second/Third/Fourth/Fifth）

**错误代码：**

- 400：至少提供一个标题参数且count必须为正数
- 401：未授权或token无效
- 404：没有找到符合条件的图片
- 500：服务器内部错误

## 8、查询用户的检查任务

**请求方法：**GET /api/check-tasks/user

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：**
- page: 页码（默认1）
- limit: 每页数量（默认10）

**curl示例：**
```bash
curl -X GET "http://localhost:3000/api/check-tasks/user?page=1&limit=10" \
  -H "Authorization: Bearer your_jwt_token"
```

**响应示例（200）：**
```json
{
  "total": 5,
  "page": 1,
  "limit": 10,
  "tasks": [
    {
      "checkImageListID": 1,
      "userID": 2,
      "state": 0,
      "imageCount": 10,
      "checked_count": 3
    },
    ...
  ]
}
```

**错误代码：**
- 401：未授权或token无效
- 500：服务器内部错误

## 9、获取检查任务详情

**请求方法：**GET /api/check-tasks/:taskId

**请求头：**

```
Authorization: Bearer <jwt_token>
```

**路径参数：**

- taskId: 检查任务ID

**curl示例：**

```bash
curl -X GET http://localhost:3000/api/check-tasks/1 \
  -H "Authorization: Bearer your_jwt_token"
```

**响应示例（200）：**

```json
{
  "task": {
    "checkImageListID": 1,
    "userID": 2,
    "state": 0,
    "imageCount": 10,
    "checked_count": 0
  },
  "images": [
    {
      "imageID": 1,
      "imgName": "example.jpg",
      "imgPath": "/img/history/politics/1.jpg",
      "First": "历史故事",
      "Second": "政治与军事故事",
      "Third": "政治谋略",
      "imageListID": 1
    },
    ...
  ]
}
```

**错误代码：**

- 401：未授权或token无效
- 404：检查任务不存在
- 500：服务器内部错误

## 

## 9、图片查询

### 9.1 分页查询图片

**请求方法：**GET /api/images

**请求参数：**

- page: 页码（默认1）
- limit: 每页数量（默认10）

**curl示例：**

```bash
curl -X GET "http://localhost:3000/api/images?page=1&limit=10"
```

**响应示例（200）：**

```json
{
  "total": 100,
  "page": 1,
  "limit": 10,
  "images": [
    {
      "imageID": 1,
      "md5": "abc123def456",
      "imgName": "example.jpg",
      "imgPath": "/uploads/example.jpg",
      "chinaElementName": "青花瓷",
      "caption": "这是一个青花瓷图片"
    },
    ...
  ]
}
```

**错误代码：**

- 500：服务器内部错误

- 

### 9.2 查询单张图片

**请求方法：**GET /api/images/{id}

**路径参数：**

- id: 图片ID

**curl示例：**

```bash
curl -X GET http://localhost:3000/api/images/1
```

**响应示例（200）：**

```json
{
  "imageID": 1,
  "md5": "abc123def456",
  "First": "元素1",
  "Second": "元素2",
  "Third": "元素3",
  "Forth": "元素4",
  "Fifth": "元素5",
  "imgName": "example.jpg",
  "imgPath": "/uploads/example.jpg",
  "chinaElementName": "青花瓷",
  "caption": "这是一个青花瓷图片",
  "state": 0,
  "imageListID": 1
}
```

**错误代码：**

- 404：图片不存在
- 500：服务器内部错误



##


