#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Date : 17/2/16 PM3:38
# Copyright: TradeShift.com
__author__ = 'liming'

import sys

from flask.ext import restful
from flask.ext.restful.reqparse import Argument as Arg
from lib.logging import create_logger
from lib.utils import get_parser
from services.build_service import build_code

reload(sys)
sys.setdefaultencoding("utf-8")

logger = create_logger(__name__)

class BUILD(restful.Resource):

    def post(self):

        arguments = [
            Arg('download_url', type=str, required=True, help='Miss download url'),
            Arg('app_name', type=str, required=True, help='Miss app name'),
            Arg('config_path', type=str, required=False, help='Miss app path'),
            Arg('code_file', type=str, required=True, help='Miss file name'),
            Arg('config_url', type=str, required=True, help='Miss config url'),
            Arg('config_name', type=str, required=True, help='Miss config name'),
            Arg('build_type', type=str, required=True, help='Miss build type'),
            Arg('env', type=str, required=False, default=''),
            Arg('version_url', type=str, required=False, default=None),
            Arg('restart', type=str, required=False, default='False'),
            Arg('exclude', type=str, required=False, default=''),
        ]
        args = get_parser(arguments).parse_args()
        build_type = args['build_type']
        exclude_list = args['exclude']
        config_path = args['config_path']
        config_name = args['config_name']
        app_name = args['app_name']
        code_file = args['code_file']
        download_url = args['download_url']
        config_url = args['config_url']
        env = args['env']
        version_url = args['version_url']
        restart = args['restart']

        s, c = build_code(app_name, download_url, config_url, version_url, code_file, build_type, config_name, config_path, env, exclude_list, restart)
        return {'status': s, 'content': c}
