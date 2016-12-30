#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
from Queue import Queue
from taobaomm import TaobaoMM

model_id = '2926468580'
queue = Queue()


def create_jobs(album_id, album_name):
    for img_link in TaobaoMM.get_img_link(model_id, album_id):
        queue.put([img_link, album_name])
    queue.join()


def get_albums():
    for album in TaobaoMM.get_album_list(model_id):
        album_id = album[0]
        album_name = album[1]
        album_page = album[2]
        print 'There are %s pictures in %s: %s' % (album_page, album_name, album_id)
        TaobaoMM.make_folder(album_name)
        create_jobs(album_id, album_name)


def create_workers():
    for _ in xrange(4):
        worker = threading.Thread(target=work)
        worker.daemon = True
        worker.start()


def work():
    while True:
        image_url = queue.get()[0]
        album_name = queue.get()[1]
        TaobaoMM.save_img(threading.current_thread().name, image_url, album_name)
        queue.task_done()


create_workers()
get_albums()


































# from selenium import webdriver
# from bs4 import BeautifulSoup
# import time
#
# options = webdriver.ChromeOptions()
# options.add_argument('user-data-dir=D:\Users\ex-zhengjin001\AppData\Local\Google\Chrome\User Data')
#
# browser = webdriver.Chrome(chrome_options=options)
# # browser.maximize_window()
# # browser.set_window_size(1280, 720)
# browser.set_window_position(200, 0)
#
#
# def test():
#     browser.get('http://weibo.com')
#     time.sleep(10)
#     for count in xrange(1, 3):
#         print 'Scrolling down: %d' % count
#         js = "window.scrollTo(0,document.body.scrollHeight)"
#         browser.execute_script(js)
#         time.sleep(3)
#     html = open('test.html', 'w')
#     soup = BeautifulSoup(browser.page_source, 'html.parser')
#     content = soup.select('li[action-type="feed_list_item"]')
#     count = 1
#     for item in content:
#         print >>html, '***************%d**************' % count
#         print >>html, item
#         count += 1
#     # print >>html, soup.prettify()
#     # Ctrl+t to open a new tab and Ctrl+w to close it.
#     # ActionChains(browser).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
#     browser.quit()
#
# test()


