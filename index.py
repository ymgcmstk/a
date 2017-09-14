#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bottle import route, run, template, post, static_file, request, redirect, default_app
from beaker.middleware import SessionMiddleware
from db_toolbox import *
from settings import *
from mytoolbox import get_html, full_listdir
import commands
import cv2
import hashlib
import json

session_opts = {
    'session.type': 'file',
    'session.data_dir': SESSION_DIR,
    'session.cookie_expires': False, # True: expire cookies when the browser is closed
    'session.auto': True
}

def session_get(key):
    session = request.environ.get('beaker.session')
    if key in session:
        return session[key]
    return None

def session_set(key, val):
    session = request.environ.get('beaker.session')
    session[key] = val
    session.save()

def check_user_consistency(note_id=None, user=None):
    if note_id is not None:
        assert user is None
        note_user_id = get_note_info_db(note_id, ['user_id'])['user_id']
        assert str(note_user_id) == str(session_get('user_id'))
        return note_user_id
    assert user is not None
    cur_user_id = get_user_id(user)
    assert str(cur_user_id) == str(session_get('user_id'))
    return cur_user_id

def get_user_from_session():
    user = session_get('user')
    if user is None:
        return None, None
    if len(user) == 0:
        return None, None
    user_id = session_get('user_id')
    return user, user_id

@route('/static/<filename1>/<filename2>')
def get_static_file(filename1, filename2):
    return static_file(filename2, root=os.path.join(DATA_DIR, filename1))

@route('/assets/<filename>')
def get_asset_file(filename):
    return static_file(filename, root=FILE_DIR)

@route('/')
def index():
    if 'q' in request.query:
        query = request.query['q']
        notes = search_notes_db(query)
    else:
        notes = get_notes_db()
    user, user_id = get_user_from_session()
    message = session_get('message')
    return template('views/index.html',
                    server=HOST_NAME,
                    port=PORT,
                    notes=notes,
                    user=user,
                    user_id=user_id,
                    my_id=session_get('user_id'),
                    message=message)

@route('/member/<user_id>')
def member(user_id):
    my_id = session_get('user_id')
    if user_id == str(my_id):
        message = session_get('message')
        notes = get_notes_full_db(user_id)
        return template('views/mypage.html',
                        server=HOST_NAME,
                        port=PORT,
                        notes=notes,
                        user=session_get('user'),
                        user_id=user_id,
                        message=message)
    else:
        # notes = get_notes_full_db()
        notes = get_notes_with_user_db(user_id)
        return template('views/index.html',
                        server=HOST_NAME,
                        port=PORT,
                        notes=notes,
                        user=session_get('user'),
                        user_id=user_id,
                        my_id=session_get('user_id'),
                        message='')

@post('/member/<user_id>')
def member_post(user_id):
    assert str(user_id) == str(session_get('user_id'))
    if 'pagetitle' in request.forms.keys():
        pdf_url = ''
        title = request.forms.get('pagetitle')
    elif 'arxivid' in request.forms.keys():
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
    note_id = insert_empty_note(title, pdf_url, user_id)

    if len(pdf_url) > 0:
        print './pdf2jpg.sh "%s" "%s" & ' % (
            pdf_url,
            str(note_id)
        )
        os.system('./pdf2jpg.sh "%s" "%s" & ' % (
            pdf_url,
            str(note_id)
        ))
    else:
        # update n_images
        update_n_images_db(note_id, '0')
    redirect('/note/%s' % str(note_id))

@route('/note/<note_id>')
def note(note_id):
    check_user_consistency(note_id=note_id)
    note_info = get_note_info_db(note_id, NOTE_INFO)
    if note_info['summary'] is None:
        note_info['summary'] = ""
    return template('views/note.html',
                    server=HOST_NAME,
                    port=PORT,
                    note_info=note_info)

@post('/save/<note_id>')
def save(note_id):
    check_user_consistency(note_id=note_id)
    summary = request.forms.get('summary')
    title = request.forms.get('title')
    update_notes_db(note_id, summary, title)

@post('/load/<note_id>')
def load(note_id):
    note_info = get_note_info_db(note_id, NOTE_INFO)
    if note_info['summary'] is None:
        note_info['summary'] = ""
    if note_info['display'] == 0:
        for pkey in note_info.keys():
            note_info[pkey] = ""
    return json.dumps(note_info)

@route('/crop/<note_id>/<x>/<y>/<w>/<h>/<im_i>')
def crop(note_id, x, y, w, h, im_i):
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    image_i = int(im_i)
    hash_str = '%d-%d-%d-%d-%d-%s' % (x, y, w, h, image_i, str(note_id))
    md5_hash = hashlib.md5(hash_str).hexdigest()
    img_path = os.path.join(IMCACHE_DIR, md5_hash + '.jpg')
    if os.path.exists(img_path):
        touch(img_path)
        return static_file(md5_hash + '.jpg', root=IMCACHE_DIR)
        # return md5_hash + '.jpg'

    org_path = os.path.join(DATA_DIR, 'data_' + str(note_id), 'out-%d.jpg' % image_i)
    assert os.path.exists(org_path)
    img = cv2.imread(org_path)
    crop_img = img[y:y+h, x:x+w]
    cv2.imwrite(img_path, crop_img)
    print md5_hash + '.jpg has been generated.'
    return static_file(md5_hash + '.jpg', root=IMCACHE_DIR)

@route('/n_images/<note_id>')
def get_n_images(note_id):
    n_images = get_n_images_db(note_id)
    base_dir = os.path.join(DATA_DIR, 'data_' + str(note_id))
    if n_images == -1 and os.path.exists(os.path.join(base_dir, 'fin')):
        n_images = len([1 for i in os.listdir(base_dir) if i.endswith('.jpg')]) - 1
        update_n_images_db(note_id, str(n_images))
    return str(n_images)

@route('/display/<note_id>')
def display(note_id):
    check_user_consistency(note_id=note_id)
    update_display_db(note_id)
    user_id = session_get('user_id')
    redirect('/member/' + str(user_id))

@route('/login')
def login():
    return template('views/login.html',
                    server=HOST_NAME,
                    port=PORT)

@route('/rules')
def rules():
    user_id = session_get('user_id')
    return template('views/rules.html',
                    server=HOST_NAME,
                    port=PORT,
                    user_id=user_id)

@post('/login')
def login_post():
    user = request.forms.get('username')
    password = hashlib.md5(request.forms.get('password')).hexdigest()
    user_id = get_user_id(user, password)
    if user_id >= 0:
        session_set('user_id', user_id)
        session_set('user', user)
        session_set('message', 'Hi %s.' % user)
    else:
        session_set('user_id', user_id)
        session_set('user', '')
        session_set('message', 'Log-in failed.')
    redirect('/')

def clean_up_images():
    im_files = sorted(full_listdir(IMCACHE_DIR), key=os.path.getmtime)
    n_remove = max(len(im_files) - N_IMCACHE, 0)
    for i in range(n_remove):
        print im_files[i], 'has been removed.'
        os.remove(im_files[i])

if __name__ == '__main__':
    app = default_app()
    app = SessionMiddleware(app, session_opts)

    create_table()
    clean_up_images()
    run(app=app, host=HOST_NAME, port=PORT, debug=True, reloader=True)
