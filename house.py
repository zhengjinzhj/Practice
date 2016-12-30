#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import csv

proxy = {'http': '10.17.171.11:8080', 'https': '10.17.171.11:8080'}


def get_city_set():
    main_url = 'http://www.anjuke.com/sy-city.html'
    print '从城市列表中抓取所有城市的链接'
    content = requests.get(main_url, proxies=proxy)
    soup = BeautifulSoup(content.text, 'html.parser')
    all_city = set()
    for i in soup.find('div', class_='cities_boxer').find_all('a'):
        link = i['href']
        if '.fang.' in link:
            link = link.replace('.fang.', '.')
        if 'com/' in link:
            continue
        all_city.add(link)
    print '共抓取到 %d 个城市的链接' % len(all_city)
    return all_city


def get_first_hand_link(city_link):
    temp = city_link.split('.')
    temp.insert(1, 'fang')
    temp.append('/fangjia/?from=hangqing_loupanlist')
    first_hand_link = '.'.join(temp)
    return first_hand_link


def get_second_hand_link(city_link):
    return city_link + '/market/'


def get_html_source(link_url):
    html = requests.get(link_url, proxies=proxy)
    return html.text


def get_price_data(html):
    pattern = re.compile('ydata:.*?"data":\[(.*?)\]', re.S)
    items = re.findall(pattern, html)
    item = items[0].strip()
    return item.split(',')


def get_city_name(html):
    soup = BeautifulSoup(html, 'html.parser')
    city_name = soup.find('span', class_='city').string
    return city_name


def get_one_city(city_link):
    one_city_data = []
    first_hand_link = get_first_hand_link(city_link)
    second_hand_link = get_second_hand_link(city_link)
    first_hand_source = get_html_source(first_hand_link)
    city_name1 = get_city_name(first_hand_source)
    second_hand_source = get_html_source(second_hand_link)
    city_name2 = get_city_name(second_hand_source)
    # 如果没有新房数据，把新房数据全置为0
    if city_name1 != city_name2:
        first_hand_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    else:
        first_hand_data = get_price_data(first_hand_source)
    second_hand_data = get_price_data(second_hand_source)
    # 不足12个月份的数据，补齐前面月份数据为0
    if len(first_hand_data) < 12:
        for _ in xrange(12-len(first_hand_data)):
            first_hand_data.insert(0, 0)
    first_hand_data.insert(0, city_name2)
    first_hand_data.append('新房')
    second_hand_data.insert(0, city_name2)
    second_hand_data.append('二手房')
    one_city_data.append(first_hand_data)
    one_city_data.append(second_hand_data)
    return one_city_data


def main():
    all_city = get_city_set()
    csv_file = open('house.csv', 'wb')
    writer = csv.writer(csv_file, dialect='excel')
    writer.writerow(['城市', '一月', '二月', '三月', '四月', '五月', '六月',
                     '七月', '八月', '九月', '十月', '十一月', '十二月', '属性'])
    for city in all_city:
        for data in get_one_city(city):
            print '正在写入 %s 的 %s 信息...' % (data[0], data[-1])
            writer.writerow(data)
    csv_file.close()


main()





