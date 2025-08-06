const express = require('express');
const router = express.Router();
const systemController = require('../controllers/systemController');
const auth = require('../middleware/auth');

// 获取软件版本号
router.get('/version', auth.verifyToken, systemController.getVersion);

module.exports = router;