#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Date : 17/2/16 PM4:02
# Copyright: TradeShift.com
__author__ = 'liming'

from app import app, api
import resource

RESOURCES = [
    (resource.BUILD, '/app/build'),
    (resource.STATUS, '/app/status/<string:app_name>/<string:status_name>'),
    (resource.ACTION, '/app/action/<string:app_name>/<string:action>'),
    (resource.READLOG, '/app/log/<string:app_name>/<string:log_type>'),
]

for res, uri in RESOURCES:
    api.add_resource(res, uri)