# Copyright (c) 2019 Robin Jarry
# SPDX-License-Identifier: MIT

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

    def test_invalid_value(self):
        # Arrange
        xpath1 = BASE_XPATH + ':types/str1'
        xpath2 = BASE_XPATH + ':types/u_int_8'
        value1 = 'HELLO'
        value2 = 9999

        # Act
        self.data.set_xpath(xpath1, value1)
        with self.assertRaises(libyang.util.LibyangError) as err:
            self.data.set_xpath(xpath2, value2)

        # Assert
        self.assertTrue('The value 9999 was not set' in str(err.exception))

    def test_invalid_path(self):
        # Arrange
        xpath1 = BASE_XPATH + ':types/str1'
        xpath2 = BASE_XPATH + ':types/uint8'
        value1 = 'HELLO'
        value2 = 99

        # Act
        self.data.set_xpath(xpath1, value1)
        with self.assertRaises(libyang.util.LibyangError) as err:
            self.data.set_xpath(xpath2, value2)

        # Assert
        self.assertTrue('The value 99 was not set' in str(err.exception))

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

    def test_loads_merges(self):
        # Arrange
        payload = '{"minimal-integrationtest:types":{"str1":"this-is-a-string"}}'

        # Act
        self.data.loads(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertEqual(next(self.data.get_xpath('/minimal-integrationtest:types/str1')).value, 'this-is-a-string')
        with self.assertRaises(StopIteration):
            next(self.data.get_xpath('/minimal-integrationtest:types/str2'))

        # Arrange
        payload = '{"minimal-integrationtest:types":{"str2":"this-is-a-string"}}'

        # Act
        self.data.merges(payload, libyang.lib.LYD_JSON)

        # Arrange
        payload = '{"minimal-integrationtest:types":{"invalid-node-name":"this-is-a-string"}}'

        # Act
        with self.assertRaises(libyang.util.LibyangError) as err:
            self.data.merges(payload, libyang.lib.LYD_JSON, strict=True)

        # Assert
        self.assertTrue('Unknown element "invalid-node-name"' in str(err.exception))
        self.assertEqual(next(self.data.get_xpath('/minimal-integrationtest:types/str1')).value, 'this-is-a-string')
        self.assertEqual(next(self.data.get_xpath('/minimal-integrationtest:types/str2')).value, 'this-is-a-string')

    def test_loads_merges_with_invalid_data_in_second_payload(self):
        # Arrange
        payload = '{"minimal-integrationtest:types":{"str1":"this-is-a-string"}}'

        # Act
        self.data.loads(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertEqual(next(self.data.get_xpath('/minimal-integrationtest:types/str1')).value, 'this-is-a-string')
        with self.assertRaises(StopIteration):
            next(self.data.get_xpath('/minimal-integrationtest:types/str2'))

        # Arrange
        payload = '{"minimal-integrationtest:types":{"u_int_8":"this-is-a-string"}}'

        # Act
        with self.assertRaises(libyang.util.LibyangError) as err_context:
            self.data.merges(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertEqual(next(self.data.get_xpath('/minimal-integrationtest:types/str1')).value, 'this-is-a-string')
        self.assertTrue('Marshalling Merge Error' in str(err_context.exception))

    def test_loads_invalid_data(self):
        # Arrange
        payload = '{"minimal-integrationtest:types":{"int_8":"this-is-a-string"}}'

        # Act
        with self.assertRaises(libyang.util.LibyangError) as err_context:
            self.data.loads(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertTrue('Marshalling Error' in str(err_context.exception))

    def test_merges_into_the_same_container(self):
        # Arrange
        payload_one = '''<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><iron><ore>AAA</ore></iron></metal></metals>'''
        payload_two = '''<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><nickel><coin>b</coin></nickel></metal></metals>'''
        payload_three = '''<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><steel><girder>c</girder></steel></metal></metals>'''

        # Act
        self.data.loads(payload_one)
        self.data.merges(payload_two)
        self.data.merges(payload_three)
        result = self.data.dumps()

        # # Assert
        xpath = '/minimal-integrationtest:metals[a="AA"][b="BB"]'
        self.assertEqual(next(self.data.get_xpath(xpath + '/metal/iron/ore')).value, 'AAA')
        self.assertEqual(next(self.data.get_xpath(xpath + '/metal/nickel/coin')).value, 'b')
        self.assertEqual(next(self.data.get_xpath(xpath + '/metal/steel/girder')).value, 'c')

        expected_result = '<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><a>AA</a><b>BB</b>'
        expected_result += '<metal><iron><ore>AAA</ore></iron><steel><girder>c</girder></steel></metal></metals>'
        self.assertEqual(result, expected_result)

    def test_merges_into_the_same_container_with_matching_default(self):
        # Arrange
        payload_one = '''<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><iron><ore>a</ore></iron></metal></metals>'''
        payload_two = '''<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><nickel><coin>b</coin></nickel></metal></metals>'''
        payload_three = '''<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><steel><girder>c</girder></steel></metal></metals>'''

        # Act
        self.data.loads(payload_one)
        self.data.merges(payload_two)
        self.data.merges(payload_three)
        result = self.data.dumps()

        # # Assert
        xpath = '/minimal-integrationtest:metals[a="AA"][b="BB"]'
        self.assertEqual(next(self.data.get_xpath(xpath + '/metal/iron/ore')).value, 'a')
        self.assertEqual(next(self.data.get_xpath(xpath + '/metal/nickel/coin')).value, 'b')
        self.assertEqual(next(self.data.get_xpath(xpath + '/metal/steel/girder')).value, 'c')

        expected_result = '<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><a>AA</a><b>BB</b>'
        expected_result += '<metal><iron><ore>a</ore></iron><steel><girder>c</girder></steel></metal></metals>'
        self.assertEqual(result, expected_result)

    def test_deep_nodes_and_get_schema(self):
        # Arrange
        xpath = '/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep'

        # Act
        self.data.set_xpath(xpath, 'down here')
        node = next(self.data.get_xpath(xpath))
        root = node.get_root()

        # Assert
        self.assertEqual(node.xpath, xpath)
        self.assertEqual(node.value, 'down here')
        self.assertEqual(repr(node.get_schema()), '<libyang.schema.Node: deep>')
        self.assertEqual(repr(root), '<libyang.data.DataNode: />')

    def test_dump_datanodes(self):
        """
        libyang definetely keeps track of insertion order.

        If we change the order of the set_xpath()'s operations we will get a different
        order in the results. This (for now) is mitigated by sorting the result by
        xpath - see data/dump_datanodes (i.e. sorted_keys.sort())
        """
        # Arrange
        xpath = '/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep'
        xpath2 = '/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2'
        xpath3 = '/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3'
        xpath4 = '/minimal-integrationtest:types/str1'

        # Act
        self.data.set_xpath(xpath, 'down here')
        self.data.set_xpath(xpath2, 'down here too')
        self.data.set_xpath(xpath3, 'im down here too')
        self.data.set_xpath(xpath4, 'top level string')

        node = next(self.data.get_xpath(xpath))
        root = node.get_root()
        results = list(root.dump_datanodes())

        # Assert
        expected_results = [
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3>',
            '<libyang.data.DataNode: /minimal-integrationtest:types/str1>'
        ]
        expected_results = [
            '<libyang.data.DataNode: /minimal-integrationtest:nesting>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3>',
            '<libyang.data.DataNode: /minimal-integrationtest:types>',
            '<libyang.data.DataNode: /minimal-integrationtest:types/str1>'
        ]

        for result in results:
            self.assertEqual(expected_results.pop(0), repr(result))

    def test_deep_nodes_and_get_schema_different_order(self):
        """
        libyang definetely keeps track of insertion order.

        If we change the order of the set_xpath()'s operations we will get a different
        order in the results.
        """
        # Arrange
        xpath = '/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep'
        xpath2 = '/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2'
        xpath3 = '/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3'
        xpath4 = '/minimal-integrationtest:types/str1'

        # Act
        self.data.set_xpath(xpath4, 'top level string')
        self.data.set_xpath(xpath3, 'im down here too')
        self.data.set_xpath(xpath2, 'down here too')
        self.data.set_xpath(xpath, 'down here')

        node = next(self.data.get_xpath(xpath))
        root = node.get_root()
        results = list(root.dump_datanodes())

        # Assert
        expected_results = [
            '<libyang.data.DataNode: /minimal-integrationtest:nesting>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2>',
            '<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3>'
        ]

        for result in results:
            self.assertEqual(expected_results.pop(0), repr(result))

    def test_loads_with_unrecognised_nodes(self):
        # Arrange
        payload = '{"minimal-integrationtest:types":{"invalid-node-name":"this-should-blowup"}}'

        # Act
        with self.assertRaises(libyang.util.LibyangError) as err:
            self.data.loads(payload, libyang.lib.LYD_JSON, strict=True)

        # Assert
        self.assertTrue('Unknown element "invalid-node-name"' in str(err.exception))
