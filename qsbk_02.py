# !/usr/bin/python
# filename: qsbk_02.py

# -*- coding: utf-8 -*-

import urllib2
import re
import xlsxwriter


class QSBK(object):
    def __init__(self):
        self.pageIndex = raw_input("please enter the page number:")
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
        self.headers = {'User-Agent': self.user_agent}
        self.proxy = urllib2.ProxyHandler({'http': '10.17.171.11:8080'})
        self.opener = urllib2.build_opener(self.proxy, urllib2.HTTPHandler)
        urllib2.install_opener(self.opener)

    def get_page(self):
        try:
            url = 'http://www.qiushibaike.com/hot/page/' + str(self.pageIndex)
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            content = response.read().decode('utf-8')
            pattern = re.compile('<div.*?author.*?>.*?<img.*?>.*?<h2>(.*?)</h2>.*?<div.*?' +
                                 'content">(.*?)</div>(.*?)<div class="stats.*?class="number">(.*?)</i>', re.S)

            items = re.findall(pattern, content)

            workbook = xlsxwriter.Workbook('test.xlsx')
            worksheet = workbook.add_worksheet('qsbk')

            title_format = workbook.add_format({'bold': True, 'font_color': 'Yellow', 'align': 'center'})
            content_format = workbook.add_format({'text_wrap': True, 'valign': 'vcenter', 'align': 'center'})
            content_format2 = workbook.add_format({'text_wrap': True, 'align': 'left'})
            worksheet.set_row(0, cell_format=title_format)
            worksheet.set_column('B:B', 50)

            worksheet.write('A1', 'Author')
            worksheet.write('B1', 'Content')
            worksheet.write('C1', 'GoodNum')
            row = 1
            col = 0
            for item in items:
                have_img = re.search('img', item[2])
                if not have_img:
                    replace_br = re.compile('<br/>')
                    remove_span = re.compile('<span>|</span>')
                    text = re.sub(replace_br, '\n', item[1])
                    text = re.sub(remove_span, '', text)
                    worksheet.write(row, col, item[0], content_format)
                    worksheet.write(row, col + 1, text.strip(), content_format2)
                    worksheet.write(row, col + 2, item[3], content_format)
                    row += 1
            workbook.close()
            # print item[0], item[3], text

        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print e.code
            if hasattr(e, "reason"):
                print e.reason
            return None


spider = QSBK()
spider.get_page()
