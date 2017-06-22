#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.sax
from threading import Thread
from queue import Queue

from base import coroutine, EventHandler, \
    emails_to_dicts, filter_on_field, show_email_message

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
