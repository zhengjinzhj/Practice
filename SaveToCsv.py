# -*- coding: utf-8 -*-

import urllib2
import re
import csv

proxy = urllib2.ProxyHandler(proxies={'http': '10.17.171.11:8080'})
opener = urllib2.build_opener(proxy, urllib2.HTTPHandler)
urllib2.install_opener(opener)
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
headers = {'User-Agent': user_agent}


def get_html(base_url):
    csv_file = file('jiandan.csv', 'wb')
    for i in [1515, 1514]:
        url = base_url + str(i)
        try:
            request = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(request)
            content = response.read().decode('utf-8')
            pattern = re.compile('<li id="comment-(.*?)">.*?class="author".*?" >(.*?)</strong>'
                                 '.*?class="text".*?<p>(.*?)</p>', re.S)
            items = re.findall(pattern, content)
            # csv_file = file('jiandan.csv', 'wb')
            writer = csv.writer(csv_file, dialect='excel')
            writer.writerow(['comment_no', 'author', 'content'])
            for item in items:
                replace_br = re.compile('<br />')
                content = re.sub(replace_br, '', item[2])
                writer.writerow([item[0], item[1], content])
            # csv_file.close()

        except urllib2.URLError, e:
            if hasattr(e, 'code'):
                print e.code
            if hasattr(e, 'reason'):
                print e.reason
    csv_file.close()

# def get_items(url):
#     html = get_html(url)
#     container = []
#     pattern = re.compile('<li id="comment-(.*?)">.*?class="author".*?" >(.*?)</strong>'
#                          '.*?class="text".*?<p>(.*?)</p>', re.S)
#     items = re.findall(pattern, html)
#     for item in items:
#         container.append([item[0], item[1], item[2]])
#         # print item[0], item[1], item[2]
#         # print ''
#     return container
# # get_items('http://jandan.net/duan')
#
#
# def write_into_csv(url):
#     csv_file = file('jiandan.csv', 'wb')
#     items = get_items(url)
#     # with open('csv_file', 'wb') as f:
#     writer = csv.writer(csv_file, dialect='excel')
#     writer.writerow(['comment_no', 'author', 'content'])
#     for item in items:
#         writer.writerow([item[0], item[1], item[2]])
#     csv_file.close()


get_html('http://jandan.net/duan/page-')
