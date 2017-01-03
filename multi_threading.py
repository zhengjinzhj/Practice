#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
from Queue import Queue
from taobaomm import TaobaoMM

MODEL_ID = '141234233'

queue = Queue()
TaobaoMM(MODEL_ID)


def create_jobs():
    for album in TaobaoMM.get_album_list():
        album_id = album[0]
        queue.put(album_id)
    queue.join()


def create_workers():
    for _ in xrange(4):
        worker = threading.Thread(target=work)
        worker.daemon = True
        worker.start()


def work():
    while True:
        album_id = queue.get()
        TaobaoMM.single_album_all_pictures(threading.current_thread().name, MODEL_ID, album_id)
        queue.task_done()


create_workers()
create_jobs()
