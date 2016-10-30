#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import xml.sax
import pprint

from threading import Thread
from queue import Queue

def coroutine(func):
    def wrapper(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return wrapper

@coroutine
def threaded(target):
    message = Queue()   # 一个消息队列
    def run_target():
        """ run_target

        一个永久循环的线程，从消息队列中拉取消息，将他们发送到目标之中
        """
        while True:
            item = message.get()
            if item is GeneratorExit:
                target.close()
                return
            else:
                target.send(item)
    Thread(target=run_target).start()
    # 接收消息，并把他们发送到线程之中
    try:
        while True:
            item = (yield)
            message.put(item)
    except GeneratorExit:
        # 通过 GeneratorExit 异常来让线程正确地关闭
        message.put(GeneratorExit)

@coroutine
def emails_to_dicts(target):
    while True:
        event, value = (yield)
        if event == 'start' and value[0] == 'entry':
            email_dict = {}
            fragments = []
            while True:
                event, value = (yield)
                if event == 'start':
                    if value[0] == 'link':
                        fragments = [value[1]['href']]
                    else:
                        fragments = []
                elif event == 'text':
                    fragments.append(value)
                elif event == 'end':
                    if value != 'entry':
                        email_dict[value] = ":".join(fragments)
                    else:
                        target.send(email_dict)
                        break


@coroutine
def filter_on_field(fieldname, value, target):
    while True:
        d = (yield)
        if d.get(fieldname) == value:
            target.send(d)


@coroutine
def show_email_message():
    while True:
        email = (yield)
        pprint.pprint(email, stream=sys.stderr)


class EventHandler(xml.sax.ContentHandler):
    def __init__(self, target):
        self.target = target
    def startElement(self, name, attrs):
        self.target.send(('start', (name, attrs._attrs)))
    def characters(self, text):
        self.target.send(('text', text))
    def endElement(self, name):
        self.target.send(('end', name))


if __name__ == '__main__':
    xml.sax.parse("test.xml", EventHandler(
        emails_to_dicts(
            threaded(
                filter_on_field("title", "Test Mail",
                    filter_on_field("title", "Test Mail",
                        show_email_message()
                    )
                )
            )
        )
    ))
