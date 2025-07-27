const express = require('express');
const router = express.Router();
const checkTaskController = require('../controllers/checkTaskController');
const auth = require('../middleware/auth');

// 创建检查任务（需要身份认证）
router.post('/', auth.verifyToken, checkTaskController.createCheckTask);

// 查询用户的检查任务列表（需要身份认证）
router.get('/user', auth.verifyToken, checkTaskController.getUserCheckTasks);

// 获取检查任务详情（需要身份认证）
router.get('/:taskId', auth.verifyToken, checkTaskController.getCheckTaskById);

// 更新质检任务状态（需要身份认证）
router.put('/:taskId/state', auth.verifyToken, checkTaskController.updateTaskState);

module.exports = router;