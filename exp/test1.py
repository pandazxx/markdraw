#!/usr/bin/env python
# -*- coding: utf-8 -*-


import fileinput, re

class line_parse(object):
    pass

class info_bean(object):
    pass

def main():
    r = re.compile(r'(?P<tabs>\t*)(?P<name>[^:]+):(?P<value>.*)')
    #print r.match('\t\tname abc:value dafadd 88**??').groupdict()
    i = '''\t\tname abc:value asdfafd 88$**
\t\tname def:value 88$**'''
    lines = []
    for line in i.splitlines():
        m = r.match(line).groupdict()
        l = line_parse()
        l.level = len(m['tabs'])
        l.name = m['name']
        l.value = m['value']
        print l.__dict__
        lines.append(l)




if __name__ == '__main__':
    main()
