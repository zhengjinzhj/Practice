#!/usr/bin/python
# filename: qsbk_10.py

# -*- coding: utf-8 -*-

import urllib2
import re


class QSBK(object):

    proxy = urllib2.ProxyHandler({'http': '10.17.171.11:8080'})
    opener = urllib2.build_opener(proxy, urllib2.HTTPHandler)
    urllib2.install_opener(opener)

    def __init__(self):
        self.pageindex = int(raw_input('Read from which page?'))  # page number, start to read from page input.
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
        self.headers = {'User-Agent': self.user_agent}
        self.storage = []  # create a list to store one piece of tweet.
        self.enable = False

    def getpage(self, pageindex):  # read one page
        try:
            url = 'http://www.qiushibaike.com/hot/page/' + str(pageindex) + '/?s=4880776'
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            content = response.read().decode('utf-8')
            pattern = re.compile('<div.*?author.*?>.*?<img.*?>.*?<h2>(.*?)</h2>.*?<div.*?' +
                                 'content">(.*?)</div>(.*?)<div class="stats.*?class="number">(.*?)</i>', re.S)

            items = re.findall(pattern, content)

            for item in items:
                haveimg = re.search("img", item[2])
                if not haveimg:
                    replacebr = re.compile('<br/>')
                    text = re.sub(replacebr, "\n", item[1])
                    self.storage.append([item[0], item[3], text])

        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print e.code
            if hasattr(e, "reason"):
                print e.reason
            return None

    def start(self):
        print "Read complete, Press 'Enter' button to read one story, press 'q' button to quit."
        self.enable = True

        while self.enable:
            self.getpage(self.pageindex)
            for i in range(len(self.storage)):
                input = raw_input()
                if input == "q":
                    self.enable = False
                    return
                print "page:%d, number:%d\nauthor: %s\nprise : %d\n%s" % (
                    self.pageindex, i+1, self.storage[i][0].strip(),
                    int(self.storage[i][1].strip()), self.storage[i][2].strip())  # strip() to remove ' ' on both side
                # print type(self.storage[i][1]) -->result = unicode

            self.pageindex += 1  # next page
            self.storage = []  # clear list


spider = QSBK()
spider.start()
