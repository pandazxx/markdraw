#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

class LayoutResult(object):
    """Base class for all layout objects"""
    def __init__(self):
        """init"""
        pass

    def to_svg_str(self):
        return "";

class Point(object):
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y

class Size(object):
    def __init__(self, width=-1, height=-1):
        self.width = width
        self.height = height


def make_point(*arg):
    if len(arg) == 1 and isinstance(arg[0], (tuple, list)):
        return Point(arg[0][0], arg[0][1])
    elif len(arg) > 1:
        return Point(arg[0], arg[1])
    else:
        raise Exception("Wrong argument:", arg)

def make_size(*arg):
    if len(arg) == 1 and isinstance(arg[0], (tuple, list)):
        return Size(arg[0][0], arg[0][1])
    elif len(arg) > 1:
        return Size(arg[0], arg[1])
    else:
        raise Exception("Wrong argument:", arg)

class _RectLayout(object):
    def __init__(self, center, size, svg_class=["rect"]):
        #ret = rect_layout()
        self.center = center
        self.size = size
        self.svg_class = svg_class
        self.origin = make_point(center.x - size.width/2, center.y - size.height/2)

    def get_junction_point(self, to_point):
        delta_x = to_point.x - self.center.x
        delta_y = to_point.y - self.center.y
        x_rato = abs(delta_x/self.size.width)
        y_rato = abs(delta_y/self.size.height)
        horizontal = x_rato > y_rato

        upper = make_point(self.center.x, self.center.y - self.size.height/2)
        lower = make_point(self.center.x, self.center.y + self.size.height/2)
        left = make_point(self.center.x - self.size.width/2, self.center.y)
        right = make_point(self.center.x + self.size.width/2, self.center.y)

        if delta_x > 0 and delta_y > 0:
            return right if horizontal else lower
        elif delta_x > 0 and delta_y < 0:
            return right if horizontal else upper
        elif delta_x < 0 and delta_y > 0:
            return left if horizontal else lower
        elif delta_x < 0 and delta_y < 0:
            return left if horizontal else upper

    def to_svg_str(self):
        ENTITY_FORMAT = '''
        <rect x="%d" y="%d" rx="20" ry="20" width="%d" height="%d" class="%s" />
        '''
        return ENTITY_FORMAT % (self.origin.x, self.origin.y, self.size.width, self.size.height, " ".join(self.svg_class))


class _ArrowLayout(LayoutResult):
    """Layout result for arrow type"""
    def __init__(self, from_point=None, to_point=None):
        """init"""
        self.from_point, self.to_point = (from_point, to_point)

    def to_svg_str(self):
        RELATION_FORMAT = '''
            <line x1="%d" y1="%d" x2="%d" y2="%d" style="stroke:rgb(255,0,0);stroke-width:2" />
        '''
        return RELATION_FORMAT % (self.from_point.x, self.from_point.y, self.to_point.x, self.to_point.y)

def slot_layout(parse_result_dict):
    canvas_size = (500, 500)
    slots = [
        [(250, 250)],
        [(100, 100), (400, 100), (100, 400), (400, 400)],
    ]
    entity_size = (100, 100)
    slots_cnt = 0
    for i in slots:
        slots_cnt = slots_cnt + len(i)

    all_entities = parse_result_dict["Entity"]

    entity_cnt = len(all_entities)
    if entity_cnt > slots_cnt:
        raise Exception("Only support up to %d entities. %d entities is provided" % (slots_cnt, entity_cnt))

    rel_matrix = [[0] * entity_cnt for _ in range(0, entity_cnt)]


    dict_entity_index = {}
    dict_name_entity = {}
    for i in range(entity_cnt):
        e = all_entities[i]
        dict_entity_index[e] = i
        dict_name_entity[e.name] = e

    rel_layouts = []
    for r in parse_result_dict["Relation"]:
        print r.__dict__
        e_from = dict_name_entity[r.from_entity]
        e_to = dict_name_entity[r.to_entity]
        rel_matrix[dict_entity_index[e_from]][dict_entity_index[e_to]] += 1

        rel_layout = _ArrowLayout()
        rel_layout.from_entity = e_from
        rel_layout.to_entity = e_to
        rel_layout.text = r.desc
        rel_layouts.append(rel_layout)

    logger.debug("Relation matrix:\n" + str(rel_matrix))

    #calc weights
    weight_of_entities = [0] * entity_cnt
    for x in range(entity_cnt):
        for y in range(entity_cnt):
            weight_of_entities[x] += rel_matrix[x][y]
            weight_of_entities[y] += rel_matrix[x][y]

    logger.debug("Weights:" + str(weight_of_entities))

    levels_of_weight_of_ents = _index_list_with_level(weight_of_entities)
    logger.debug("Leveled weights" + str(levels_of_weight_of_ents))

    fit_levels = []
    tmp_level = 0
    for w in levels_of_weight_of_ents:
        fit_levels.append(_find_fit_level(len(w), slots, tmp_level))
        tmp_level = fit_levels[-1]

    entity_layouts = {}
    for i in range(len(levels_of_weight_of_ents)):
        matched_slots = slots[fit_levels[i]]
        for j in range(len(levels_of_weight_of_ents[i])):
            ent_idx = levels_of_weight_of_ents[i][j][0]
            ent = all_entities[ent_idx]
            slot = matched_slots[j]
            r = _RectLayout(make_point(slot), make_size(entity_size))
            r.entity = ent
            entity_layouts[ent.name] = r

    for i in entity_layouts:
        logger.debug(entity_layouts[i].entity.name)
        logger.debug(entity_layouts[i].center)
        logger.debug(entity_layouts[i].size)

    for rl in rel_layouts:
        from_ent_layout = entity_layouts[rl.from_entity.name]
        to_ent_layout = entity_layouts[rl.to_entity.name]
        from_pnt = from_ent_layout.get_junction_point(to_ent_layout.center)
        to_pnt = to_ent_layout.get_junction_point(from_ent_layout.center)
        rl.from_point = from_pnt
        rl.to_point = to_pnt

    return entity_layouts.values() + rel_layouts

def _index_list_with_level(l):
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

def _find_fit_level(cnt, slots, from_level):
    for i in range(from_level, len(slots)):
        if cnt <= len(slots[i]):
            return i
    raise Exception("Cannot find fit level")
