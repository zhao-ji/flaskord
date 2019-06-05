#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser
from hashlib import md5
from json import loads
from random import randint

from requests import get, post, packages, Session

from local_settings import *

packages.urllib3.disable_warnings()


class Colorizing(object):
    colors = {
        'none': "",
        'default': "\033[0m",
        'bold': "\033[1m",
        'underline': "\033[4m",
        'blink': "\033[5m",
        'reverse': "\033[7m",
        'concealed': "\033[8m",

        'black': "\033[30m",
        'red': "\033[31m",
        'green': "\033[32m",
        'yellow': "\033[33m",
        'blue': "\033[34m",
        'magenta': "\033[35m",
        'cyan': "\033[36m",
        'white': "\033[37m",

        'on_black': "\033[40m",
        'on_red': "\033[41m",
        'on_green': "\033[42m",
        'on_yellow': "\033[43m",
        'on_blue': "\033[44m",
        'on_magenta': "\033[45m",
        'on_cyan': "\033[46m",
        'on_white': "\033[47m",

        'beep': "\007",
    }

    @classmethod
    def colorize(cls, s, color=None):
        if color in cls.colors:
            return "{0}{1}{2}".format(
                cls.colors[color], s, cls.colors['default'])
        else:
            return s


def bing(text):
    headers = {}
    headers["Ocp-Apim-Subscription-Key"] = BING_KEY1
    params = {}
    params["api-version"] = "3.0"
    if len(text) == len(text.decode("utf8")):
        params["from"] = "en"
        params["to"] = "zh-Hans"
    else:
        params["to"] = "en"

    session = Session()
    session.headers.update(headers)
    session.params.update(params)
    session.verify = False

    data = [{"Text": text}]

    try:
        translate_ret = session.post(
            url=BING_TRANSLATE_URL, json=data, timeout=3)
        diction_lookup_ret = session.post(
            url=BING_DICTIONARY_LOOKUP_URL, json=data, timeout=3)
    except BaseException, e:
        print e
        return

    trans_ret = translate_ret.json()[0]["translations"][0]["text"]
    print _c('微软翻译：' + trans_ret.encode("utf-8"), 'yellow')

    lookup_ret = diction_lookup_ret.json()[0]['translations']
    if len(lookup_ret) > 0:
        print _c("\t字典查询：", 'cyan')
        for explain in lookup_ret:
            print "\t\t* " + explain["posTag"] + ". " + explain["displayTarget"]

        # if we can find any dictionary translation
        examples_data = [
            {"Text": text, "Translation": i["normalizedTarget"]}
            for i in lookup_ret
        ]

        try:
            examples_ret = session.post(
                url=BING_DICTIONARY_EXAMPLE_URL, json=examples_data, timeout=3)
        except BaseException, e:
            print e
            return

        print _c("\t例句：", 'cyan')
        for explain in examples_ret.json():
            if "examples" in explain and explain["examples"]:
                for example in explain["examples"][:1]:
                    print "\t\t* " \
                        + example["sourcePrefix"] + example["sourceTerm"] \
                        + example["sourceSuffix"] + "  " \
                        + example["targetPrefix"] + example["targetTerm"] \
                        + example["targetSuffix"]

    session.close()


def google(text):
    params = {}
    params["key"] = GOOGLE_API_KEY
    params["q"] = text
    if len(text) == len(text.decode("utf8")):
        params["from"] = "en"
        params["target"] = "zh-cn"
    else:
        params["from"] = "zh-CN"
        params["target"] = "en"

    try:
        ret = get(url=GOOGLE_URL, params=params, timeout=3)
    except BaseException, e:
        print e
        return
    trans_ret = loads(ret.text)
    print _c('谷歌翻译：' + trans_ret["data"]["translations"][0]["translatedText"].encode('utf8'), 'yellow')


def baidu(text):
    params = {}
    params['q'] = text
    if len(text) == len(text.decode("utf8")):
        params["from"] = "en"
        params["to"] = "zh"
    else:
        params["from"] = "zh"
        params["to"] = "en"
    params['appid'] = BAIDU_APP_ID
    params['salt'] = str(randint(0, 2**16))
    params['sign'] = md5(''.join([
        params['appid'], params['q'],
        params['salt'], BAIDU_SECRET_KEY,
    ])).hexdigest()

    try:
        ret = get(url=BAIDU_URL, params=params, timeout=3)
    except BaseException, e:
        print e
        return
    trans_ret = loads(ret.text)
    print _c('百度翻译：' + trans_ret["trans_result"][0]["dst"].encode('utf8'), 'yellow')


def youdao(text):
    params = {}
    params['keyfrom'] = YOUDAO_KEYFROM
    params['key'] = YOUDAO_KEY
    params['type'] = 'data'
    params['doctype'] = 'json'
    params['version'] = '1.1'
    params['q'] = text

    try:
        ret = get(url=YOUDAO_URL, params=params, timeout=3)
        # , proxies=PROXIES)
    except BaseException, e:
        print e
        return

    trans_ret = loads(ret.text)

    translation = ', '.join(trans_ret.get('translation', []))
    print _c('有道翻译：' + translation.encode('utf8'), 'yellow')

    if 'basic' in trans_ret:
        if 'phonetic' in trans_ret["basic"]:
            print _c("\t发音：", 'cyan')
            print "\t\t* [{}]".format(trans_ret["basic"]["phonetic"].encode('utf8'))
            if 'uk-phonetic' in trans_ret["basic"]:
                print "\t\t* UK: [{}]".format(trans_ret["basic"]["uk-phonetic"].encode('utf8'))
            if 'us-phonetic' in trans_ret["basic"]:
                print "\t\t* US: [{}]".format(trans_ret["basic"]["us-phonetic"].encode('utf8'))

        print _c("\t基本查询：", 'cyan')
        for explain in trans_ret['basic']['explains']:
            print "\t\t* " + explain.encode('utf8')

    if 'web' in trans_ret:
        print _c("\t网络查询：", 'cyan')
        for i in trans_ret["web"]:
            print "\t\t* " + i["key"].encode('utf8') + " " + ', '.join(i.encode('utf-8') for i in i["value"])


def record(text):
    payload = {"word": text}
    post(RECORD_URL, data=payload, auth=('word', 'password'))


if __name__ == '__main__':
    parser = ArgumentParser(
        description="translate your word",
        epilog="enjoy it!",
    )
    parser.add_argument(
        'text', nargs='+',
        help='the text you want to translate by youdao',
    )

    args = parser.parse_args()
    text = " ".join(args.text)
    _c = Colorizing.colorize

    bing(text)
    youdao(text)
    google(text)
    baidu(text)
    record(text)
