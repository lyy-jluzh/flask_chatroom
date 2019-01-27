#!/usr/bin/python
# -*- coding: UTF-8 -*-

from src.db.mysqlTemplate import newTemplate

template = newTemplate('user')


def save(obj):
    return template.save(obj)

def find(filter, fields=None, skip=0, limit=999, sort=None):
    return template.find(filter, fields, skip, limit, sort)

def findOne(filter):
    return template.findOne(filter)

def count(filter):
    return template.count(filter)

def update(filter,update_data):
    return template.update(filter,update_data)
