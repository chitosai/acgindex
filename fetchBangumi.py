# -*- coding: utf-8 -*-

import re, time

from base.utility import *

# 准备需要的正则表达式
re_name_cn = re.compile('<li><span class="tip">中文名: </span>(.+)</li>')
re_h1      = re.compile('<h1 class="nameSingle">[\r\n\s]*<a href="/subject/(\d+)" title=".*">(.+)</a>[\r\n\s]*(?:<small class="grey">.+</small>)*[\s]*</h1>')
re_tags    = re.compile('<li><span class="tip"(?: style="visibility:hidden;")?>别名: </span>(.+?)</li>')
re_cate    = re.compile('<a href="/(\w+)"\s?class="focus">')
re_cover   = re.compile('<a href="(.+?)" title=".+?" alt=".+?" class="thickbox cover">')
re_total   = re.compile('<li><span class="tip">话数: </span>(\d+?)</li>')

re_benpian = re.compile('<li\sclass="cat">本篇</li>(.*?)(?:<li\sclass="cat">|</ul>)', re.S)
re_ep      = re.compile('<a href="/ep/\d+">(.+?)</a>(?:<span class="tip"> / (.*?)</span>)?')
re_repl    = re.compile('^\d+\.')

#
# 抓条目
#

# 从bangumi抓序号从start到end的条目
def FetchBangumi( start, end ):
	end += 1
	for i in range(start, end):
		i = str(i)
		r = FetchSubjectFromBangumi(i)
		# 返回值不为bool时表示出了问题，记录下来
		if type(r) != bool:
			Tsukasa.debug( i + ' ' + r )
		elif r:
			Tsukasa.log( i + ' success')
		else:
			Tsukasa.log( i + ' dosent exists')


# 根据id从Bangumi抓一个条目
def FetchSubjectFromBangumi( id ):
	global URL_BGM, CATE_BGM, ERROR_NET

	# 获取页面
	c = Haruka.Get( URL_BGM + id )
	if not c : 
		return ERROR_NET # 网络有问题的话就跳过

	# 先检查条目是否存在
	if '数据库中没有查询您所指定的条目' in c :
		return False

	# 查找中文名
	m = re.search( re_name_cn, c )
	if m :
		name_cn = m.group(1)
	else:
		name_cn = None
	
	# 查找h1
	m = re.search( re_h1, c )
	if m :
		bgm = int(m.group(1))
		name_jp = m.group(2)
	else:
		return '无法获取h1'

	# 没有中文名时说明本身就是中文作品
	if not name_cn:
		name_cn = name_jp

	# 获取所属分类
	m = re.search( re_cate, c )
	if m :
		cid = CATE_BGM[m.group(1)]
	else:
		return '无法获取所属分类'

	# 动画作品要获取总话数
	total = -1
	if cid == CATE_BGM['anime'] :
		m = re.search( re_total, c )
		if m:
			total = m.group(1)
		else:
			total = 1 # 没有总话数一般是剧场版之类的，认为只有1话就是了

	# 向entry表写入数据
	ai = Ai()
	eid = ai.AddEntry(name_cn, name_jp, cid, bgm, total)

	if eid == ERROR_DK:
		return '重复条目，跳过'
	elif eid == False:
		return '写入数据库出错'

	# 获取TAGS
	m = re.findall( re_tags, c )
	if m :
		for each in m:
			ai.AddTag( each, eid )

	del ai

	if not DEBUG:
		# 获取图片
		m = re.search( re_cover, c )
		if m:
			if not Haruka.GetImage( eid, cid, m.group(1)) : return '获取图片时网络超时'
		else:
			return '没有封面'

	# 成功获取返回True
	return True



#
# 抓章节
#
# 主循环
def FetchEpFromBangumi( start, end ):
	# 准备活动
	global CATE_BGM, RANGE_BGM
	ai = Ai()
	end += 1

	for i in range( start, end ):
		i = str(i)
		# 取这条数据
		entry = ai.GetEntryById( i )
		if type(entry) != tuple :
			Tsukasa.debug( i + ' 读取数据库时失败')

		# 确定是动画条目
		if entry[3] != CATE_BGM['anime'] or entry[8] == 1 :
			Tsukasa.log( i + ' skip')
			continue

		# GO
		r = FetchEpOfAnEntryFromBangumi( i, str(entry[4]) )
		if r != True:
			Tsukasa.debug( i + ' ' + r )

		# 总之先拿1s做实验吧...
		Tsukasa.log( i + ' success' )
		time.sleep(2)

	return True



# 根据id从bangumi抓取 动画 条目的话数信息
def FetchEpOfAnEntryFromBangumi( id, bgmid ):
	global URL_BGM, ERROR_NET

	# 获取页面
	c = Haruka.Get( URL_BGM + bgmid + '/ep' )
	if not c : return ERROR_NET

	# 先把"本篇"部分抓出来，再单独处理
	m = re.search( re_benpian, c )
	if not m : return '找不到章节列表'

	# 再抓具体的内容
	m = re.findall( re_ep, m.group(1) )
	if not m : return '章节列表为空?'

	# 处理、写入数据
	epid = 1
	for each in m:
		name_jp = re.sub( re_repl, '', each[0] )
		name_cn = re.sub( re_repl, '', each[1] )

		ai = Ai()
		ai.AddEp( id, epid, name_jp, name_cn )

		epid += 1

	return True



FetchBangumi(45001,54001)
#FetchEpFromBangumi(43567, 43566)