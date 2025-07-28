const pool = require('../db');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

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

  // 图片上传
  static async uploadImage(req, res) {
    try {
      if (!req.file) {
        return res.status(400).json({ message: '未上传图片文件' });
      }

      const file = req.file;
      const fileBuffer = await fs.readFile(file.path);
      const md5Hash = crypto.createHash('md5').update(fileBuffer).digest('hex');
      const ext = path.extname(file.originalname);
      const newFileName = `${md5Hash}${ext}`;
      const targetPath = path.join(path.dirname(file.path), newFileName);

      // 重命名文件
      await fs.rename(file.path, targetPath);

      // 更新数据库信息
      const [result] = await pool.query(
        'UPDATE image SET imageName = ?, imagePath = ? WHERE imageID = ?',
        [newFileName, targetPath, req.body.imageID]
      );

      if (result.affectedRows === 0) {
        return res.status(404).json({ message: '未找到对应的图片记录' });
      }

      res.status(200).json({
        message: '图片上传并更新成功',
        imageID: req.body.imageID,
        md5: md5Hash,
        fileName: newFileName,
        filePath: targetPath
      });
    } catch (error) {
      res.status(500).json({ message: '图片上传失败', error: error.message });
    }
  }

  static async getImageStatistics(req, res) {
    try {
      // 1. 获取总图片数
      const [totalResult] = await pool.query('SELECT COUNT(*) AS total FROM image');
      const total = totalResult[0].total;

      // 2. 获取各状态数量
      const [stateResult] = await pool.query(
        'SELECT state, COUNT(*) AS count FROM image GROUP BY state'
      );
      const stateCounts = { 0: 0, 1: 0, 3: 0, 4: 0, 5: 0 };
      stateResult.forEach(item => {
        if ([0, 1, 3, 4, 5].includes(item.state)) {
          stateCounts[item.state] = item.count;
        }
      });

      // 3. 获取各级标题统计（总数和状态分布）
      const titleLevels = ['First', 'Second', 'Third', 'Fourth', 'Fifth'];
      const titleStatistics = {};

      for (const level of titleLevels) {
        // 标题总数
        const [titleTotalResult] = await pool.query(
          `SELECT ${level}, COUNT(*) AS count FROM image WHERE ${level} IS NOT NULL GROUP BY ${level}`
        );

        // 标题下各状态数量
        const [titleStateResult] = await pool.query(
          `SELECT ${level}, state, COUNT(*) AS count FROM image WHERE ${level} IS NOT NULL GROUP BY ${level}, state`
        );

        // 整理结果
        const levelStats = {};
        titleTotalResult.forEach(item => {
          levelStats[item[level]] = {
            total: item.count,
            stateCounts: { 0: 0, 1: 0, 3: 0, 4: 0, 5: 0 }
          };
        });

        titleStateResult.forEach(item => {
          if (levelStats[item[level]] && [0, 1, 3, 4, 5].includes(item.state)) {
            levelStats[item[level]].stateCounts[item.state] = item.count;
          }
        });

        titleStatistics[level] = levelStats;
      }

      res.json({
        total,
        stateCounts: {
          '0': stateCounts[0],
          '1': stateCounts[1],
          '2': stateCounts[3],
          '3': stateCounts[4],
          '4': stateCounts[5]
        },
        titleStatistics
      });
    } catch (error) {
      res.status(500).json({ message: '获取图片统计数据失败', error: error.message });
    }
  }

  // 按多级标题分页查询图片
  static async getImagesByTitles(req, res) {
    try {
      const { page = 1, limit = 10, First, Second, Third, Fourth, Fifth } = req.query;
      const offset = (page - 1) * limit;
      const queryParams = [];
      const conditions = [];

      // 动态构建查询条件
      if (First) {
        conditions.push('First = ?');
        queryParams.push(First);
      }
      if (Second) {
        conditions.push('Second = ?');
        queryParams.push(Second);
      }
      if (Third) {
        conditions.push('Third = ?');
        queryParams.push(Third);
      }
      if (Fourth) {
        conditions.push('Fourth = ?');
        queryParams.push(Fourth);
      }
      if (Fifth) {
        conditions.push('Fifth = ?');
        queryParams.push(Fifth);
      }

      // 基础查询语句
      let query = 'SELECT * FROM image';
      let countQuery = 'SELECT COUNT(*) AS total FROM image';

      // 添加条件
      if (conditions.length > 0) {
        query += ' WHERE ' + conditions.join(' AND ');
        countQuery += ' WHERE ' + conditions.join(' AND ');
      }

      // 添加分页
      query += ' LIMIT ? OFFSET ?';
      queryParams.push(parseInt(limit), parseInt(offset));

      // 执行查询
      const [images] = await pool.query(query, queryParams);
      const [totalResult] = await pool.query(countQuery, queryParams.slice(0, -2));
      const total = totalResult[0].total;

      res.json({
        total,
        page: parseInt(page),
        limit: parseInt(limit),
        images
      });
    } catch (error) {
      res.status(500).json({ message: '按标题查询图片失败', error: error.message });
    }
  }

  // 获取各级标题的所有类型
  static async getTitleTypes(req, res) {
    try {
      const titleLevels = ['First', 'Second', 'Third', 'Fourth', 'Fifth'];
      const titleTypes = {};

      // 并行查询各级标题的不重复值
      const queries = titleLevels.map(level => 
        pool.query(`SELECT DISTINCT ${level} FROM image WHERE ${level} IS NOT NULL`)
      );
      const results = await Promise.all(queries);

      // 整理结果
      titleLevels.forEach((level, index) => {
        titleTypes[level] = results[index][0].map(item => item[level]);
      });

      res.json(titleTypes);
    } catch (error) {
      res.status(500).json({ message: '获取标题类型失败', error: error.message });
    }
  }
}

module.exports = ImageController;