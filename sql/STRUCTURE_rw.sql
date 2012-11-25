# 条目表
DROP TABLE IF EXISTS `_rw_`;
CREATE TABLE `_rw_` (
`rwid` INT NOT NULL COMMENT '肉丸id',
`count` INT NOT NULL COMMENT '已收录话数',
PRIMARY KEY ( `rwid` )
) ENGINE = MYISAM ;

# ep表
DROP TABLE IF EXISTS `_rw_ep_`;
CREATE TABLE `_rw_ep_` (
`rwid` INT NOT NULL COMMENT '肉丸id',
`epid` INT NOT NULL COMMENT '话数',
`url` VARCHAR( 50 ) NOT NULL COMMENT '资源地址',
INDEX ( `rwid` , `epid` )
) ENGINE = MYISAM ;

# tags表
DROP TABLE IF EXISTS `_rw_tags_`;
CREATE TABLE `_rw_tags_` (
`name` VARCHAR( 255 ) NOT NULL COMMENT '标签',
`rwid` INT NOT NULL COMMENT '对应的肉丸Id',
PRIMARY KEY ( `name` )
) ENGINE = MYISAM ;