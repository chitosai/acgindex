# -*- coding: utf-8 -*-

import re, time, os

from base.utility import *

# 准备需要的正则表达式
re_av    = re.compile("var aid='(\d+)';")
re_cate  = re.compile('''<a href="/">主页</a> &gt; <a href='/video/(\w+).html'>.+</a>''')
re_title = re.compile('<h2>(.+?)</h2>')
re_tags  = re.compile("kwtags\(\[(.+?)?\],\[(.+?)?\]\);")


# 根据id从bili抓一个视频
def FetchAvFromBili( id ):
	global URL_BILI, ERROR_NET

	# 获取页面
	c = Haruka.Get( URL_BILI % id )
	if not c : return ERROR_NET + ' Unknown' 

	# #
	# 检查是否存在/是否会员限定

	# 这样应该是404了，没救了
	if '<title>出错啦! - bilibili.tv</title>' in c:
		return '不存在 - 404'

	# 这样貌似也没救了，大概是没通过审核的
	if '<title>bilibili - 提示</title>' in c:
		return False

	# 这样有一定几率登录后可见
	if '<div class="z-msg">' in c:
		return FetchAvFromBiliWithLogin( id )

	# 没这几个提示的话应该是没啥问题
	return FetchInfoFromBili( id, c )


# 带登录状态访问bili
def FetchAvFromBiliWithLogin( id ):
	global URL_BILI, ERROR_NET, FILE_COOKIE_BILI

	# CONNECT
	c = Haruka.GetWithCookie( URL_BILI % id, FILE_COOKIE_BILI )
	if not c: return ERROR_NET

	# 还是先检查提示
	if '<div class="z-msg">' in c:
		return '不存在 - 403'

	return FetchInfoFromBili( id, c, memberonly = 1 )



# 登录bili
def LoginBilibili():
	global FILE_COOKIE_BILI, ERROR_NET

	c = Haruka.GetWithCookie( 'https://secure.bilibili.tv/login', FILE_COOKIE_BILI, 
							  'userid=' + BILI_USER + '&pwd=' + BILI_PASS + '&keeptime=2592000&act=login&gourl=http://www.bilibili.tv/')
	if not c: return ERROR_NET

	# 确认登录成功
	if '成功登录' in c:
		return True
	else:
		return '登录返回的状态有点奇怪，检查一下!'

