#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
# import time

# filename = 'cookie.txt'
# 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
# 如果只是利用cookie请求访问另一个网址，可不保存cookie
cookie = cookielib.CookieJar()
# 利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
handler = urllib2.HTTPCookieProcessor(cookie)
# 通过handler来构建opener
opener = urllib2.build_opener(handler)
post_data = urllib.urlencode({'j_username': 'CHENYIBING797', 'j_password': 'aaaaa888'})
# 登录TSS系统的URL
loginUrl = 'http://nts-tss-rt.paic.com.cn/login?loginType=login'
# 模拟登录，服务器返回的Cookie被自动保存到变量cookie中
# 此处的open方法同urllib2的urlopen方法，也可以传入request
# result = opener.open(loginUrl, post_data)  # 方法1
request = urllib2.Request(loginUrl, post_data)  # 方法2
response = opener.open(request)  # 方法2
# 保存cookie到cookie.txt中
# cookie.save(ignore_discard=True, ignore_expires=True)
# cookie.load('cookie.txt', ignore_discard=True, ignore_expires=True)
# 利用cookie请求访问另一个网址，此网址是.do的地址
testUrl = ['http://nts-tss-rt.paic.com.cn/exter.client.relation_adjust.do',
           'http://nts-tss-rt.paic.com.cn/fish.redeemAffirm.exportExcel.do',
           'http://nts-tss-rt.paic.com.cn/fish.send.sms.do',
           'http://nts-tss-rt.paic.com.cn/redeem.pay.affirm.query.do',
           'http://nts-tss-rt.paic.com.cn/preserved.message.do'
           ]
# 请求访问.do的网址，并判断有没有权限
for i in range(0, len(testUrl)):
    # if (i != 0) & (i % 70 == 0):
    #     time.sleep(10)
    try:
        # CookieJar自动管理cookie，第一次build_opener的时候把对应的CookieJar传进去
        # 以后每次的http的request都会自动包含cookie了
        html = opener.open(testUrl[i]).read()
        if '您没有权限访问' in html:
            print '第', str(i+2), '行没有权限'
        else:
            print '第', str(i+2), '行有权限'
    except urllib2.HTTPError, e:
        print '第', str(i+2), '行有权限', str(e.code), e.reason
