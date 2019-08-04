# Copyright (c) 2018 Robin Jarry
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from _libyang import ffi
from _libyang import lib
from libyang import LibyangError
from .util import c2str

from .data import DataNode


DIFF_PATH_CREATED = 1
DIFF_PATH_MODIFIED = 2
DIFF_PATH_REMOVED = 3


class Differ:
    """
    Provide a diff of two objects.

    Note: the two objects must come from the same libyang context - otherwise modifies
    are not interpreted correctly. This is a shame but understandable.


    """

    def __init__(self, ctx):
        self._ctx = ctx._ctx

    def diff(self, node_a, node_b):
        if not (node_a._ctx == self._ctx and node_b._ctx == self._ctx):
            raise LibyangError('Both nodes must match the libyang context of this object instance (%s)' % (self._ctx))

        if node_a._root is None:
            raise LibyangError('Node A does not have any data - unable to diff')
        if node_b._root is None:
            raise LibyangError('Node B does not have any data - unable to diff')

        diff = lib.lyd_diff(node_a._root, node_b._root, 0)
        i = 0
        while True:
            if diff.type[i] == lib.LYD_DIFF_END:
                break

            xpath = None
            #
            if diff.type[i] == lib.LYD_DIFF_CREATED:  # 4
                newnode = lib.lypy_get_last_lyd_node(diff.second[i])
                xpath = c2str(lib.lyd_path(newnode))
                oldval = None
                newval = DataNode(self._ctx, newnode).value
                yield(xpath, oldval, newval, DIFF_PATH_CREATED)
            elif diff.type[i] == lib.LYD_DIFF_DELETED:
                oldnode = lib.lypy_get_last_lyd_node(diff.first[i])
                xpath = c2str(lib.lyd_path(oldnode))
                newval = None
                oldval = DataNode(self._ctx, oldnode).value
                yield(xpath, oldval, newval, DIFF_PATH_REMOVED)
            elif diff.type[i] == lib.LYD_DIFF_CHANGED:
                oldnode = lib.lypy_get_last_lyd_node(diff.first[i])
                newnode = lib.lypy_get_last_lyd_node(diff.second[i])
                xpath = c2str(lib.lyd_path(oldnode))
                newval = DataNode(self._ctx, newnode).value
                oldval = DataNode(self._ctx, oldnode).value
                yield(xpath, oldval, newval, DIFF_PATH_MODIFIED)
            else:
                raise ValueError('UNHANDLE DIFF TYPE', diff.type[i], i)

            i = i + 1

        lib.lyd_free_diff(diff)
    #
    # def _process_diff(self, diff_node, diff_type=0):
    #     print('PROCESS:', c2str(lib.lyd_path(lib.lypy_get_last_lyd_node(diff_node))))
    #     yield (c2str(lib.lyd_path(lib.lypy_get_last_lyd_node(diff_node))))
    #     if not diff_node.next == ffi.NULL:
    #         self._process_diff(diff_node.next)
