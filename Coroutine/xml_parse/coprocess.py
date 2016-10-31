#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import xml.sax
import time
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
    def run_target():
        """ run_target

        """
        fd = open("pipe.data", "rb")
        try:
            while True:
                # 这里使用了一个笨办法，子进程睡眠一会，
                #   等待父进程数据写入完成了以后再读取数据
                time.sleep(1)
                item = pickle.load(fd)
                target.send(item)
        except EOFError:
            target.close()

    Process(target=run_target).start()

    fd = open("pipe.data", "wb")
    try:
        while True:
            item = (yield)
            pickle.dump(item, fd)
            fd.flush()
    except StopIteration:
        fd.close()


if __name__ == '__main__':
    xml.sax.parse("test.xml", EventHandler(
        emails_to_dicts(
            processed(
                filter_on_field("title", "Test Mail",
                    show_email_message()
                )
            )
        )
    ))
