const express = require('express');
const router = express.Router();
const checkTaskController = require('../controllers/checkTaskController');
const auth = require('../middleware/auth');

// 创建检查任务（需要身份认证）
router.post('/', auth.verifyToken, checkTaskController.createCheckTask);

// 获取检查任务详情（需要身份认证）
router.get('/:taskId', auth.verifyToken, checkTaskController.getCheckTaskById);

module.exports = router;