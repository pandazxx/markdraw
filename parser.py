#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

class ParsedEntity(object):
    """Parsed entity"""
    def __init__(self, **kwarg):
        """Init method"""
        self.__dict__ = kwarg

    def _add_attribute(self, key, value):
        if key in self.__dict__:
            v = self.__dict__[key]
            if isinstance(v, list):
                v.append(value)
            else:
                l = [v, value]
                self.__dict__[key] = l
        else:
            self.__dict__[key] = value


def tab_parse(str_to_be_parsed):
    class line_parse_object(object):
        def __init__(self, level, name, value):
            self.level = level
            self.name = name
            self.value = value
    lines = str_to_be_parsed.splitlines()
    r = re.compile(r'(?P<tabs>\t*)(?P<name>[^:]+):(?P<value>.*)')

    parse_results = []
    for line in lines:
        match = r.match(line)
        group = match.groupdict()
        l = line_parse_object(
            len(group['tabs']),
            group['name'],
            group['value'])
        parse_results.append(l)

    ret_dict = {}
    current_ent = None
    for res in parse_results:
        if res.level == 0:
            current_ent = ParsedEntity()
            current_ent.type = res.name
            current_ent.name = res.value
            _append_to_dict(ret_dict, current_ent.type, current_ent)
        else:
            if current_ent:
                current_ent._add_attribute(res.name, res.value)
    return ret_dict

def _append_to_dict(dest_dict, key, value):
    if not key in dest_dict:
        dest_dict[key] = []

    dest_dict[key].append(value)

