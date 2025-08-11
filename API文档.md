# 后端API功能设计



## 0、获取软件版本号

**请求方法：**GET /api/system/version

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：** 无

**curl示例：**
```bash
curl -X GET http://localhost:3000/api/system/version \
  -H "Authorization: Bearer your_jwt_token"
```

**响应示例（200）：**
```json
{
  "success": true,
  "version": "1.0.0"
}
```

**错误代码：**
- 401：未授权或token无效
- 500：服务器内部错误


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

**错误代码：**
- 401：邮箱或密码错误
- 422：参数验证失败
- 500：服务器内部错误

## 3、刷新登录信息

**请求方法：**POST /api/user/refresh-token

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：** 无

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/user/refresh-token \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json"
```

**响应示例（200）：**
```json
{
  "token": "new_jwt_token_string",
  "user": {
    "id": 1,
    "name": "test",
    "email": "test@example.com",
    "role": 0
  }
}
```

**错误代码：**
- 401：无效的访问令牌或token已过期
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

## 8、查询用户的检查任务并更新任务信息

**请求方法：**GET /api/check-tasks/user

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**请求参数：**
- page: 页码（默认1）
- limit: 每页数量（默认10）

**功能说明：**
- 查询用户的检查任务列表
- 自动更新每个任务的checked_count（状态不等于1的图片数量）
- 如果checked_count等于imageCount，自动将任务state更新为2

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
      "state": 2,  // 如果checked_count等于imageCount，state为2
      "imageCount": 10,
      "checked_count": 10  // 状态不等于1的图片数量
    },
    ...
  ]
}
```

## 9、添加图片接口

**请求方法：**POST /api/image

**请求头：**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**请求参数：**
```json
{
  "First": "一级标题（可选）",
  "Second": "二级标题（可选）",
  "Third": "三级标题（可选）",
  "Fourth": "四级标题（可选）",
  "Fifth": "五级标题（可选）",
  "caption": "图片描述（可选）"
}
```

**注意：**至少需要提供一个标题参数（First/Second/Third/Fourth/Fifth）

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/image \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"First":"历史故事","Second":"政治与军事故事","caption":"这是一张历史图片"}'
```

**响应示例（201）：**
```json
{
  "message": "图片添加成功",
  "imageID": 123,
  "First": "历史故事",
  "Second": "政治与军事故事",
  "Third": null,
  "Fourth": null,
  "Fifth": null,
  "caption": "这是一张历史图片"
}
```

**错误代码：**
- 400：至少提供一个标题参数
- 401：未授权或token无效
- 500：服务器内部错误

## 10、文件上传接口

**请求方法：** POST /api/image/upload

**请求头：**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**请求参数：**
- image: 图片文件（form-data格式）
- imageID: 图片ID（form-data的text字段）

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/image/upload \
  -H "Authorization: Bearer your_jwt_token" \
  -F "image=@/path/to/your/image.jpg" \
  -F "imageID=123"
```

**响应示例（200）：**
```json
{
  "message": "图片上传并更新成功",
  "imageID": 123,
  "md5": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  "fileName": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6.jpg",
  "filePath": "uploads/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6.jpg"
}
```

**错误代码：**
- 400: 未上传图片文件
- 401: 未授权或token无效
- 404: 未找到对应的图片记录
- 500: 服务器内部错误

**错误代码：**
- 401：未授权或token无效
- 500：服务器内部错误

## 10、修改图片chinaElementName

**请求方法：** POST /api/image/update-china-element-name

**请求头：**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**请求参数：**
```json
{
  "imageID": 1,
  "chinaElementName": "新的中国元素名称"
}
```

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/image/update-china-element-name \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"imageID":1,"chinaElementName":"新的中国元素名称"}'
```

**响应示例（200）：**
```json
{
  "message": "chinaElementName更新成功",
  "imageID": 1,
  "newChinaElementName": "新的中国元素名称",
  "affectedRows": 1
}
```

**错误代码：**
- 400：必须提供imageID和chinaElementName
- 401：未授权或token无效
- 404：图片不存在
- 500：服务器内部错误


## 11、修改图片caption

**请求方法：** POST /api/image/update-captions

**请求头：**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**请求参数：**
```json
{
  "captions": [
    {
      "imageID": 1,
      "caption": "更新的图片描述1"
    },
    {
      "imageID": 2,
      "caption": "更新的图片描述2"
    }
  ]
}
```

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/image/update-captions \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"captions":[{"imageID":1,"caption":"更新的图片描述1"},{"imageID":2,"caption":"更新的图片描述2"}]}'
```

**响应示例（200）：**
```json
{
  "message": "caption更新成功",
  "results": [
    {
      "imageID": 1,
      "affectedRows": 1
    },
    {
      "imageID": 2,
      "affectedRows": 1
    }
  ]
}
```

