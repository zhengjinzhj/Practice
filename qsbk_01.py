#!/usr/bin/python
# filename: qsbk_01.py

# -*- coding: utf-8 -*-

import urllib2
import re

proxy = urllib2.ProxyHandler({'http': '10.17.171.11:8080'})
opener = urllib2.build_opener(proxy, urllib2.HTTPHandler)
urllib2.install_opener(opener)

page = raw_input("please enter the page number:")
url = 'http://www.qiushibaike.com/8hr/page/' + page + '/?s=4880477'

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
headers = {'User-Agent': user_agent}
try:
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    # response = opener.open(request)
    content = response.read().decode('utf-8')
#    pattern = re.compile('<div.*?author.*?>.*?<img.*?>.*?<h2>(.*?)</h2>.*?<div.*?' +
#                         'content">(.*?)</div>(.*?)<div class="stats.*?class="number">(.*?)</i>', re.S)
    pattern = re.compile('<div.*?author.*?<h2>(.*?)</h2>'
                         '.*?<div.*?content">(.*?)</div>(.*?)'
                         '<div class="stats.*?class="number">(.*?)</i>', re.S)
    items = re.findall(pattern, content)
    for item in items:
        haveImg = re.search('img', item[2])
        # print haveImg
        if not haveImg:
            replaceBr = re.compile('<br/>')
            text = re.sub(replaceBr, "\n", item[1])
            print item[0], item[3], text
except urllib2.URLError, e:
    if hasattr(e, "code"):
        print e.code
    if hasattr(e, "reason"):
        print e.reason
