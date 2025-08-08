const pool = require('../db');

class CheckTaskController {

    //获取用户的检查任务列表并更新任务信息
    static async getUserCheckTasks(req, res) {
        try {
            const userID = req.user.userID;
            const page = parseInt(req.query.page) || 1;
            const limit = parseInt(req.query.limit) || 10;
            const offset = (page - 1) * limit;

            // 查询任务总数
            const [totalResult] = await pool.query(
                'SELECT COUNT(*) as total FROM checkImageList WHERE userID = ?',
                [userID]
            );
            const total = totalResult[0].total;

            // 查询用户的检查任务列表
            const [tasks] = await pool.query(
                'SELECT * FROM checkImageList WHERE userID = ? ORDER BY checkImageListID DESC LIMIT ? OFFSET ?',
                [userID, limit, offset]
            );

            // 如果有任务，更新每个任务的checked_count和状态
            if (tasks.length > 0) {
                const connection = await pool.getConnection();
                try {
                    await connection.beginTransaction();

                    for (const task of tasks) {
                        // 查询状态不等于1的图片数量
                        const [imageResult] = await connection.query(
                            'SELECT COUNT(*) as count FROM image WHERE imageListID = ? AND state != 1',
                            [task.checkImageListID]
                        );
                        const checkedCount = imageResult[0].count;

                        // 更新任务的checked_count
                        await connection.query(
                            'UPDATE checkImageList SET checked_count = ? WHERE checkImageListID = ?',
                            [checkedCount, task.checkImageListID]
                        );

                        // 如果checked_count等于imageCount，更新state为2
                        if (checkedCount === task.imageCount) {
                            await connection.query(
                                'UPDATE checkImageList SET state = 2 WHERE checkImageListID = ?',
                                [task.checkImageListID]
                            );
                        }
                    }

                    await connection.commit();

                    // 重新查询更新后的任务列表
                    const [updatedTasks] = await pool.query(
                        'SELECT * FROM checkImageList WHERE userID = ? ORDER BY checkImageListID DESC LIMIT ? OFFSET ?',
                        [userID, limit, offset]
                    );

                    res.status(200).json({
                        total,
                        page: parseInt(page),
                        limit: parseInt(limit),
                        tasks: updatedTasks
                    });
                } catch (error) {
                    await connection.rollback();
                    throw error;
                } finally {
                    connection.release();
                }
            } else {
                res.status(200).json({
                    total,
                    page: parseInt(page),
                    limit: parseInt(limit),
                    tasks: []
                });
            }
        } catch (error) {
            res.status(500).json({ message: '查询检查任务失败', error: error.message });
        }
    }

    //获取检查任务详情
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

    //创建检查任务
    static async createCheckTask(req, res) {
        try {
            const { First, Second, Third, Fourth, Fifth, count } = req.body;
            const userID = req.user.userID;

            // 收集提供的标题参数
            const titles = [First, Second, Third, Fourth, Fifth].filter(Boolean);

            // 拼接标题为path
            const path = titles.join('/');

            // 参数验证：至少提供一个标题且count有效
            if (titles.length === 0 || !count || count <= 0) {
                return res.status(400).json({ message: '至少提供一个标题参数且count必须为正数' });
            }

            const connection = await pool.getConnection();
            try {
                await connection.beginTransaction();

                // 1. 创建检查任务
                const [taskResult] = await connection.query(
                    'INSERT INTO checkImageList (userID, state, imageCount, checked_count, path) VALUES (?, 0, ?, 0, ?)',
                    [userID, count, path]
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
                conditions.push('imageListID IS NULL');

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

    // 更新质检任务状态
    static async updateTaskState(req, res) {
        try {
            const { taskId } = req.params;
            const { state } = req.body;
            const userID = req.user.userID;

            // 验证状态值是否有效
            if (![0, 1, 2].includes(state)) {
                return res.status(400).json({ message: '无效的状态值，必须是0、1或2' });
            }

            // 检查任务是否存在且属于当前用户
            const [task] = await pool.query(
                'SELECT * FROM checkImageList WHERE checkImageListID = ? AND userID = ?',
                [taskId, userID]
            );

            if (task.length === 0) {
                return res.status(404).json({ message: '检查任务不存在或不属于当前用户' });
            }

            // 更新任务状态
            await pool.query(
                'UPDATE checkImageList SET state = ? WHERE checkImageListID = ?',
                [state, taskId]
            );

            // 返回更新后的任务信息
            const [updatedTask] = await pool.query(
                'SELECT * FROM checkImageList WHERE checkImageListID = ?',
                [taskId]
            );

            res.status(200).json(updatedTask[0]);
        } catch (error) {
            res.status(500).json({ message: '更新任务状态失败', error: error.message });
        }
    }

    // 放弃检查任务
    static async abandonCheckTask(req, res) {
        try {
            const { taskId } = req.params;
            const userID = req.user.userID;

            // 检查任务是否存在且属于当前用户
            const [task] = await pool.query(
                'SELECT * FROM checkImageList WHERE checkImageListID = ? AND userID = ?',
                [taskId, userID]
            );

            if (task.length === 0) {
                return res.status(404).json({ message: '检查任务不存在或不属于当前用户' });
            }

            const connection = await pool.getConnection();
            try {
                await connection.beginTransaction();

                // 1. 将对应图片的state改为0，imageListID改为null
                await connection.query(
                    'UPDATE image SET state = 0, imageListID = NULL WHERE imageListID = ?',
                    [taskId]
                );

                // 2. 删除检查任务
                await connection.query(
                    'DELETE FROM checkImageList WHERE checkImageListID = ?',
                    [taskId]
                );

                await connection.commit();

                res.status(200).json({ message: '检查任务已放弃', taskId });
            } catch (error) {
                await connection.rollback();
                throw error;
            } finally {
                connection.release();
            }
        } catch (error) {
            res.status(500).json({ message: '放弃检查任务失败', error: error.message });
        }
    }
}

module.exports = CheckTaskController;