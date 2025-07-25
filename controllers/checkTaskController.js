const pool = require('../db');

class CheckTaskController {
  static async getCheckTaskById(req, res) {
    try {
      const { taskId } = req.params;
      const userID = req.user.userID;

      // 查询任务信息
      const [task] = await pool.query(
        'SELECT * FROM checkImageList WHERE checkImageListID = ?',
        [taskId]
      );

      if (task.length === 0) {
        return res.status(404).json({ message: '检查任务不存在' });
      }

      // 查询该任务下的所有图片
      const [images] = await pool.query(
        'SELECT * FROM image WHERE imageListID = ?',
        [taskId]
      );

      res.status(200).json({
        task: task[0],
        images: images
      });
    } catch (error) {
      res.status(500).json({ message: '获取检查任务失败', error: error.message });
    }
  }

  static async createCheckTask(req, res) {
    try {
      const { First, Second, Third, Fourth, Fifth, count } = req.body;
      const userID = req.user.userID;

      // 收集提供的标题参数
      const titles = [First, Second, Third, Fourth, Fifth].filter(Boolean);
      
      // 参数验证：至少提供一个标题且count有效
      if (titles.length === 0 || !count || count <= 0) {
        return res.status(400).json({ message: '至少提供一个标题参数且count必须为正数' });
      }

      const connection = await pool.getConnection();
      try {
        await connection.beginTransaction();

        // 1. 创建检查任务
        const [taskResult] = await connection.query(
          'INSERT INTO checkImageList (userID, state, imageCount, checked_count) VALUES (?, 0, ?, 0)',
          [userID, count]
        );
        const taskID = taskResult.insertId;

        // 2. 查询符合条件的未检查图片
        // 动态构建查询条件
        let conditions = [];
        const queryParams = [];

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

        // 添加固定条件和分页参数
        conditions.push('state = 0');
        queryParams.push(count);

        // 执行查询
        const [images] = await connection.query(
          `SELECT imageID FROM image WHERE ${conditions.join(' AND ')} LIMIT ?`,
          queryParams
        );

        if (images.length === 0) {
          await connection.rollback();
          return res.status(404).json({ message: '没有找到符合条件的图片' });
        }

        const imageIDs = images.map(img => img.imageID);

        // 3. 更新图片的检查任务ID
        const [updateResult] = await connection.query(
            'UPDATE image SET imageListID = ?, state = 1 WHERE imageID IN (?)',
            [taskID, imageIDs]
          );

        const assignedCount = updateResult.affectedRows;

        // 4. 更新任务的实际图片数量
        await connection.query(
          'UPDATE checkImageList SET imageCount = ? WHERE checkImageListID = ?',
          [assignedCount, taskID]
        );

        await connection.commit();

        res.status(201).json({
          checkImageListID: taskID,
          userID,
          imageCount: assignedCount,
          assignedImages: assignedCount
        });
      } catch (error) {
        await connection.rollback();
        throw error;
      } finally {
        connection.release();
      }
    } catch (error) {
      res.status(500).json({ message: '创建检查任务失败', error: error.message });
    }
  }
}

module.exports = CheckTaskController;