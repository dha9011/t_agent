#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Date : 8/3/16 PM1:10
# Copyright: TradeShift.com
__author__ = 'liming'

import requests
from lib.logging import create_logger
import uuid
import os

logger = create_logger(__name__)

tmp_dir = '/data/temp/'

def download_file(download_url, code_file, version_url=None):

    try:
        # r = requests.get(nexus_url.format(app_name, version, file_type))
        r = requests.get(download_url)
    except Exception, e:
        logger.error('Download error from nexus: %s' % str(e))
        return 9, 'Download Error from nexus', None
    # print 'download finish'
    # print r.status_code
    if r.status_code == 404:
        return 1, 'No such version : %s' % download_url, None

    elif r.status_code == 200:
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        f_name = tmp_dir + '/' + code_file + '_' + uuid.uuid1().hex
        with open(f_name, 'wb') as f:
            f.write(r.content)

        # get version info
        version_info = None
        if version_url:
            try:
                r =requests.get(version_url)
                if r.status_code == 200:
                    version_info = r.content
            except Exception, e:
                logger.warning('Can not get version info for %s: %s' % (version_url, str(e)))

        return 0, f_name, version_info

    else:
        return 2, 'nexus return error: %s' % r.status_code, None

