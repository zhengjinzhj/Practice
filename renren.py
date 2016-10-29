#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import urllib2
#
# handler = urllib2.FileHandler()
# opener = urllib2.build_opener(handler)
#
# request = urllib2.Request(url='file:/D:\Users\ex-zhengjin001\Downloads\list_newest_0.json')
# f = opener.open(request)
# print f.read()

import urllib2
import urllib
import cookielib
# import json

cookie = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cookie)
proxy = urllib2.ProxyHandler({'http': '10.17.171.11:8080'})
opener = urllib2.build_opener(proxy, handler)
urllib2.install_opener(opener)

login_url = 'http://www.renren.com/PLogin.do'
value = {'email': 'zhengjinzhj@126.com', 'password': 'naobing123'}
data = urllib.urlencode(value)
login = opener.open(login_url, data)
# test_url = 'http://friend.renren.com/managefriends'
friend = opener.open('http://friend.renren.com/groupsdata')
content = friend.read()
print content.decode('unicode-escape').replace('\\', '')  # method 1
# print unicode(content, encoding='unicode-escape', errors='replace').replace('\\', '')  # method 2
# test_str2 = '\u4f60\u597d'
# print eval('u"%s"' % test_str2)  # method 3
# print json.loads('"%s"' % test_str2)  # method 4
# test_str = 'prov%3D%u6CB3%u5357%u7701%26city%3D%u5E73%u9876%u5C71%u5E02%26dist%3D%u9C81%u5C71%u53BF'
# print urllib.unquote(test_str.replace('%u', '\u').decode('unicode-escape'))
