#!/usr/bin/env python
# coding: utf-8

from flask import abort
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

import boto3
import logbook
import redis
from requests import get, post

from local_settings import URBAN_DICTIONARY_API_KEY, URBAN_DICTIONARY_URL
from local_settings import CHATGPT_URL, CHATGPT_API_KEY

app = Flask(__name__)
rdb_14 = redis.StrictRedis(db=14)
rdb_15 = redis.StrictRedis(db=15)
translate = boto3.client(service_name='translate',
                         region_name='us-west-2', use_ssl=True)


def apply_logging():
    from os.path import abspath, exists, dirname, join

    server_log_file = join(dirname(abspath(__file__)), "record.log")
    if not exists(server_log_file):
        open(server_log_file, "w").close()

    logbook.set_datetime_format("local")
    local_log = logbook.FileHandler(server_log_file)
    local_log.format_string = (
        u'[{record.time:%Y-%m-%d %H:%M:%S}] '
        u'lineno:{record.lineno} '
        u'{record.level_name}:{record.message}')
    local_log.push_application()


apply_logging()


@app.route("/record", methods=['POST'])
def record():
    data = request.get_json()
    word = data.get("word", None)
    if not word:
        abort(400)
    ip = request.headers.get("X-Real-IP", "")
    logbook.info(" {} {}".format(ip, word.encode("utf-8")))
    return ""


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


@app.route("/amazon", methods=['GET'])
def amazon():
    ret_data = {}

    text = request.args.get("text", "")
    source = request.args.get("source", "")
    target = request.args.get("target", "")

    result = translate.translate_text(
        Text=text, SourceLanguageCode=source, TargetLanguageCode=target)
    ret_data["result"] = result.get('TranslatedText')

    return jsonify(ret_data)


@app.route("/urban_dictionary", methods=['GET'])
def urban_dictionary():
    text = request.args.get("text", "")
    ret_data = {}

    headers = {"X-RapidAPI-Key": URBAN_DICTIONARY_API_KEY}
    params = {"term": text}
    ret = get(URBAN_DICTIONARY_URL, headers=headers, params=params)
    if ret.ok:
        ret_data["result"] = ret.json().get("list", None)

    return jsonify(ret_data)


@app.route("/chatgpt", methods=['GET'])
def chatgpt():
    text = request.args.get("text", "")
    source = request.args.get("source", "")
    target = request.args.get("target", "")

    headers = {"Authorization": "Bearer {}".format(CHATGPT_API_KEY)}
    if source.lower() == "en" and target.lower() == "zh":
        prompt = "Translate sentence or word into Mandarin."
    else:
        prompt = "Translate sentence or word into English."

    json = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        "temperature": 0,
        "user": "flaskord",
    }

    ret = post(CHATGPT_URL, headers=headers, json=json)

    ret_data = {}
    if ret.ok:
        choices = ret.json().get("choices", [])
        if len(choices) > 0:
            ret_data["result"] = choices[0]["message"]["content"]

    return jsonify(ret_data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8003)
