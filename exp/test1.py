#!/usr/bin/env python
# -*- coding: utf-8 -*-


import fileinput, re

class line_parse(object):
    pass

class info_bean(object):
    pass

def append_to_dict(dest_dict, key, value):
    if not key in dest_dict:
        dest_dict[key] = []

    dest_dict[key].append(value)

ENTITY_FORMAT = '''
  <rect x="%d" y="%d" rx="20" ry="20" width="%d" height="%d" style="fill:red;stroke:black;stroke-width:5;opacity:0.5" />
'''

def main():
    r = re.compile(r'(?P<tabs>\t*)(?P<name>[^:]+):(?P<value>.*)')
    #print r.match('\t\tname abc:value dafadd 88**??').groupdict()
    i = '''Entity:A
\tcolor:red
\tsize:big
Entity:B
\tcolor:yellow
\tsize:small
Relation:A-B
\tfrom_entity:A
\tto_entity:B
\tdesc:rel from a to b'''
    lines = []
    for line in i.splitlines():
        m = r.match(line).groupdict()
        l = line_parse()
        l.level = len(m['tabs'])
        l.name = m['name']
        l.value = m['value']
        print l.__dict__
        lines.append(l)

    ent_dict = {}
    cur_info = None
    for l in lines:
        info = info_bean()
        if l.level == 0:
            info.type = l.name
            info.name = l.value
            append_to_dict(ent_dict, info.type, info)
            cur_info = info
        else:
            if cur_info:
                info.name = l.name
                info.value = l.value
                append_to_dict(cur_info.__dict__, info.name, info)

    for key in ent_dict:
        print key
        for i in ent_dict[key]:
            print i.__dict__

    f = open("/tmp/svg_out.svg", 'w')
    f.write('''
<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
            ''')
    for e in layout(ent_dict):
        f.write(e.print_svg_element())
    f.write('''</svg>''')
    f.close()

    layout_1(ent_dict)

class rect_layout(object):
    def print_svg_element(self):
        return ENTITY_FORMAT % (self.x, self.y, self.width, self.height)

class arrow_layout(object):
    pass

def layout(elem_dict):
    layout_objs = []
    start_x = 10
    start_y = 10
    width = 150
    height = 150
    margin = 150

    x = start_x
    y = start_y
    for i in elem_dict['Entity']:
        r = rect_layout()
        (r.x, r.y, r.width, r.height) = (x, y, width, height)
        layout_objs.append(r)
        x = x + width + margin

    return layout_objs

def layout_1(elem_dict):
    canvas_size = (500, 500)
    slots = [
        [(250, 250)],
        [(100, 100), (400, 100), (100, 400), (400, 400)],
    ]
    entity_size = (100, 100)
    slots_cnt = 0
    for i in slots:
        slots_cnt = slots_cnt + len(i)

    ent_cnt = len(elem_dict["Entity"])
    if ent_cnt > entity_size:
        raise Exception("Only support up to %d entities. %d entities is provided" % (slots_cnt, ent_cnt))

    m_rel = [[0] * ent_cnt for _ in range(0, ent_cnt)]

    ent_idx_map = {}
    name_ent_map = {}
    for i in range(0, ent_cnt):
        e = elem_dict["Entity"][i]
        ent_idx_map[e] = i
        name_ent_map[e.name] = e

    for r in elem_dict["Relation"]:
        e_from = name_ent_map[r.from_entity[0]]
        e_to = name_ent_map[r.to_entity[0]]
        m_rel[ent_idx_map[e_from]][ent_idx_map[e_to]] = 1

    print m_rel





if __name__ == '__main__':
    main()
