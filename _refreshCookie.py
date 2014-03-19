# -*- coding: utf-8 -*-
# 这个脚本专门负责更新bili的cookie
# 
# 写个cron每周日0:00更新cookie，确保cookie一直有效
# 0 0 * * 0 python /var/www/acgindex/_refreshCookie.py

from fetchBilibili import LoginBilibili

LoginBilibili()