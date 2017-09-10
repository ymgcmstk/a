#!/usr/bin/env python
# -*- coding:utf-8 -*-

from settings import *


"""
QUERY_SELECT_IN = 'SELECT key, value FROM %s ' % TABLE_NAME + \
               'WHERE key in (%s)'
QUERY_SELECT_LIKE = 'SELECT key, value FROM %s ' % TABLE_NAME + \
                    'WHERE key LIKE %s'
QUERY_REPLACE = 'INSERT OR REPLACE INTO %s ' % TABLE_NAME + \
                '(key, value) VALUES %s'
"""

QUERY_UPDATE = 'UPDATE %s ' % TABLE_NAME + \
               'SET updated_at = datetime("now"), summary = "%s" WHERE id = %s;'
QUERY_UPDATE_N_IMAGES = 'UPDATE %s ' % TABLE_NAME + \
                        'SET updated_at = datetime("now"), n_images = %s WHERE id = %s;'

QUERY_SELECT = 'SELECT %s' + ' FROM %s ' % TABLE_NAME + \
               'WHERE id = %s'
QUERY_SELECT_ALL = 'SELECT id, title FROM %s ' % TABLE_NAME + \
                   'ORDER BY updated_at DESC' #  LIMIT 30
QUERY_LAST = 'SELECT LAST_INSERT_ROWID() FROM %s' % TABLE_NAME
# QUERY_REPLACE % ', '.join(['(%s,%s)' % (key, value) for key, value in data_dict])
QUERY_INSERT = 'INSERT INTO %s (url, title)' % TABLE_NAME + \
               ' VALUES("%s", "%s")'

def create_table():
    CURSOR.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s'" % (TABLE_NAME))
    temp = CURSOR.fetchone()
    if temp[0] > 0:
        return

    query = "CREATE TABLE %s(%s)" % (TABLE_NAME, ','.join(PAPERS_VARS))
    query = query.replace('AUTO_INCREMENT', 'AUTOINCREMENT').replace('INT(11)', 'INTEGER')
    print query
    CURSOR.execute(query)
    CONNECTOR.commit()

"""
def get_from_db(keys):
    query = QUERY_SELECT_IN % ','.join(['"%s"' % cur_key for cur_key in keys])
    CURSOR.execute(query)
    results = {i[0]: i[1] for i in CURSOR.fetchall()}
    return results

def get_like_from_db(key):
    query = QUERY_SELECT_LIKE % key
    CURSOR.execute(query)
    results = {i[0]: i[1] for i in CURSOR.fetchall()}
    return results
def update_db(data_dict):
    query = QUERY_REPLACE % ', '.join(['("%s", "%s")' % (key, value) for key, value in data_dict.iteritems()])
    CURSOR.execute(query)
    CONNECTOR.commit()
"""


def get_papers_db():
    query = QUERY_SELECT_ALL
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

def update_papers_db(paper_id, summary):
    query = QUERY_UPDATE % (summary.replace('"', "'"), paper_id)
    print query
    CURSOR.execute(query)
    CONNECTOR.commit()

def update_n_images_db(paper_id, n_images):
    query = QUERY_UPDATE_N_IMAGES % (n_images, paper_id)
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
