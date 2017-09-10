#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bottle import route, run, template, post, static_file, request, redirect
from db_toolbox import *
from settings import *
from mytoolbox import get_html, full_listdir
import commands
import cv2
import hashlib

@route('/static/<filename1>/<filename2>')
def get_static_file(filename1, filename2):
    return static_file(filename2, root=os.path.join(DATA_DIR, filename1))

@route('/assets/<filename>')
def get_asset_file(filename):
    return static_file(filename, root=FILE_DIR)

@route('/')
def index():
    papers = get_papers_db()
    return template('view/viewer.html',
                    server=HOST_NAME,
                    port=PORT_VIEWER,
                    papers=papers)

@route('/memo/<paper_id>')
def memo(paper_id):
    paper_info = get_paper_info_db(paper_id, PAPER_INFO)
    if paper_info['summary'] is None:
        paper_info['summary'] = ""
    return template('view/memo_viewer.html',
                    server=HOST_NAME,
                    port=PORT_VIEWER,
                    paper_info=paper_info)

@route('/memo/crop/<paper_id>/<x>/<y>/<w>/<h>/<im_i>')
def crop(paper_id, x, y, w, h, im_i):
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    image_i = int(im_i)
    hash_str = '%d-%d-%d-%d-%d-%s' % (x, y, w, h, image_i, str(paper_id))
    md5_hash = hashlib.md5(hash_str).hexdigest()
    img_path = os.path.join(IMCACHE_DIR, md5_hash + '.jpg')
    if os.path.exists(img_path):
        touch(img_path)
        return static_file(md5_hash + '.jpg', root=IMCACHE_DIR)
        # return md5_hash + '.jpg'

    org_path = os.path.join(DATA_DIR, 'data_' + str(paper_id), 'out-%d.jpg' % image_i)
    assert os.path.exists(org_path)
    img = cv2.imread(org_path)
    crop_img = img[y:y+h, x:x+w]
    cv2.imwrite(img_path, crop_img)
    print md5_hash + '.jpg has been generated.'
    return static_file(md5_hash + '.jpg', root=IMCACHE_DIR)

if __name__ == '__main__':
    run(host=HOST_NAME, port=PORT_VIEWER, debug=True, reloader=True)
