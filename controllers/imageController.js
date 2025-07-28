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

  // 图片上传接口
  static async uploadImage(req, res) {
    try {
      // 检查是否有文件上传
      if (!req.file) {
        return res.status(400).json({ code: 400, message: '请上传图片文件' });
      }

      const { imageID } = req.body;
      if (!imageID) {
        return res.status(400).json({ code: 400, message: '缺少imageID参数' });
      }

      try {
        // 获取图片存储路径
        // 查询图片的各级标题字段
          const [imgResult] = await pool.query(
            'SELECT First, Second, Third, Fourth, Fifth FROM image WHERE imageID = ?', 
            [imageID]
          );
          if (!imgResult || imgResult.length === 0) {
            return res.status(404).json({ code: 404, message: '未找到对应的图片记录' });
          }
          
          // 提取并过滤路径部分
          const { First, Second, Third, Fourth, Fifth } = imgResult[0];
          const pathParts = [First, Second, Third, Fourth, Fifth]
            .filter(part => part && part.trim() !== ''); // 过滤空值
          
          if (pathParts.length === 0) {
            return res.status(400).json({ code: 400, message: '图片路径信息不完整' });
          }
        // 计算文件MD5
        const md5 = crypto.createHash('md5').update(req.file.buffer).digest('hex');
        // 获取文件扩展名
        const ext = path.extname(req.file.originalname).toLowerCase();
        // 构建完整存储路径
        // 使用resolve处理可能的绝对路径问题，确保正确拼接
        const imgDir = pathParts.join(path.sep);
          const fullDir = path.resolve(__dirname, '../img', imgDir);
        const fileName = `${md5}${ext}`;
        const filePath = path.join(fullDir, fileName);

        // 确保目录存在
        await fs.mkdir(fullDir, { recursive: true });

        // 保存文件
          await fs.writeFile(filePath, req.file.buffer);

          // 更新数据库中的md5、imgName和imgPath
          const fullImgPath = path.join(imgDir, fileName);
          await pool.query(
            'UPDATE image SET md5 = ?, imgName = ?, imgPath = ? WHERE imageID = ?',
            [md5, fileName, fullImgPath, imageID]
          );

          // 返回成功响应
        res.json({
          message: '图片上传成功',
          imageID: imageID,
          md5: md5,
          fileName: fileName,
          filePath: path.join('img', imgDir, fileName)
        });
      } catch (dbError) {
        res.status(500).json({ code: 500, message: '数据库操作失败', error: dbError.message });
      }
    } catch (error) {
      res.status(500).json({ code: 500, message: '服务器内部错误', error: error.message });
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