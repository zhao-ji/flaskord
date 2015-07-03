#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser

from gevent import joinall, spawn
from requests import get, post

YOUDAO_KEY = ''
YOUDAO_KEYFROM = 'ScriptsOfTranslate'
YOUDAO_URL = 'http://fanyi.youdao.com/openapi.do'

GOOGLE_API_KEY = ""
GOOGLE_URL = "https://www.googleapis.com/language/translate/v2"

RECORD_URL = 'http://chashuibiao.org/word/'


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
    trans_ret = ret.json()
    print "谷歌翻译：", trans_ret["data"]["translations"][0]["translatedText"]
    print ""


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
    except BaseException, e:
        print e
        return
    trans_ret = ret.json()

    translation = ', '.join(trans_ret.get('translation', []))
    print '有道翻译：' + translation.encode('utf8')
    print ""

    if 'basic' in trans_ret:
        basic = ('\n\t').join(trans_ret['basic']['explains'])
        print '基本查询：' + basic.encode('utf8')

    if 'web' in trans_ret:
        web = ('\n\t').join(
            '{}: {}'.format(
                item['key'].encode('utf8'),
                ', '.join(i.encode('utf-8') for i in item['value']))
            for item in trans_ret['web'])
        print '网络查询：' + web


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
    joinall([
        spawn(google, text), spawn(youdao, text), spawn(record, text),
    ])
