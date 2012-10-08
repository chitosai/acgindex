# -*- coding: utf-8 -*-

import re, time, os

from base.utility import *

# 准备需要的正则表达式
re_av    = re.compile("var aid='(\d+)';")
re_cate  = re.compile('''<a href="/">主页</a> &gt; <a href='/video/(\w+).html'>.+</a>''')
re_title = re.compile('<h2>(.+?)</h2>')
re_tags  = re.compile("kwtags\(\[(.+?)?\],\[(.+?)?\]\);")



# 从bili抓序号从start到end的条目
def FetchBilibili( start, end ):
	end += 1

	# 开始循环之前，先准备一份登录状态的cookie
	r = LoginBilibili()

	# 如果登录不成功立刻退出，不开始主循环
	if r != True:
		Tsukasa.debug(r)
		return r


	# 开始循环
	for i in range( start, end ):
		i = str(i)

		r = FetchAvFromBili( i )
		if type(r) == str:
			Tsukasa.debug( i + ' ' + r )
		elif r == True:
			Tsukasa.log( i + ' success' )
		elif not r:
			Tsukasa.log( i + ' dosent exists' )

		time.sleep(3)




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




# 抓需要的信息
def FetchInfoFromBili( id, content, memberonly = 0 ):
	global CATE_BILI

	# av号
	av = re.search( re_av, content )
	if not av : return -2

	# 所属分类
	cate = re.search( re_cate, content )
	if not cate : return '找不到所属分类'

	# 标题
	title = re.search( re_title, content )
	if not title : return '找不到标题'

	# 写数据库
	ai = Ai()
	av = ai.AddBiliEntry( av.group(1), CATE_BILI[cate.group(1)], title.group(1), memberonly )
	if av == 0 :
		return '重复插入'
	elif av == False:
		return '写入条目数据时失败'

	# 获取TAG
	tags = re.search( re_tags, content )
	if not tags : return 'ERROR FETCHING TAGS'

	# 检查是否确实有TAGS
	if tags.group(1) != None:
		tags = tags.group(1).split(',')

		# 写TAG
		for tag in tags:
			r = ai.AddBiliTag( av, tag[1:-1] )

	del ai

	# 大丈夫！
	return True



# 登录bili
def LoginBilibili():
	global FILE_COOKIE_BILI, ERROR_NET

	c = Haruka.GetWithCookie( 'https://secure.bilibili.tv/login', FILE_COOKIE_BILI, 'userid=ithec&pwd=$s^IgW#Lv3*a50W9t1$7w8b3&keeptime=2592000&act=login&gourl=http://www.bilibili.tv/')
	if not c: return ERROR_NET

	# 确认登录成功
	if '成功登录' in c:
		return True
	else:
		return '登录返回的状态有点奇怪，检查一下!'





# 修复LOG里记录的某些视频...
def fix():
	f = open('log\\2012-08-01.log','r').readlines()
	for eachline in f:
		m = re.search('\[\d{2}:\d{2}:\d{2}\] (\d+)找不到av号', eachline)
		if m:
			r = FetchAvFromBili(m.group(1))
			Tsukasa.log('已补救 ' + m.group(1))




# bili的1是公告，爬数据时要从2开始
fix()
#FetchBilibili(250001, 260000)
#print FetchAvFromBili('321354')
