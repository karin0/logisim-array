import re
import xml.etree.ElementTree as ET
from os.path import splitext
from copy import deepcopy

__all__ = ['array']

def loc_parse(loc):
    return tuple(map(int, loc[1:-1].split(',')))

def loc_shift(loc, x, y):
    ox, oy = loc_parse(loc)
    return f'({ox + x},{oy + y})'

reg = re.compile(r'\$\{(.+?)\}\$')
def parse(value, i, t, enable_expression):
    value = value.replace('$$$', str(t)).replace('$$', str(i))
    if not enable_expression:
        return value

    def repl(_m):
        if id(t) + i < 0: # to catch them
            print('QAQ')
        return str(eval(_m[1]))
    return reg.sub(repl, value)

loc_attrs = frozenset(['loc', 'from', 'to'])
def get_copy(comp, index, token, xoff, yoff, enable_expression):
    comp = deepcopy(comp)
    for e in comp.iter():
        for k, v in e.attrib.items():
            if k in loc_attrs:
                e.set(k, loc_shift(v, xoff, yoff))
            else:
                e.set(k, parse(v, index, token, enable_expression))
    return comp

def wire_vert(wire):
    ax, _ = loc_parse(wire.get('from'))
    bx, _ = loc_parse(wire.get('to'))
    return ax == bx
wire_horiz = lambda wire: not wire_vert(wire)

def find_wires(circ, omitted_comps):
    if 'wire' in omitted_comps:
        return []

    skip_x = 'wirex' in omitted_comps
    skip_y = 'wirey' in omitted_comps
    if skip_x and skip_y:
        return []

    wires = circ.findall('wire')
    if skip_x:
        return list(filter(wire_vert, wires))
    if skip_y:
        return list(filter(wire_horiz, wires))
    return wires

def decomum(f):
    return lambda p: p[1] if p[0] is None else f(*p)

def array_circ(circ, tokens, arrange,
    offset_x, offset_y,
    margin_x, margin_y,
    wrap_count, omitted_comps,
    enable_expression):

    tokens = range(1) if tokens is None else list(tokens)
    if omitted_comps:
        if isinstance(omitted_comps, str):
            omitted_comps = omitted_comps.split()
        omitted_comps = [s.lower() for s in omitted_comps]
    else:
        omitted_comps = []

    def comp_check(comp):
        name = comp.get('name')
        if not name:
            return True
        name = name.lower()
        return not any(key in name for key in omitted_comps)

    comps = list(filter(comp_check, circ.findall('comp'))) + find_wires(circ, omitted_comps)
    for comp in comps:
        circ.remove(comp)

    if not (offset_x and offset_y):
        xmin = ymin = xmax = ymax = None
        for comp in comps:
            for e in comp.iter():
                for attr in loc_attrs:
                    if loc := e.get(attr):
                        x, y = loc_parse(loc)
                        xmin, ymin = map(decomum(min), ((xmin, x), (ymin, y)))
                        xmax, ymax = map(decomum(max), ((xmax, x), (ymax, y)))
        if offset_x is None:
            offset_x = xmax - xmin + margin_x

        if offset_y is None:
            offset_y = ymax - ymin + margin_y

    for index, token in enumerate(tokens):
        if arrange == 'x':
            x = index
            y = 0
        elif arrange == 'y':
            x = 0
            y = index
        else:
            if wrap_count is None:
                wrap_count = max(1, int(len(tokens) ** 0.5))
            if arrange == 'xwrap':
                x = index % wrap_count
                y = index // wrap_count
            elif arrange == 'ywrap':
                x = index // wrap_count
                y = index % wrap_count
            else:
                raise ValueError(f'arrange: {arrange}')

        x *= offset_x
        y *= offset_y
        for comp in comps:
            circ.append(get_copy(comp, index, token, x, y, enable_expression))

def array(fn, tokens=None, arrange='x',
    offset_x=None, offset_y=None,
    margin_x=80, margin_y=80,
    wrap_count=None, omitted_comps=None,
    enable_expression=False,
    circ_config=None):

    common_conf = locals()
    del common_conf['fn'], common_conf['circ_config']

    base, ext = splitext(fn)
    if not ext:
        fn = base + (ext := '.circ')
    tree = ET.parse(fn)
    root = tree.getroot()
    circs = root.findall('circuit')

    if circ_config is None:
        suf = str(1 if tokens is None else len(tokens))
        for circ in circs:
            array_circ(**common_conf)
    else:
        suf = []
        for circ in circs:
            name = circ.get('name')
            if name and (conf := circ_config.get(name)) is not None:
                suf.append(name)
                array_circ(**dict(common_conf, circ=circ, **conf))
        suf = '-'.join(suf)

    tree.write(base + '-' + suf + ext)
