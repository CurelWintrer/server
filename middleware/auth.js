const jwt = require('jsonwebtoken');
const pool = require('../db');

const auth = {
  // 验证JWT令牌
  verifyToken: async (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ message: '未提供访问令牌' });

    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const [users] = await pool.query('SELECT * FROM user WHERE userID = ?', [decoded.userID]);
      if (!users.length) return res.status(401).json({ message: '用户不存在' });
      
      req.user = users[0];
      next();
    } catch (err) {
      res.status(401).json({ message: '无效的访问令牌', error: err.message });
    }
  },

  // 管理员权限校验
  adminRequired: (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ message: '未授权访问' });
    }
    
    // 确保role是数字类型进行比较
    const role = parseInt(req.user.role);
    if (role !== 1) {
      return res.status(403).json({ message: '需要管理员权限' });
    }
    next();
  }
};

module.exports = auth;