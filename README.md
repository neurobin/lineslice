[![Build Status](https://travis-ci.org/neurobin/rcslice.svg?branch=release)](https://travis-ci.org/neurobin/rcslice)


This package provides Python module to slice a list of sliceables (1 indexed, both start and end index are inclusive). Helps to slice file content line by line or column by column or a combination of both.

# Install

Install from Pypi:

```bash
pip install rcslice
```

# Usage

```python
from rcslice import RowSlice

rs = RowSlice()

list_of_sliceables = rs.slice(list_of_sliceables, '1-2,2.4-4.5,8-2.6')

```

# Slicing syntax

Below, r is the row number, and c is the column number. All indexes are inclusive and 1 indexed.

    r.c-r.c
    r.c-r.c,r.c-r.c,...
    .c-.c       [not specifying both r means slice on every row for the columns]
    1.c-.c      [not specifying r means the last row when another r is specified]
    .c-1        [last row.c to first row, reversion]
    r           [only r'th row]
    r1-r2       [when both r is not the same, not specifying c means the first c for start index and last c for end index]
    r1-r2.c     [first c of r1 to r2.c]
    r1.c-r2     [r1.c to last c of r2]
    r-r.c       [when both r is the same, not specifying one c will mean the last c]
    r-r         [when both r is the same, not specifying both c means the first c for start index and last c for end index]
    e.c-e.c     [e means last row]
    e-e         [last row]
    e-e.c       [last c of e to e.c]
    e.c-e       [e.c to last c of e]
    e.e-e.e     [same as e-e, e in column is stripped off]
    
The e to specify the last row is exclusively for row only. Do keep in mind that the class name is RowSlice. It gives special priority on row and not just with the special character e. You will see some major difference in how r and c works in above syntax explanation.

For multiple slice syntax `r.c-r.c,r.c-r.c,...`, a separator will be inserted between each slice. You can set the separator by passing it during class object instantiation:

```python
rs = RowSlice(['I am a separator'])
```

This separator is essentially a list of sliceables.


# Examples

An example of slicing a file content read by `readlines()`:

```python

import os
from rcslice import RowSlice

def get_file_lines(filename):
    content = []
    try:
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
            content = f.readlines()
    except OSError as e:
        raise
    return content


rs = RowSlice(['','']) # ['',''] will add 2 new lines for multi slice syntax (e.g 1-2,3-4,...)

list_of_lines = get_file_lines('test.txt')

print("before: ", list_of_lines)

list_of_lines = rs.slice(list_of_lines, '1-2,1.2-4.5,3.4-1.3,.4-.9')

print("after: ", list_of_lines)

```
