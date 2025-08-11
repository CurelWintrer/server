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
  //图片状态统计
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
        if ([0, 1, 2, 3, 4].includes(item.state)) {
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
          if (levelStats[item[level]] && [0, 1, 2, 3, 4].includes(item.state)) {
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
          '2': stateCounts[2],
          '3': stateCounts[3],
          '4': stateCounts[4]
        },
        titleStatistics
      });
    } catch (error) {
      res.status(500).json({ message: '获取图片统计数据失败', error: error.message });
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
        const imgDir = pathParts.join('/');
        const fullDir = path.resolve(__dirname, '../img', imgDir);
        const fileName = `${md5}${ext}`;
        const filePath = path.join(fullDir, fileName);

        // 确保目录存在
        await fs.mkdir(fullDir, { recursive: true });

        // 保存文件
        await fs.writeFile(filePath, req.file.buffer);

        // 使用正斜杠构造路径以确保跨平台一致性
        const fullImgPath = `${imgDir}/${fileName}`;
        await pool.query(
          'UPDATE image SET md5 = ?, imgName = ?, imgPath = ? WHERE imageID = ?',
          [md5, fileName, fullImgPath, imageID]
        );

        // 获取更新后的记录以确保返回数据库中的imgPath
        const [updatedImage] = await pool.query(
          'SELECT imgPath FROM image WHERE imageID = ?',
          [imageID]
        );

        // 返回成功响应
        res.json({
          message: '图片上传成功',
          imageID: imageID,
          md5: md5,
          fileName: fileName,
          imgPath: updatedImage[0].imgPath
        });
      } catch (dbError) {
        res.status(500).json({ code: 500, message: '数据库操作失败', error: dbError.message });
      }
    } catch (error) {
      res.status(500).json({ code: 500, message: '服务器内部错误', error: error.message });
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

      // 处理goodState参数，过滤状态为5的图片
      const { goodState } = req.query;
      const isGoodState = goodState === 'true';
      if (isGoodState) {
        conditions.push('state != 4');
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


  static async updateImageStates(req, res) {
    try {
      const { states } = req.body;
      
      if (!states || !Array.isArray(states) || states.length === 0) {
        return res.status(400).json({ message: '请提供有效的图片ID和state数组' });
      }
      
      // 验证状态值是否有效
      const validStates = [0, 1, 2, 3, 4];
      for (const item of states) {
        if (!item.imageID || item.state === undefined || !validStates.includes(item.state)) {
          return res.status(400).json({ message: '每个state项必须包含有效的imageID和state值(0,1,2,3,4)' });
        }
      }
      
      const connection = await pool.getConnection();
      await connection.beginTransaction();
      
      const results = [];
      for (const item of states) {
        // 检查图片是否存在
        const [image] = await connection.query('SELECT imageID FROM image WHERE imageID = ?', [item.imageID]);
        if (image.length === 0) {
          await connection.rollback();
          connection.release();
          return res.status(404).json({ message: `图片不存在，imageID: ${item.imageID}` });
        }
        
        const [result] = await connection.query(
          'UPDATE image SET state = ? WHERE imageID = ?',
          [item.state, item.imageID]
        );
        
        results.push({
          imageID: item.imageID,
          affectedRows: result.affectedRows,
          newState: item.state
        });
      }
      
      await connection.commit();
      connection.release();
      
      res.json({
        message: '图片状态更新成功',
        results
      });
    } catch (error) {
      res.status(500).json({ message: '更新图片状态失败', error: error.message });
    }
  }

  static async updateImageCaptions(req, res) {
    try {
      const { captions } = req.body;

      if (!captions || !Array.isArray(captions) || captions.length === 0) {
        return res.status(400).json({ message: '请提供有效的图片ID和caption数组' });
      }

      // 验证每个元素是否包含imageID和caption
      for (const item of captions) {
        if (!item.imageID || item.caption === undefined) {
          return res.status(400).json({ message: '每个caption项必须包含imageID和caption字段' });
        }
      }

      const connection = await pool.getConnection();
      await connection.beginTransaction();

      const results = [];
      for (const item of captions) {
        // 检查图片是否存在
        const [image] = await connection.query('SELECT imageID FROM image WHERE imageID = ?', [item.imageID]);
        if (image.length === 0) {
          await connection.rollback();
          connection.release();
          return res.status(404).json({ message: `图片不存在，imageID: ${item.imageID}` });
        }

        const [result] = await connection.query(
          'UPDATE image SET caption = ? WHERE imageID = ?',
          [item.caption, item.imageID]
        );

        results.push({
          imageID: item.imageID,
          affectedRows: result.affectedRows,
          newCaption: item.caption
        });
      }

      await connection.commit();
      connection.release();

      res.json({
        message: 'caption更新成功',
        results
      });
    } catch (error) {
      res.status(500).json({ message: '更新caption失败', error: error.message });
    }
  }

    // 根据imgName字段批量查询图片
  static async getImagesByImgNames(req, res) {
    try {
      const { imgNames } = req.body;

      if (!imgNames || !Array.isArray(imgNames) || imgNames.length === 0) {
        return res.status(400).json({ code: 400, message: '请提供有效的imgNames数组' });
      }

      // 构建IN查询条件
      const placeholders = imgNames.map(() => '?').join(',');
      const query = `SELECT * FROM image WHERE imgName IN (${placeholders})`;

      const [images] = await pool.query(query, imgNames);

      res.json({
        total: images.length,
        images
      });
    } catch (error) {
      res.status(500).json({ code: 500, message: '按imgName批量查询图片失败', error: error.message });
    }
  }

  // 获取标题树
  static async getTitleTree(req, res) {
    try {
      // 查询所有标题，包含remark字段
      const [allTitles] = await pool.query('SELECT imageTitleID, title, parentID, level, remark FROM image_title');

      // 构建树形结构
      const titleMap = new Map();
      const rootTitles = [];

      // 首先将所有标题放入映射
      allTitles.forEach(title => {
        titleMap.set(title.imageTitleID, {
          id: title.imageTitleID,
          title: title.title,
          remark: title.remark,
          level: title.level,
          children: [],
        });
      });

      // 构建树结构
      allTitles.forEach(title => {
        if (title.parentID === null) {
          // 根节点
          rootTitles.push(titleMap.get(title.imageTitleID));
        } else {
          // 子节点
          const parent = titleMap.get(title.parentID);
          if (parent) {
            parent.children.push(titleMap.get(title.imageTitleID));
          }
        }
      });

      res.json({
        success: true,
        titleTree: rootTitles
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: '获取标题树失败',
        error: error.message
      });
    }
  }

  // 查询重复或类似的chinaElementName
  static async getDuplicateChinaElements(req, res) {
    try {
      // 查询所有非空的chinaElementName及完整图片信息
      const [elements] = await pool.query(
        'SELECT * FROM image WHERE chinaElementName IS NOT NULL AND chinaElementName != ""'
      );

      if (elements.length === 0) {
        return res.json({ message: '没有找到相关元素名称记录', duplicates: [] });
      }

      // 存储重复或类似的元素组
      const duplicateGroups = [];
      const processed = new Set();

      // 比较所有元素名称，查找相似或重复的
      for (let i = 0; i < elements.length; i++) {
        if (processed.has(elements[i].imageID)) continue;

        const currentGroup = [elements[i]];
        const currentName = elements[i].chinaElementName.trim().toLowerCase();

        for (let j = i + 1; j < elements.length; j++) {
          if (processed.has(elements[j].imageID)) continue;

          const compareName = elements[j].chinaElementName.trim().toLowerCase();

          // 完全匹配或包含关系视为相似
          if (currentName === compareName || currentName.includes(compareName) || compareName.includes(currentName)) {
            currentGroup.push(elements[j]);
            processed.add(elements[j].imageID);
          }
        }

        // 如果组内有多个元素，则认为是重复组
        if (currentGroup.length > 1) {
          duplicateGroups.push({
            chinaElementName: elements[i].chinaElementName,
            images: currentGroup
          });
          processed.add(elements[i].imageID);
        }
      }

      res.json({
        message: '查询成功',
        totalGroups: duplicateGroups.length,
        duplicates: duplicateGroups
      });
    } catch (error) {
      res.status(500).json({ message: '查询重复元素失败', error: error.message });
    }
  }

  // 更新图片的chinaElementName
  static async updateImageChinaElementName(req, res) {
    try {
      const { imageID, chinaElementName } = req.body;

      if (!imageID || chinaElementName === undefined) {
        return res.status(400).json({ message: '必须提供imageID和chinaElementName' });
      }

      // 检查图片是否存在
      const [image] = await pool.query('SELECT imageID FROM image WHERE imageID = ?', [imageID]);
      if (image.length === 0) {
        return res.status(404).json({ message: '图片不存在' });
      }

      // 更新chinaElementName
      const [result] = await pool.query(
        'UPDATE image SET chinaElementName = ? WHERE imageID = ?',
        [chinaElementName, imageID]
      );

      res.json({
        message: 'chinaElementName更新成功',
        imageID: imageID,
        newChinaElementName: chinaElementName,
        affectedRows: result.affectedRows
      });
    } catch (error) {
      res.status(500).json({ message: '更新chinaElementName失败', error: error.message });
    }
  }

  // 修改标题的remark
  static async updateImageTitleRemark(req, res) {
    try {
      const { imageTitleID, remark } = req.body;

      if (!imageTitleID || remark === undefined) {
        return res.status(400).json({ message: '必须提供imageTitleID和remark' });
      }

      // 检查标题是否存在
      const [title] = await pool.query('SELECT imageTitleID FROM image_title WHERE imageTitleID = ?', [imageTitleID]);
      if (title.length === 0) {
        return res.status(404).json({ message: '标题不存在' });
      }

      // 更新remark
      const [result] = await pool.query(
        'UPDATE image_title SET remark = ? WHERE imageTitleID = ?',
        [remark, imageTitleID]
      );

      res.json({
        message: '标题remark更新成功',
        imageTitleID: imageTitleID,
        newRemark: remark,
        affectedRows: result.affectedRows
      });
    } catch (error) {
      res.status(500).json({ message: '更新标题remark失败', error: error.message });
    }
  }

  // 添加新图片
  static async addImage(req, res) {
    try {
      const { First, Second, Third, Fourth, Fifth, caption } = req.body;

      // 验证至少提供一个标题
      if (!First && !Second && !Third && !Fourth && !Fifth) {
        return res.status(400).json({ message: '至少提供一个标题参数' });
      }

      // 插入新图片记录
      const [result] = await pool.query(
        'INSERT INTO image (First, Second, Third, Fourth, Fifth, caption, state) VALUES (?, ?, ?, ?, ?, ?, 0)',
        [First, Second, Third, Fourth, Fifth, caption || '']
      );

      const newImageID = result.insertId;

      // 查询完整的图片信息
      const [newImage] = await pool.query('SELECT * FROM image WHERE imageID = ?', [newImageID]);

      res.status(201).json({
        message: '图片添加成功',
        image: newImage[0]
      });
    } catch (error) {
      res.status(500).json({ message: '添加图片失败', error: error.message });
    }
  }
}

module.exports = ImageController;