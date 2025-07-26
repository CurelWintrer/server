const jwt = require('jsonwebtoken');

function generateToken(user) {
  return jwt.sign(
    { userID: user.userID, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '24h' }
  );
}

module.exports = { generateToken };