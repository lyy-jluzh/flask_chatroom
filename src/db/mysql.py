#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql


def getConn():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='bee',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection