# -*- coding: utf-8 -*-
import datetime, json

from fix import *

NEED_HANDLE = []
#
# 每小时执行一次，查找番组资源
#
def UpdateBili():
	global ERROR_NET, URL_BILI_ON_AIR, NEED_HANDLE

	# 获取周日的列表，这样可以拿到所有番组的lastupdate
	c = Haruka.Get( URL_BILI_ON_AIR )
	if not c:
		return ERROR_NET

	# 解析
	r = json.loads(c)
	if type(r) != dict : 
		Tsukasa.debug('bili送来的JSON好像有问题')
		return False

	# 更新番组
	local_time = time.time()
	on_air_list = r['list']
	for remote_entry in on_air_list:
		remote_time = remote_entry['lastupdate']
		remote_name = remote_entry['title']
		remote_epid = int(remote_entry['bgmcount'])

		# 根据lastupdate时间来判断是否是最新话
		# 259200秒 = 72小时，最后更新时间距离现在超过72小时说明不是最新一话
		if local_time - remote_time > 259200: continue

		# 否则就开始处理
		else:
			# 从本地数据库取数据
			ai = Ai()
			# 先从names表里找，这里也存着-1等特殊状态
			local_entry = ai.GetAnimeByAlterName( 'bili', remote_name )
			# 如果在names表里没有找到，那么到entry表里取
			if not local_entry : local_entry = ai.GetAnimeByName(remote_name)
			# 如果取到name_cn == -1，说明是人工验证只有生肉的或不存在的，跳过
			elif local_entry[0]['name_cn'] == '-1' : continue

			# 此番应该是需要添加bili别名
			if not local_entry:
				log = '[NO ENTRY] name: %s' % remote_name.encode('utf-8')
				Tsukasa.debug(log)
				NEED_HANDLE.append(log)
				continue
			else:
				local_entry = local_entry[0]

			# 检查远端提供的话数是否需要修正
			if 'ep_revise' in local_entry : remote_epid += local_entry['ep_revise']

			local_id = local_entry['id']
			local_name = local_entry['name_cn']
			local_bid = local_entry['bgm']
			local_ep = ai.GetEp( local_id, remote_epid )
			
			del ai

			# ep表为空，这个情况应该是在一个季度刚开始连载时
			# 如果在连载中出现这个提示应该是出问题了吧
			if not local_ep:
				log = '[NO EP] id: %s | bid: %s | name: %s' % (local_id, local_bid, remote_name.encode('utf-8'))
				Tsukasa.debug(log)
				NEED_HANDLE.append(log)
				# 自动添加ep表
				UpdateEntry(local_bid)
				continue

			# 对照一下最新话，看看本地数据是否已经是最新的
			if (local_ep['bili'] != u'-1') and (local_ep['bili'] != u'') : continue

			# 到这里就是待更新的番组了
			# 先等待3秒好了..省得...
			time.sleep(3)
			# 搜bili
			r = SearchBilibili( local_name.encode('utf-8'), remote_epid )
			if not r: 
				Tsukasa.debug( '[skip] id: %s | ep.%s | name: %s' % (local_id, remote_epid, remote_name.encode('utf-8')))
				continue

			# 找到了的话，就插入数据库
			ai = Ai()
			ai.UpdateEpBili( r, local_id, remote_epid )
			del ai

			# 并且更新一下ep信息，一般来说bangumi应该会比bili早更新的
			r = FetchEpOfAnEntryFromBangumi( local_id, str(local_bid) )
			# 本来是觉得既然是新番，应该不会没人更新每话标题吧
			# 结果就真没有！{漫画少女}
			# 所以拉倒了，bili更新的时候bangumi还没人更新的话，就这样算了吧
			# if r != True:
			# 	Tsukasa.debug( str(local_id) + ' : ' + str(local_bid) + ' ' + r + ' {bangumi} ep info not updated yet')
			# 	continue

			# 运行到这里就是更新完毕啦
			Tsukasa.debug('[success] id: %s | ep.%s | name: %s' % (local_id, remote_epid, remote_name.encode('utf-8')))

# 被直接执行时...
if __name__ == '__main__':
	if len(sys.argv) > 1:
		param = sys.argv[1]

		if param == 'update_bili':
			Tsukasa.debug('update bili resources\n========================================================')

			try:
				UpdateBili()
			except Exception, e:
				Tsukasa.debug('Error: %s' % e)
				Tsukasa.debug(traceback.format_exc())
				
			Tsukasa.debug('END\n')

			# 如果有需要人工处理的条目就发个邮件给我
			if len(NEED_HANDLE) > 0:
				Risa.sendmail(NEED_HANDLE)

	# 没有传入参数
	else : Tsukasa.debug('No param specified')
