# -*- coding: utf-8 -*-
import datetime, time, json, urllib, sys

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
	if d == 7: d = 0 # bili的周末是0
	
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
		# 周末时会出现许多不是当天更新的番组也被列在json中
		# 所以只好用个麻烦的方法筛除掉了
		if r[each]['weekday'] != d : continue

		entry = ai.GetAnimeByName(r[each]['title'])
		if not entry : continue
		if entry[0]['id'] not in on_air_list:
			on_air_list[entry[0]['id']] = {
				'lastupdate': r[each]['lastupdate'],
				'ep'        : r[each]['bgmcount']
			}

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
	ct = time.time()
	_on_air_list = {}
	for each in on_air_list:
		# 取bgmid
		ai = Ai()
		entry = ai.GetEntryById(each)
		name = entry['name_cn']
		bid = entry['bgm']
		del ai

		entry = on_air_list[each]
		epid = entry['ep']

		# 先等待3秒好了..省得...
		time.sleep(3)

		# 根据lastupdate时间来判断是否是最新话
		if ct - entry['lastupdate'] > 86400: 
			# 86400秒 = 24小时，最后更新时间距离现在超过24小时说明不是最新一话
			Tsukasa.log( '%s ep.%s not updated yet' % (name.encode('gbk'), (epid + 1)))
			_on_air_list[each] = entry
			continue
		else:
			# 搜bili
			r = SearchBilibili( name.encode('utf-8'), epid )
			if not r: 
				Tsukasa.debug( 'Error fetching ' + name.encode('utf-8') + ' ep.' + str(epid) )
				continue

			# 找到了的话，就插入数据库
			ai = Ai()
			ai.UpdateEpBili( r, each, epid )
			del ai

			# 并且更新一下ep信息，一般来说bangumi应该会比bili早更新的
			r = FetchEpOfAnEntryFromBangumi( each, str(bid) )
			if r != True:
				_on_air_list[each] = entry
				Tsukasa.debug( 'Error Updating info of ' + str(bid) + ' ' + r)
				continue

			Tsukasa.debug('%s ep.%s SUCCEED' % (name.encode('utf-8'), epid))

	# 用新列表替换旧列表
	on_air_list = _on_air_list

	f = open( PATH_TMP + FILE_ON_AIR_LIST, 'w+' )
	json.dump( on_air_list, f )
	f.close()


# 被直接执行时...
if __name__ == '__main__':
	if len(sys.argv) > 1:
		param = sys.argv[1]

		if param == 'update' : UpdateBangumi()
		elif param == 'append' : AppendOnAirBangumi()

	# 没有传入参数
	else : Tsukasa.debug('No param specified')
