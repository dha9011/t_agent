#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Date : 9/3/16 PM12:46
# Copyright: TradeShift.com
__author__ = 'liming'

from app import cfg
import xmlrpclib, os, commands
from lib.logging import create_logger
from lib.common import retry

logger = create_logger(__name__)

class SupervisorRpc(object):

    def __init__(self):
        url = cfg['supervisor_url']
        self.conn = xmlrpclib.Server(url)

    @retry(attempt=3)
    def start_app(self, app_name):
        try:
            _, c = self.get_app_info(app_name)
            if c.get('statename') == 'RUNNING':
                return 0, 'Already running'
            if self.conn.supervisor.startProcess(app_name):
                # check status
                _, _c = self.get_app_info(app_name)
                if _c.get('statename') != 'RUNNING':
                    return 2, 'Start error'
                else:
                    return 0, ''
            else:
                return 1, 'Supervisor Error'
        except Exception, e:
            logger.error('Supervisor exception: %s' % str(e))
            return 1, 'Supervisor Error'

    @retry(attempt=3)
    def stop_app(self, app_name):
        try:
            _, c = self.get_app_info(app_name)
            if c.get('statename') == 'STOPPED':
                return 0, 'Already stopped'
            if self.conn.supervisor.stopProcess(app_name):
                # check status
                _, _c = self.get_app_info(app_name)
                if _c.get('statename') != 'STOPPED':
                    return 2, 'Stop error'
                else:
                    return 0, ''
            else:
                return 1, 'Supervisor Error'
        except Exception, e:
            logger.error('Supervisor exception: %s' % str(e))
            return 1, 'Supervisor Error'

    def restart_app(self, app_name):
        try:
            s, _ = self.stop_app(app_name)
            if s:
                return 2, 'Fail to stop when restart'
            s, _ = self.start_app(app_name)
            if s:
               return 2, 'Fail to start when restart'
        except Exception, e:
            logger.error('Supervisor exception when restart: %s' % str(e))
            return 1, 'Supervisor Error'
        return 0, 'Done'

    def get_log(self, app_name, offset=0, length=0):
        try:
            return 0, self.conn.supervisor.readProcessLog(app_name, offset, length)
        except Exception, e:
            logger.error('Supervisor exception: %s' % str(e))
            return 1, 'Supervisor Error'

    @retry(attempt=3)
    def get_app_info(self, app_name):
        try:
            _state = self.conn.supervisor.getProcessInfo(app_name)
            # state = 'unknown' if not _state else _state.get('statename').lower()
            # start_time = 'unknown' if not _state else _state.get('start')
            return 0, _state
        except Exception, e:
            logger.error('Supervisor exception: %s' % str(e))
            return 1, 'Supervisor Error'

    def get_app_log(self, app_name, log_type, lines=20):
        try:
            if lines <= 0:
                lines = 20
            _conf = self.conn.supervisor.getProcessInfo(app_name)
            std_f = _conf.get('stdout_logfile')
            ste_f = _conf.get('stderr_logfile')
            if log_type == 'stdout':
                f_name = std_f
            elif log_type == 'stderr':
                f_name = ste_f
            else:
                return 1, 'Bad log type'
            if f_name is None:
                logger.debug('log file is not found')
                return 1, 'log file is not found'

            if not os.path.isfile(f_name):
                logger.debug('log file %s is not exist' % f_name)
                return 1, 'log file %s is not exist' % f_name

            cmd = 'tail -n %s %s' % (lines, f_name)
            s, c = commands.getstatusoutput(cmd)
            if s:
                logger.debug('read log file %s error' % f_name)
                return 1, 'read log file %s error' % f_name
            else:
                return 0 , c
        except Exception, e:
            logger.error('Error when read log file of %s: %s' % (app_name, str(e)))
            return 2, 'Some error'
