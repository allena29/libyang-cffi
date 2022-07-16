# Copyright (c) 2018-2019 Robin Jarry
# SPDX-License-Identifier: MIT

from _libyang import ffi


#------------------------------------------------------------------------------
class LibyangError(Exception):
    pass


#------------------------------------------------------------------------------
class InvalidSchemaOrValueError(LibyangError):
    def __init__(self, value, xpath):
        super().__init__(
            (
                "The value could not be set, either the value or path is invalid\n"
                f'Value: "{value}"\n'
                f"XPATH: {xpath}\n"
            )
        )


def str2c(s):
    if s is None:
        return ffi.NULL
    if hasattr(s, 'encode'):
        s = s.encode('utf-8')
    return ffi.new('char []', s)


#------------------------------------------------------------------------------
def c2str(c):
    if c == ffi.NULL:
        return None
    s = ffi.string(c)
    if hasattr(s, 'decode'):
        s = s.decode('utf-8')
    return s
