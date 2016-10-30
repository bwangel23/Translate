#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import xml.sax
from multiprocessing import Process

from base import coroutine, EventHandler, \
    emails_to_dicts, show_email_message, filter_on_field


@coroutine
def sendto(f):
    try:
        while True:
            item = (yield)
            pickle.dump(item, f)
            f.flush()
    except StopIteration:
        f.close()

@coroutine
def recvfrom(f, target):
    try:
        while True:
            item = pickle.load(f)
            target.send(item)
    except EOFError:
        target.close()

@coroutine
def processed(target):
    fd = open("pipe.data", "w+")
    def run_target():
        """ run_target

        一个永久循环的线程，从消息队列中拉取消息，将他们发送到目标之中
        """
        try:
            while True:
                item = pickle.load(fd)
                target.send(item)
        except EOFError:
            target.close()
    Process(target=run_target).start()
    try:
        while True:
            item = (yield)
            print(item, type(item))
            pickle.dump(item, fd)
            fd.flush()
    except StopIteration:
        fd.close()



if __name__ == '__main__':
    xml.sax.parse("test.xml", EventHandler(
        emails_to_dicts(
            processed(
                filter_on_field("title", "Test Mail",
                    filter_on_field("title", "Test Mail",
                        show_email_message()
                    )
                )
            )
        )
    ))
