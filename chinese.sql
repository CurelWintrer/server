create table image_title
(
    imageTitleID int auto_increment
        primary key,
    title        varchar(255) not null,
    parentID     int          null,
    constraint image_title_image_title__fk
        foreign key (parentID) references image_title (imageTitleID)
);

create table user
(
    userID     int auto_increment
        primary key,
    name       varchar(100)                       not null,
    email      varchar(255)                       not null,
    password   varchar(255)                       not null,
    role       int                                not null,
    state      int      default 1                 null,
    created_at datetime default CURRENT_TIMESTAMP not null,
    constraint email
        unique (email)
);

create table checkimagelist
(
    checkImageListID int auto_increment
        primary key,
    userID           int                                not null,
    state            int      default 0                 null,
    path             varchar(255)                       null,
    imageCount       int      default 0                 null,
    checked_count    int      default 0                 null,
    created_at       datetime default CURRENT_TIMESTAMP not null,
    updated_at       datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    constraint checkimagelist_ibfk_1
        foreign key (userID) references user (userID)
            on delete cascade
);

create index userID
    on checkimagelist (userID);

create table image
(
    imageID          int auto_increment
        primary key,
    md5              char(32)                           not null,
    First            varchar(100)                       null,
    Second           varchar(100)                       null,
    Third            varchar(100)                       null,
    Fourth           varchar(100)                       null,
    Fifth            varchar(100)                       null,
    imgName          varchar(255)                       null,
    imgPath          text                               null,
    chinaElementName varchar(255)                       null,
    caption          text                               null,
    state            int                                null,
    imageListID      int                                null,
    created_at       datetime default CURRENT_TIMESTAMP not null,
    updated_at       datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    constraint image_ibfk_1
        foreign key (imageListID) references checkimagelist (checkImageListID)
            on delete set null
);

create index imageListID
    on image (imageListID);

create table image_log
(
    imageLogID int auto_increment
        primary key,
    imageID    int                                not null,
    userID     int                                not null,
    operation  varchar(255)                       not null,
    last       varchar(255)                       null,
    next       varchar(255)                       null,
    created_at datetime default CURRENT_TIMESTAMP not null,
    constraint image_log__image_fk
        foreign key (imageID) references image (imageID),
    constraint image_log_user_userID_fk
        foreign key (userID) references user (userID)
);

