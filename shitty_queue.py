from __future__ import print_function
from flask import Flask, render_template, session, redirect, url_for, request,\
        current_app, abort
from flask.ext.wtf.csrf import CsrfProtect, generate_csrf, validate_csrf
import pycrest
from collections import deque
import os


app = Flask(__name__)
CsrfProtect(app)


@app.context_processor
def inject_jinja():
    return {
        'eve': current_app.eve,
        'queue': current_app.queue,
    }


@app.before_first_request
def register_crest():
    current_app.eve = pycrest.EVE(
            client_id=os.environ['CLIENT_ID'],
            api_key=os.environ['CLIENT_SECRET'],
            redirect_uri=url_for('login', _external=True))


@app.before_first_request
def initialize_queue():
    current_app.queue = deque()


@app.route('/')
def index():
    return render_template('base.html', queue=current_app.queue)


@app.route('/login')
def login():
    # Check CSRF
    #if not validate_csrf(int(request.args['state'])):
        #abort(401)
    auth_conn = current_app.eve.authorize(request.args['code'])
    info = auth_conn.whoami()
    session['authenticated'] = True
    session['current_character'] = info['CharacterName']
    current_app.queue.append(session['current_character'])
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    current_app.queue.remove(session['current_character'])
    session['authenticated'] = False
    del session['authenticated']
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'foobar'
    app.run(debug=True)

