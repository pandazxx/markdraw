#!/usr/bin/env python
# -*- coding: utf-8 -*-
import parser, layout
import sys

import logging

logger = logging.getLogger(__name__)

_DEFAULT_TEMPLATE="templates/default-template.svg"

def main():
    inf = None
    if len(sys.argv) > 1:
        inf = open(sys.argv[1], 'r')
    else:
        inf = sys.stdin

    parse_results = parser.tab_parse(inf.read())
    inf.close()
    layout_results = layout.slot_layout(parse_results)

    body_str = ""

    for l in layout_results:
        body_str += l.to_svg_str()

    template_inf = open(_DEFAULT_TEMPLATE, 'r')
    template_str = template_inf.read()
    template_inf.close()

    output_str = template_str % body_str

    outf = open('/tmp/output.svg', 'w')
    outf.write(output_str)
    outf.close()

if __name__ == '__main__':
    main()
