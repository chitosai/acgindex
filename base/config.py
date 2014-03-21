# -*- coding: utf-8 -*-
import platform, os, sys

from accounts import *

# 版本信息
ACGINDEX_VERSION = '0.1 Beta'
ACGINDEX_UA = ('User-agent', 'ACGINDEX/' + ACGINDEX_VERSION + ' ( im just a little spider; please let me in; contact: ' + ACGINDEX_EMAIL + ' )' )

# DEBUG MODE
DEBUG = False

# 分隔符
if platform.system() == 'Windows': SLASH = '\\'
else: SLASH = '/'

# ABS_PATH
ABS_PATH = sys.path[0] + SLASH

# 存储路径
PATH_COVER   = ABS_PATH + 'cover' + SLASH
PATH_LOG     = ABS_PATH + 'log' + SLASH
PATH_TMP     = ABS_PATH + '_tmp_' + SLASH

# 存储文件名
FILE_COOKIE_BILI  = 'bilibili.txt'
FILE_PROXY_LIST   = 'proxy.txt'

# 搜索分类关键词
BILI_SEARCH_PREFIX_SINGLE = '新番'
BILI_SEARCH_PREFIX_COLLECTION = '完结动画'

# 地址前缀
URL_BILI					= 'http://www.bilibili.tv/video/av%s/'
URL_BILI_SEARCH             = 'http://api.bilibili.tv/search?type=json&keyword=%s&page=1&order=default&appkey=' + BILI_APPKEY
URL_BILI_ON_AIR             = 'http://api.bilibili.tv/bangumi?type=json&btype=2&weekday=0&appkey=' + BILI_APPKEY
URL_BGM						= 'http://bgm.tv/subject/'
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

NAMES_SOURCES = {
	'bili'  : 0,
    'bt'    : 9
}

# 一些通用的出错提示
ERROR_NET  = '网络出错，无法获取'
ERROR_DK   = 'Duplicated Key'
ERROR_NF   = 'NOT FOUND'