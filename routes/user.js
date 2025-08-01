const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const auth = require('../middleware/auth');

// 用户注册
router.post('/register', userController.register);

// 用户登录
router.post('/login', userController.login);
router.post('/refresh-token', auth.verifyToken, userController.refreshToken);

// 获取用户列表（管理员权限）
router.get('/list', auth.verifyToken, auth.adminRequired, userController.getUsers);

// 修改用户角色（管理员权限）
router.put('/:id/role', auth.verifyToken, auth.adminRequired, userController.updateRole);

// 修改用户状态（管理员权限）
router.put('/:id/state', auth.verifyToken, auth.adminRequired, userController.updateState);

// 批量修改用户状态（管理员权限）
router.put('/batch-state', auth.verifyToken, auth.adminRequired, userController.batchUpdateState);

// 重置密码
router.post('/reset-password', auth.verifyToken, userController.resetPassword);

module.exports = router;