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

    LYPY_MIN_LIBYANG_VERSION = '1.1.30'

    def __init__(self, search_path=None,
                 options=lib.LY_CTX_DISABLE_SEARCHDIR_CWD):
        # This is a placeholder whilst working out what the earliest version of
        # libyang is that supports the new data tree things. This may only be
        # useful whilst new people come up to speed with libyang... once things
        # settle down this probably can just be reverted.
        installed_version = '{0}.{1}.{2}'.format(lib.LY_VERSION_MAJOR,
                                                 lib.LY_VERSION_MINOR,
                                                 lib.LY_VERSION_MICRO)
        if not installed_version == self.LYPY_MIN_LIBYANG_VERSION:
            raise RuntimeError('libyangversion installed {0} but require {1}'.format(installed_version,
                                                                                     self.LYPY_MIN_LIBYANG_VERSION))

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
        self._ctx = ctx._ctx
        self._root = None

    def set_xpath(self, xpath, value):
        """
        Set a value by XPAH - with siblings/dependent nodes getting created.

        If the path already exists with the same value (no data change0 then lyd_new_path
        will return NULL.
        """

        libyang_value = DataNode.convert_python_value(value)

        if self._root is None:
            node = lib.lyd_new_path(ffi.NULL, self._ctx, str2c(xpath), libyang_value, 0, lib.LYD_PATH_OPT_UPDATE)
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

        if self._root is None:
            return

        node_set = lib.lyd_find_path(self._root, str2c(xpath))
        if node_set == ffi.NULL:
            return

        for i in range(node_set.number):
            yield DataNode(self, node_set.set.d[i], xpath)
        lib.ly_set_free(node_set)

    def gets_xpath(self, xpath):
        """
        Get the XPATH of each list element wtithin the list - returns a generator
        """
        if self._root is None:
            return

        node_set = lib.lyd_find_path(self._root, str2c(xpath))
        if node_set == ffi.NULL:
            return []

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

        if not node_set.number == 1:
            raise LibyangError('delete_xpath only tested to delete single xpaths to avoid caring about order')
        lib.lyd_unlink(node_set.set.d[0])

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

    def load(self, filename, format=lib.LYD_XML):
        """
        Load from a file with the specified format
        # TODO:  what about freeing an initial root if one exists
        """
        if self._root:
            raise LibyangError('load() not supported when data is already set - because the old node is not cleanly released.')
        self._root = lib.lyd_parse_path(self._ctx, str2c(filename), format, lib.LYD_OPT_CONFIG)
        if self._root == ffi.NULL:
            msg = c2str(lib.ly_errmsg(self._ctx))
            path = c2str(lib.ly_errpath(self._ctx))
            raise ValueError('%s %s' %(msg, path))

    def loads(self, payload, format=lib.LYD_XML):
        """
        Load from a string with the specified format
        """
        if self._root:
            raise LibyangError('load() not supported when data is already set - because the old node is not cleanly released.')

        self._root = lib.lyd_parse_mem(self._ctx, str2c(payload), format, lib.LYD_OPT_CONFIG)
        if self._root == ffi.NULL:
            msg = c2str(lib.ly_errmsg(self._ctx))
            path = c2str(lib.ly_errpath(self._ctx))
            raise ValueError('%s %s' %(msg, path))

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

        DataNode._find_nodes(self._ctx, nodelist, start_node)

        for node in nodelist:
            yield nodelist[node]


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
