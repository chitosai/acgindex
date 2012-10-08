# -*- coding: utf-8 -*-

import re, time

from base.utility import *

# 准备需要的正则表达式
re_name    = re.compile('''首页</a>&nbsp;&nbsp;&raquo;&nbsp;&nbsp;<a href='/cat/\d+.html' >.+?</a>&nbsp;&nbsp;&raquo;&nbsp;&nbsp;(.+?)<a href="javascript:;" onClick="addFavorite''')
re_ep_list = re.compile('''<ul id="iul1" class="addrlist">\r\n\s{10}<ul>(.+)</ul>\r\n\s{8}</ul>''')
re_ep      = re.compile('<li><a href=\'(.+?)\' target="_blank">.+?</a></li>')


# 抓从start到end的条目
def fetchRw( start, end ):
	end += 1
	for i in range( start, end ):
		i = str(i)
		r = fetchViewFromRw( i )
		if type(r) == str:
			Tsukasa.debug( i + ' ' + r )
		elif r:
			Tsukasa.log( i + ' success' )
		else:
			Tsukasa.log( i + ' dosent exists' )

		# 肉丸的条目量很少，慢慢爬也没关系
		time.sleep(5)




# 根据id抓一个条目
def fetchViewFromRw( id ):
	global URL_RW, ERROR_NET

	# 获取页面
	try:
		c = Haruka.Get( URL_RW % id ).decode('gbk').encode('utf-8')
	except:
		return '编码错误'
	if not c : return ERROR_NET

	# 还是先确定是否存在
	if '<title>404 - 肉丸网盘速载站 - 肉丸115下载站 - 肉丸动漫社</title>' in c:
		return False

	# 抓动画标题
	name = re.search( re_name, c )
	if not name : return '抓不到标题'

	# 抓章节
	eps = re.search( re_ep_list, c )
	if not eps : return '抓不到章节列表'
	ep = re.findall( re_ep, eps.group(1) )
	if not ep : return '抓具体章节失败'

	# 写数据
	ai = Ai()

	# 主条目
	ai.AddRwEntry( id, len(ep) )

	# 标签
	tags = name.group(1).split('/')
	for tag in tags:
		ai.AddRwTags( tag, id )

	# 章节列表
	epid = len(ep)
	for each in ep:
		ai.AddRwEp( id, epid, each.strip() )
		epid -= 1

	del ai

	# OK
	return True



fetchRw(1,1434)
#print fetchViewFromRw('1415')
