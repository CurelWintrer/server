const express = require('express');
const dotenv = require('dotenv');
const pool = require('./db');
const userRoutes = require('./routes/user');

const app = express();

dotenv.config();
app.use(express.json());

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

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`服务器运行在端口 ${PORT}`);
});