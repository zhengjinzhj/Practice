#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re
import os
import csv


class TaobaoMM(object):

    def __init__(self):
        self.site_url = 'https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8' \
                        '&pageSize=100&currentPage='
        self.https_proxy = urllib2.ProxyHandler({'https': '10.17.171.11:8080'})
        self.http_proxy = urllib2.ProxyHandler({'http': '10.17.171.11:8080'})
        self.opener = urllib2.build_opener(self.http_proxy, self.https_proxy)
        urllib2.install_opener(self.opener)

    def get_page(self, page_index):
        # Get the given page's (index page) page source and do some small 'formatted'.
        url = self.site_url + str(page_index)

        response = self.opener.open(url)
        response = response.read().decode('gbk')
        source_data = self.remove_double_quotation_marks(response)
        return source_data

    def get_contents(self, page_index):
        # Get the wanted data from given page source (index page).
        source_data = self.get_page(page_index)
        pattern = re.compile('\{avatarUrl:(.*?),cardUrl:(.*?),city:(.*?),.*?,identityUrl.*?realName:(.*?),'
                             'totalFanNum:(.*?),totalFavorNum:(.*?),userId:(.*?),.*?}', re.S)
        items = re.findall(pattern, source_data)
        contents = []
        for item in items:
            contents.append([item[0], item[1], item[2], item[3], item[4], item[5], item[6]])
        return contents

    def get_model_info(self, model_id):
        info_url = 'https://mm.taobao.com/self/info/model_info_show.htm?user_id=' + str(model_id)
        response = self.opener.open(info_url).read()
        response = response.decode('gbk').encode('utf-8')
        model_info = []
        pattern = re.compile('<ul class="mm-p-info-cell clearfix">.*?<span>(.*?)</span>.*?<span>(.*?)</span>'
                             '.*?<span>(.*?)</span>.*?<span>(.*?)</span>.*?<span>(.*?)</span>.*?<span>(.*?)</span>'
                             '.*?<span>(.*?)</span>.*?<p>(.*?)</p>.*?<p>(.*?)</p>.*?<p>(.*?)</p>.*?<p>(.*?)</p>'
                             '.*?<p>(.*?)</p>', re.S)
        items = re.findall(pattern, response)
        for item in items:
            birthday = item[1].strip()
            birthday = self.remove_space(birthday)
            education = item[5].strip()
            education = self.remove_space(education)
            model_info.append([item[0], birthday, item[2], item[3], item[4], education, item[6],
                               item[7], item[8], item[9], item[10], item[11]])
        return model_info

    def get_album_list(self, model_id):
        # Get page number of all albums, after this, crawl all the pages and find the link and name of all these albums
        first_album_list_url = 'https://mm.taobao.com/self/album/open_album_list.htm?user_id=' + str(model_id)
        response = self.opener.open(first_album_list_url)
        find_total_page = response.read().decode('gbk').encode('utf-8')
        page_no_pattern = re.compile('<input name="totalPage.*?value="(.*?)" type="hidden" />', re.S)
        total_page = re.findall(page_no_pattern, find_total_page)
        # print total_page[0], type(total_page[0])
        albums = []
        for i in xrange(1, int(total_page[0])+1):
            album_list_url = first_album_list_url + '&page=' + str(i)
            # print album_list_url  # Just for testing
            response = self.opener.open(album_list_url)
            response = response.read()
            album_link_page = response.decode('gbk').encode('utf-8')
            # album_link_page = self.remove_double_quotation_marks(album_link_page)
            album_link_pattern = re.compile('<h4>.*?&album_id=(.*?)&album_flag.*?target="_blank">(.*?)'
                                            '</a></h4>.*?mm-pic-number">\((.*?)张\)</span>', re.S)
            album_list = re.findall(album_link_pattern, album_link_page)
            for item in album_list:
                album_name = item[1].strip()  # Something wrong here (fixed by strip()).
                # item[0]=album id, item[1]=album name
                # item[2]=how many pictures in this album
                albums.append([item[0], album_name, item[2]])
        # print albums  # Just for testing
        return albums

    def download_album(self, model_id, model_name):
        album_info = self.get_album_list(model_id)
        for album in album_info:
            # print album, type(album)
            # for item in album:
            #     print item
            album_name = self.remove_dot(album[1])
            print 'Album ' + album_name + ' has ' + str(album[2]) + ' pictures'
            self.make_folder('mm.taobao' + '/' + model_name + '/' + album_name)
            print 'Downloading album ' + album_name
            image_list = self.get_img_link(model_id, album[0])
            for image_url in image_list:
                self.save_img(image_url, 'mm.taobao' + '/' + model_name + '/' + album_name)

    def get_img_link(self, model_id, album_id):
        image_url = []
        first_album_url = 'https://mm.taobao.com/album/json/get_photo_list_tile_data.htm?user_id='\
                    + str(model_id) + '&album_id=' + str(album_id)
        response = self.opener.open(first_album_url)
        response = response.read()
        page_no_pattern = re.compile('<input name="totalPage.*?value="(.*?)" type="hidden" />', re.S)
        total_page = re.findall(page_no_pattern, response)
        for i in xrange(1, int(total_page[0])+1):
            album_url = first_album_url + '&page=' + str(i)
            response = self.opener.open(album_url)
            response = response.read()
            pattern = re.compile('<li class="default-item ">.*?<img src="(.*?)" class="favory-img".*?</li>', re.S)
            image_urls = re.findall(pattern, response)
            for item in image_urls:
                image_url.append('http:' + item)
        return image_url

    @staticmethod
    def make_folder(folder_name):  # folder_name is model name or album name
        if not os.path.exists(folder_name):
            print 'Making folder "' + folder_name + '"'
            os.mkdir(folder_name)
        else:
            print 'Folder already exists, skip...'

    @staticmethod
    def remove_double_quotation_marks(source_data):
        # Some small 'formatted' of the page source.
        pattern = re.compile('\"')
        source_data = re.sub(pattern, '', source_data)
        return source_data

    @staticmethod
    def remove_space(source_data):
        pattern = re.compile('&nbsp;')
        source_data = re.sub(pattern, '', source_data)
        return source_data

    @staticmethod
    def remove_dot(source_data):
        pattern = re.compile('\.')
        source_data = re.sub(pattern, '', source_data)
        return source_data

    def save_img(self, image_url, folder_name):
        image_name = image_url.split('/').pop()
        image_location = folder_name + '/' + image_name
        if not os.path.isfile(image_location):
            print 'Saving picture ' + image_name
            image_data = self.opener.open(image_url)
            image_data = image_data.read()
            f = open(image_location, 'wb')
            f.write(image_data)
            f.close()
        else:
            print image_name + ' already exists, skip...'

    def main(self, page_index):
        # Something like the main function.
        self.make_folder('mm.taobao')
        csv_file = file('mm.taobao/model_info.csv', 'wb')
        writer = csv.writer(csv_file, dialect='excel')
        writer.writerow(['昵称', '生日', '所在城市', '职业', '血型', '学校/专业', '风格',
                         '身高', '体重', '三围', '罩杯', '鞋码'])
        contents = self.get_contents(page_index)
        for item in contents:
            # Found the popular model and skip these that is not so popular.
            if int(item[4]) > 1000 or int(item[5]) > 500:
                print 'Found a popular model, her name is ' + item[3] + ', she has ' + str(item[4]) + \
                      ' fans and her total favor number is ' + str(item[5])
                print 'Writing ' + item[3] + "'s info..."
                model_info = self.get_model_info(str(item[6]))
                writer.writerow([model_info[0][0], model_info[0][1], model_info[0][2], model_info[0][3],
                                model_info[0][4], model_info[0][5], model_info[0][6], model_info[0][7],
                                model_info[0][8], model_info[0][9], model_info[0][10], model_info[0][11]])
                model_name = self.remove_dot(item[3])
                self.make_folder('mm.taobao' + '/' + model_name)
                self.download_album(item[6], model_name)
            else:
                print 'Found a model, her name is ' + item[3] + ', but she is not very popular, skip...'
        csv_file.close()

demo = TaobaoMM()
for page in xrange(11, 12):
    print '='*20 + 'PAGE ' + str(page) + '='*20
    demo.main(page)


























