# -*- coding: utf-8 -*-

import urllib2
import MySQLdb
import time
import socket
import zlib

from StringIO import StringIO
from gzip import GzipFile
from urllib import urlretrieve
from cookielib import MozillaCookieJar

from config import *
from accounts import *

# 设置网络超时时间
socket.setdefaulttimeout(15) 

# 初始化普通的只带一个UA的Header
Amagami = urllib2.build_opener(
	# urllib2.ProxyHandler({'http': '121.33.249.170:8080'})
)
Amagami.addheaders = [ ACGINDEX_UA ]
urllib2.install_opener( Amagami )

class Haruka:
	'森岛遥 Morishima Haruka'

	# GET
	@staticmethod
	def Get( url, retry = 3 ):
		try:
			res = urllib2.urlopen( url )
			return Haruka.GetContent( res )
		except:
			# 这里有3次重新连接的机会，3次都超时就跳过
			if retry > 0 : 
				return Haruka.Get( url, retry-1 )
			else:
				return False



	# 带cookie的 GET / POST
	# 不带data时就是GET,带data时当成POST，并且保存新cookie
	@staticmethod
	def GetWithCookie( url, cookie_name, data = '', retry = 3):
		global PATH_TMP, ACGINDEX_UA

		try:
			cj = MozillaCookieJar( PATH_TMP + cookie_name )

			try :
				cj.load( PATH_TMP + cookie_name )
			except:
				pass # 还没有cookie只好拉倒咯

			ckproc = urllib2.HTTPCookieProcessor( cj )

			AmagamiSS = urllib2.build_opener( ckproc )
			AmagamiSS.addheaders = [ ACGINDEX_UA ]


			if data != '':
				request = urllib2.Request( url = url, data = data )
				res = AmagamiSS.open( request )
				cj.save() # 只有在post时才保存新获得的cookie
			else:
				res = AmagamiSS.open( url )

			return Haruka.GetContent( res )

		except:
			# 这里有3次重新连接的机会，3次都超时就跳过
			if retry > 0 : 
				return Haruka.GetWithCookie( url, cookie_name, data , retry-1 )
			else:
				return False


	# 抓图
	@staticmethod
	def GetImage( eid, cid, url, retry = 3 ):
		global PATH_COVER
		try:
			urlretrieve( url, PATH_COVER + str(eid) + '_' + str(cid) + '.jpg')
			return True
		except:
			if retry > 0 :
				return Haruka.GetImage( eid, cid, url, retry-1 )
			else:
				return False



	# 取数据，主要是检查有没有gzip
	@staticmethod
	def GetContent( res ):
		# 检查是否被GZIP
		if res.info().get('Content-Encoding') == 'gzip':
		    buf = StringIO( res.read() )
		    f = GzipFile( fileobj=buf )
		    data = f.read()
		elif res.info().get('Content-Encoding') == 'deflate':
			gz = StringIO( Haruka.deflate( res.read() ) )
			_res = urllib2.addinfourl( gz, res.headers, res.url, res.code )
			_res.msg = res.msg
			data = _res.read()
		else:
			data = res.read()

		return data

	# 尝试对reflate内容进行解压...
	@staticmethod
	def deflate( data ):
		try:
			return zlib.decompress(data, -zlib.MAX_WBITS)
		except zlib.error:
			return zlib.decompress(data)




