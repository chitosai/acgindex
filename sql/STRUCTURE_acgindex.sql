-- phpMyAdmin SQL Dump
-- version 2.10.2
-- http://www.phpmyadmin.net
-- 
-- 主机: localhost
-- 生成日期: 2013 年 03 月 14 日 15:38
-- 服务器版本: 5.0.45
-- PHP 版本: 5.2.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

-- 
-- 数据库: `acgindex`
-- 

-- --------------------------------------------------------

-- 
-- 表的结构 `entry`
-- 

DROP TABLE IF EXISTS `entry`;
CREATE TABLE `entry` (
  `id` int(11) NOT NULL auto_increment COMMENT '序号',
  `name_cn` varchar(255) NOT NULL COMMENT '中文名',
  `name_jp` varchar(255) NOT NULL COMMENT '日文名',
  `cid` tinyint(4) NOT NULL COMMENT '所属分类',
  `bgm` int(11) NOT NULL,
  `bili` varchar(255) NOT NULL,
  `url2` varchar(255) NOT NULL default '',
  `url3` varchar(255) NOT NULL default '',
  `total` int(11) NOT NULL COMMENT '总话数',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `bgm` (`bgm`),
  KEY `name_cn` (`name_cn`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=65275 ;

-- --------------------------------------------------------

-- 
-- 表的结构 `ep`
-- 

DROP TABLE IF EXISTS `ep`;
CREATE TABLE `ep` (
  `eid` int(11) NOT NULL COMMENT '属于哪部作品',
  `epid` int(11) NOT NULL COMMENT '第几话',
  `name_cn` varchar(255) NOT NULL COMMENT '这话的中文名',
  `name_jp` varchar(255) NOT NULL COMMENT '日文名',
  `bili` varchar(255) NOT NULL,
  `url2` varchar(255) NOT NULL default '',
  `url3` varchar(255) NOT NULL default '',
  KEY `pid` (`eid`,`epid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

-- 
-- 表的结构 `link`
-- 

DROP TABLE IF EXISTS `link`;
CREATE TABLE `link` (
  `tid` int(11) NOT NULL COMMENT 'TAG_ID',
  `eid` int(11) NOT NULL COMMENT 'ENTRY_ID',
  KEY `tid` (`tid`,`eid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

-- 
-- 表的结构 `names`
-- 

DROP TABLE IF EXISTS `names`;
CREATE TABLE `names` (
  `source` tinyint(4) NOT NULL COMMENT '来源站',
  `eid` int(11) NOT NULL COMMENT 'entry id',
  `index_name` varchar(36) NOT NULL COMMENT 'bili新番列表收录的名字',
  `real_name` varchar(36) NOT NULL COMMENT 'up主实际上传时用的名字',
  PRIMARY KEY  (`index_name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

-- 
-- 表的结构 `tags`
-- 

DROP TABLE IF EXISTS `tags`;
CREATE TABLE `tags` (
  `name` varchar(255) NOT NULL COMMENT '中文名',
  `tid` int(11) NOT NULL auto_increment COMMENT 'TAG_ID',
  PRIMARY KEY  (`tid`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=12823 ;
