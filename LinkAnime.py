# -*- coding: utf-8 -*-

from base.utility import *

import re

def LinkRw():
	# 取动画条目列表
	ai = Ai()
	entry_list = ai.GetAnimeEntry()
	if not entry_list : return '取不到动画条目列表'

	# 取肉丸条目列表
	rw_tag_list = ai.GetRwTags()
	if not rw_tag_list : return '取不到肉丸TAG列表'

	# 循环
	for entry in entry_list:
		# 已经收录了rw地址的话就跳过
		if entry[2] != '' : continue

		# 先用name_cn匹配
		for tag in rw_tag_list:
			print entry,tag
			if entry[1] in tag[0]:
				LinkEntry( entry, tag )
				continue

		# 再取bgm TAG做匹配
		bgm_tag_list = ai.GetBgmTags()
		print bgm_tag_list[1]

		return 'end'


		#ai.Query("SELECT `tags`.`name` FROM `tags` INNER JOIN `link` ON `tags`.`tid`=`link`.`tid` INNER JOIN `entry` ON `link`.`eid` = `entry`.`id` WHERE `entry`.`id` = %s")



print LinkRw()