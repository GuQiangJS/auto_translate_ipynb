"""
自动转换 英文 内容的 ipynb 文档为 简体中文 文档。

本工具通过调用 `py_translator` 来自动访问 Google翻译，翻译ipynb文档中的 *标记* 部分。

转换后的简体中文部分会增加至原本的英文说明部分的下方，便于对照。

默认文档编码为 `utf-8`

转换成功后会在待转换的文件的文件夹下生成新的文件，文件名后面自动增加 `_zh-cn`。

默认会使用 本机1080端口的代理 来访问Google。

---

如果需要转换为其他语言。可以修改文档中的 `dest` 属性设置。
"""

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


def newTranslator(
        proxies={'http': '127.0.0.1:1080', 'https': '127.0.0.1:1080'}):
    """

    :param use_proxies: 代理
    :return:
    """
    return Translator(proxies=proxies)


def getFullPath():
    val = ''
    while not val or not os.path.exists(val):
        val = input('Input fullpath:')

    d = os.path.dirname(val)
    f = os.path.basename(val)
    f, e = os.path.splitext(f)
    return val, d, f, e


def find_cells(js):
    """查找cells节点。所有内容均存放在此节点内。"""
    if 'cells' in js:
        return js['cells']
    elif 'worksheets' in js:
        return find_cells(js['worksheets'][0])


if __name__ == '__main__':
    fullpath, dirname, filename, ext = getFullPath()
    if fullpath:
        translator = newTranslator()

        newpath = ''
        if newpath == '':
            newpath = dirname
        with open(fullpath, encoding='utf=8') as f:
            js = json.load(f)
            cells=find_cells(js)
            if not cells:
                logging.warning('Not found cells.')
            for j in find_cells(js):
                if j['cell_type'] == 'markdown' and j['source']:
                    j['source'] += '\n'
                    for i in range(0, len(j['source']), 1):
                        s = j['source'][i]
                        j['source'].append(
                            trans(translator, s) if BeautifulSoup(s,
                                                                  'lxml').text.strip() else s)
                        logging.debug(s + ' -> ' + j['source'][-1])
            with open(os.path.join(newpath, filename + '_' + dest + ext),
                      mode='wt+', encoding=encoding) as nf:
                json.dump(js, nf, ensure_ascii=False)
    else:
        logging.error('Fullpath is empty')
