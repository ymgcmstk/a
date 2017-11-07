#!/usr/bin/env python
# -*- coding:utf-8 -*-

from settings import *
import urllib

QUERY_UPDATE = 'UPDATE %s ' % NOTES_TABLE_NAME + \
               'SET updated_at = datetime("now"), summary = "%s", title="%s" WHERE id = %s;'
QUERY_UPDATE_N_IMAGES = 'UPDATE %s ' % NOTES_TABLE_NAME + \
                        'SET updated_at = datetime("now"), n_images = %s WHERE id = %s;'
QUERY_UPDATE_DISPLAY = 'UPDATE %s ' % NOTES_TABLE_NAME + \
                       'SET display = 1 - display WHERE id = %s;'

QUERY_SELECT = 'SELECT %s' + ' FROM %s ' % NOTES_TABLE_NAME + \
               'WHERE id = %s'
QUERY_SELECT_ALL = 'SELECT notes.id, notes.title, notes.updated_at, user, user_id FROM %s ' % NOTES_TABLE_NAME + \
                   'INNER JOIN users ON users.id = notes.user_id WHERE display = 1 ORDER BY notes.updated_at DESC' #  LIMIT 30
QUERY_SELECT_ALL_WITH_USER = 'SELECT notes.id, notes.title, notes.updated_at, user, user_id FROM %s ' % NOTES_TABLE_NAME + \
                             'INNER JOIN users ON users.id = notes.user_id WHERE display = 1 AND user_id = %s ORDER BY notes.updated_at DESC' #  LIMIT 30
QUERY_SELECT_ALL_FULL = 'SELECT id, title, display, updated_at FROM %s ' % NOTES_TABLE_NAME + \
                        'WHERE user_id = %s ORDER BY updated_at DESC' #  LIMIT 30

QUERY_SELECT_WITH_QUERY = 'SELECT notes.id, notes.title, notes.updated_at, user, notes.user_id FROM %s ' % NOTES_TABLE_NAME + \
                          'INNER JOIN users ON users.id = notes.user_id WHERE notes.display = 1 AND %s ORDER BY notes.updated_at DESC' #  LIMIT 30
QUERY_SELECT_ALL_WITH_USER_AND_QUERY = 'SELECT notes.id, notes.title, notes.updated_at, user, user_id FROM %s ' % NOTES_TABLE_NAME + \
                                       'INNER JOIN users ON users.id = notes.user_id WHERE display = 1 AND user_id = %s AND %s ORDER BY notes.updated_at DESC' #  LIMIT 30
QUERY_SELECT_ALL_FULL_WITH_QUERY = 'SELECT id, title, display, updated_at FROM %s ' % NOTES_TABLE_NAME + \
                                   'WHERE user_id = %s AND %s ORDER BY updated_at DESC' #  LIMIT 30

QUERY_LAST = 'SELECT LAST_INSERT_ROWID() FROM %s' % NOTES_TABLE_NAME
# QUERY_REPLACE % ', '.join(['(%s,%s)' % (key, value) for key, value in data_dict])
QUERY_INSERT = 'INSERT INTO %s (url, title, user_id)' % NOTES_TABLE_NAME + \
               ' VALUES("%s", "%s", %s)'

### FOR USER TABLE
QUERY_INSERT_USER = 'INSERT INTO %s (user, password)' % USERS_TABLE_NAME + \
                    ' VALUES("%s", "%s")'
QUERY_SELECT_USER = 'SELECT %s' + ' FROM %s ' % USERS_TABLE_NAME + \
                    'WHERE id = %s'
QUERY_SELECT_WITH_NAME_USER = 'SELECT %s' + ' FROM %s ' % USERS_TABLE_NAME + \
                              'WHERE user = "%s"'
QUERY_LAST_USER = 'SELECT LAST_INSERT_ROWID() FROM %s' % USERS_TABLE_NAME
# QUERY_REPLACE % ', '.join(['(%s,%s)' % (key, value) for key, value in data_dict])



def encodeURI(query):
    return urllib.quote(query, safe='~@#$&()*!+=:;,.?/\'');

def create_table():
    CURSOR.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s'" % (NOTES_TABLE_NAME))
    temp = CURSOR.fetchone()
    print temp
    if temp[0] == 0:
        query = "CREATE TABLE %s(%s)" % (NOTES_TABLE_NAME, ','.join(NOTES_VARS))
        query = query.replace('AUTO_INCREMENT', 'AUTOINCREMENT').replace('INT(11)', 'INTEGER')
        CURSOR.execute(query)
        CONNECTOR.commit()

    CURSOR.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s'" % (USERS_TABLE_NAME))
    temp = CURSOR.fetchone()
    if temp[0] == 0:
        query = "CREATE TABLE %s(%s)" % (USERS_TABLE_NAME, ','.join(USERS_VARS))
        query = query.replace('AUTO_INCREMENT', 'AUTOINCREMENT').replace('INT(11)', 'INTEGER')
        CURSOR.execute(query)
        CONNECTOR.commit()

