# -*- coding: utf-8 -*-

import re, json
from urllib import quote_plus

from base.utility import *

###

# bili无效视频
BILI_INVALID_FLAG = ['生肉', '被退回']

# 话数 阿拉伯数字转其他表示方法
EP_IN_NUM   = ['01','02','03','04','05','06','07','08','09','10']
EP_IN_CN	= ['一','二','三','四','五','六','七','八','九','十']
EP_IN_GREEK	= ['I','II','III','IV','V','VI','VII','VIII','IX','X']

# 匹配bili单话资源的正则
BILI_REGX = [
	'第\s*%s\s*话',
	'\s*%s\s*[^月]',
	'\s*%s$'
]

###

# 接口
def AddBiliResource( start, end ):
	global ERROR_NF
	end += 1
	# 准备Bili的cookie
	LoginBilibili();

	for i in range( start, end ):
		ret = doAddBiliResource( i )
		if ret == ERROR_NF : 
			Tsukasa.log( str(i) + ' dosent match anything')
			time.sleep(3)
		elif ret : 
			Tsukasa.log( str(i) + ' success')
			time.sleep(3)
		else : 
			Tsukasa.log( str(i) + ' skipped')

# 为entry、ep添加bili资源
def doAddBiliResource( eid, forceEP = False ):
	global CATE_BGM, ERROR_NF, ERROR_NET

	# 维护一个别名表
	names = []

	# 读取entry信息
	ai = Ai()
	entry = ai.GetEntryById( eid )
	cid = entry['cid']
	ep_total = entry['total']

	names.append( entry['name_cn'] )

	# 非动画或话数不正常的条目直接返回
	if cid != CATE_BGM['anime'] or ep_total < 1 : return False

	# 检查是否有bili别名
	bili_name = ai.GetAlterNameById( eid, 'bili' )
	if bili_name: 
		# 有人工指定的bili名说明错不了就是她了
		names.pop()
		names.append( bili_name )
	else:
		# 否则从tag表里取其他别名，加上entry['name_cn']一起搜索
		names.extend( ai.GetTagById(eid) )
		del ai

	# 先搜索资源
	for name in names:
		if LookForBiliResource( entry, name, forceEP ):
			return True

	# 实在找不到就算了
	return ERROR_NF

# 查找资源
# 找到返回True / 找不到返回False
def LookForBiliResource( entry, name, forceEP = False ):
	eid = entry['id']
	ep_total = entry['total']

	# 留个flag表示是否找到资源
	found = False

	name = name.encode('utf-8')
	av = SearchBilibili( name )

	if type(av) != bool and av.encode('utf-8') == ERROR_NET : exit(1)

	# 没有找到合集的情况下
	if not av or forceEP:
		
		# 再单独搜索每一话的资源
		tried = 0 # 留一个标识变量，如果前三次匹配都没有找到资源就跳过这整部动画，节约时间
		for epid in range( 1, ep_total + 1):
			# 主动放弃机制
			if tried > 3 and (not found):
				ai = Ai()
				for epid_x in range( epid, ep_total + 1 ):
					ai.AddBiliEp( -1, eid, epid_x )
				del ai

				# 记录放弃本动画，然后返回NOT FOUND
				Tsukasa.log( str(eid) + ' abandoned' )
				return False

			# 然后开始匹配
			time.sleep(3)
			aid = SearchBilibili( name, epid )
			if type(aid) == str and aid == ERROR_NET : 
				Tsukasa.debug( ERROR_NET )
				exit(1)

			ai = Ai()

			if not aid : 
				ai.AddBiliEp( -1, eid, epid )
				Tsukasa.log( str(eid) + ' ep.' + str(epid) + ' not found' )
				tried += 1

			else:
				# 找到了这话的资源，检查是否需要登录
				if NeedLogin( aid ) : aid = 'x' + str(aid)

				ai.AddBiliEp(aid, eid, epid )
				Tsukasa.log( str(eid) + ' ep.' + str(epid) + ' success' )

				found = True

			del ai

	# 在找到合集的情况下
	else:
		ai = Ai()
		for epid in range( 1, ep_total + 1 ):
			ai.AddBiliEp( av + '/index_' + unicode(epid)  + '.html', eid, epid )
		del ai

		Tsukasa.debug('find collection of {eid:' + str(eid) + '},{bgmid:' + str(entry['bgm']) + '} as ' + name)

		found = True

	return found

