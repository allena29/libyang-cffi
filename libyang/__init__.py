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

from .schema import Module
from .schema import Node
from .util import LibyangError
from .util import c2str
from .util import str2c


class Data(object):

    def __init__(self, ctx, options=lib.LY_CTX_DISABLE_SEARCHDIR_CWD):
        self._ctx =  ctx._ctx
        self.root = [None, None]
        print("Libyang initialised with a ctx")

    def set_data_by_xpath(self, xpath, value, doc_id=0):
        if self.root[doc_id] is None:
            print("We do not have a roto document yet:c tx", self._ctx)
            self.root[doc_id] = lib.lyd_new_path(ffi.NULL, self._ctx, str2c(xpath), str2c(value),0,0)
            print(self.root[doc_id])
        else:
            print("We do ahve root ", self._ctx, self.root[doc_id])
            node = lib.lyd_new_path(self.root[doc_id], ffi.NULL, str2c(xpath), str2c(value), 0,0)

        #x=2str(lib.adams())
        #print(x)

    def load_from_file(self, filename, doc_id=0, format="xml"):
        """
        Load XML or JSON from a file into a data structure.
        """
        if self.root[doc_id]:
            print("We need to think about clean up the old root....")

        self.root[doc_id] = lib.lyd_parse_path(self._ctx, str2c(filename), self._get_format(format), lib.LYD_OPT_CONFIG)

    def dump(self, filename, doc_id=0, format="xml"):
        """
        Dump XML or JSON to a file from a data structure.
        """
        print("Dump to ",filename)
        f=open(filename,"w")
        lib.lyd_print_file(f, self.root[doc_id], self._get_format(format), lib.LYP_WITHSIBLINGS)
        f.close()

    def diff(self):
        print("diff")
        diff_list = lib.lyd_diff(self.root[0], self.root[1], 0)

        for i in range(40):
            diff_type = diff_list.type[i];

            if diff_type == lib.LYD_DIFF_END:
                print("END OF DIFF SET", i)
                return

            if diff_type == lib.LYD_DIFF_DELETED:
                print("DIFF DELETED", i)
                print(c2str(lib.lyd_path(diff_list.first[i])))

    def _get_format(self, format):
        if format == "xml":
            return  lib.LYD_XML
        elif format == "json":
            return lib.LYD_JSON

        raise ValueError("Format must be 'json' or 'xml'")
#------------------------------------------------------------------------------


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


#------------------------------------------------------------------------------
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
