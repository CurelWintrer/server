-- 1. 用户表
CREATE TABLE `user` (
    userID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    state INT DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 图片审核列表表
CREATE TABLE checkImageList (
    checkImageListID INT AUTO_INCREMENT PRIMARY KEY,
    userID INT NOT NULL,
    state INT DEFAULT 0,
    imageCount INT DEFAULT 0,
    checked_count INT DEFAULT 0,
    FOREIGN KEY (userID) REFERENCES `user`(userID) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 图片表
CREATE TABLE image (
    imageID INT AUTO_INCREMENT PRIMARY KEY,
    md5 CHAR(32) NOT NULL,
    First VARCHAR(100),
    Second VARCHAR(100),
    Third VARCHAR(100),
    Forth VARCHAR(100),
    Fifth VARCHAR(100),
    imgName VARCHAR(255),
    imgPath TEXT,
    chinaElementName VARCHAR(255),
    caption TEXT,
    state INT DEFAULT 0,
    imageListID INT,
    FOREIGN KEY (imageListID) REFERENCES checkImageList(checkImageListID) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
