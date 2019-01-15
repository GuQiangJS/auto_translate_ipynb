from __future__ import unicode_literals

import json
import logging
import os
import re
import sys

from bs4 import BeautifulSoup
from py_translator import Translator

dest = 'zh-cn'
encoding = 'utf-8'
fullpath = r''

replace_left = True
replace_right = True
replace_k = True
replace_l1 = True
replace_l2 = True
replace_shape = True
skip_math = True

RE_K = re.compile('(#+)[^ #]')
RE_MATH = re.compile('\$[^$]*\$')

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


def trans(translator, str):
    if not translator:
        translator = newTranslator()
    math_dic = {}
    if skip_math:
        maths = RE_MATH.findall(str)
        if maths:
            for i in range(len(maths)):
                math_dic[maths[i]] = 'math_{0}_math'.format(i)
            for k, v in math_dic.items():
                str = str.replace(k, v)
    r = translator.translate(str, dest=dest).text
    if skip_math and math_dic:
        for k, v in math_dic.items():
            r = r.replace(v, ' ' + k + ' ')
    if replace_left:
        r = r.replace('（', '(')
    if replace_right:
        r = r.replace('）', ')')
    if replace_left:
        r = r.replace('“', '`')
    if replace_right:
        r = r.replace('”', '`')
    if replace_shape:
        r = r.replace('＃', '#')
    r = r.replace(r'\ text', r'\text')
    if replace_k:
        m = RE_K.search(r)
        if m:
            r = r.replace(m.group(1), m.group(1) + ' ')
    return '\n' + r


def newTranslator():
    return Translator(proxies={'http': '127.0.0.1:1080', 'https': '127.0.0.1:1080'})


def getFullPath():
    val = ''
    while not val or not os.path.exists(val):
        val = input('input fullpath:')

    d = os.path.dirname(val)
    f = os.path.basename(val)
    f, e = os.path.splitext(f)
    return val, d, f, e


if __name__ == '__main__':
    fullpath, dirname, filename, ext = getFullPath()
    if fullpath:
        translator = newTranslator()

        newpath = ''
        if newpath == '':
            newpath = dirname
        with open(fullpath, encoding='utf=8') as f:
            js = json.load(f)
            for j in js['cells']:
                if j['cell_type'] == 'markdown' and j['source']:
                    j['source'] += '\n'
                    for i in range(0, len(j['source']), 1):
                        s = j['source'][i]
                        j['source'].append(trans(translator, s) if BeautifulSoup(s,'lxml').text.strip() else s)
                        logging.debug(s + ' -> ' + j['source'][-1])
            with open(os.path.join(newpath, filename + '_' + dest + ext), mode='wt+', encoding=encoding) as nf:
                json.dump(js, nf, ensure_ascii=False)
    else:
        logging.error('fullpath is empty')
