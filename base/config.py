# -*- coding: utf-8 -*-

# 版本信息
ACGINDEX_VERSION = '0.1 Beta'
ACGINDEX_UA = ('User-agent', 'ACGINDEX/=w= ( im just a little spider; please dont block me;)' )

# DEBUG MODE
DEBUG = True

# 数据库配置
DB_HOST = 'localhost'
DB_NAME = 'acgindex'

# 存储路径
PATH_COVER   = 'cover\\'
PATH_LOG     = 'log\\'
PATH_TMP     = '_tmp_\\'

# 存储文件名
FILE_COOKIE_BILI  = 'bilibili.txt'
FILE_PROXY_LIST   = 'proxy.txt'

# 地址前缀
URL_BILI					= 'http://www.bilibili.tv/video/av%s/'
URL_BGM						= 'http://bgm.tv/subject/'
URL_RW						= 'http://d.52rwdm.com/view/%s.html'
URL_KTXP					= 'http://bt.ktxp.com'
URL_KTXP_SEARCH_COLLECTION	= URL_KTXP + '/search.php?sort_id=28&order=seeders&keyword='
URL_KTXP_SEARCH_SINGLE		= URL_KTXP + '/search.php?sort_id=12&order=seeders&keyword='

# 分类 id<=>中文 转换
CATE_BGM = {
	'book'	: 1,
	'anime'	: 2,
	'music'	: 3,
	'game'	: 4,
	'mono'	: 5,
	'real'	: 6
}

CATE_BILI = {
	'douga'		: 1, # 动画
	'music'		: 2, # 音乐
	'game'		: 3, # 游戏
	'technology': 4, # 技术
	'ent'		: 5, # 娱乐
	'part'		: 6, # 合集
	'bangumi'	: 7, # 新番
}

# 抓数据的范围
RANGE_BILI = ['music', 'part', 'bangumi']

# 一些通用的出错提示
ERROR_NET  = '网络出错，无法获取 ----------------------------------------------------[ ERROR ] '