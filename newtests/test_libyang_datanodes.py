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


YANG_DIR = os.path.join(os.path.dirname(__file__), 'yang')
YANG_MODULE = 'minimal-integrationtest'
BASE_XPATH = '/' + YANG_MODULE


class test_libyangdata(unittest.TestCase):

    def setUp(self):
        self.ctx = libyang.Context(YANG_DIR)
        self.ctx.load_module('minimal-integrationtest')
        self.data = libyang.DataTree(self.ctx)

    def test_basic(self):
        # Act
        xpath = BASE_XPATH + ':types/str1'
        value = 'this-is-a-string'
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, value)

    def test_multiple(self):
        # Act
        self.data.set_xpath(BASE_XPATH + ':types/str1', 'A')
        self.data.set_xpath(BASE_XPATH + ':types/str2', 'B')

        result = list(self.data.get_xpath(BASE_XPATH + ':types/*'))

        # Assert
        self.assertEqual(len(result), 2)

    def test_delete(self):
        # Arrange
        self.data.set_xpath(BASE_XPATH + ':types/str1', 'A')
        result = list(self.data.get_xpath(BASE_XPATH + ':types/str1'))
        self.assertEqual(len(result), 1)

        # Act
        self.data.delete_xpath(BASE_XPATH + ':types/str1')

        # Assert
        result = list(self.data.get_xpath(BASE_XPATH + ':types/str1'))
        self.assertEqual(len(result), 0)

    def test_numbers(self):
        # Arrange
        for node, value in (
            ('int_8', -128), ('int_16', 234), ('int_32', 32444),
                ('u_int_8', 255), ('u_int_16', 234), ('u_int_32', 32444)):
            xpath = BASE_XPATH + ':types/' + node

            # Act
            self.data.set_xpath(xpath, value)
            result = next(self.data.get_xpath(xpath)).value

            # Assert
            self.assertEqual(result, value)

    def test_decimal64(self):
        # Arrange
        xpath = BASE_XPATH + ':types/dec_64'
        value = 4.442

        # Act
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, value)

    def test_empty(self):
        # Arrange
        xpath = BASE_XPATH + ':types/void'
        value = None

        # Act
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, True)

    def test_boolean_true(self):
        # Act
        xpath = BASE_XPATH + ':types/bool'
        value = True

        # Act
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, value)

    def test_boolean_false(self):
        # Arrange
        xpath = BASE_XPATH + ':types/bool'
        value = False

        # Act
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, value)

    def test_list(self):
        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='mykey']/x"
        value = 'mykey'

        xpath2 = BASE_XPATH + ":types/collection[x='mykey']/y"
        value2 = 'mynonkey'

        xpath3 = BASE_XPATH + ":types/collection[x='mykey']"

        xpath4 = BASE_XPATH + ":types/collection[x='my-non-exist']"

        # Act
        self.data.set_xpath(xpath, value)
        self.data.set_xpath(xpath2, value2)
        result = next(self.data.get_xpath(xpath)).value
        result2 = next(self.data.get_xpath(xpath2)).value
        result3 = next(self.data.get_xpath(xpath3)).value
        result4 = list(self.data.get_xpath(xpath4))
        length = self.data.count_xpath(BASE_XPATH + ':types/collection')

        # Assert
        self.assertEqual(result, value)
        self.assertEqual(result2, value2)
        self.assertEqual(result3, True)
        self.assertEqual(result4, [])
        self.assertEqual(length, 1)

    def test_leaflist(self):
        # Arrange
        xpath = BASE_XPATH + ':types/simplecollection'
        value = 'ABC'
        value2 = 'DEF'
        value3 = 'GHI'

        # Act
        self.data.set_xpath(xpath, value)
        self.data.set_xpath(xpath, value)
        self.data.set_xpath(xpath, value2)
        self.data.set_xpath(xpath, value3)
        results = self.data.get_xpath(xpath)

        # Assert
        expected_results = ['ABC', 'DEF', 'GHI']
        for result in results:
            self.assertEqual(result.value, expected_results.pop(0))

    # def test_load(self):
    #     # Act
    #     self.data.load('/tmp/unittest.json', libyang.lib.LYD_JSON)
    #
    #     self.assertEqual(next(self.data.get_xpath('/minimal-integrationtest:types/str1')).value, 'this-is-a-string')
    #
    # def test_dump(self):
    #     # Arrange
    #     xpath = BASE_XPATH + ':types/str1'
    #     value = 'this-is-a-string'
    #     self.data.set_xpath(xpath, value)
    #
    #     # Act
    #     self.data.dump('/tmp/unittest.json', libyang.lib.LYD_JSON)

    def test_dumps(self):
        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='mykey']/x"
        value = 'mykey'
        self.data.set_xpath(xpath, value)

        # Act
        result = self.data.dumps(libyang.lib.LYD_JSON)

        # Assert
        expected_result = '{"minimal-integrationtest:types":{"collection":[{"x":"mykey"}]}}'
        self.assertEqual(result, expected_result)

    def test_loads(self):
        # Arrange
        payload = '{"minimal-integrationtest:types":{"str1":"this-is-a-string"}}'

        # Act
        self.data.loads(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertEqual(next(self.data.get_xpath('/minimal-integrationtest:types/str1')).value, 'this-is-a-string')

    def test_deep_nodes_and_get_schema(self):
        # Arrange
        xpath = '/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep'

        # Act
        self.data.set_xpath(xpath, "down here")
        node = next(self.data.get_xpath(xpath))
        root = node.get_root()

        # Assert
        self.assertEqual(node.xpath, xpath)
        self.assertEqual(node.value, 'down here')
        self.assertEqual(repr(node.get_schema()), '<libyang.schema.Node: deep>')
        self.assertEqual(repr(root), '<libyang.data.DataNode: />')