class Ai:
	'七咲逢 Nanasaki Ai'

	# 构造函数时连接数据库
	def __init__(self, dbname = DB_NAME):
		try:
			self._ = MySQLdb.connect( DB_HOST, DB_USER, DB_PASS, dbname, charset="utf8" )
			self.c  = self._.cursor( MySQLdb.cursors.DictCursor ) # 使fetchall的返回值为带key的字典形式
		except Exception, e:
			Tsukasa.debug('数据库连接出错 : ' + str(e))
			exit(1)

	# 析构时关闭数据库
	def __del__(self):
		self.c.close()
		self._.close()


	# 通用部分
	###

	# 查询
	def Query( self, sql, data = None):
		try:
			if data : 
				self.c.execute( sql, data )
			else : 
				self.c.execute( sql )

			return self.c.fetchall()
		except Exception, e:
			Tsukasa.debug( str(e[0]) + ' : ' + e[1] )
			return False # 返回False表示数据库出错


	# 执行
	def Run( self, sql, data ):
		try:
			self.c.execute( sql, data )
			return self._.insert_id()
		except Exception, e:
			# 1062是UNIQUE键重复，这是正常情况
			if e[0] == 1062 : return ERROR_DK
			Tsukasa.debug( str(e[0]) + ' : ' + e[1] )
			# 其他错误要捕获
			return False # 返回False表示数据库出错


	# BGM部分
	###

	# 根据id取一个条目
	def GetEntryById( self, id ):
		sql = "SELECT * FROM `entry` WHERE `id` = %s"
		return self.Query( sql, id )[0]

	# 根据bgmid取一个条目
	def GetEntryByBgmId( self, bid ):
		sql = "SELECT * FROM `entry` WHERE `bgm` = %s"
		r = self.Query( sql, bid )
		if len(r): return r[0]
		else: return None

	# 根据名字取条目
	def GetEntryByName( self, name ):
		name += '%'
		# 先直接匹配entry.name_cn
		sql = "SELECT * FROM `entry` WHERE `name_cn` LIKE %s"
		r = self.Query( sql, name )
		if len(r): return r

		# 再匹配tags表
		sql = "SELECT * FROM `entry`,`link`,`tags` WHERE `entry`.`id` = `link`.`eid` AND `link`.`tid` = `tags`.`tid` AND `tags`.`name` LIKE %s"
		r = self.Query( sql, name )
		if len(r): return r
		else: return 0




	# 根据名字取动画
	def GetAnimeByName( self, name ):
		global CATE_BGM
		name += '%'
		# 先直接匹配entry.name_cn
		sql = "SELECT * FROM `entry` WHERE `name_cn` LIKE %s AND `cid` = %s"
		r = self.Query( sql, ( name, CATE_BGM['anime'] ) )
		if len(r): return r

		# 再匹配tags表
		sql = "SELECT `entry`.* FROM `entry`,`link`,`tags` WHERE `entry`.`id` = `link`.`eid` AND `entry`.`cid` = %s AND `link`.`tid` = `tags`.`tid` AND `tags`.`name` LIKE %s"
		r = self.Query( sql, ( CATE_BGM['anime'], name ) )
		if len(r): return r
		else: return False

	# 取动画的bili别名
	def GetAnimeByAlterName( self, source, index_name ):
		global NAMES_SOURCES
		# 准备SQL
		sql = "SELECT * FROM `names` WHERE `source` = %s AND `index_name` = %s"
		r = self.Query( sql, (NAMES_SOURCES[source], index_name) )

		# 如果没有存别名，那就返回
		if not len(r): return False
		else: r = r[0]

		# 如果存了别名，就从entry表中取出相应的条目，把name_cn替换成bili使用的real_name，然后返回
		entry = self.GetEntryById( r['eid'] )

		if r['real_name'] == '':
			entry['name_cn'] = r['index_name']
		else:
			entry['name_cn'] = r['real_name']

		# 如果话术需要修正，那么也带上话数修正数据
		if r['ep_revise'] != 0 : entry['ep_revise'] = r['ep_revise']

		return (entry,)




	# 检查某个entry是否有别名
	def GetAlterNameById( self, eid, source ):
		global NAMES_SOURCES
		# 准备SQL
		sql = "SELECT * FROM `names` WHERE `source` = %s AND `eid` = %s"
		r = self.Query( sql, ( NAMES_SOURCES[source], eid) )

		# 返回值
		if len(r): 
			r = r[0]
			if r['real_name'] != '' : return r['real_name']
			else : return r['index_name']
		else:
			return False




	# 获取EP数据
	def GetEp( self, *args ):
		sql = "SELECT * FROM `ep` WHERE `eid` = %s AND `epid` = %s"
		r = self.Query( sql, args )
		if len(r) : return r[0]
		else: return False





	# 根据id取他的所有tag
	def GetTagById( self, id ):
		sql = "SELECT `name` FROM `tags` INNER JOIN `link` ON `link`.`tid` = `tags`.`tid` INNER JOIN `entry` ON `entry`.`id` = %s AND `entry`.`id` = `link`.`eid`"
		tags = self.Query( sql, id )
		tag_list = []

		if type(tags) == tuple and len(tags) :
			for tag in tags:
				tag_list.append(tag['name'])

		return tag_list




	# 按分类获取
	def GetEntryByCategory( self, category_name ):
		global CATE_BGM
		sql = "SELECT `id`,`name_cn` FROM `entry` WHERE `cid` = " + str(CATE_BGM[category_name])
		return self.Query( sql )



	### 
	### 插入
	###


	# 添加entry
	def AddEntry( self, *args ):
		sql = "INSERT INTO `entry` (`name_cn` ,`name_jp` ,`cid` , `bgm` ,`total`) VALUES ( %s, %s, %s, %s, %s ) "
		return self.Run( sql, args )

	# 添加ep
	def AddEp( self, *args ):
		# 先检查此ep是否已存在
		sql = "SELECT COUNT(*) FROM `ep` WHERE `eid` = %s AND `epid` = %s"
		r = self.Query( sql, ( args[0], args[1] ) )[0]['COUNT(*)']

		# 没有这个条目的话就新插入
		if not r :
			sql = "INSERT INTO `ep` ( `eid`, `epid`, `name_jp`, `name_cn` ) VALUES ( %s, %s, %s, %s ) "
			return self.Run( sql, args )
		# 否则就更新
		else:
			sql = "UPDATE `ep` SET `name_jp` = %s, `name_cn` = %s WHERE `eid` = %s AND `epid` = %s"
			return self.Run( sql, (args[2], args[3], args[0], args[1]) )

	# 添加tag - 新TAG时写入LINK表
	def AddTag( self, name, eid ):
		global ERROR_DK
		sql = "INSERT INTO `tags` ( `name` ) VALUES ( %s )"
		tid = self.Run( sql, name )

		# Duplicated Key表示TAG已存在，那么获取已存在的TAGID
		if tid == ERROR_DK : 
			tid = self.Query( "SELECT `tid` FROM `tags` WHERE `name` = %s", name)[0]['tid']
						
		self.LinkTAGtoENTRY( tid, eid )

	# 添加 TAG 与 ENTRY 的关联
	def LinkTAGtoENTRY( self, *args ):
		sql = "SELECT COUNT(*) FROM `link` WHERE `tid` = %s AND `eid` = %s"
		r = self.Query( sql, args )[0]['COUNT(*)']

		# 当取到的行数为0时说明还没有添加过这个link
		if not r:
			sql = "INSERT INTO `link` ( `tid`, `eid` ) VALUES ( %s, %s )"
			return self.Run( sql, args )

	# 为条目添加别名
	def AddAlterNameToBgmid( self, bgmid, source, index_name, real_name = '' ):
		global NAMES_SOURCES
		# 先取entry id
		sql = "SELECT `id` FROM `entry` WHERE `bgm` = %s"
		eid = self.Query( sql, bgmid )

		# 也许会超过目前抓到的最大bgmid？
		if not len(eid) : return -1
		else : eid = eid[0]['id']

		# 处理数据
		source_id = NAMES_SOURCES[source]

		# 插入别名
		sql = "INSERT INTO `names` ( `eid`, `source`, `index_name`, `real_name` ) VALUES ( %s, %s, %s, %s )"
		return self.Run( sql, ( eid, source_id, index_name, real_name ))




	###
	### 更新
	###



	# 更新条目
	def UpdateTotalEpOfAnEntry( self, *args ):
		sql = "UPDATE `entry` SET `total` = %s WHERE `bgm` = %s"
		return self.Run( sql, args )

	# 更新ep
	def UpdateEpBili( self, *args ):
		sql = "UPDATE `ep` SET `bili` = %s WHERE `eid` = %s AND `epid` = %s"
		return self.Run( sql, args )




	# BILI部分
	###

	# 添加合集
	def AddBiliCollection( self, *args ):
		sql = "UPDATE `entry` SET `bili` = %s WHERE `id` = %s"
		return self.Run( sql, args )

	# 添加EP
	def AddBiliEp( self, *args ):
		sql = "UPDATE `ep` SET `bili` = %s WHERE `eid` = %s AND `epid` = %s "
		return self.Run( sql, args )


class Tsukasa:
	'绚辻 词 Ayatsuji Tsukasa'

	# 获取当前时间
	@staticmethod
	def GetTime():
		return time.strftime('[%H:%M:%S] ',time.localtime(time.time()))

	# 普通的记录方法
	@staticmethod
	def log( message ):
		# 判断输出环境编码，并用该编码输出
		if sys.stdout.encoding != None :
			stdout_encoding = sys.stdout.encoding
		else:
			stdout_encoding = 'utf-8'
		print Tsukasa.GetTime() + message.decode('utf-8').encode(stdout_encoding)

	# 输出到记录
	@staticmethod
	def debug( message ):
		Tsukasa.log( message )
		try:
			f = open( PATH_LOG + time.strftime('%Y-%m-%d.log', time.localtime(time.time())), 'a+')
		except:
			f = open( PATH_LOG + time.strftime('%Y-%m-%d.log', time.localtime(time.time())), 'w+')
		finally:
			f.write( Tsukasa.GetTime() + message + '\n' )
			f.close()
