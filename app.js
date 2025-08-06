const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');
const pool = require('./db');
const userRoutes = require('./routes/user');
const imageRoutes = require('./routes/image');
const checkTaskRoutes = require('./routes/checkTask');
const systemRoutes = require('./routes/system');

const app = express();
app.use(cors());

dotenv.config();
app.use(express.json());
app.use('/img', express.static(path.join(__dirname, 'img')));

// 数据库连接测试
pool.getConnection()
  .then(conn => {
    console.log('MySQL连接成功');
    conn.release();
  })
  .catch(err => {
    console.error('数据库连接失败:', err);
  });

// 路由配置
app.use('/api/user', userRoutes);
app.use('/api/image', imageRoutes);
app.use('/api/check-tasks', checkTaskRoutes);
app.use('/api/system', systemRoutes);



const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`服务器运行在端口 ${PORT}`);
});