# 通过bili的API查找结果
def SearchBilibili( name, ep = None ):
	global URL_BILI_SEARCH, ERROR_NET, FILE_COOKIE_BILI, BILI_SEARCH_PREFIX_SINGLE, BILI_SEARCH_PREFIX_COLLECTION

	# 加上搜索范围
	if ep : keyword = name + ' ' + str(ep) + ' @' + BILI_SEARCH_PREFIX_SINGLE
	else : keyword = name + ' @' + BILI_SEARCH_PREFIX_COLLECTION

	# 连接
	c = Haruka.GetWithCookie( URL_BILI_SEARCH % quote_plus(keyword), FILE_COOKIE_BILI )
	if not c : return ERROR_NET

	# 解析json
	ret = json.loads(c)
	
	# 检查返回集是否为空
	try:
		if not ret['total'] > 0 : return False
	except:
		return False

	if ep :
		return FindEp( name, ep, ret['result'] )
	else :
		return FindCollection( ret['result'] )
	
# 查找合集
def FindCollection( results ):
	global BILI_SEARCH_PREFIX_COLLECTION
	# 只要有返回集，验证类型是完结动画就行了
	for index in range(len(results)):
		if results[str(index)]['typename'].encode('utf-8') == BILI_SEARCH_PREFIX_COLLECTION:
			return results[str(index)]['aid']

	# 如果运行到这里就是没有匹配的结果了
	return False

# 查找单话
def FindEp( name, ep, results ):
	for index in range(len(results)):
		if MatchTitle( name, ep, results[str(index)]['title'] ):
			return results[str(index)]['aid']

	# 如果运行到这里就是没有匹配的结果了
	return False

# 匹配番组的标题... 
# 目前的策略是，分辨作品别名交给bili去做，只要bili返回了结果，我就认为这是我要找的作品
# 比如说，在匹配“那朵花 5 @新番”时，返回的第一个结果title实际包含的是“我们仍未知道那天所看见的花的名字 05”
# 我并不自己检验这个结果的标题或TAG是否包含“那朵花”，而是相信bili返回的结果就是“那朵花 05”的别名
# 所以我检查完 05 是正确的之后，就当作是正确的结果返回了
def MatchTitle( name, ep, title ):
	title = title.encode('utf-8')

	# 首先检查是否是正常视频
	for keyword in BILI_INVALID_FLAG:
		if keyword in title:
			return False # 包含指示本视频链接无效的关键词则跳过这个结果

	# 开始匹配标题
	# 首先，话数小于10时，可能会有UP主用非阿拉伯数字来写话数
	if ep <= 10 :
		ep_patterns = [str(ep), EP_IN_NUM[ep-1], EP_IN_CN[ep-1], EP_IN_GREEK[ep-1]]
	else:
		ep_patterns = [str(ep)]

	# 匹配！
	for ep_pattern in ep_patterns:
		for regx in BILI_REGX:
			m = re.search(regx % ep_pattern, title)
			if m: return True

	# 不匹配
	return False

# 检查一个视频是否是会员限定
# 因为bili增加了验证码，这个功能暂时失效
def NeedLogin( av ):
	global URL_BILI, FILE_COOKIE_BILI

	# 不带cookie的访问
	c = Haruka.Get( URL_BILI % av )
	if not c : return False

	if '<div class="z-msg">' in c:
		# # 不带cookie时提示403了，再带上cookie看看
		c = Haruka.GetWithCookie( URL_BILI % av, FILE_COOKIE_BILI )
		if not c: return False

		# # 带上cookie后没有403提示了，则认为这是会员限定视频
		if '<div class="z-msg">' not in c:
			return True

		# 现在bili增加了验证码，登录失效了，所以凡是403的统统算作需要登录吧
		return True

	return False

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