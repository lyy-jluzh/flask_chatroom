#!/usr/bin/python
# -*- coding: UTF-8 -*-
import redis

redis_cli = redis.StrictRedis(host='localhost', port=6379, db=0)

def get():
    return redis_cli