const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const pool = require('../db');
const { generateToken } = require('../utils/auth');

class UserController {
  // 用户注册
  static async register(req, res) {
    try {
      const { name, email, password, role } = req.body;
      const hashedPassword = await bcrypt.hash(password, 10);

      const [result] = await pool.query(
        'INSERT INTO user (name, email, password, role, state) VALUES (?, ?, ?, ?, ?)',
        [name, email, hashedPassword, role, 0]
      );

      const [user] = await pool.query('SELECT * FROM user WHERE userID = ?', [result.insertId]);
      res.status(201).json(user[0]);
    } catch (error) {
      res.status(400).json({ message: '注册失败', error: error.message });
    }
  }

  // 用户登录
  static async login(req, res) {
    try {
      const { email, password } = req.body;
      const [users] = await pool.query('SELECT * FROM user WHERE email = ?', [email]);
      
      if (!users.length) {
        return res.status(404).json({ message: '用户不存在' });
      }

      const user = users[0];
      const validPassword = await bcrypt.compare(password, user.password);
      
      if (!validPassword) {
        return res.status(401).json({ message: '密码错误' });
      }

      const token = generateToken(user);
      res.json({ ...user, token });
    } catch (error) {
      res.status(500).json({ message: '登录失败', error: error.message });
    }
  }

  // 获取用户列表
  static async getUsers(req, res) {
    try {
      const { role } = req.query;
      let query = 'SELECT * FROM user';
      const params = [];

      if (role) {
        query += ' WHERE role = ?';
        params.push(role);
      }

      const [users] = await pool.query(query, params);
      res.json({
        count: users.length,
        users
      });
    } catch (error) {
      res.status(500).json({ message: '获取用户失败', error: error.message });
    }
  }

  // 更新用户角色
  static async updateRole(req, res) {
    try {
      const { id } = req.params;
      const { role } = req.body;
      
      await pool.query('UPDATE user SET role = ? WHERE userID = ?', [role, id]);
      const [user] = await pool.query('SELECT * FROM user WHERE userID = ?', [id]);
      
      res.json(user[0]);
    } catch (error) {
      res.status(400).json({ message: '更新角色失败', error: error.message });
    }
  }

  // 更新用户状态
  static async updateState(req, res) {
    try {
      const { id } = req.params;
      const { state } = req.body;
      
      await pool.query('UPDATE user SET state = ? WHERE userID = ?', [state, id]);
      const [user] = await pool.query('SELECT * FROM user WHERE userID = ?', [id]);
      
      res.json(user[0]);
    } catch (error) {
      res.status(400).json({ message: '更新状态失败', error: error.message });
    }
  }

  // 批量更新用户状态
  static async batchUpdateState(req, res) {
    try {
      const { userIDs, state } = req.body;
      
      if (!Array.isArray(userIDs) || userIDs.length === 0) {
        return res.status(400).json({ message: '用户ID列表不能为空' });
      }

      // 使用 IN 操作符批量更新用户状态
      const placeholders = userIDs.map(() => '?').join(',');
      await pool.query(`UPDATE user SET state = ? WHERE userID IN (${placeholders})`, [state, ...userIDs]);
      
      // 获取更新后的用户列表
      const [users] = await pool.query(`SELECT * FROM user WHERE userID IN (${placeholders})`, [...userIDs]);
      
      res.json({
        updatedCount: users.length,
        users: users
      });
    } catch (error) {
      res.status(400).json({ message: '批量更新状态失败', error: error.message });
    }
  }
  // 刷新令牌
  static async refreshToken(req, res) {
    try {
      // 使用当前用户信息生成新令牌
      const newToken = generateToken(req.user);
      res.json({
        token: newToken,
        user: {
          id: req.user.userID,
          name: req.user.name,
          email: req.user.email,
          role: req.user.role
        }
      });
    } catch (error) {
      res.status(500).json({ message: '刷新令牌失败', error: error.message });
    }
  }

  // 重置密码
  static async resetPassword(req, res) {
    try {
      const { currentPassword, newPassword } = req.body;
      const userId = req.user.userID;

      // 获取用户当前密码
      const [users] = await pool.query('SELECT password FROM user WHERE userID = ?', [userId]);
      if (!users.length) {
        return res.status(404).json({ message: '用户不存在' });
      }

      const user = users[0];
      const validPassword = await bcrypt.compare(currentPassword, user.password);
      if (!validPassword) {
        return res.status(401).json({ message: '当前密码错误' });
      }

      // 加密新密码
      const hashedNewPassword = await bcrypt.hash(newPassword, 10);
      await pool.query('UPDATE user SET password = ? WHERE userID = ?', [hashedNewPassword, userId]);

      res.json({ message: '密码重置成功' });
    } catch (error) {
      res.status(500).json({ message: '重置密码失败', error: error.message });
    }
  }
}

module.exports = UserController;