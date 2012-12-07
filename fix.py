# -*- coding: utf-8 -*-

from fetchBangumi import *
from fetchBilibili import *

# 重新抓取某个特定的bgm条目
# 重新抓取时如果是动画条目会直接把ep也抓取出来
def updateEntry( bid ):
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

	# 动画作品要获取总话数及每话信息
	total = -1
	if cid == CATE_BGM['anime'] :
		m = re.search( re_total, c )
		if m:
			total = m.group(1)
		else:
			total = 1 # 没有总话数一般是剧场版之类的，认为只有1话就是了

		# 获取每话信息
		if FetchEpOfAnEntryFromBangumi( eid, str(bid) ) != True:
			Tsukasa.debug( i + ' ' + r )
			return '获取每话信息出错'

	# 更新entry表数据
	ai = Ai()
	r = ai.UpdateEntry(name_cn, name_jp, total, bid)
	if type(r) == bool and not r : return '写入数据库出错'

	# 获取TAGS
	m = re.findall( re_tags, c )
	if m :
		for each in m:
			ai.AddTag( each, eid )

	del ai

	# 最后更新资源
	doAddBiliResource( eid )

	# 成功获取返回True
	return True

print updateEntry(29648)