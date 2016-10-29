#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import urllib
import json

get_time = '2016-10-21 15:50:00'
time_tuple = time.strptime(get_time, '%Y-%m-%d %H:%M:%S')  # convert a formatted time to time tuple
long_time = time.mktime(time_tuple)
# print type(time_tuple)
# print time_tuple
print int(long_time)

x = time.localtime(1477470600)  # return time tuple of current time
print time.strftime('%Y-%m-%d %H:%M:%S', x)  # convert time tuple of current time to a string as formatted

test_str = 'prov%3D%u6CB3%u5357%u7701%26city%3D%u5E73%u9876%u5C71%u5E02%26dist%3D%u9C81%u5C71%u53BF'
test_str2 = u'"\u6cb3\u5357"'
test_str3 = '\u4f60\u597d'


print urllib.unquote(test_str.replace('%u', '\u').decode('unicode-escape'))
print eval('u"%s"' % test_str3)
print json.loads('"%s"' % test_str3)
