#!/usr/bin/env python
# -*- coding:utf-8 -*-

from settings import *
import urllib

QUERY_UPDATE = 'UPDATE %s ' % TABLE_NAME + \
               'SET updated_at = datetime("now"), summary = "%s", title="%s" WHERE id = %s;'
QUERY_UPDATE_N_IMAGES = 'UPDATE %s ' % TABLE_NAME + \
                        'SET updated_at = datetime("now"), n_images = %s WHERE id = %s;'
QUERY_UPDATE_DISPLAY = 'UPDATE %s ' % TABLE_NAME + \
                       'SET display = 1 - display WHERE id = %s;'

QUERY_SELECT = 'SELECT %s' + ' FROM %s ' % TABLE_NAME + \
               'WHERE id = %s'
QUERY_SELECT_ALL = 'SELECT id, title, updated_at FROM %s ' % TABLE_NAME + \
                   'WHERE display = 1 ORDER BY updated_at DESC' #  LIMIT 30
QUERY_SELECT_ALL_FULL = 'SELECT id, title, display, updated_at FROM %s ' % TABLE_NAME + \
                   'ORDER BY updated_at DESC' #  LIMIT 30

QUERY_SELECT_WITH_QUERY = 'SELECT id, title, updated_at FROM %s ' % TABLE_NAME + \
                          'WHERE display = 1 AND %s ORDER BY updated_at DESC' #  LIMIT 30

QUERY_LAST = 'SELECT LAST_INSERT_ROWID() FROM %s' % TABLE_NAME
# QUERY_REPLACE % ', '.join(['(%s,%s)' % (key, value) for key, value in data_dict])
QUERY_INSERT = 'INSERT INTO %s (url, title)' % TABLE_NAME + \
               ' VALUES("%s", "%s")'

def encodeURI(query):
    return urllib.quote(query, safe='~@#$&()*!+=:;,.?/\'');


def create_table():
    CURSOR.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s'" % (TABLE_NAME))
    temp = CURSOR.fetchone()
    if temp[0] > 0:
        return

    query = "CREATE TABLE %s(%s)" % (TABLE_NAME, ','.join(PAPERS_VARS))
    query = query.replace('AUTO_INCREMENT', 'AUTOINCREMENT').replace('INT(11)', 'INTEGER')
    CURSOR.execute(query)
    CONNECTOR.commit()

def search_papers_db(q):
    words = q.split()
    conditions = []
    for cur_word in words:
        cur_word = cur_word.lower()
        enc_word = encodeURI(cur_word).replace('%', '%%')
        cur_condition = '(LOWER(title) LIKE "%' + cur_word + '%" OR LOWER(summary) LIKE "%' + enc_word + '%")'
        conditions.append(cur_condition)
    query = QUERY_SELECT_WITH_QUERY % ' AND '.join(conditions)
    print query
    CURSOR.execute(query)
    results = CURSOR.fetchall()
    return results

def get_papers_db():
    query = QUERY_SELECT_ALL
    CURSOR.execute(query)
    results = CURSOR.fetchall()
    return results

def get_papers_full_db():
    query = QUERY_SELECT_ALL_FULL
    CURSOR.execute(query)
    results = CURSOR.fetchall()
    return results

def get_paper_info_db(paper_id, keys):
    query = QUERY_SELECT % (','.join(keys), paper_id)
    CURSOR.execute(query)
    results = {key: val for key, val in zip(keys, CURSOR.fetchall()[0])}
    return results

def get_n_images_db(paper_id):
    query = QUERY_SELECT % ('n_images', paper_id)
    CURSOR.execute(query)
    return CURSOR.fetchall()[0][0]

def update_papers_db(paper_id, summary, title):
    query = QUERY_UPDATE % (summary.replace('"', "'"), title.replace('"', "'"), paper_id)
    print query
    CURSOR.execute(query)
    CONNECTOR.commit()

def update_n_images_db(paper_id, n_images):
    query = QUERY_UPDATE_N_IMAGES % (n_images, paper_id)
    CURSOR.execute(query)
    CONNECTOR.commit()

def update_display_db(paper_id):
    query = QUERY_UPDATE_DISPLAY % (paper_id)
    CURSOR.execute(query)
    CONNECTOR.commit()

def insert_empty_paper(title, url):
    query = QUERY_INSERT % (url, title.replace('"', "'"))
    print query
    CURSOR.execute(query)
    CONNECTOR.commit()

    query = QUERY_LAST
    CURSOR.execute(query)
    paper_id = CURSOR.fetchall()[0][0]
    return paper_id
