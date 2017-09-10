#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sqlite3
from mytoolbox import makedirs_if_missing, makebsdirs_if_missing

HOST_NAME = '0.0.0.0'
PORT = 10002
PORT_VIEWER = PORT + 1016
ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(os.getcwd(), __file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
FILE_DIR = os.path.join(ROOT_DIR, 'assets')
IMCACHE_DIR = os.path.join(DATA_DIR, 'imcache')

N_IMCACHE = 100

# database name and table name
DB_NAME = 'papers'
TABLE_NAME = 'papers'
DB_FILE_NAME = os.path.join(DATA_DIR, 'basic', '%s.db' % DB_NAME)

makedirs_if_missing(IMCACHE_DIR)
makebsdirs_if_missing(DB_FILE_NAME)

# connector and cursor
CONNECTOR = sqlite3.connect(DB_FILE_NAME)
CURSOR = CONNECTOR.cursor()

KVS_VARS = [
    'key TEXT PRIMARY KEY',
    'value TEXT',
]

PAPERS_VARS = [
    'id INTEGER PRIMARY KEY AUTOINCREMENT',
    'title TEXT',
    'summary TEXT',
    'url TEXT',
    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    'n_images INTEGER DEFAULT -1',
]

PAPER_INFO = ['id', 'title', 'summary', 'url', 'n_images', 'updated_at', 'created_at']

ARXIV_ABS_URL = 'https://arxiv.org/abs/%s'
ARXIV_PDF_URL = 'https://arxiv.org/pdf/%s.pdf'

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)
