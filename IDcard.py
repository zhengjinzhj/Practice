#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os


def get_validate_code(num_str):
    check_dict = {0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_num = 0
    for index, num in enumerate(num_str):  # 341281 --> [0:3, 1:4, 2:1, 3:2, 4:8, 5:1]
        # print '%s --> %s' % (index, num)
        # weight = 2**(17-index) % 11
        check_num += int(num) * weight[index]
    right_code = check_dict.get(check_num % 11)  # right_code is get from check_dict by KEY
    id_card_number = num_str + right_code
    print 'The validate code of this ID card is: %s\nThe ID card number is: %s'\
          % (right_code, id_card_number)

# get_validate_code('34128119801106579')

my_list = [{'players.vis_name': 'Khazri', 'players.role': 'Midfielder', 'players.country': 'Tunisia',
            'players.last_name': 'Khazri', 'players.player_id': '989', 'players.first_name': 'Wahbi',
            'players.date_of_birth': '08/02/1991', 'players.team': 'Bordeaux'},
           {'players.vis_name': 'Khazri', 'players.role': 'Midfielder', 'players.country': 'Tunisia',
            'players.last_name': 'Khazri', 'players.player_id': '989', 'players.first_name': 'Wahbi',
            'players.date_of_birth': '08/02/1991', 'players.team': 'Sunderland'},
           {'players.vis_name': 'Lewis Baker', 'players.role': 'Midfielder', 'players.country': 'England',
            'players.last_name': 'Baker', 'players.player_id': '9574', 'players.first_name': 'Lewis',
            'players.date_of_birth': '25/04/1995', 'players.team': 'Vitesse'}]


def list_to_csv():
    with open('list_to_csv.csv', 'wb') as f:
        writer = csv.writer(f)
        title = my_list[0].keys()
        writer.writerow(title)
        for row in my_list:
            writer.writerow(row.values())
        f.close()
# list_to_csv()


def csv_to_dict():
    with open('list_to_csv.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        fieldnames = next(reader)
        print fieldnames
        reader = csv.DictReader(f, fieldnames=fieldnames, delimiter=',')
        for row in reader:
            print row

# csv_to_dict()
print os.getcwd()
os.mkdir('test--temp')
print os.getcwd()




