#!/usr/bin/env python
# coding: utf8

from time import strftime

from flask import abort
from flask import Flask
from flask import render_template
from flask import request

import logbook
import redis

app = Flask(__name__)
rdb_14 = redis.StrictRedis(db=14)
rdb_15 = redis.StrictRedis(db=15)


@app.route("/", methods=['POST'])
def record():
    data = request.get_json()
    word = data.get("word", None)
    if not word:
        abort(400)
    logbook.info(word)

    rdb_15.incr(word)

    time_str = strftime("%y%m%d%H%M%S")
    rdb_14.set(time_str, word)

    return ''


@app.route("/", methods=['GET'])
def select():
    day_time = request.args.get("day", "")
    assert day_time.isdigit() is True
    assert len(day_time) == 6

    day_words = rdb_14.keys("{}??????".format(day_time))
    day_words.sort(key=int, reverse=True)
    logbook.info(day_words)

    word_list = []
    for word_day in day_words:
        word = {}
        word["time"] = word_day
        word["word"] = rdb_14.get(word_day)
        word["freq"] = rdb_15.get(word["word"])
        logbook.info(word)
        word_list.append(word)

    return render_template(
        "summary.html",
        word_list=word_list,
    )


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

    app.run(host='127.0.0.1', port=8003)
