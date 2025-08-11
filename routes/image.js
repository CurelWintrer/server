const express = require('express');
const router = express.Router();
const imageController = require('../controllers/imageController');
const auth = require('../middleware/auth');
const multer = require('multer');
// 配置临时存储目录
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// 添加新图片
router.post('/', auth.verifyToken, imageController.addImage);

// 分页查询图片
router.get('/', auth.verifyToken, imageController.getImages);
router.get('/statistics', auth.verifyToken, imageController.getImageStatistics);
router.get('/by-titles', auth.verifyToken, imageController.getImagesByTitles);
router.get('/title-types', auth.verifyToken, imageController.getTitleTypes);
router.get('/duplicate-elements', auth.verifyToken, imageController.getDuplicateChinaElements);
router.get('/title-tree', auth.verifyToken, imageController.getTitleTree);
router.get('/:id', auth.verifyToken, imageController.getImageById);
router.post('/update-captions', auth.verifyToken, imageController.updateImageCaptions);
router.post('/update-states', auth.verifyToken, imageController.updateImageStates);
router.post('/update-china-element-name', auth.verifyToken, imageController.updateImageChinaElementName);
router.post('/upload', auth.verifyToken, upload.single('image'), imageController.uploadImage);
router.post('/by-img-names', auth.verifyToken, imageController.getImagesByImgNames);

module.exports = router;