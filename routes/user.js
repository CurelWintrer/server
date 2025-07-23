const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const auth = require('../middleware/auth');

// 用户注册
router.post('/register', userController.register);

// 用户登录
router.post('/login', userController.login);

// 获取用户列表（管理员权限）
router.get('/list', auth.adminRequired, userController.getUsers);

// 修改用户角色（管理员权限）
router.put('/:id/role', auth.adminRequired, userController.updateRole);

// 修改用户状态（管理员权限）
router.put('/:id/state', auth.adminRequired, userController.updateState);

module.exports = router;