const jwt = require('jsonwebtoken');

function generateToken(user) {
  return jwt.sign(
    { userID: user.userID, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '240h' }
  );
}

module.exports = { generateToken };