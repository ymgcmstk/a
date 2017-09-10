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
    return template('index.html',
                    server=HOST_NAME,
                    port=PORT,
                    papers=papers)

@post('/')
def index_post():
    if 'arxivid' in request.forms.keys():
        arXiv_id = request.forms.get('arxivid')
        pdf_url = ARXIV_PDF_URL % str(arXiv_id)
        abs_url = ARXIV_ABS_URL % str(arXiv_id)
        cur_html = get_html(abs_url) #, cache=True)
        cur_html = cur_html[:cur_html.find('</title>')]
        cur_html = cur_html[cur_html.find('<title>') + len('<title>'):]
        cur_html = cur_html[cur_html.find(']') + len(']'):]
        title = cur_html
    else:
        pdf_url = request.forms.get('pdfurl')
        title = request.forms.get('pdftitle')
    paper_id = insert_empty_paper(title, pdf_url)

    # update n_images
    print './pdf2jpg.sh "%s" "%s" & ' % (
        pdf_url,
        str(paper_id)
    )
    os.system('./pdf2jpg.sh "%s" "%s" & ' % (
        pdf_url,
        str(paper_id)
    ))
    redirect('/memo/%s' % str(paper_id))

@route('/memo/<paper_id>')
def memo(paper_id):
    paper_info = get_paper_info_db(paper_id, PAPER_INFO)
    if paper_info['summary'] is None:
        paper_info['summary'] = ""
    return template('memo.html',
                    server=HOST_NAME,
                    port=PORT,
                    paper_info=paper_info)

@post('/memo/save/<paper_id>')
def save(paper_id):
    summary = request.forms.get('summary')
    update_papers_db(paper_id, summary)

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

@route('/memo/n_images/<paper_id>')
def get_n_images(paper_id):
    n_images = get_n_images_db(paper_id)
    base_dir = os.path.join(DATA_DIR, 'data_' + str(paper_id))
    if n_images == -1 and os.path.exists(os.path.join(base_dir, 'fin')):
        n_images = len([1 for i in os.listdir(base_dir) if i.endswith('.jpg')]) - 1
        update_n_images_db(paper_id, str(n_images))
    return str(n_images)

@post('/delete')
def delete():
    raise NotImplementedError()

def clean_up_images():
    im_files = sorted(full_listdir(IMCACHE_DIR), key=os.path.getmtime)
    n_remove = max(len(im_files) - N_IMCACHE, 0)
    for i in range(n_remove):
        print im_files[i], 'has been removed.'
        os.remove(im_files[i])

if __name__ == '__main__':
    create_table()
    clean_up_images()
    run(host=HOST_NAME, port=PORT, debug=True, reloader=True)
