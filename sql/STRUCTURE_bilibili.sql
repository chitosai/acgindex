# 条目
DROP TABLE IF EXISTS `_bili_`;
CREATE TABLE `_bili_` (
`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
`av` INT NOT NULL COMMENT 'av号',
`cid` TINYINT NOT NULL COMMENT '分类id',
`title` VARCHAR( 255 ) NOT NULL COMMENT '标题',
`memberonly` BOOL NOT NULL DEFAULT '0' COMMENT '会员限定',
INDEX ( `title` ),
UNIQUE( `av` )
) ENGINE = MYISAM ;

# 标签
DROP TABLE IF EXISTS `_bili_tags_`;
CREATE TABLE `_bili_tags_` (
`aid` INT NOT NULL COMMENT '对应的视频id',
`tag` VARCHAR( 255 ) NOT NULL COMMENT '标签',
INDEX ( `aid` )
) ENGINE = MYISAM ;