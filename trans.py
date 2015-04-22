#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser

from requests import get, post

KEY = '1842459857'
KEYFROM = 'ScriptsOfTranslate'
URL = 'http://fanyi.youdao.com/openapi.do'
RECORD_URL = 'https://chashuibiao.org/word'


def translate(text):
    params = {}
    params['keyfrom'] = KEYFROM
    params['key'] = KEY
    params['type'] = 'data'
    params['doctype'] = 'json'
    params['version'] = '1.1'
    params['q'] = text

    try:
        ret = get(url=URL, params=params, timeout=5)
    except BaseException, e:
        print e
        return
    trans_ret = ret.json()

    print '结果：'

    translation = ', '.join(trans_ret['translation'])
    print ' ' * 4 + '翻译：' + translation.encode('utf8')

    if 'basic' in trans_ret:
        basic = ('\n'+' '*9).join(trans_ret['basic']['explains'])
        print ' ' * 4 + '基本查询：' + basic.encode('utf8')

    if 'web' in trans_ret:
        web = ('\n'+' '*9).join(
            '{}: {}'.format(
                item['key'].encode('utf8'),
                ', '.join(i.encode('utf-8') for i in item['value']))
            for item in trans_ret['web'])
        print ' ' * 4 + '网络查询：' + web


def record(text):
    payload = {"word": text}
    post(RECORD_URL, data=payload)


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
    word = ' '.join(args.text)
    print word
    translate(word)
    record(word)
