#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Date : 9/3/16 AM10:47
# Copyright: TradeShift.com
__author__ = 'liming'
from lib.logging import create_logger
from http_retrieve import download_file
import uuid, os, shutil
from commands import getstatusoutput
from lib.common import cur_time
from .supervisor import SupervisorRpc
from .app_env import APPENV
import json

logger = create_logger(__name__)
tmp_path = '/data/tmp'

def setConfig(env, config, config_path, config_name):
    try:
        env = json.loads(env.replace("u'", "'").replace("'", '"'))
        for item in env:
            with open(config) as o:
                out = o.read()
                key = item['varKey']
                value = item['value']
                out = out.replace(key, value)
                if not os.path.exists(config_path):
                    os.mkdir(config_path)
                config_target = config_path.rstrip('/') + '/' + config_name
                with open(config_target, 'w') as config_file:
                    config_file.write(out)
    except Exception, e:
        logger.error('Error when modify config: %s' % (str(e)))
        return 20, 'Modify config file failed'

def build_code(app_name, download_url, config_url, version_url, code_file, build_type, config_name, config_path, env, exclude_list='', restart=False):
    logger.info('New build: name:%s, download:%s, config_url: %s, version_url: %s, code_file:%s, build_type: %s, config_name:%s, config_path:%s,'
                ' exclude: %s,restart: %s' % (app_name, download_url, config_url, version_url, code_file, build_type,
                                                           config_name, config_path, exclude_list, restart))
    s, f, v = download_file(download_url, code_file, version_url)
    if s:
        # return json.dumps({'status': s, 'content': f})
        return s, f

    _env = APPENV(app_name).running_env
    app_path = _env['app_path']
    if app_path is None:
        return 9, 'Can not find app path'

    if not os.path.exists(app_path):
        os.mkdir(app_path)

    # get app_path from supervisor
    if build_type == 'tar':
        # need uncompress
        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)
        src_dir = tmp_path + '/' + uuid.uuid1().hex + '/'
        os.mkdir(src_dir)

        exclude = ''
        if exclude_list:
            for i in exclude_list.split(','):
                exclude += '--exclude=%s ' % str(i)
        s, c = getstatusoutput('tar -zxf %s -C %s' % (f, src_dir))
        if s:
            logger.error('Error when uncompress file %s: %s' % (f, c))
            return 1, 'os uncompress error'
        s, c = getstatusoutput('rsync -avrtopgl %s %s %s' % (exclude, src_dir.rstrip('/') + '/', app_path.rstrip('/')))
        if s:
            logger.error('Error when rsync file %s: %s' % (f, c))
            return 1, 'os rsync error'
        print 'rsync -avrtopgl %s %s %s' % (exclude, src_dir.rstrip('/') + '/', app_path.rstrip('/'))
        try:
            # os.removedirs(src_dir)
            # os.removedirs could only delete 2 dir
            shutil.rmtree(src_dir)
            os.remove(f)
        except Exception, e:
            logger.error('Error when remove src files: %s, %s : %s' % (src_dir, f, str(e)))

    elif build_type == 'file':
        # single file
        dst_f = app_path.rstrip('/') + '/' + code_file
        if os.path.isfile(dst_f):
            logger.debug('start to remove old file %s' % dst_f)
            os.remove(dst_f)
        try:
            shutil.move(f, dst_f)
        except Exception, e:
            logger.error('Replace new file error: %s  -- %s, error is : %s' % (f, dst_f, str(e)))
            # return json.dumps({'status': 9, 'content': 'Copy new file error'})
            return 1, 'Copy new file error'

    else:
        logger.error('Unknown deploy type: %s' % build_type)
        return {'status': 2, 'content': 'Unknown deploy type: %s' % build_type}

    # write version file
    with open(app_path + '/' + 'AUTO_VERSION.txt', 'w') as f_handle:
        f_handle.write(cur_time() + '\n')
        if not v:
            f_handle.write('Latest version' + '\n')
        else:
            f_handle.write(v)

    #add modify config function
    s, config, v = download_file(config_url, config_name, version_url)
    if s:
        # return json.dumps({'status': s, 'content': f})
        return s, f

    setConfig(env, config, config_path, config_name)
    ####

    if restart == "True":
        p = SupervisorRpc()
        s, c = p.restart_app(app_name)
        if s:
            return 3, c
    # xml module will transport dict to json
    return 0, 'done'



