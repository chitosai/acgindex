# -*- coding: utf-8 -*-
import datetime, time, json, urllib

from fetchBilibili import *
from fetchBangumi import *

#
# 每天获取一次今日更新番组列表
#
def AppendOnAirBangumi():
	global ERROR_NET, URL_BILI_ON_AIR, PATH_TMP, FILE_ON_AIR_LIST

	try:
		f = open( PATH_TMP + FILE_ON_AIR_LIST )
		on_air_list = json.load(f)
		f.close()
	except:
		on_air_list = {}

	# 获取今天星期几，1 = 周一 ...
	d = datetime.datetime.now().weekday() + 1
	
	# 获取今天的番组列表
	c = Haruka.Get( URL_BILI_ON_AIR % d )
	if not c:
		return ERROR_NET

	# 解析
	r = json.loads(c)
	if type(r) != dict : return 'bili送来的JSON好像有问题'

	r = r['list']
	ai = Ai()
	for each in r:
		entry = ai.GetAnimeByName(r[each]['title'])
		if not entry : continue
		if entry[0]['id'] not in on_air_list:
			on_air_list[entry[0]['id']] = r[each]['bgmcount']

	del ai

	# 保存
	f = open( PATH_TMP + FILE_ON_AIR_LIST, 'w+' )
	json.dump(on_air_list, f)
	f.close()


#
# 每小时执行一次，查找番组资源
#
def UpdateBangumi():
	global ERROR_NET, PATH_TMP, FILE_ON_AIR_LIST

	# 读取待更新番组列表\
	try:
		f = open( PATH_TMP + FILE_ON_AIR_LIST )
		on_air_list = json.load(f)
		f.close()
	except:
		Tsukasa.debug('没有待更新番组列表？')
		return False

	# 更新番组
	_on_air_list = {}
	for each in on_air_list:
		# 取中文名
		ai = Ai()
		entry = ai.GetEntryById(each)
		name = entry['name_cn']
		bid = entry['bgm']
		del ai

		# 先等待3秒好了..省得...
		time.sleep(3)

		# 搜bili
		r = SearchBilibili( name.encode('utf-8'), on_air_list[each] )
		print name, r
		if not r: 
			_on_air_list[each] = on_air_list[each]
			continue

		# 找到了的话，就插入数据库
		ai = Ai()
		ai.UpdateEpBili( r, each, on_air_list[each] )
		del ai

		# 并且更新一下ep信息，一般来说bangumi应该会比bili早更新的
		r = FetchEpOfAnEntryFromBangumi( each, str(bid) )
		if r != True:
			_on_air_list[each] = on_air_list[each]
			Tsukasa.debug( i + ' ' + r )
			continue

	# 用新列表替换旧列表
	on_air_list = _on_air_list

	f = open( PATH_TMP + FILE_ON_AIR_LIST, 'w+' )
	json.dump( on_air_list, f )
	f.close()


#AppendOnAirBangumi()
UpdateBangumi()
