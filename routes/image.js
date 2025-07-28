const express = require('express');
const router = express.Router();
const imageController = require('../controllers/imageController');
const auth = require('../middleware/auth');
const multer = require('multer');
// 配置临时存储目录
const upload = multer({ dest: 'uploads/' });

// 分页查询图片
router.get('/', auth.verifyToken, imageController.getImages);
router.get('/statistics', auth.verifyToken, imageController.getImageStatistics);
router.get('/by-titles', auth.verifyToken, imageController.getImagesByTitles);
router.get('/title-types', auth.verifyToken, imageController.getTitleTypes);
router.get('/:id', auth.verifyToken, imageController.getImageById);

// 文件上传接口
router.post('/upload', auth.verifyToken, upload.single('image'), imageController.uploadImage);

module.exports = router;