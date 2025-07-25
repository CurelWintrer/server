const express = require('express');
const router = express.Router();
const imageController = require('../controllers/imageController');

// 分页查询图片
router.get('/', imageController.getImages);

// 查询单张图片
router.get('/:id', imageController.getImageById);

module.exports = router;