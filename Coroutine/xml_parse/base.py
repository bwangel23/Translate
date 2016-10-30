#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pprint
import xml.sax
import sys

def coroutine(func):
    def wrapper(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return wrapper

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
