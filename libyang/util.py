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


# ------------------------------------------------------------------------------
class DataXpathDoesNotExistError(LibyangError):
    def __init__(self, xpath):
        super().__init__(
            (
                f"The provided XPATH did not provide any results - check the XPATH\n"
                f"XPATH: {xpath}\n"
            )
        )


# ------------------------------------------------------------------------------
class DataXpathResultsInMultipleResultsError(LibyangError):
    def __init__(self, xpath, results):
        super().__init__(
            (
                f"The provided XPATH provided {results}- "
                "correct the XPATH to specify a single result by specifying predicates.\n"
                f"XPATH: {xpath}\n"
            )
        )


# ------------------------------------------------------------------------------
class AttributeCannotBeSetError(LibyangError):
    def __init__(self, xpath, module, attribute_name, attribute_value):
        super().__init__(
            (
                f'The attribute {module}:{attribute_name} could not be set to "{attribute_value}"\n'
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
