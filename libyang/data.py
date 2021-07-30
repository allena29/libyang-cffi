# Copyright (c) 2019 Robin Jarry
# SPDX-License-Identifier: MIT

from _libyang import ffi
from _libyang import lib

from .schema import Node
from .util import c2str
from .util import str2c
from .util import LibyangError


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

    BOOL_TYPES = (lib.LY_TYPE_BOOL,)

    DECIMAL_TYPES = (lib.LY_TYPE_DEC64,)

    EMPTY_TYPES = (lib.LY_TYPE_EMPTY,)

    def __init__(self, context, lyd_node):
        self.value = self._get_value_from_lyd_node(lyd_node)
        self.name = c2str(lyd_node.schema.name)
        self.xpath = c2str(ffi.gc(lib.lyd_path(lyd_node), lib.free))
        self.lyd_node = lyd_node
        self.context = context

    def get_root(self):
        return DataNode(self.context, lib.lypy_get_root_node(self.lyd_node))

    def parent(self):
        if self.lyd_node.parent == ffi.NULL:
            raise LibyangError(
                "cannot use parent() to go above a root node %s" % (self.xpath)
            )
        return DataNode(self.context, self.lyd_node.parent)

    def get_schema(self):
        return Node.new(self.context, self.lyd_node.schema)
    
    def get_schema_path(self):
        return Node(self.context, self.lyd_node.schema).schema_path()
   
    def get_list_key_values(self, data_node=None):
        if data_node:
            lyd_node = data_node.lyd_node
            xpath = data_node.xpath
        else:
            lyd_node = self.lyd_node
            xpath = self.xpath
        if lyd_node.schema.nodetype != lib.LYS_LIST:
            raise LibyangError("cannot extract list keys from non-list node")

        lyd_list_node = ffi.cast('struct lys_node_list *', lyd_node.schema)
        for i in range(lyd_list_node.keys_size):
            list_key = c2str(ffi.cast('struct lys_node *', lyd_list_node.keys[i]).name)
            node_set = ffi.gc(lib.lyd_find_path(lyd_node, str2c(xpath+"/"+list_key)), lib.ly_set_free)
            if node_set == ffi.NULL:
                raise LibyangError('Inconsistent data-tree - list-key does not exist in the data tree')
            list_val = self._get_value_from_lyd_node(node_set.set.d[0])
            yield list_key, list_val

    def get_all_list_key_values(self):
        result = []
        lyd_node = self.lyd_node
        while lyd_node != ffi.NULL:
            if lyd_node.schema.nodetype == lib.LYS_LIST:
                result.append(self.get_list_key_values(DataNode(self.context, lyd_node)))
            lyd_node = lyd_node.parent
        
        result.reverse()
        for r in result:
            yield from r
    
    def get_all_node_names(self):
        result = []
        lyd_node = self.lyd_node
        while lyd_node != ffi.NULL:
            result.append(c2str(lyd_node.schema.name))
            lyd_node = lyd_node.parent

        result.reverse()
        for r in result:
            yield r
    
    @staticmethod
    def convert_python_value(value):
        if isinstance(value, bool):
            if value is True:
                return str2c("true")
            return str2c("false")

        if value is None:
            return ffi.NULL

        return str2c(str(value))

    @staticmethod
    def _get_value_from_lyd_node(lyd_node):
        """
        When data is set /got from a lyd_node things come back as strings instead of
        their proper types.

        This method gets the value from a lyd_node and converts it to proper python
        types.
        """
        if lyd_node.schema.nodetype in (lib.LYS_LEAF, lib.LYS_LEAFLIST):
            leaf = ffi.cast("struct lyd_node_leaf_list *", lyd_node)
            sleaf = ffi.cast("struct lys_node_leaf *", lyd_node.schema)
            type = ffi.addressof(sleaf.type).base
            if type in DataNode.INT_TYPES:
                return int(c2str(leaf.value_str))
            elif type in DataNode.BOOL_TYPES:
                if c2str(leaf.value_str) == "true":
                    return True
                return False
            elif type in DataNode.DECIMAL_TYPES:
                return float(c2str(leaf.value_str))
            elif type in DataNode.EMPTY_TYPES:
                return ""
            return c2str(leaf.value_str)

        if lyd_node.schema.nodetype == lib.LYS_LIST:
            return ""

        if lyd_node.schema.nodetype == lib.LYS_CONTAINER:
            return ""

        return None

    def __str__(self):
        if not self.xpath:
            return "/"
        return self.xpath

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s: %s>" % (cls.__module__, cls.__name__, str(self))

    @staticmethod
    def _find_nodes(context, start_node, base_schema_path):
        node = start_node
        while 1:
            if node.schema.nodetype in (1, 4, 8):  # LEAF or LEAF_LIST
                xpath = c2str(ffi.gc(lib.lyd_path(node), lib.free))
                if base_schema_path:
                    if c2str(ffi.gc(lib.lys_path(node.schema, 0), lib.free)).startswith(base_schema_path):
                        yield DataNode(context, node)
                else:
                    yield DataNode(context, node)

            if node.schema.nodetype not in (4, 8):  # LEAF or LEAF_LIST
                if not node.child == ffi.NULL:
                    if base_schema_path:
                        if c2str(ffi.gc(lib.lys_path(node.child.schema, 0), lib.free)).startswith(base_schema_path):
                            yield from DataNode._find_nodes(context, node.child, base_schema_path)
                    else:
                        yield from DataNode._find_nodes(context, node.child, base_schema_path)

            if node.next == ffi.NULL:
                break

            node = node.next
