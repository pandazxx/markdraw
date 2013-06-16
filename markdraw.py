#!/usr/bin/env python
# -*- coding: utf-8 -*-
import parser, layout
import sys

import logging

logger = logging.getLogger(__name__)


def main():
    inf = None
    if len(sys.argv) > 1:
        inf = open(sys.argv[1], 'r')
    else:
        inf = sys.stdin

    parse_results = parser.tab_parse(inf.read())
    inf.close()
    layout_results = layout.slot_layout(parse_results)

    outf = open('/tmp/output.svg', 'w')
    outf.write('''
<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
            ''')
    for l in layout_results:
        outf.write(l.to_svg_str())
    outf.write('''</svg>''')
    outf.close()

if __name__ == '__main__':
    main()
