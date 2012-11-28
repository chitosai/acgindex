# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib, gzip
import MySQLdb
import time
import socket

from config import *
from accounts import *
from sys import stderr
from StringIO import StringIO

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
			cj = cookielib.MozillaCookieJar( PATH_TMP + cookie_name )

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
			urllib.urlretrieve( url, PATH_COVER + str(eid) + '_' + str(cid) + '.jpg')
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
		    f = gzip.GzipFile( fileobj=buf )
		    data = f.read()
		else:
			data = res.read()

		return data




class Ai:
	'七咲逢 Nanasaki Ai'

	# 构造函数时连接数据库
	def __init__(self, dbname = DB_NAME):
		try:
			self._ = MySQLdb.connect( DB_HOST, DB_USER, DB_PASS, dbname, charset="utf8" )
			self.c  = self._.cursor( MySQLdb.cursors.DictCursor )
		except:
			Tsukasa.debug('数据库连接出错')
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
			return False # 返回False表示数据库出错


	# 执行
	def Run( self, sql, data ):
		try:
			self.c.execute( sql, data )
			return self._.insert_id()
		except Exception, e:
			# 1062是UNIQUE键重复，这是正常情况
			if e[0] == 1062 : return ERROR_DK
			Tsukasa.debug( e[0] + ' : ' + e[1] )
			# 其他错误要捕获
			return False # 返回False表示数据库出错


	# BGM部分
	###

	# 根据id取一个条目
	def GetEntryById( self, id ):
		sql = "SELECT * FROM `entry` WHERE `id` = %s"
		return self.Query( sql, id )[0]

	# 根据id取他的所有tag
	def GetTagById( self, id ):
		sql = "SELECT `name` FROM `tags` INNER JOIN `link` ON `link`.`tid` = `tags`.`tid` INNER JOIN `entry` ON `entry`.`id` = %s AND `entry`.`id` = `link`.`eid`"
		return self.Query( sql, id )

	# 按分类获取
	def GetEntryByCategory( self, category_name ):
		global CATE_BGM
		sql = "SELECT `id`,`name_cn` FROM `entry` WHERE `cid` = " + str(CATE_BGM[category_name])
		return self.Query( sql )


	# 添加entry
	def AddEntry( self, *args ):
		sql = "INSERT INTO `entry` (`name_cn` ,`name_jp` ,`cid` , `bgm` ,`total`) VALUES ( %s, %s, %s, %s, %s ) "
		return self.Run( sql, args )

	# 添加ep
	def AddEp( self, *args ):
		sql = "INSERT INTO `ep` ( `eid`, `epid`, `name_jp`, `name_cn` ) VALUES ( %s, %s, %s, %s ) "
		return self.Run( sql, args )

	# 添加tag - 新TAG时写入LINK表
	def AddTag( self, name, eid ):
		sql = "INSERT INTO `tags` ( `name` ) VALUES ( %s )"
		tid = self.Run( sql, name )
		
		# tid=0表示TAG已存在，那么获取已存在的TAGID
		if tid == 0 : 
			tid = self.Query( "SELECT `tid` FROM `tags` WHERE `name` = %s", name)[0][0]
						
		self.LinkTAGtoENTRY( tid, eid )

	# 添加 TAG 与 ENTRY 的关联
	def LinkTAGtoENTRY( self, *args ):
		sql = "INSERT INTO `link` ( `tid`, `eid` ) VALUES ( %s, %s )"
		return self.Run( sql, args )


	# BILI部分
	###

	# 添加合集
	def AddBiliCollection( self, *args ):
		sql = "UPDATE `entry` SET `url1` = %s WHERE `id` = %s"
		return self.Run( sql, args )

	# 添加EP
	def AddBiliEp( self, *args ):
		sql = "UPDATE `ep` SET `url1` = %s, `bili_flag` = %s WHERE `eid` = %s AND `epid` = %s "
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
		print Tsukasa.GetTime() + message

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