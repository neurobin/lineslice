"""
==================================================================
                    rcslice module
==================================================================

See <https://github.com/neurobin/rcslice> for documentation.

Copyright Md. Jahidul Hamid <jahidulhamid@yahoo.com>

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)
"""

from .version import __version__

class RowSlice(object):
    """Class to provide slicing methods for row column slice for a list of sliceables.    
    """
    
    def __init__(self, row_slice_separator=[]):
        """
        
        Parameters
        ----------
        
        row_slice_separator    A list of entities that will be inserted between two adjacent single operation slice (e.g between 2-3 and 4-5 in 2-3,4-5 slice syntax)
        
        """
        self.row_slice_separator = row_slice_separator
        self.__common_value_error_format = "Unknown row/column number/range (%s) passed in row slice syntax %s"

    def get_zero_index_from_one_index(self, idx):
        """Convert 1 index to zero index"""
        if idx is not None:
            idx = idx - 1
            if idx < 0:
                idx = None
        return idx
    
    def get_two_less_index(self, idx):
        """subtract 2 from index """
        column_sliceable = None
        if idx is not None:
            idx = idx - 2
            if idx < 0:
                idx = None
                column_sliceable = False
        return idx, column_sliceable
    
    def parse_slice_string(self, slice_string):
        """Parse slice string and return a list of lists.
        
        Below, r is the row number, and c is the column number. All indexes are inclusive and 1 indexed.
        
        Slice string syntax:
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
        
        Returned List format:

            [
                [[start.r, start.c], [end.r, end.c], [rstep, cstep, column_sliceable]]
            ]
            
            column_sliceable is generally None, when it's False, it means column-slice-only should not be done.
        
        """
        def get_lns_or_lne(n):
            """The returned list (format: [r c]) have exactly 2 elements"""
            if n:
                lns = n.split('.')
            else:
                return [None, None]
            if len(lns) > 2:
                raise ValueError(self.__common_value_error_format % (n, slice_string,))
            lns = [int(x) if x else None for x in lns]
            for i in lns:
                if i is not None and i <= 0:
                    raise ValueError("Row/Column number/range can not be <= 0. Detected %s in row slice syntax %s" % (n, slice_string,))
            if len(lns) == 1:
                lns.append(None)
            elif len(lns) <= 0:
                raise ValueError(self.__common_value_error_format % (n, slice_string,))
            return lns
        
        ll = []
        for r in slice_string.split(','):
            if r:
                l = r.split('-')
                if len(l) > 2:
                    raise ValueError(self.__common_value_error_format % (r, slice_string,))
                l = [x if x else None for x in l]
                if len(l) == 1:
                    lns = get_lns_or_lne(l[0])
                    lne = [lns[0], None]
                    step = [1, 1, None]
                    lns = [self.get_zero_index_from_one_index(x) for x in lns]
                    # end index is exclusive, we don't need to do -1
                    # because end index is inclusive for us
                    ll.append([lns, lne, step])
                elif len(l) == 2:
                    lns = get_lns_or_lne(l[0])
                    lne = get_lns_or_lne(l[1])
                    
                    lstep = 1 if lne[0] is None or (lns[0] is not None and lns[0] <= lne[0]) else -1
                    cstep = 1 if lne[1] is None or (lns[1] is not None and lns[1] <= lne[1]) else -1
                    
                    lns = [self.get_zero_index_from_one_index(x) for x in lns]
                    # end index is exclusive, we don't need to do -1
                    # because end index is inclusive for us
                    column_sliceable = None
                    if lstep < 0:
                        # negative step, we need to do -2 for end index
                        lne[0], column_sliceable = self.get_two_less_index(lne[0])
                    
                    # we can not do this properly here, final slicing method can do it properly
                    # ~ if cstep < 0:
                        # ~ # negative step, we need to do -2 for end index
                        # ~ lne[1], column_slicebale = self.get_two_less_index(lne[1])
                        
                    ll.append([lns, lne, [lstep, cstep, column_sliceable]])
                else:
                    raise ValueError(self.__common_value_error_format % (r, slice_string,))
        return ll
        
    def slice_list_of_sliceables(self, sliceables, slice_string):
        """Take slices of sliceables by slice string (e.g 1,1-4,1.2-4.7,7.8-1.5 etc.)
        """
        e = len(sliceables)
        if e > 0 and slice_string:
            # convert e to end index
            slice_string = slice_string.replace('.e', '.')
            slice_string = slice_string.replace('e', '{}'.format(e))
            sidxs = self.parse_slice_string(slice_string)
            c = 0
            new_sliceables = []
            for sidx in sidxs:
                # sidx is of the format: [[start.l, start.c], [end.l, end.c], [lstep, cstep]]
                start = sidx[0]
                end = sidx[1]
                step = sidx[2]
                if c > 0:
                    new_sliceables.extend(self.row_slice_separator)
                c = c + 1
                now_slice = sliceables[start[0]:end[0]:step[0]]
                cstep = step[1]
                if now_slice:
                    if len(now_slice) == 1:
                        if cstep < 0:
                            # negative step, we need to do -2 for end index
                            end[1], column_sliceable = self.get_two_less_index(end[1])
                        now_slice[0] = now_slice[0][start[1]:end[1]:cstep]
                    else:
                        if start[0] is None and end[0] is None and step[2] is not False:
                            if cstep < 0:
                                # negative step, we need to do -2 for end index
                                end[1], column_sliceable = self.get_two_less_index(end[1])
                            for i in range(len(now_slice)):
                                now_slice[i] = now_slice[i][start[1]:end[1]:cstep]
                        else:
                            now_slice[0] = now_slice[0][start[1]:]
                            now_slice[-1] = now_slice[-1][:end[1]]
                new_sliceables.extend(now_slice)
            
            return new_sliceables if sidxs else sliceables
        else: return sliceables

