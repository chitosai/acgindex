# -*- coding: utf-8 -*-

from fetchBangumi import *
from fetchBilibili import *

# 重新抓取某个特定的bgm条目
# 重新抓取时如果是动画条目会直接把ep也抓取出来
# 默认是强制单独抓每一话的，不会抓合集！
def UpdateEntry( bid, forceEP = True ):
	# 检查条目是否存在
	ai = Ai()
	r = ai.GetEntryByBgmId( bid )
	del ai

	# 不存在就直接返回
	if not r : return 'NOT FOUND'
	eid = r['id']
	cid = r['cid']

	# 重新抓数据
	global URL_BGM, CATE_BGM, ERROR_NET

	# 获取页面
	c = Haruka.Get( URL_BGM + str(bid) )
	if not c : 
		return ERROR_NET # 网络有问题的话就跳过

	# 先检查条目是否存在
	if '数据库中没有查询您所指定的条目' in c :
		return False

	#
	# 这里不重新抓取中文、日文名是怕如果人工修改过那两个字段，重新自动抓取就白改了
	#

	# 动画作品要获取总话数及每话信息
	total = -1
	if cid == CATE_BGM['anime'] :
		m = re.search( re_total, c )
		if m:
			total = m.group(1)
		else:
			# 一般需要重抓数据的应该都是新番吧，新番抓不到总话数的一般是年番之类的长篇，就当做100话来处理好了
			total = 100 
			# 这个时候为了防止章节列表数量太少，先添加100个空白条目到ep表里
			# 不先添加好的话，新番自动更新时会认为ep表有误
			ai = Ai()
			for i in range(1, 100):
				ai.AddEp(eid, i, '', '')

		# 获取每话信息
		r = FetchEpOfAnEntryFromBangumi( eid, str(bid) )
		if r!= True:
			Tsukasa.debug( '%s ep.%s %s' % (eid, bid, r) )
			return '获取每话信息出错'

	# 更新entry表的ep数据
	ai = Ai()
	r = ai.UpdateTotalEpOfAnEntry( total, bid )
	if type(r) == bool and not r : return '写入数据库出错'

	# 获取TAGS
	m = re.findall( re_tags, c )
	if m :
		for each in m:
			ai.AddTag( each, eid )

	del ai

	# 最后更新资源
	doAddBiliResource( eid, forceEP )

	# 成功获取返回True
	return True

# 手动为条目绑定别名，并抓取该条目在bangumi的最新数据
def UpdateEntryWithAlterName( bgmid, source, index_name, real_name ):
	ai = Ai()
	r = ai.AddAlterNameToBgmid( bgmid, source, index_name, real_name )
	del ai

	if type(r) == bool and not r :
		Tsukasa.debug('error add alter name for ' + bgmid + ' : ' + index_name)
		return False

	# 如果real_name是-1说明这番有问题，那就不去更新了
	if real_name == '-1' or real_name == -1:
		return True

	# 否则就更新条目信息
	UpdateEntry(bgmid)

	return True

# 清理自动产生100个ep时留下的多余条目
def ClearEmptyEp():
	ai = Ai()
	sql = 'SELECT * FROM `entry` WHERE `total` = 100'
	r = ai.Query(sql)
	del ai

	for item in r:
	    UpdateEntryTotal(item)