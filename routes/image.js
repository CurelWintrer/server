const express = require('express');
const router = express.Router();
const imageController = require('../controllers/imageController');
const auth = require('../middleware/auth');

// 分页查询图片
router.get('/', auth.verifyToken, imageController.getImages);

// 查询单张图片
router.get('/:id', auth.verifyToken, imageController.getImageById);

module.exports = router;