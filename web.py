import os
import json
from subprocess import Popen, PIPE, TimeoutExpired, check_output
from threading import Lock
from bottle import hook, get, post, run, template, request, response, abort, static_file, redirect
from sgf_pattern_search import pattern_search, search_formatter

TIMEOUT = 29

search_lock = Lock()
search_process = None

@hook('after_request')
def enable_cors():
    response.set_header('Access-Control-Allow-Origin', '*')

@post('/search.json')
def search():
    global search_process

    sgf = request.forms.sgf # attributeアクセスでunicodeを取得できる
    disable_alphago_vs_alphago = request.forms.getunicode('disable_alphago_vs_alphago', False)
    if not sgf:
        abort(400, 'Bad Request')

    abortable = request.forms.getunicode('abortable', False)
    if abortable == 'true' and search_process:
        search_process.kill()
    search_lock.acquire(True)

    args = [
        'python',
        'sgf_pattern_search.py'
    ]
    if disable_alphago_vs_alphago == 'true':
        args.append('--disable_alphago_vs_alphago')
    args.append('-')

    search_process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    try:
        outs, errs = search_process.communicate(input=sgf.encode("utf-8"), timeout=TIMEOUT)
        return json.loads(outs)
    except TimeoutExpired:
        p.kill()
        abort(408, 'Request Timeout')
    except ValueError:
        print('ValueError')
        print(outs)
        abort(500, 'Internal Server Error')
    finally:
        search_process = None
        search_lock.release()

#app = default_app()
run(server='paste', host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
