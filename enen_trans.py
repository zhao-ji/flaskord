#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser
from json import loads
import xml.etree.ElementTree as ET

from gevent import joinall, spawn
from requests import get

from local_settings import *

def extract_merriam_webster_result(c, t):
    trans_ret = ET.fromstring(c.text.encode("utf-8"))
    t_ret = ET.fromstring(t.text.encode("utf-8"))
    print "Merriam Webster:"
    for definition in trans_ret:
        word_node = definition.find("./ew")
        if word_node is not None:
            print "\t{}:".format(word_node.text)
        etymology_node = definition.find("./fl")
        if etymology_node is not None:
            print "\t\tetymology: {}".format(etymology_node.text)

        pr_node = definition.find("./pr")
        hw_node = definition.find("./hw")
        if pr_node is not None:
            print "\t\tpronounciation: {}".format(
                pr_node.text.encode("utf-8"),
            )
        if hw_node is not None:
            print "\t\tstress: {}".format(
                hw_node.text.encode("utf-8"),
            )

    for definition in t_ret[0].findall("./sens"):
        define_node = definition.find("./mc")
        example_node = definition.find("./vi")
        if define_node is not None:
            print "\tdefinition: {}".format(
                define_node.text,
            )
        if example_node is not None:
            print "\texample: {}".format(
                " ".join(list(example_node.itertext()))
            )


def merriam_webster(text):
    collegiate_url = MERRIAM_WEBSTER_URL.format(
        MERRIAM_WEBSTER_COLLEGIATE, text)
    thesaurus_url = MERRIAM_WEBSTER_URL.format(
        MERRIAM_WEBSTER_THESAURUS, text)

    try:
        collegiate_ret = get(
            url=collegiate_url,
            params={"key": MERRIAM_WEBSTER_COLLEGIATE_KEY},
            timeout=3)
        thesaurus_ret = get(
            url=thesaurus_url,
            params={"key": MERRIAM_WEBSTER_THESAURUS_KEY},
            timeout=3)
    except BaseException, e:
        print e
        return

    extract_merriam_webster_result(collegiate_ret, thesaurus_ret)


def extract_oxford_result(trans_ret):
    print "Oxford:"
    for i in trans_ret["results"]:
        for index, entry in enumerate(i["lexicalEntries"]):
            print "\tlexical category: {}".format(entry["lexicalCategory"])
            if "etymologies" in entry:
                print "\tetymology: {}".format(". ".join(entry["etymologies"]))
            for sense in entry["entries"][0]["senses"]:
                if "short_definitions" in sense:
                    print "\tshort definition: {}".format(
                        ". ".join(sense["short_definitions"]))
                if "definitions" in sense:
                    print "\tdefinition: {}".format(
                        ". ".join(sense["definitions"]))
                if "etymologies" in sense:
                    print "\tetymologies: {}".format(
                        ". ".join(sense["etymologies"]))
                if "examples" in sense:
                    print "\texamples: {}".format(
                        ". ".join([i["text"] for i in sense["examples"]]))

                if "subsenses" in sense:
                    print "\tsub senses:"
                    for index, subsense in enumerate(sense["subsenses"]):
                        print "\t\tshort definition: {}".format(
                            ". ".join(subsense["short_definitions"]))
                        print "\t\tdefinition: {}".format(
                            ". ".join(subsense["definitions"]))
                        if "examples" in subsense:
                            print "\t\texamples: {}".format(". ".join(
                                [i["text"] for i in subsense["examples"]]))


def oxford(text):
    headers = {}
    headers["app_id"] = OXFORD_APP_ID
    headers["app_key"] = OXFORD_APP_KEY

    try:
        ret = get(url=OXFORD_URL.format(text), headers=headers, timeout=3)
    except BaseException, e:
        print e
        return

    if "{" not in ret.text:
        # sometimes word is not found is diction, server would return html
        return
    trans_ret = loads(ret.text.replace(u"‘", u"").replace(u"’", u""))
    extract_oxford_result(trans_ret)


def dict_service(text):
    params = {}
    params["word"] = text

    try:
        ret = get(url=DICT_SERVICE_URL, params=params, timeout=3)
    except BaseException, e:
        print e
        return

    trans_ret = ET.fromstring(ret.text.encode("utf-8"))
    for definition in trans_ret[1]:
        print "{}: {}".format(definition[1][0].text, definition[2].text)


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
    try:
        if len(text) == len(text.decode("utf8")) and " " not in text:
            joinall([
                spawn(dict_service, text),
                spawn(merriam_webster, text),
                spawn(oxford, text),
            ])
    except KeyboardInterrupt:
        exit()
