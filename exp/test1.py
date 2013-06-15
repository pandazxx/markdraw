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

RELATION_FORMAT = '''
    <line x1="%d" y1="%d" x2="%d" y2="%d" style="stroke:rgb(255,0,0);stroke-width:2" />
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
Entity:C
\tcolor:blue
\tsize:small
Relation:A-C
\tfrom_entity:A
\tto_entity:C
\tdesc:rel from a to c
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

    (entity_layouts, relation_layouts) = layout_1(ent_dict)

    f = open("/tmp/svg_out2.svg", "w")
    f.write('''
             <svg xmlns="http://www.w3.org/2000/svg" version="1.1">
            ''')
    f.write(draw_entities(entity_layouts))
    f.write(draw_relations(relation_layouts))
    f.write('''</svg>''')
    f.close()



class rect_layout(object):
    def __init__(self, center, size):
        #ret = rect_layout()
        self.center = center
        self.size = size
        self.origin = (center[0] - size[0]/2, center[1] - size[1]/2)

    def get_junction_point(self, to_point):
        delta_x = to_point[0] - self.center[0]
        delta_y = to_point[1] - self.center[1]
        x_rato = abs(delta_x/self.size[0])
        y_rato = abs(delta_y/self.size[1])
        horizontal = x_rato > y_rato

        upper = (self.center[0], self.center[1] - self.size[1]/2)
        lower = (self.center[0], self.center[1] + self.size[1]/2)
        left = (self.center[0] - self.size[0]/2, self.center[1])
        right = (self.center[0] + self.size[0]/2, self.center[1])

        if delta_x > 0 and delta_y > 0:
            return right if horizontal else lower
        elif delta_x > 0 and delta_y < 0:
            return right if horizontal else upper
        elif delta_x < 0 and delta_y > 0:
            return left if horizontal else lower
        elif delta_x < 0 and delta_y < 0:
            return left if horizontal else upper

    def print_svg_element(self):
        return ENTITY_FORMAT % (self.origin[0], self.origin[1], self.size[0], self.size[1])

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
        r = rect_layout((x, y), (width, height))
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

    relation_list = []

    for r in elem_dict["Relation"]:
        e_from = name_ent_map[r.from_entity[0].value]
        e_to = name_ent_map[r.to_entity[0].value]
        m_rel[ent_idx_map[e_from]][ent_idx_map[e_to]] = 1

        rel_layout = arrow_layout()
        rel_layout.from_ent = e_from
        rel_layout.to_ent = e_to
        rel_layout.text = r.desc[0].value
        relation_list.append(rel_layout)

    print m_rel

    weight = [0] * ent_cnt
    for x in range(0, ent_cnt):
        for y in range(0, ent_cnt):
            weight[x] += m_rel[x][y]
            weight[y] += m_rel[x][y]

    print weight

    leveled_weight = index_list_with_level(weight)
    print "leveled weight"
    print leveled_weight

    fit_levels = []
    tmp_level = 0
    for w in leveled_weight:
        fit_levels.append(find_fit_level(len(w), slots, tmp_level))
        tmp_level = fit_levels[-1]

    print "level:"
    print fit_levels

    ret = {}
    for i in range(len(leveled_weight)):
        level_slots = slots[fit_levels[i]]
        for j in range(len(leveled_weight[i])):
            ent_idx = leveled_weight[i][j][0]
            ent = elem_dict["Entity"][ent_idx]
            slot = level_slots[j]
            r = rect_layout(slot, entity_size)
            r.ent = ent
            ret[ent.name] = r

    for k in ret:
        print ret[k].ent.name
        print ret[k].center
        print ret[k].origin

    for rl in relation_list:
        #from_layout = ret[ent_idx_map[rl.from_ent]]
        #to_layout = ret[ent_idx_map[rl.to_ent]]
        from_layout = ret[rl.from_ent.name]
        to_layout = ret[rl.to_ent.name]
        from_pnt = from_layout.get_junction_point(to_layout.center)
        to_pnt = to_layout.get_junction_point(from_layout.center)
        rl.from_point = from_pnt
        rl.to_point = to_pnt

    for k in relation_list:
        print "K in rl"
        print k.from_point
        print k.to_point

    return (ret, relation_list)

def draw_entities(entities_layouts):
    ret = ""
    for el in entities_layouts:
        l = entities_layouts[el]
        ret += ENTITY_FORMAT % (l.origin[0], l.origin[1], l.size[0], l.size[1])
    return ret

def draw_relations(relation_layouts):
    ret = ""
    for rl in relation_layouts:
        ret += RELATION_FORMAT % (rl.from_point[0], rl.from_point[1], rl.to_point[0], rl.to_point[1])
    return ret;

def index_list_with_level(l):
    d = [(i, l[i]) for i in range(len(l))]
    d = sorted(d, key=lambda i:i[1], reverse=True)
    print d
    ret = [[]]
    cur_ret = ret[0]
    for i in d:
        if len(cur_ret) > 0 and i[1] < cur_ret[0][1]:
            cur_ret = []
            ret.append(cur_ret)
        cur_ret.append(i)
        print cur_ret

    return ret

def find_fit_level(cnt, slots, from_level):
    for i in range(from_level, len(slots)):
        if cnt <= len(slots[i]):
            return i
    raise Exception("Cannot find fit level")


if __name__ == '__main__':
    main()
