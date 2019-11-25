# Copyright (c) 2019 Robin Jarry
# SPDX-License-Identifier: MIT

from _libyang import ffi
from _libyang import lib

from .schema import Node
from .util import c2str
from .util import str2c


class DataNode(object):

    INT_TYPES = (
        lib.LY_TYPE_INT8,
        lib.LY_TYPE_INT16,
        lib.LY_TYPE_INT32,
        lib.LY_TYPE_INT64,
        lib.LY_TYPE_UINT8,
        lib.LY_TYPE_UINT16,
        lib.LY_TYPE_UINT32,
        lib.LY_TYPE_UINT64,
    )

    BOOL_TYPES = (
        lib.LY_TYPE_BOOL,
    )

    DECIMAL_TYPES = (
        lib.LY_TYPE_DEC64,
    )

    EMPTY_TYPES = (
        lib.LY_TYPE_EMPTY,
    )

    def __init__(self, context, lyd_node, xpath=None):
        self.value = self._get_value_from_lyd_node(lyd_node, xpath)
        self.xpath = xpath
        self.lyd_node = lyd_node
        self.context = context

    def get_root(self):
        return DataNode(self.context, lib.lypy_get_root_node(self.lyd_node))

    def get_schema(self):
        return Node(self.context, self.lyd_node.schema)

    @staticmethod
    def convert_python_value(value):
        if isinstance(value, bool):
            if value is True:
                return str2c('true')
            return str2c('false')

        if value is None:
            return ffi.NULL

        return str2c(str(value))

    @staticmethod
    def _get_value_from_lyd_node(lyd_node, xpath=None):
        """
        When data is set /got from a lyd_node things come back as strings instead of
        their proper types.

        This method gets the value from a lyd_node and converts it to proper python
        types.
        """
        if lyd_node.schema.nodetype in (lib.LYS_LEAF, lib.LYS_LEAFLIST):
            leaf = ffi.cast('struct lyd_node_leaf_list *', lyd_node)
            sleaf = ffi.cast('struct lys_node_leaf *', lyd_node.schema)
            type = ffi.addressof(sleaf.type).base
            if type in DataNode.INT_TYPES:
                return int(c2str(leaf.value_str))
            elif type in DataNode.BOOL_TYPES:
                if c2str(leaf.value_str) == 'true':
                    return True
                return False
            elif type in DataNode.DECIMAL_TYPES:
                return float(c2str(leaf.value_str))
            elif type in DataNode.EMPTY_TYPES:
                return True
            return c2str(leaf.value_str)

        if lyd_node.schema.nodetype == lib.LYS_LIST:
            return True

        if lyd_node.schema.nodetype == lib.LYS_CONTAINER:
            return True

        return None

    def __str__(self):
        if not self.xpath:
            return '/'
        return self.xpath

    def __repr__(self):
        cls = self.__class__
        return '<%s.%s: %s>' % (cls.__module__, cls.__name__, str(self))

    def dump_datanodes(self):
        # This is suboptimal at present - want to move this down to C or
        # avoid the extra funaction call.
        nodelist = {}
        start_node = self.lyd_node

        DataNode._find_nodes(self.context, nodelist, start_node)

        sorted_keys = list(nodelist.keys())
        sorted_keys.sort()

        for key in sorted_keys:
            yield nodelist[key]

    @staticmethod
    def _find_nodes(context, nodelist, start_node):
        node = start_node
        while 1:
            if node.schema.nodetype in (1, 4, 8):    # LEAF or LEAF_LIST
                xpath = c2str(lib.lyd_path(node))
                nodelist[xpath] = DataNode(context, node, xpath)

            if node.schema.nodetype not in (4, 8):    # LEAF or LEAF_LIST
                if not node.child == ffi.NULL:
                    DataNode._find_nodes(context, nodelist, node.child)

            if node.next == ffi.NULL:
                break

            node = node.next
