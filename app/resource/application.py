#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Date : 9/3/16 PM2:57
# Copyright: TradeShift.com
__author__ = 'liming'

import sys

from flask.ext import restful
from flask.ext.restful.reqparse import Argument as Arg
from lib.utils import get_parser
from lib.logging import create_logger
from services.supervisor import SupervisorRpc

reload(sys)
sys.setdefaultencoding("utf-8")

logger = create_logger(__name__)

class STATUS(restful.Resource):

    def __init__(self):
        self.p = SupervisorRpc()

    def post(self, app_name, status_name):
        # arguments = [
        #     Arg('status_name', type=str, required=False, default=None),
        # ]
        # args = get_parser(arguments).parse_args()
        # status_name = args['status_name']
        s, c = self.p.get_app_info(app_name)
        if s:
            return {'status': 1, 'content': 'Supervisor error'}

        if status_name == 'all':
            _info = c
        else:
            _info = c.get(status_name)

        return {'status': 0, 'content': _info}


class ACTION(restful.Resource):

    def __init__(self):
        self.p = SupervisorRpc()

    def post(self, action, app_name):
        logger.info('New action: %s, name: %s ' %(action, app_name))
        funcs = {'start': self.p.start_app,
                'stop': self.p.stop_app,
                 'restart': self.p.restart_app}

        func = funcs.get(action, lambda x: (9, 'unknown action'))
        s, c = func(app_name)
        return {'status': s, 'content': c}

class READLOG(restful.Resource):

    def __init__(self):
        self.p = SupervisorRpc()

    def post(self, app_name, log_type):
        arguments = [
            Arg('lines', type=int, required=False, default=20),
        ]
        args = get_parser(arguments).parse_args()
        lines = args['lines']
        s, c = self.p.get_app_log(app_name, log_type, lines)
        return {'status': s, 'content': c}
