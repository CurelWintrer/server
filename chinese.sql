-- 用户表
CREATE TABLE user (
    userID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    state INT DEFAULT 1 NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 注册时间
    CONSTRAINT email UNIQUE (email)
);

-- 质检图片列表表
CREATE TABLE checkimagelist (
    checkImageListID INT AUTO_INCREMENT PRIMARY KEY,
    userID INT NOT NULL,
    state INT DEFAULT 0 NULL,
    imageCount INT DEFAULT 0 NULL,
    checked_count INT DEFAULT 0 NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 更新时间
    CONSTRAINT checkimagelist_ibfk_1 FOREIGN KEY (userID) REFERENCES user (userID) ON DELETE CASCADE
);

CREATE INDEX userID ON checkimagelist (userID);

-- 图片表
CREATE TABLE image (
    imageID INT AUTO_INCREMENT PRIMARY KEY,
    md5 CHAR(32) NOT NULL,
    First VARCHAR(100) NULL,
    Second VARCHAR(100) NULL,
    Third VARCHAR(100) NULL,
    Fourth VARCHAR(100) NULL,
    Fifth VARCHAR(100) NULL,
    imgName VARCHAR(255) NULL,
    imgPath TEXT NULL,
    chinaElementName VARCHAR(255) NULL,
    caption TEXT NULL,
    state INT DEFAULT 0 NULL,
    imageListID INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT image_ibfk_1 FOREIGN KEY (imageListID) REFERENCES checkimagelist (checkImageListID) ON DELETE SET NULL
);

CREATE INDEX imageListID ON image (imageListID);

-- 图片日志表
CREATE TABLE image_log (
    imageLogID INT AUTO_INCREMENT PRIMARY KEY,
    imageID INT NOT NULL,
    userID INT NOT NULL,
    operation VARCHAR(255) NOT NULL,
    last VARCHAR(255) NULL,
    next VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 日志创建时间
    CONSTRAINT image_log__image_fk FOREIGN KEY (imageID) REFERENCES image (imageID),
    CONSTRAINT image_log_user_userID_fk FOREIGN KEY (userID) REFERENCES user (userID)
);