**错误代码：**
- 400：参数格式错误或缺少必要字段
- 401：未授权或token无效
- 404：指定imageID的图片不存在
- 500：服务器内部错误

## 11、修改图片状态

**请求方法：** POST /api/image/update-states

**请求头：**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**请求参数：**
```json
{
  "states": [
    {
      "imageID": 1,
      "state": 1
    },
    {
      "imageID": 2,
      "state": 3
    }
  ]
}
```

**状态值说明：**
- 0: 未检查
- 1: 正在检查
- 3: 正在审核
- 4: 审核通过
- 5: 废弃

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/image/update-states \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"states":[{"imageID":1,"state":1},{"imageID":2,"state":3}]}'
```

**响应示例（200）：**
```json
{
  "message": "图片状态更新成功",
  "results": [
    {
      "imageID": 1,
      "affectedRows": 1,
      "newState": 1
    },
    {
      "imageID": 2,
      "affectedRows": 1,
      "newState": 3
    }
  ]
}
```

**错误代码：**
- 400：参数格式错误或状态值无效
- 401：未授权或token无效
- 404：指定imageID的图片不存在
- 500：服务器内部错误

## 9、重置密码接口

**请求方法：** POST /api/user/reset-password

**请求头：**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**请求参数：**
```json
{
  "currentPassword": "old_password",
  "newPassword": "new_password"
}
```

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/user/reset-password \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"currentPassword":"old_password","newPassword":"new_password"}'
```

**响应示例（200）：**
```json
{
  "message": "密码重置成功"
}
```

**错误代码：**
- 400：参数格式错误
- 401：未授权或当前密码错误
- 404：用户不存在
- 500：服务器内部错误


## 10、根据imgName批量查询图片接口

**请求方法：** POST /api/image/by-img-names

**请求头：**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**请求参数：**
```json
{
  "imgNames": ["abc123.jpg", "def456.png"]
}
```

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/image/by-img-names \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"imgNames":["abc123.jpg","def456.png"]}'
```

**响应示例（200）：**
```json
{
  "total": 2,
  "images": [
    {
      "imageID": 1,
      "imgName": "abc123.jpg",
      "imgPath": "path/to/image.jpg",
      "state": 0,
      ...
    },
    {
      "imageID": 2,
      "imgName": "def456.png",
      "imgPath": "path/to/another.jpg",
      "state": 1,
      ...
    }
  ]
}
```

**错误代码：**
- 400：参数格式错误或缺少必要字段
- 401：未授权或token无效
- 500：服务器内部错误

## 11、获取标题树接口

#### 请求方法
GET /api/image/title-tree

#### 请求头
Authorization: Bearer {token}

#### 响应格式
```json
{
  "success": true,
  "titleTree": [
    {
      "id": 1,
      "title": "一级标题1",
      "children": [
        {
          "id": 2,
          "title": "二级标题1-1",
          "children": []
        },
        {
          "id": 3,
          "title": "二级标题1-2",
          "children": [
            {
              "id": 4,
              "title": "三级标题1-2-1",
              "children": []
            }
          ]
        }
      ]
    },
    {
      "id": 5,
      "title": "一级标题2",
      "children": []
    }
  ]
}
```

#### 请求示例
```curl
curl -X GET -H "Authorization: Bearer {token}" http://localhost:3000/api/image/title-tree
```

#### 错误码
- 401: 未授权或token无效
- 500: 服务器内部错误

## 12、获取检查任务详情

**请求方法：** POST /api/image/update-captions

**请求头：**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**请求参数：**
```json
{
  "captions": [
    {
      "imageID": 1,
      "caption": "更新的图片描述1"
    },
    {
      "imageID": 2,
      "caption": "更新的图片描述2"
    }
  ]
}
```

**curl示例：**
```bash
curl -X POST http://localhost:3000/api/image/update-captions \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"captions":[{"imageID":1,"caption":"更新的图片描述1"},{"imageID":2,"caption":"更新的图片描述2"}]}'
```

**响应示例（200）：**
```json
{
  "message": "caption更新成功",
  "results": [
    {
      "imageID": 1,
      "affectedRows": 1
    },
    {
      "imageID": 2,
      "affectedRows": 1
    }
  ]
}
```

**错误代码：**
- 400：参数格式错误或缺少必要字段
- 401：未授权或token无效
- 404：指定imageID的图片不存在
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

## 10、更新质检任务状态

**请求方法：**PUT /api/check-tasks/:taskId/state

**请求头：**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**路径参数：**
- taskId: 检查任务ID

**请求参数：**
```json
{
  "state": 1
}
```

## 11、放弃检查任务

**请求方法：**DELETE /api/check-tasks/:taskId

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**路径参数：**
- taskId: 检查任务ID

**请求参数：** 无

**curl示例：**
```bash
curl -X DELETE http://localhost:3000/api/check-tasks/1 \
  -H "Authorization: Bearer your_jwt_token"
