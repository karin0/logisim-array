
### Usage
Insecure module `xml.etree.ElementTree` is used, so never use this against untrusted circuit files.

```python
from logisim_array import array

# Generates an array of 32 copies for every component in all circuits in reg.circ
# Occurred "$$" and "$$$" in components labels will be replaced with the index 0, 1, 2, ..., 31 of each duplicate
# Output file is written to reg-32.circ
array('reg.circ', range(32))

# Any iterable can be provided as tokens to substitute for "$$$" in labels, where "$$" still denotes its index
# File extension '.circ' is optional
array('reg', ['CLK' + str(i) for i in range(32)])

# If `enable_expression` is truthy, "${...}$" in labels will be substituted with the evaluated result of the Python expression inside
# Variable `i` and `t` denote the index and the iterated token in the inner context
# e. g. "CLK${i*4+1}$" or "CLK${t+1}$"
array('reg', range(0, 32, 4), enable_expression=True)

# Arranges the duplicates into 6 rows
# Available values for `arrange` are 'x' (as default), 'y', 'xwrap' and 'ywrap'
array('reg', range(32), arrange='xwrap')

# When `arrange` is *wrap, `wrap_count` specifies the maximum number of items placed in a single row (column if ywrap)
# When not specified, floor(sqrt(len(tokens))) is used
array('reg', range(32), 'xwrap', wrap_count=3)

# Margins are added to the unpadded circuit width/height as positional offsets between duplicates
# Both are set to 80 by default
array('reg', range(32), 'xwrap', margin_x=70, margin_y=65)

# Positional offsets can be specified directly, where margins are ignored
array('mux', range(32), 'y', offset_y=10)

# Components whose name includes keywords in `omitted_comps` are omiited when duplicating
# Refer to wires as "wire", horizontal wires as "wirex" and vertical wires as "wirey"
# Keywords are case-insensitive
array('mux', range(32), 'y', offset_y=10, omitted_comps='plex')
array('mux', range(32), 'y', offset_y=10, omitted_comps='multip demultip')
array('mux', range(32), 'y', offset_y=10, omitted_comps=['multip', 'demultip'])

# `circ_config` specifies variant parameters for circuits in a file
array('qwq', circ_config={
    'reg': {
        'tokens': range(32),
        'arrange': 'xwrap',
    },
    'wire': {
        'tokens': range(0, 32, 4),
        'arrange': 'xwrap',
    },
    'mux': {
        'tokens': range(0, 32, 3),
        'offset_y': 30,
        'omitted_comps': 'multiplexer',
        'enable_expression': True
    }
})
```
