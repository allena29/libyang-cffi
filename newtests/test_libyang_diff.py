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

import os
import unittest

import libyang
from libyang import diff


YANG_DIR = os.path.join(os.path.dirname(__file__), 'yang')
YANG_MODULE = 'minimal-integrationtest'
BASE_XPATH = '/' + YANG_MODULE


class test_libyangdata(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 888880
        self.ctx = libyang.Context(YANG_DIR)
        self.ctx.load_module('minimal-integrationtest')
        self.data = libyang.DataTree(self.ctx)
        self.data_2 = libyang.DataTree(self.ctx)

        self.subject = libyang.diff.Differ(self.ctx)

    def test_basic_diff_modify(self):
        # Arrange
        self.data.set_xpath('/minimal-integrationtest:types/str1', 'ABC')
        self.data_2.set_xpath('/minimal-integrationtest:types/str1', 'DEF')

        # Act
        result = list(self.subject.diff(self.data, self.data_2))

        # Assert
        expected_result = [
            ('/minimal-integrationtest:types/str1', 'ABC', 'DEF', libyang.diff.DIFF_PATH_MODIFIED)
        ]
        self.assertEqual(expected_result, result)

    def test_basic_diff_add(self):
        # Arrange
        self.data.set_xpath('/minimal-integrationtest:types/str1', 'ABC')
        self.data_2.set_xpath('/minimal-integrationtest:types/str1', 'ABC')
        self.data_2.set_xpath('/minimal-integrationtest:types/str2', 'DEF')
        self.data_2.set_xpath('/minimal-integrationtest:types/str3', 'GHI')

        # Act
        result = list(self.subject.diff(self.data, self.data_2))

        # Assert
        expected_result = [
            ('/minimal-integrationtest:types/str2', None, 'DEF', libyang.diff.DIFF_PATH_CREATED),
            ('/minimal-integrationtest:types/str3', None, 'GHI', libyang.diff.DIFF_PATH_CREATED)
        ]
        self.assertEqual(expected_result, result)

    def test_basic_diff_delete(self):
        # Arrange
        self.data.set_xpath('/minimal-integrationtest:types/str1', 'ABC')
        self.data.set_xpath('/minimal-integrationtest:types/str2', 'DEF')
        self.data_2.set_xpath('/minimal-integrationtest:types/str1', 'ABC')

        # Act
        result = list(self.subject.diff(self.data, self.data_2))

        # Assert
        expected_result = [
            ('/minimal-integrationtest:types/str2', 'DEF', None, libyang.diff.DIFF_PATH_REMOVED)
        ]
        self.assertEqual(expected_result, result)

    def test_basic_diff_list_removed(self):
        # Arrange
        self.data.set_xpath("/minimal-integrationtest:types/collection[x='a']/x", 'a')
        self.data.set_xpath("/minimal-integrationtest:types/collection[x='b']/x", 'b')
        self.data.set_xpath("/minimal-integrationtest:types/collection[x='c']/x", 'c')

        self.data_2.set_xpath("/minimal-integrationtest:types/collection[x='a']/x", 'a')
        self.data_2.set_xpath("/minimal-integrationtest:types/collection[x='c']/x", 'c')

        # Act
        result = list(self.subject.diff(self.data, self.data_2))

        # Assert
        expected_result = [
            ("/minimal-integrationtest:types/collection[x='b']/x", 'b', None, libyang.diff.DIFF_PATH_REMOVED)
        ]
        self.assertEqual(expected_result, result)

    def test_basic_diff_list_ordering(self):
        """
        In the first version we are not handling list ordering...
        ... TODO: if a list has ordered by user on it then it will report a diffset for the
        following. The information is there.

        """
        # Arrange
        self.data.set_xpath("/minimal-integrationtest:types/collection[x='a']/x", 'a')
        self.data.set_xpath("/minimal-integrationtest:types/collection[x='b']/x", 'b')
        self.data.set_xpath("/minimal-integrationtest:types/collection[x='c']/x", 'c')

        self.data_2.set_xpath("/minimal-integrationtest:types/collection[x='c']/x", 'c')
        self.data_2.set_xpath("/minimal-integrationtest:types/collection[x='b']/x", 'b')
        self.data_2.set_xpath("/minimal-integrationtest:types/collection[x='a']/x", 'a')

        # Act
        result = list(self.subject.diff(self.data, self.data_2))

        # Assert
        expected_result = [
        ]
        self.assertEqual(expected_result, result)

    def test_basic_diff_leaf_list_no_change(self):
        # Arrange
        self.data.set_xpath('/minimal-integrationtest:types/simplecollection', 'a')
        self.data.set_xpath('/minimal-integrationtest:types/simplecollection', 'b')
        self.data.set_xpath('/minimal-integrationtest:types/simplecollection', 'c')

        self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'a')
        self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'b')
        self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'c')

        # Act
        result = list(self.subject.diff(self.data, self.data_2))

        # Assert
        expected_result = [
        ]
        self.assertEqual(expected_result, result)

    def test_basic_diff_leaf_list_add(self):
        # Arrange
        self.data.set_xpath('/minimal-integrationtest:types/simplecollection', 'z')
        self.data.set_xpath('/minimal-integrationtest:types/simplecollection', 'b')

        self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'z')
        self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'b')
        self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'c')
        self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'd')

        # Act
        result = list(self.subject.diff(self.data, self.data_2))

        # Assert
        expected_result = [
            ("/minimal-integrationtest:types/simplecollection[.='c']", None, 'c', libyang.diff.DIFF_PATH_CREATED),
            ("/minimal-integrationtest:types/simplecollection[.='d']", None, 'd', libyang.diff.DIFF_PATH_CREATED)
        ]
        self.assertEqual(expected_result, result)
    #
    # def test_basic_diff_leaf_list_add_against_empty(self):
    #     # Arrange
    #     self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'c')
    #     self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'd')
    #
    #     # Act
    #     result = list(self.subject.diff(self.data, self.data_2))
    #     raise ValueError(result)
    #     # Assert
    #     expected_result = [
    #         ('/minimal-integrationtest:types/simplecollection[.='c']', None, 'c', libyang.diff.DIFF_PATH_CREATED),
    #         ('/minimal-integrationtest:types/simplecollection[.='d']', None, 'd', libyang.diff.DIFF_PATH_CREATED)
    #     ]
    #     self.assertEqual(expected_result, result)

    def test_basic_diff_leaf_list_remove(self):
        # Arrange
        self.data.set_xpath('/minimal-integrationtest:types/simplecollection', 'z')
        self.data.set_xpath('/minimal-integrationtest:types/simplecollection', 'b')

        self.data_2.set_xpath('/minimal-integrationtest:types/simplecollection', 'b')

        # Act
        result = list(self.subject.diff(self.data, self.data_2))

        # Assert
        expected_result = [
            ("/minimal-integrationtest:types/simplecollection[.='z']", 'z', None, libyang.diff.DIFF_PATH_REMOVED)
        ]
        self.assertEqual(expected_result, result)

    def test_multiple_diff_results(self):

        # Arrange
        self.data.set_xpath('/minimal-integrationtest:types/u_int_8', 50)
        self.data.set_xpath('/minimal-integrationtest:types/u_int_16', 60)
        self.data.set_xpath('/minimal-integrationtest:types/u_int_32', 80)
        self.data.set_xpath('/minimal-integrationtest:types/u_int_64', 90)

        self.data_2.set_xpath('/minimal-integrationtest:types/int_8', 10)
        self.data_2.set_xpath('/minimal-integrationtest:types/int_16', 20)
        self.data_2.set_xpath('/minimal-integrationtest:types/u_int_32', 88)
        self.data_2.set_xpath('/minimal-integrationtest:types/u_int_64', 99)

        # Act
        result = list(self.subject.diff(self.data, self.data_2))
        # raise ValueError(result)
        # Assert
        expected_result = [
            ('/minimal-integrationtest:types/u_int_32', 80, 88, 2),
            ('/minimal-integrationtest:types/u_int_64', 90, 99, 2),
            ('/minimal-integrationtest:types/u_int_8', 50, None, 3),
            ('/minimal-integrationtest:types/u_int_16', 60, None, 3),
            ('/minimal-integrationtest:types/int_8', None, 10, 1),
            ('/minimal-integrationtest:types/int_16', None, 20, 1)
        ]

        self.assertEqual(expected_result, result)
