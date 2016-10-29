#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re
import csv
import os

https_proxy = urllib2.ProxyHandler({'https': '10.17.171.11:8080'})
http_proxy = urllib2.ProxyHandler({'http': '10.17.171.11:8080'})
opener = urllib2.build_opener(https_proxy, http_proxy)
urllib2.install_opener(opener)


def main():
    make_folder('taobaomm')
    csv_file = file('taobaomm.csv', 'wb')
    writer = csv.writer(csv_file, dialect='excel')
    writer.writerow(['avatarUrl', 'cardUrl', 'city', 'height', 'realName', 'totalFanNum', 'totalFavorNum', 'userID'])
    url = 'https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8' \
          '&searchRegion=city%3A%E6%88%90%E9%83%BD&currentPage=1&pageSize=100'
    content = opener.open(url).read()
    content = content.decode('gbk').encode('utf-8')
    data = remove_other(content)
    pattern = re.compile('\{avatarUrl:(.*?),cardUrl:(.*?),city:(.*?),height:(.*?),identityUrl.*?realName:(.*?),'
                         'totalFanNum:(.*?),totalFavorNum:(.*?),userId:(.*?),.*?weight:(.*?)}', re.S)
    items = re.findall(pattern, data)
    for item in items:
        writer.writerow([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]])
    csv_file.close()
    # u = opener.open('http://img.alicdn.com/sns_logo/i1/T1K9T7FfVeXXb1upjX.jpg')
    # print u.read()
    for item in items:
        try:
            avatar_url = 'http://' + item[0]
            avatar_name = 'taobaomm' + '/' + item[4].decode('utf-8').encode('cp936') + '1.jpg'
            if not os.path.isfile(avatar_name):
                print 'Saving ' + item[4] + "'s avatar..."
                save_img(avatar_url, avatar_name)
            else:
                print 'Already exists, skip...'
            card_url = 'http://' + item[1]
            card_name = 'taobaomm' + '/' + item[4].decode('utf-8').encode('cp936') + '2.jpg'
            if len(card_url) > 10:
                if not os.path.isfile(card_name):
                    print 'Saving ' + item[4] + "'s card..."
                    save_img(card_url, card_name)
                else:
                    print 'Already exists, skip...'
            else:
                print item[4] + ' has no card picture'
        except urllib2.HTTPError, e:
            print str(e.code) + e.reason

    # print data


def remove_other(content):
    remove_quota = re.compile('\"')
    remove_back = re.compile('//')
    content = re.sub(remove_quota, '', content)
    content = re.sub(remove_back, '', content)
    return content


def save_img(image_url, file_name):
    u = opener.open(image_url)
    data = u.read()
    f = open(file_name, 'wb')
    f.write(data)
    f.close()


def make_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

main()