```

**响应示例（200）：**
```json
{
  "message": "检查任务已放弃",
  "taskId": 1
}
```

**错误代码：**
- 401：未授权或token无效
- 404：检查任务不存在或不属于当前用户
- 500：服务器内部错误


**参数说明：**
- state: 任务状态（0: 未开始, 1: 进行中, 2: 已完成）

**curl示例：**
```bash
curl -X PUT http://localhost:3000/api/check-tasks/1/state \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"state": 1}'
```

**响应示例（200）：**
```json
{
  "checkImageListID": 1,
  "userID": 2,
  "state": 1,
  "imageCount": 10,
  "checked_count": 0,
  "path": "历史故事/政治与军事故事/政治谋略"
}
```

**错误代码：**
- 400：无效的状态值
- 401：未授权或token无效
- 404：检查任务不存在或不属于当前用户
- 500：服务器内部错误

## 图片查询

### 9.1 分页查询图片

**请求方法：**GET /api/image

**请求参数：**

- page: 页码（默认1）
- limit: 每页数量（默认10）

**curl示例：**

```bash
curl -X GET "http://localhost:3000/api/image?page=1&limit=10"
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

**请求方法：**GET /api/image/{id}

**路径参数：**

- id: 图片ID

**curl示例：**

```bash
curl -X GET http://localhost:3000/api/image/1
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



### 11、获取图片统计数据
- 请求方法：GET
- 请求URL：/api/image/statistics
- 请求头：
  Authorization: Bearer {token}
- 响应示例：
```json
{
  "total": 120,
  "stateCounts": {
    "0": 30,
    "1": 25,
    "2": 20,
    "3": 40,
    "4": 5,
    "5": 10,
  },
  "titleStatistics": {
    "First": {
      "标题1": {
        "total": 50,
        "stateCounts": {
          "0": 10,
          "1": 15,
          "2": 5,
          "3": 18,
          "4": 2,
          "5": 10,
        }
      },
      // ... 其他一级标题统计
    },
    // ... 其他级别标题统计
  }
}
```
- 错误码：
  401: 未授权或token无效
  500: 服务器内部错误


### 12、按多级标题查询图片
- 请求方法：GET
- 请求URL：/api/image/by-titles
- 请求头：
  Authorization: Bearer {token}

#### 请求参数
| 参数名 | 类型 | 是否必填 | 描述 |
|--------|------|----------|------|
| page | int | 否 | 页码，默认1 |
| limit | int | 否 | 每页数量，默认10 |
| First | string | 否 | 一级标题 |
| Second | string | 否 | 二级标题 |
| Third | string | 否 | 三级标题 |
| Fourth | string | 否 | 四级标题 |
| Fifth | string | 否 | 五级标题 |
| goodState | boolean | 否 | 可选参数，若为true则不返回状态为5的图片，默认返回所有图片 |

#### 响应格式
```json
{
  "total": 100,
  "page": 1,
  "limit": 10,
  "images": [
    {
      "imageID": 1,
      "First": "标题1",
      "Second": "标题2",
      ...
      "state": 0
    },
    ...
  ]
}
```

#### 请求示例
```curl
curl -X GET "http://localhost:3000/api/image/by-titles?First=动物&goodState=true"```

- 错误码：
  401: 未授权或token无效
  500: 服务器内部错误


### 13、获取各级标题类型
- 请求方法：GET
- 请求URL：/api/image/title-types
- 请求头：
  Authorization: Bearer {token}
- 响应示例：
```json
{
  "First": ["标题1", "标题2", "标题3"],
  "Second": ["子标题1", "子标题2", "子标题3"],
  "Third": ["三级标题A", "三级标题B"],
  "Fourth": [],
  "Fifth": []
}
```
- 错误码：
  401: 未授权或token无效
  500: 服务器内部错误



## 图片相关API

### 查询重复或类似的chinaElementName
**请求方法：**GET /api/image/duplicate-elements

**请求头：**
```
Authorization: Bearer <jwt_token>
```

**功能描述：** 查询image表中chinaElementName字段的重复或类似值，返回互相重复的图片分组

**curl示例：**
```bash
curl -X GET http://localhost:3000/api/image/duplicate-elements \
  -H "Authorization: Bearer your_jwt_token"
```

**响应示例（200）：**
```json
{
  "message": "查询成功",
  "totalGroups": 2,
  "duplicates": [
    {
      "chinaElementName": "故宫",
      "images": [
        {"imageID": 1, "chinaElementName": "故宫"},
        {"imageID": 5, "chinaElementName": "故宫博物院"}
      ]
    },
    {
      "chinaElementName": "长城",
      "images": [
        {"imageID": 3, "chinaElementName": "长城"},
        {"imageID": 7, "chinaElementName": "万里长城"}
      ]
    }
  ]
}
```

**错误代码：**
- 401：无效的访问令牌或token已过期
- 500：服务器内部错误


