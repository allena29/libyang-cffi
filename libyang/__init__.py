# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

import logging
import os

from _libyang import ffi
from _libyang import lib

from .data import DataNode
from .schema import Module
from .schema import Node
from .util import LibyangError
from .util import c2str
from .util import str2c


# ------------------------------------------------------------------------------
class Context(object):

    def __init__(self, search_path=None,
                 options=lib.LY_CTX_DISABLE_SEARCHDIR_CWD):
        self._ctx = ffi.gc(lib.ly_ctx_new(ffi.NULL, options),
                           lambda c: lib.ly_ctx_destroy(c, ffi.NULL))
        if not self._ctx:
            raise self.error('cannot create context')

        search_dirs = []
        if 'YANGPATH' in os.environ:
            search_dirs.extend(
                os.environ['YANGPATH'].strip(': \t\r\n\'"').split(':'))
        elif 'YANG_MODPATH' in os.environ:
            search_dirs.extend(
                os.environ['YANG_MODPATH'].strip(': \t\r\n\'"').split(':'))
        if search_path:
            search_dirs.extend(search_path.strip(': \t\r\n\'"').split(':'))

        for path in search_dirs:
            if not os.path.isdir(path):
                continue
            if lib.ly_ctx_set_searchdir(self._ctx, str2c(path)) != 0:
                raise self.error('cannot set search dir')

    def error(self, msg, *args):
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
                    errors.append(': '.join(e))
                err = err.next
        finally:
            lib.ly_err_clean(self._ctx, ffi.NULL)

        msg %= args
        if errors:
            msg += ': ' + ' '.join(errors)

        return LibyangError(msg)

    def load_module(self, name):
        mod = lib.ly_ctx_load_module(self._ctx, str2c(name), ffi.NULL)
        if not mod:
            raise self.error('cannot load module')

        return Module(self, mod)

    def get_module(self, name):
        mod = lib.ly_ctx_get_module(self._ctx, str2c(name), ffi.NULL, False)
        if not mod:
            raise self.error('cannot get module')

        return Module(self, mod)

    def find_path(self, path):
        node_set = ffi.gc(lib.ly_ctx_find_path(self._ctx, str2c(path)),
                          lib.ly_set_free)
        if not node_set:
            raise self.error('cannot find path')

        for i in range(node_set.number):
            yield Node.new(self, node_set.set.s[i])

    def __iter__(self):
        """
        Return an iterator that yields all implemented modules from the context
        """
        idx = ffi.new('uint32_t *')
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
    """

    def __init__(self, ctx):
        self._ctx = ctx
        self._lyctx = ctx._ctx
        self._root = None

    def set_xpath(self, xpath, value):
        """
        Set a value by XPAH - with siblings/dependent nodes getting created.

        If the path already exists with the same value (no data change0 then lyd_new_path
        will return NULL.
        """

        libyang_value = DataNode.convert_python_value(value)

        if self._root is None:
            node = lib.lyd_new_path(ffi.NULL, self._lyctx , str2c(xpath), libyang_value, 0, lib.LYD_PATH_OPT_UPDATE)
            if not node:
                raise LibyangError('The value {0} was not set at {1}\nCheck the path and value'.format(value, xpath))
            self._root = node
        else:
            node = lib.lyd_new_path(self._root, ffi.NULL, str2c(xpath), libyang_value, 0, lib.LYD_PATH_OPT_UPDATE)

        if not node:
            node_set = lib.lyd_find_path(self._root, str2c(xpath))
            if node_set.number == 0:
                raise LibyangError('The value {0} was not set at {1}\nCheck the path and value'.format(value, xpath))

    def get_xpath(self, xpath):
        """
        Get the value at XPATH - returns a generator
        """
        # TODO: work out what happens with a python generator, if the caller just calls next() does gc get as
        # far as actually calling ly_set_free()????
        if self._root is not None:
            node_set = lib.lyd_find_path(self._root, str2c(xpath))
            if node_set == ffi.NULL:
                yield None

            for i in range(node_set.number):
                yield DataNode(self, node_set.set.d[i], xpath)
            lib.ly_set_free(node_set)

    def gets_xpath(self, xpath):
        """
        Get the XPATH of each list element wtithin the list - returns a generator
        """
        if self._root is not None:
            node_set = lib.lyd_find_path(self._root, str2c(xpath))
            if node_set == ffi.NULL:
                yield []
            else:
                for i in range(node_set.number):
                    yield c2str(lib.lyd_path(node_set.set.d[i]))
            lib.ly_set_free(node_set)

    def delete_xpath(self, xpath):
        """
        Delete the value at XPATH
        """
        if self._root is None:
            return

        node_set = lib.lyd_find_path(self._root, str2c(xpath))
        if node_set == ffi.NULL:
            return

        if node_set.number > 0:
            result = lib.lyd_unlink(node_set.set.d[0])
            if result:
                raise LibyangError('Unable to delete xpath: %s' %(xpath))

    def count_xpath(self, xpath):
        """
        Count results for a given XPATH
        """
        if self._root is None:
            return 0

        node_set = lib.lyd_find_path(self._root, str2c(xpath))
        if node_set == ffi.NULL:
            return 0
        return int(node_set.number)

    def dump(self, filename, format=lib.LYD_XML):
        """
        Dump to a file with the specified format
        """
        with open(filename, 'w') as fh:
            lib.lyd_print_file(fh, self._root, format, lib.LYP_WITHSIBLINGS)

    def load(self, filename, format=lib.LYD_XML, trusted=False, strict=True):
        """
        Load from a file with the specified format
        # TODO:  what about freeing an initial root if one exists
        """
        option = lib.LYD_OPT_CONFIG
        if strict:
            option = option | lib.LYD_OPT_STRICT
        if trusted:
            option = option | lib.LYD_OPT_TRUSTED
        if self._root:
            raise LibyangError('load() not supported when data is already set - because the old node is not cleanly released.')
        self._root = lib.lyd_parse_path(self._lyctx , str2c(filename), format, option)
        if self._root == ffi.NULL:
            raise self._ctx.error('Marshalling Error')

    def loads(self, payload, format=lib.LYD_XML, trusted=False, strict=True):
        """
        Load from a string with the specified format
        """
        option = lib.LYD_OPT_CONFIG
        if strict:
            option = option | lib.LYD_OPT_STRICT
        if trusted:
            option = option | lib.LYD_OPT_TRUSTED
        if self._root:
            raise LibyangError('load() not supported when data is already set - because the old note is not cleanly released.')

        self._root = lib.lyd_parse_mem(self._lyctx, str2c(payload), format, option)
        if self._root == ffi.NULL:
            raise self._ctx.error('Marshalling Error')

    def merges(self, payload, format=lib.LYD_XML, trusted=True, strict=True):
        """
        Load from a string with the specified format
        """
        option = lib.LYD_OPT_CONFIG
        if strict:
            option = option | lib.LYD_OPT_STRICT
        if trusted:
            option = option | lib.LYD_OPT_TRUSTED
        if not self._root:
            raise LibyangError('merges() not possible until data exists on the root object.')

        tmp = lib.lyd_parse_mem(self._lyctx, str2c(payload), format, option)
        if tmp == ffi.NULL:
            raise self._ctx.error('Marshalling Merge Error')

        if not lib.lyd_merge(self._root, tmp, lib.LYD_OPT_EXPLICIT) == 0:
            return self._ctx.error('Merge Error')
    
    def advancedmerge(self, payload, format=lib.LYD_XML, trusted=True, strict=True):
        if self._root:
            option = lib.LYD_OPT_CONFIG
            if strict:
                option = option | lib.LYD_OPT_STRICT
            if trusted:
                option = option | lib.LYD_OPT_TRUSTED
            template_root = lib.lyd_parse_mem(self._lyctx, str2c(payload), format, option)
            
            if lib.lypy_process_attributes(self._root, self._lyctx, template_root) == 1:
                raise LibyangError('Validation failed after processing attributes')
        else:
            raise LibyangError('advanced merges() not possible until data exists on the root object.')

    def dumps(self, format=lib.LYD_XML):
        """
        Load from a string with the specified format
        """
        if not self._root:
            raise LibyangError('No data to dump')

        buf = ffi.new('char **')
        lib.lyd_print_mem(buf, self._root, format, lib.LYP_WITHSIBLINGS)
        return c2str(buf[0])

    def dump_datanodes(self):
        # This is suboptimal at present - want to move this down to C or
        # avoid the extra funaction call.
        nodelist = {}
        start_node = lib.lypy_get_root_node(self._root)

        DataNode._find_nodes(self._lyctx, nodelist, start_node)

        for node in nodelist:
            yield nodelist[node]

    def validate(self):
        if not self._root:
            return True

        result = lib.validate_data_tree(self._root, self._ctx._ctx)

        if result == 0:
            return True
        raise self._ctx.error('Validation Error')


# ------------------------------------------------------------------------------
LOG_LEVELS = {
    lib.LY_LLERR: logging.ERROR,
    lib.LY_LLWRN: logging.WARNING,
    lib.LY_LLVRB: logging.INFO,
    lib.LY_LLDBG: logging.DEBUG,


}


@ffi.def_extern(name='lypy_log_cb')
def libyang_c_logging_callback(level, msg, path):
    args = [c2str(msg)]
    if path:
        fmt = '%s: %s'
        args.append(c2str(path))
    else:
        fmt = '%s'
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
