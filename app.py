#!/usr/bin/env python
# coding: utf8

from time import strftime

from flask import Flask
from flask import request
from flask import abort

import logbook
import redis

app = Flask(__name__)


@app.route("/", methods=['POST'])
def record():
    word = request.form.get("word", "")
    if not word:
        abort(400)
    logbook.info(word)

    rdb_15.incr(word)

    time_str = strftime("%y%m%d%H%M%S")
    rdb_14.set(time_str, word)

    return ''

if __name__ == '__main__':
    from os.path import abspath, exists, dirname, join

    server_log_file = join(dirname(abspath(__file__)), "record.log")
    if not exists(server_log_file):
        open(server_log_file, "w").close()

    local_log = logbook.FileHandler(server_log_file)
    local_log.format_string = (
        u'[{record.time:%H:%M:%S}] '
        u'lineno:{record.lineno} '
        u'{record.level_name}:{record.message}')
    local_log.push_application()

    rdb_15 = redis.StrictRedis(db=15)
    rdb_14 = redis.StrictRedis(db=14)

    app.run(host='127.0.0.1', port=4444)
