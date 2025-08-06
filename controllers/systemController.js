const constants = require('../utils/constants');

class SystemController {
  // 获取软件版本号
  static getVersion(req, res) {
    try {
      res.json({
        success: true,
        version: constants.VERSION
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        message: '获取版本号失败',
        error: error.message
      });
    }
  }
}

module.exports = SystemController;