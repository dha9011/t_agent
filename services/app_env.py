#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Date : 9/4/16 PM5:30
# Copyright: TradeShift.com
__author__ = 'liming'

import re
from lib.logging import create_logger

logger = create_logger(__name__)

_conf = '/etc/supervisor/conf.d/{0}.conf'

class APPENV(object):


    def __init__(self, app_name):
        self.app_name = app_name
        self.conf = _conf.format(app_name)
        self.env = {}

    @property
    def running_env(self):
        d, c = None, None
        try:
            with open(self.conf, 'r') as f:
                for i in f.readlines():
                    _d = re.match('^directory=', i)
                    _c = re.match('^command=', i)
                    if _d:
                        d = _d.string.split('=')[1].strip('\n')
                    if _c:
                        c = _c.string.split('=')[1].strip('\n')
        except Exception,e:
            logger.error('Read supervisor config failed for app %s: %s' % (self.app_name, str(e)))
        self.env = {'app_path': d,
                    'command': c}
        return self.env