const pool = require('../db');

class ImageController {
  // 分页查询图片
  static async getImages(req, res) {
    try {
      const { page = 1, limit = 10 } = req.query;
      const offset = (page - 1) * limit;

      const [images] = await pool.query(
        'SELECT * FROM image LIMIT ? OFFSET ?',
        [parseInt(limit), parseInt(offset)]
      );
      const [totalResult] = await pool.query('SELECT COUNT(*) AS total FROM image');
      const total = totalResult[0].total;

      res.json({
        total,
        page: parseInt(page),
        limit: parseInt(limit),
        images
      });
    } catch (error) {
      res.status(500).json({ message: '获取图片失败', error: error.message });
    }
  }

  // 查询单张图片
  static async getImageById(req, res) {
    try {
      const { id } = req.params;
      const [images] = await pool.query('SELECT * FROM image WHERE imageID = ?', [id]);

      if (images.length === 0) {
        return res.status(404).json({ message: '图片不存在' });
      }

      res.json(images[0]);
    } catch (error) {
      res.status(500).json({ message: '获取图片失败', error: error.message });
    }
  }
}

module.exports = ImageController;