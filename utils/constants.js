// 系统常量定义
const packageJson = require('../package.json');

module.exports = {
  // 软件版本号，从package.json中读取
  VERSION: packageJson.version
};