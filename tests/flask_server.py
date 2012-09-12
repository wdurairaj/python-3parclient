#from flask import Flask, request, abort, make_response, session, escape
from flask import *
import pprint
import json, os, random, string
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

__all__ = ['make_json_app']

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for x in range(size))

def make_json_app(import_name, **kwargs):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    """
    def make_json_error(ex):
        pprint.pprint(ex)
        pprint.pprint(ex.code)
        #response = jsonify(message=str(ex))
        response = jsonify(ex)
        ass = jsonify(shit='balls')
        pprint.pprint(ass)
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    app = Flask(import_name, **kwargs)
    app.secret_key = id_generator(24)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app

app = make_json_app(__name__)

session_key = id_generator(24)


def throw_error(http_code, error_code=None, desc=None, debug1=None, debug2=None):
    if error_code:
        info = {'code': error_code, 'desc': desc}
        if debug1:
            info['debug1'] = debug1
        if debug2:
            info['debug2'] = debug2
        abort(Response(json.dumps(info), status=http_code))
    else:
        abort(http_code)

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    abort(401)

@app.route('/hello')
def hello():
    return 'Hello World'

@app.route('/api/v1/credentials', methods=['GET', 'POST'])
def credentials():
    pprint.pprint("credentials %s" % request.method)
    #pprint.pprint("data = %s" % request.data)

    if request.method == 'GET':
        return 'GET credentials called'

    elif request.method == 'POST':
	data = json.loads(request.data)

        if data['user'] == 'user' and data['password'] == 'hp':
            #do something good here
            try:
                resp = make_response(json.dumps({'key':session_key}), 201)
                resp.headers['Location'] = '/api/v1/credentials/%s' % session_key
                session['username'] = data['user']
                session['password'] = data['password']
                session['session_key'] = session_key
                return resp
            except Exception as ex:
                pprint.pprint(ex)

        else:
            #authentication failed!
            throw_error(401, "HTTP_AUTH_FAIL", "Username and or Password was incorrect")


@app.route('/api/v1/credentials/<session_key>', methods=['DELETE'])
def credentials_logout(session_key):
    pprint.pprint("credentials %s" % request.method)
    session.clear()
    return 'DELETE credentials called'



if __name__ == "__main__":
    app.run(debug=True)
