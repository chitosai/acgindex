-- phpMyAdmin SQL Dump
-- version 3.5.8.1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2013 年 09 月 11 日 21:01
-- 服务器版本: 5.5.31-0ubuntu0.12.04.1
-- PHP 版本: 5.3.10-1ubuntu3.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- 数据库: `acgindex`
--

-- --------------------------------------------------------

--
-- 表的结构 `entry`
--

DROP TABLE IF EXISTS `entry`;
CREATE TABLE `entry` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '序号',
  `name_cn` varchar(255) NOT NULL COMMENT '中文名',
  `name_jp` varchar(255) NOT NULL COMMENT '日文名',
  `cid` tinyint(4) NOT NULL COMMENT '所属分类',
  `bgm` int(11) NOT NULL,
  `bili` varchar(255) NOT NULL DEFAULT '',
  `url2` varchar(255) NOT NULL DEFAULT '',
  `url3` varchar(255) NOT NULL DEFAULT '',
  `total` int(11) NOT NULL COMMENT '总话数',
  PRIMARY KEY (`id`),
  UNIQUE KEY `bgm` (`bgm`),
  KEY `name_cn` (`name_cn`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `ep`
--

DROP TABLE IF EXISTS `ep`;
CREATE TABLE `ep` (
  `eid` int(11) NOT NULL COMMENT '属于哪部作品',
  `epid` float NOT NULL COMMENT '第几话',
  `name_cn` varchar(255) NOT NULL COMMENT '这话的中文名',
  `name_jp` varchar(255) NOT NULL COMMENT '日文名',
  `bili` varchar(255) NOT NULL DEFAULT '',
  `url2` varchar(255) NOT NULL DEFAULT '',
  `url3` varchar(255) NOT NULL DEFAULT '',
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
-- 表的结构 `log`
--

DROP TABLE IF EXISTS `log`;
CREATE TABLE `log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `bgm` int(11) NOT NULL COMMENT 'bgmid',
  `epid` int(11) NOT NULL COMMENT '话数id',
  `source` varchar(6) COLLATE utf8_unicode_ci NOT NULL COMMENT '来源网站',
  `status` tinyint(1) NOT NULL COMMENT '是否找到资源',
  `count` int(11) NOT NULL DEFAULT '1' COMMENT '访问量',
  PRIMARY KEY (`id`),
  KEY `eid` (`bgm`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

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
  `ep_revise` int(11) NOT NULL DEFAULT '0' COMMENT '修正来源站发来的话数错误',
  KEY `index_name` (`index_name`),
  KEY `eid` (`eid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- 表的结构 `statistics`
--

DROP TABLE IF EXISTS `statistics`;
CREATE TABLE `statistics` (
  `key` varchar(24) COLLATE utf8_unicode_ci NOT NULL COMMENT '统计值名',
  `value` int(11) NOT NULL COMMENT '统计值'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- 表的结构 `tags`
--

DROP TABLE IF EXISTS `tags`;
CREATE TABLE `tags` (
  `name` varchar(255) NOT NULL COMMENT '中文名',
  `tid` int(11) NOT NULL AUTO_INCREMENT COMMENT 'TAG_ID',
  PRIMARY KEY (`tid`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;
