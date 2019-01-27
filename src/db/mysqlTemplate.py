#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import src.db.mysql
import src.utils.Utils as Utils

def query(sql):
    conn = src.db.mysql.getConn()
    with conn.cursor() as cursor:
        cursor.execute(sql)
        conn.commit()
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return {'data': data}
        
def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value) and not name.startswith('_'):
            pr[name] = value
    return pr

def fields_sql(entity_name,fields):
    if fields != None:
        filter_str = ''
        for field in fields:
            if isinstance(field,dict):
                filter_str += (list(field.keys())[0] + ',')
        if len(filter_str) > 0:
            filter_str = filter_str[0,-1]
            sql = 'select ' + filter_str + ' from `' + entity_name + '`'
        else:
            sql = 'select * from `' + entity_name + '`'
        return sql
    else:
        sql = 'select * from `' + entity_name + '`'
        return sql

def filter_condition(sql,child_key,child_value):
    condition_key = list(child_value.keys())[0]
    if condition_key == '$regex':
        sql += (child_key + ' like "%' + str(child_value[condition_key]) + '%"')
    elif condition_key == '$nl':
        sql += (child_key + ' not like "％' + str(child_value[condition_key]) + '%"')
    elif condition_key == '$ne':
        if child_value[condition_key] == None:
            sql += (child_key + 'is not null ')
        else:
            sql += (child_key + ' != "' + str(child_value[condition_key]) + '"')
    elif condition_key == '$gt':
        sql += (child_key + ' > ' + str(child_value[condition_key]))
    elif condition_key == '$gte':
        sql += (child_key + ' >= ' + str(child_value[condition_key]))
    elif condition_key == '$lt':
        sql += (child_key + ' < ' + str(child_value[condition_key]))
    elif condition_key == '$lte':
        sql += (child_key + ' <= ' + str(child_value[condition_key]))
    elif condition_key == '$in':
        condition = '('
        for c in child_value[condition_key]:
            if isinstance(c,str):
                condition += '"' + c + '",'
            else:
                condition += str(c) + ','
        condition = condition[0:len(condition)-1]
        condition = condition + ')'
        sql += (child_key + ' in ' + condition)
    elif condition_key == '$not in':
        condition = '('
        for c in child_value[condition_key]:
            if isinstance(c,str):
                condition += '"' + c + '",'
            else:
                condition += str(c) + ','
        condition = condition[0:len(condition)-1]
        condition = condition + ')'
        sql += (child_key + 'not in ' + condition)
    return sql

def filter_sql(sql,filter):
    if len(filter) == 0:
        return sql
    sql += ' where '
    field_keys = list(filter.keys())
    for field_index in range(len(field_keys)):
        field_key = field_keys[field_index]
        field_value = filter[field_key]
        if field_index > 0:
            sql += ' and '
        if isinstance(field_value, dict):
            if field_key == '$and' or field_key == '$or':
                child_keys = list(field_value.keys())
                sql += ' ('
                for child_field_index in range(len(child_keys)):
                    child_key = child_keys[child_field_index]
                    child_value = field_value[child_key]
                    if isinstance(child_value, str):
                        child_value = '"' + child_value + '"'
                    if child_field_index > 0:
                        if field_key == '$or':
                            sql += ' or '
                        else:
                            sql += ' and '
                    sql = filter_condition(sql, child_key, child_value)
            else:
                sql = filter_condition(sql, field_key, field_value)
        else:
            if isinstance(field_value, str):
                field_value = '"' + field_value + '"'
            else:
                field_value = str(field_value)
            sql += (field_key + '=' + field_value)
    return sql

def sort_sql(sql,sort):
    sql += ' order by';
    if sort != None and len(sort) > 0:
        for index in range(len(sort.keys())):
            if index > 0:
                sql += ','
            key = list(sort.keys())[index]
            sql += (' ' + key)
            if sort[key] == -1 or sort[key] == 'desc':
                sql += ' desc'
            else:
                sql += ' asc'
    else:
        sql += (' id desc')
    return sql

class Template:

    entity_name = ''


    def __init__(self, entity_name):
        self.entity_name = entity_name

    def find(self, filter, fields={}, skip=None, limit=None, sort={}):
        conn = src.db.mysql.getConn()
        with conn.cursor() as cursor:
            sql = fields_sql(self.entity_name,fields)
            sql = filter_sql(sql,filter)
            sql = sort_sql(sql,sort)
            if skip != None and limit != None:
                sql = sql + ' limit ' + str(skip) + ',' + str(limit)
            cursor.execute(sql)
            rs = cursor.fetchall()
            if rs == ():
                rs = []
            conn.commit()
            cursor.close()
            conn.close()
            return {'data': rs}
       


    def findOne(self, filter, sort={'id': 1}):
        conn = src.db.mysql.getConn()
        with conn.cursor() as cursor:
            sql = 'select * from `' + self.entity_name + '`'
            sql = filter_sql(sql,filter)
            sql = sort_sql(sql,sort)
            cursor.execute(sql)
            rs = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            return {'data': rs}
    

    def count(self, filter):
        conn = src.db.mysql.getConn()
        with conn.cursor() as cursor:
            sql = 'select count(*) as count from `' + self.entity_name + '` '
            sql = filter_sql(sql,filter)
            cursor.execute(sql)
            rs = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            if rs.get('err') != None:
                return rs
            return {'data': rs.get('count')}

    def save(self, obj):
        conn = src.db.mysql.getConn()
        with conn.cursor() as cursor:
            if obj.createtime != None:
                obj.createtime = Utils.getStamp()
            if obj.version != None:
                obj.version = time.strftime('%Y-%m-%d',time.localtime())
            sql = 'insert into `' + self.entity_name + '` ('
            dict = props(obj)

            for key in dict.keys():
                sql += key + ','
            sql = sql[0:(len(sql)-1)] + ') values ('
            for value in list(dict.values()):
                if isinstance(value,str):
                    sql += "'" + value + "',"
                else:
                    if value == None:
                        value = 'Null'
                    sql += str(value)+ ','
            length = len(sql) - 1
            sql = sql[0:length] + ')'
            cursor.execute(sql)
            conn.commit()
            cursor.execute("select last_insert_id();")
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            return {'data': {'insertId': list(data[0].values())[0] }}
       

    def update(self, filter, update_data):
        conn = src.db.mysql.getConn()
        with conn.cursor() as cursor:
            sql = 'update `' + self.entity_name + '` set '
            
            for key in update_data:
                if isinstance(update_data[key], str):
                    sql += key + '="' + update_data[key] + '",'
                elif isinstance(update_data[key], dict):
                    opt_key = list(update_data[key].keys())[0]
                    if opt_key == '$add':
                        sql += (key + ' = (' + key + '+' + str(update_data[key][opt_key]) + '),')
                    elif opt_key == '$subtract':
                        sql += (key + ' = (' + key + '-' + str(update_data[key][opt_key]) + '),')
                    elif opt_key == '$multiply':
                        sql += (key + ' = (' + key + '*' + str(update_data[key][opt_key]) + '),')
                    elif opt_key == '$divide':
                        sql += (key + ' = (' + key + '/' + str(update_data[key][opt_key]) + '),')
                else:
                    sql += (key + '=' + str(update_data[key]) + ',')
            sql = sql[0:(len(sql) - 1)]
            sql = filter_sql(sql,filter)
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()


    def delete(self, filter):
        conn = src.db.mysql.getConn()
        with conn.cursor() as cursor:
            sql = 'delete from ' + self.entity_name
            sql = filter_sql(sql, filter)
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()


def newTemplate(entity_name):
    return Template(entity_name)