def search_notes_db(q):
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

def get_notes_db():
    query = QUERY_SELECT_ALL
    CURSOR.execute(query)
    results = CURSOR.fetchall()
    return results

def search_notes_with_user_db(user_id, q):
    words = q.split()
    conditions = []
    for cur_word in words:
        cur_word = cur_word.lower()
        enc_word = encodeURI(cur_word).replace('%', '%%')
        cur_condition = '(LOWER(title) LIKE "%' + cur_word + '%" OR LOWER(summary) LIKE "%' + enc_word + '%")'
        conditions.append(cur_condition)
    query = QUERY_SELECT_ALL_WITH_USER_AND_QUERY % (str(user_id), ' AND '.join(conditions))
    print query
    CURSOR.execute(query)
    results = CURSOR.fetchall()
    return results

def get_notes_with_user_db(user_id):
    query = QUERY_SELECT_ALL_WITH_USER % str(user_id)
    print query
    CURSOR.execute(query)
    results = CURSOR.fetchall()
    return results

def search_notes_full_db(user_id, q):
    words = q.split()
    conditions = []
    for cur_word in words:
        cur_word = cur_word.lower()
        enc_word = encodeURI(cur_word).replace('%', '%%')
        cur_condition = '(LOWER(title) LIKE "%' + cur_word + '%" OR LOWER(summary) LIKE "%' + enc_word + '%")'
        conditions.append(cur_condition)
    query = QUERY_SELECT_ALL_FULL_WITH_QUERY % (str(user_id), ' AND '.join(conditions))
    CURSOR.execute(query)
    results = CURSOR.fetchall()
    return results

def get_notes_full_db(user_id):
    query = QUERY_SELECT_ALL_FULL % str(user_id)
    CURSOR.execute(query)
    results = CURSOR.fetchall()
    return results

def get_note_info_db(note_id, keys):
    query = QUERY_SELECT % (','.join(keys), note_id)
    print query
    CURSOR.execute(query)
    results = {key: val for key, val in zip(keys, CURSOR.fetchall()[0])}
    return results

def get_n_images_db(note_id):
    query = QUERY_SELECT % ('n_images', note_id)
    CURSOR.execute(query)
    return CURSOR.fetchall()[0][0]

def update_notes_db(note_id, summary, title):
    query = QUERY_UPDATE % (summary.replace('"', "'"), title.replace('"', "'"), note_id)
    print query
    CURSOR.execute(query)
    CONNECTOR.commit()

def update_n_images_db(note_id, n_images):
    query = QUERY_UPDATE_N_IMAGES % (n_images, note_id)
    CURSOR.execute(query)
    CONNECTOR.commit()

def update_display_db(note_id):
    query = QUERY_UPDATE_DISPLAY % (note_id)
    CURSOR.execute(query)
    CONNECTOR.commit()

def insert_empty_note(title, url, user_id):
    query = QUERY_INSERT % (url, title.replace('"', "'"), str(user_id))
    print query
    CURSOR.execute(query)
    CONNECTOR.commit()

    query = QUERY_LAST
    CURSOR.execute(query)
    note_id = CURSOR.fetchall()[0][0]
    update_display_db(note_id) # TO BE CONSIDERED
    return note_id

# for user table
def add_user(user, password):
    query = QUERY_INSERT_USER % (user, password)
    CURSOR.execute(query)
    CONNECTOR.commit()

    query = QUERY_LAST_USER
    CURSOR.execute(query)
    user_id = CURSOR.fetchall()[0][0]
    return user_id

def get_user_id(user, password=None):
    if password is None:
        query = QUERY_SELECT_WITH_NAME_USER % ('id', user)
        CURSOR.execute(query)
        user_id = CURSOR.fetchall()[0][0]
        return user_id
    else:
        query = QUERY_SELECT_WITH_NAME_USER % ('id, password', user)
        print query
        CURSOR.execute(query)
        results = CURSOR.fetchall()
        if len(results) == 1:
            user_id, org_password = results[0]
            if password == org_password:
                return user_id
            else:
                return -1
        assert len(results) == 0
        # return -1
        return add_user(user, password)

if __name__ == '__main__':
    print get_note_info_db(1, NOTE_INFO)
