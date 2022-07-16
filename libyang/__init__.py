# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT
import gc
import logging
import os

from _libyang import ffi
from _libyang import lib

from .data import DataNode
from .schema import Module
from .schema import Node
from .util import (
    LibyangError,
    InvalidSchemaOrValueError,
    DataXpathDoesNotExistError,
    DataXpathResultsInMultipleResultsError,
    DataTreeExistsError,
    DataTreeEmptyError,
    LibyangMarshallingError,
    AttributeCannotBeSetError,
)
from .util import c2str
from .util import str2c


# ------------------------------------------------------------------------------
class Context(object):
    def __init__(self, search_path=None, options=lib.LY_CTX_DISABLE_SEARCHDIR_CWD):
        self._data_tree = []
        self._ctx = ffi.gc(lib.ly_ctx_new(ffi.NULL, options), self.destroy)

        if not self._ctx:
            raise self.error("cannot create context")

        search_dirs = []
        if "YANGPATH" in os.environ:
            search_dirs.extend(os.environ["YANGPATH"].strip(": \t\r\n'\"").split(":"))
        elif "YANG_MODPATH" in os.environ:
            search_dirs.extend(
                os.environ["YANG_MODPATH"].strip(": \t\r\n'\"").split(":")
            )
        if search_path:
            search_dirs.extend(search_path.strip(": \t\r\n'\"").split(":"))

        for path in search_dirs:
            if not os.path.isdir(path):
                continue
            if lib.ly_ctx_set_searchdir(self._ctx, str2c(path)) != 0:
                raise self.error("cannot set search dir")

    def destroy(self, c):
        for data_tree in self._data_tree:
            lib.lyd_free_withsiblings(data_tree)
        if self._ctx is not None:
            lib.ly_ctx_destroy(c, ffi.NULL)
            self._ctx = None
        gc.collect()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.destroy()

    def error(self, msg, *args):
        if not self._ctx:
            msg %= args
            return LibyangError(msg)

        errors = []
        try:
            err = lib.ly_err_first(self._ctx)
            while err:
                e = []
                if err.path:
                    e.append(c2str(err.path))
                if err.msg:
                    e.append(c2str(err.msg))
                if err.apptag:
                    e.append(c2str(err.apptag))
                if e:
                    errors.append(": ".join(e))
                err = err.next
        finally:
            lib.ly_err_clean(self._ctx, ffi.NULL)

        msg %= args
        if errors:
            msg += ": " + " ".join(errors)

        return LibyangError(msg)

    def load_module(self, name):
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        mod = lib.ly_ctx_load_module(self._ctx, str2c(name), ffi.NULL)
        if not mod:
            raise self.error("cannot load module")

        return Module(self, mod)

    def get_module(self, name):
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        mod = lib.ly_ctx_get_module(self._ctx, str2c(name), ffi.NULL, False)
        if not mod:
            raise self.error("cannot get module")

        return Module(self, mod)

    def find_path(self, path):
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        node_set = ffi.gc(lib.ly_ctx_find_path(self._ctx, str2c(path)), lib.ly_set_free)
        if not node_set:
            raise self.error("cannot find path")

        for i in range(node_set.number):
            yield Node.new(self, node_set.set.s[i])

    def __iter__(self):
        """
        Return an iterator that yields all implemented modules from the context
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        idx = ffi.new("uint32_t *")
        mod = lib.ly_ctx_get_module_iter(self._ctx, idx)
        while mod:
            yield Module(self, mod)
            mod = lib.ly_ctx_get_module_iter(self._ctx, idx)


# ------------------------------------------------------------------------------


class DataTree:

    """
    Manage a libyang data tree in memory, which can then later be seralised
    into XML/JSON with libyang itself.

    As elements of data are set they will be validated against the schema of
    that particular node.

    At the time this fork was taken there was little in the way of DataTree
    upstream in robin jarry's project, which itself has moved across to the
    main libyang repo. Ultimately this project needs to contribute back there.
    """

    def __init__(self, ctx):
        self._ctx = ctx
        self._lyctx = ctx._ctx
        self._root = None

    def error(self, msg, *args, exception_type=LibyangMarshallingError):
        if not self._lyctx:
            return LibyangError(msg)

        errors = []
        try:
            err = lib.ly_err_first(self._lyctx)
            while err:
                e = []
                if err.path:
                    e.append(c2str(err.path))
                if err.msg:
                    e.append(c2str(err.msg))
                if err.apptag:
                    e.append(c2str(err.apptag))
                if e:
                    errors.append(": ".join(e))
                err = err.next
        finally:
            lib.ly_err_clean(self._lyctx, ffi.NULL)

        if errors:
            msg += ": " + " ".join(errors)

        return exception_type(msg, *args)

    def set_xpath(self, xpath, value):
        """
        Set a value by XPAH - with siblings/dependent nodes getting created.

        If the path already exists with the same value (no data change0 then lyd_new_path
        will return NULL.
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")

        libyang_value = DataNode.convert_python_value(value)

        if self._root is None:
            node = lib.lyd_new_path(
                ffi.NULL,
                self._lyctx,
                str2c(xpath),
                libyang_value,
                0,
                lib.LYD_PATH_OPT_UPDATE,
            )
            if not node:
                raise InvalidSchemaOrValueError(value, xpath)
            self._root = node
            self._ctx._data_tree.append(self._root)
        else:
            node = lib.lyd_new_path(
                self._root,
                ffi.NULL,
                str2c(xpath),
                libyang_value,
                0,
                lib.LYD_PATH_OPT_UPDATE,
            )

        if not node:
            node_set = ffi.gc(
                lib.lyd_find_path(self._root, str2c(xpath)), lib.ly_set_free
            )
            if node_set.number == 0:
                raise InvalidSchemaOrValueError(value, xpath)

    def remove_attribute(
        self,
        xpath: str,
        attribute_name: str,
        attribute_value: str = None,
    ) -> bool:
        """
        Delete an attribute

        Attributes:
            xpath: the xpath to an existing data node
            attribute_name: the name of the attribute (e.g. operation)
            attribute_value: the value of the attribute (e.g. replace) - optional

        Returns:
            True if the attribute was removed
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        data_nodes = list(self.get_xpath(xpath))
        if len(data_nodes) < 1:
            raise DataXpathDoesNotExistError(xpath)
        if len(data_nodes) > 1:
            raise DataXpathResultsInMultipleResultsError(xpath, len(data_nodes))

        attr = data_nodes[0].lyd_node.attr
        while attr != ffi.NULL:
            if c2str(attr.name) == attribute_name:
                if not attribute_value or attribute_value == c2str(attr.value_str):
                    if lib.lyd_free_attr(self._lyctx, data_nodes[0].lyd_node, attr, 0):
                        return True
                    else:
                        break
            attr = attr.next
        return False

    def insert_attribute(
        self, xpath: str, module: str, attribute_name: str, attribute_value: str
    ) -> bool:
        """
        Insert an attribute:

        Attributes:
            xpath: the xpath to an existing data node
            module: may be a python None if the attribute belongs to the same module-
                    otherwise the prefix of the module (e.g. ietf-netconf)
            attribute_name: the name of the attribute (e.g. operation)
            attribute_value: the value of the attribute (e.g. replace)

        Returns:
            True if the attribute was succesfully set.
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        data_nodes = list(self.get_xpath(xpath))
        if len(data_nodes) < 1:
            raise DataXpathDoesNotExistError(xpath)
        if len(data_nodes) > 1:
            raise DataXpathResultsInMultipleResultsError(xpath, len(data_nodes))

        if module:
            if lib.lyd_insert_attr(
                data_nodes[0].lyd_node,
                ffi.NULL,
                str2c(f"{module}:{attribute_name}"),
                str2c(attribute_value),
            ):
                return True
        if lib.lyd_insert_attr(
            data_nodes[0].lyd_node,
            ffi.NULL,
            str2c(attribute_name),
            str2c(attribute_value),
        ):
            return True
        raise AttributeCannotBeSetError(xpath, module, attribute_name, attribute_value)

    def get_xpath(self, xpath):
        """
        Get the value at XPATH - returns a generator
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        if self._root is not None:
            node_set = ffi.gc(
                lib.lyd_find_path(self._root, str2c(xpath)), lib.ly_set_free
            )
            if node_set == ffi.NULL:
                yield None

            for i in range(node_set.number):
                yield DataNode(self, node_set.set.d[i])

    def gets_xpath(self, xpath):
        """
        Get the XPATH of each list element wtithin the list - returns a generator
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        if self._root is not None:
            node_set = ffi.gc(
                lib.lyd_find_path(self._root, str2c(xpath)), lib.ly_set_free
            )
            if node_set == ffi.NULL:
                yield []
            else:
                for i in range(node_set.number):
                    yield c2str(ffi.gc(lib.lyd_path(node_set.set.d[i]), lib.free))

    def delete_xpath(self, xpath):
        """
        Delete the value at XPATH
        """
        if self._root is None:
            return
        if not self._ctx:
            raise RuntimeError("context already destroyed")

        node_set = ffi.gc(lib.lyd_find_path(self._root, str2c(xpath)), lib.ly_set_free)
        if node_set == ffi.NULL:
            return

        for i in range(node_set.number):
            result = lib.lyd_unlink(node_set.set.d[i])
            if result:
                raise LibyangError("Unable to delete xpath: %s" % (xpath))

    def count_xpath(self, xpath):
        """
        Count results for a given XPATH
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        if self._root is None:
            return 0

        node_set = ffi.gc(lib.lyd_find_path(self._root, str2c(xpath)), lib.ly_set_free)
        if node_set == ffi.NULL:
            return 0
        return int(node_set.number)

    def dump(self, filename, format=lib.LYD_XML):
        """
        Dump to a file with the specified format
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        with open(filename, "w") as fh:
            lib.lyd_print_file(fh, self._root, format, lib.LYP_WITHSIBLINGS)

    def load(self, filename, format=lib.LYD_XML, trusted=False, strict=True):
        """
        Load from a file with the specified format
        # TODO:  what about freeing an initial root if one exists
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        option = lib.LYD_OPT_CONFIG
        if strict:
            option = option | lib.LYD_OPT_STRICT
        if trusted:
            option = option | lib.LYD_OPT_TRUSTED
        if self._root:
            raise DataTreeExistsError(
                (
                    "load() not supported when data is already set - because the old node will not be freed\n"
                    "use merge() instead."
                )
            )
        self._root = lib.lyd_parse_path(self._lyctx, str2c(filename), format, option)
        if self._root == ffi.NULL:
            raise self.error("Marshalling Error", format)
        self._ctx._data_tree.append(self._root)

    def loads(self, payload, format=lib.LYD_XML, trusted=False, strict=True):
        """
        Load from a string with the specified format
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        option = lib.LYD_OPT_CONFIG
        if strict:
            option = option | lib.LYD_OPT_STRICT
        if trusted:
            option = option | lib.LYD_OPT_TRUSTED
        if self._root:
            raise DataTreeExistsError(
                (
                    "loads() not supported when data is already set - because the old node will not be freed\n"
                    "use merges() instead"
                )
            )

        self._root = lib.lyd_parse_mem(self._lyctx, str2c(payload), format, option)
        if self._root == ffi.NULL:
            raise self.error("Marshalling Error", format)
        self._ctx._data_tree.append(self._root)

    def merge(self, filename, format=lib.LYD_XML, trusted=True, strict=True):
        """
        Merge from a file with the specified format
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        option = lib.LYD_OPT_CONFIG
        if strict:
            option = option | lib.LYD_OPT_STRICT
        if trusted:
            option = option | lib.LYD_OPT_TRUSTED
        if not self._root:
            raise DataTreeEmptyError(
                "merges() not possible until data exists on the root object."
            )

        tmp = lib.lyd_parse_path(self._lyctx, str2c(filename), format, option)
        if tmp == ffi.NULL:
            raise self.error("Marshalling Merge Error", format)

        if not lib.lyd_merge(self._root, tmp, lib.LYD_OPT_EXPLICIT) == 0:
            raise self.error("Merge Error")

    def merges(self, payload, format=lib.LYD_XML, trusted=True, strict=True):
        """
        Merge from a string with the specified format
        """
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        option = lib.LYD_OPT_CONFIG
        if strict:
            option = option | lib.LYD_OPT_STRICT
        if trusted:
            option = option | lib.LYD_OPT_TRUSTED
        if not self._root:
            raise DataTreeEmptyError(
                "merges() not possible until data exists on the root object."
            )

        tmp = lib.lyd_parse_mem(self._lyctx, str2c(payload), format, option)
        if tmp == ffi.NULL:
            raise self.error("Marshalling Merge Error", format)

        if not lib.lyd_merge(self._root, tmp, lib.LYD_OPT_EXPLICIT) == 0:
            raise self.error("Merge Error")

    def advanced_merge(self, filename, format=lib.LYD_XML, trusted=True, strict=True):
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        if self._root:
            option = lib.LYD_OPT_CONFIG
            if strict:
                option = option | lib.LYD_OPT_STRICT
            if trusted:
                option = option | lib.LYD_OPT_TRUSTED
            template_root = lib.lyd_parse_path(
                self._lyctx, str2c(filename), format, option
            )
            if template_root == ffi.NULL:
                raise self.error("Marshalling Error")

            if lib.lypy_process_attributes(self._root, self._lyctx, template_root) == 1:
                raise self.error(
                    "Validation failed after processing attributes to remove/replace items in the existing data tree.",
                )
        else:
            raise DataTreeEmptyError(
                "advanced merges() not possible until data exists on the root object."
            )

    def advanced_merges(self, payload, format=lib.LYD_XML, trusted=True, strict=True):
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        if self._root:
            option = lib.LYD_OPT_CONFIG
            if strict:
                option = option | lib.LYD_OPT_STRICT
            if trusted:
                option = option | lib.LYD_OPT_TRUSTED
            template_root = lib.lyd_parse_mem(
                self._lyctx, str2c(payload), format, option
            )
            if template_root == ffi.NULL:
                raise self.error("Marshalling Error")

            if lib.lypy_process_attributes(self._root, self._lyctx, template_root) == 1:
                raise self._ctx.error(
                    "Validation failed after processing attributes to replace/remove items before merging into the data tree."
                )
        else:
            raise DataTreeEmptyError(
                "advanced merges() not possible until data exists on the root object."
            )

    def dumps(self, format=lib.LYD_XML):
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        """
        Load from a string with the specified format
        """
        if not self._root:
            raise DataTreeEmptyError("No data to dump")

        buf = ffi.new("char **")
        lib.lyd_print_mem(buf, self._root, format, lib.LYP_WITHSIBLINGS)
        return c2str(buf[0])

    def dump_datanodes(self, start_node=None):
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        if not start_node:
            start_node = lib.lypy_get_root_node(self._root)
            base_schema_path = None
        else:
            start_node = start_node.lyd_node
            base_schema_path = c2str(
                ffi.gc(lib.lys_path(start_node.schema, 0), lib.free)
            )
        yield from DataNode._find_nodes(self._lyctx, start_node, base_schema_path)

    def validate(self):
        if not self._ctx:
            raise RuntimeError("context already destroyed")
        if not self._root:
            return True

        result = lib.validate_data_tree(self._root, self._ctx._ctx)

        if result == 0:
            return True
        raise self._ctx.error("Validation Error")


# ------------------------------------------------------------------------------
LOG_LEVELS = {
    lib.LY_LLERR: logging.ERROR,
    lib.LY_LLWRN: logging.WARNING,
    lib.LY_LLVRB: logging.INFO,
    lib.LY_LLDBG: logging.DEBUG,
}


@ffi.def_extern(name="lypy_log_cb")
def libyang_c_logging_callback(level, msg, path):
    args = [c2str(msg)]
    if path:
        fmt = "%s: %s"
        args.append(c2str(path))
    else:
        fmt = "%s"
    LOG.log(LOG_LEVELS.get(level, logging.NOTSET), fmt, *args)


def set_log_level(level):
    for ly_lvl, py_lvl in LOG_LEVELS.items():
        if py_lvl == level:
            lib.ly_verb(ly_lvl)
            return


set_log_level(logging.ERROR)
lib.ly_set_log_clb(lib.lypy_log_cb, True)
lib.ly_log_options(lib.LY_LOLOG | lib.LY_LOSTORE)
LOG = logging.getLogger(__name__)
LOG.addHandler(logging.NullHandler())
