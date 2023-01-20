# Copyright (c) 2019 Robin Jarry
# SPDX-License-Identifier: MIT

import os
import unittest

import libyang


YANG_DIR = os.path.join(os.path.dirname(__file__), "yang")
YANG_MODULE = "minimal-integrationtest"
BASE_XPATH = "/" + YANG_MODULE


class test_libyangdata(unittest.TestCase):
    def setUp(self):
        self.ctx = libyang.Context(YANG_DIR)
        self.ctx.load_module("minimal-integrationtest")
        self.ctx.load_module("ietf-netconf")
        self.ctx.load_module("ietf-yang-metadata")
        self.ctx.load_module("other")
        self.maxDiff = 90000000
        self.data = libyang.DataTree(self.ctx)

    def test_basic(self):
        # Act
        xpath = BASE_XPATH + ":types/str1"
        value = "this-is-a-string"
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, value)

    def test_multiple(self):
        # Act
        self.data.set_xpath(BASE_XPATH + ":types/str1", "A")
        self.data.set_xpath(BASE_XPATH + ":types/str2", "B")

        result = list(self.data.get_xpath(BASE_XPATH + ":types/*"))

        # Assert
        self.assertEqual(len(result), 2)

    def test_delete(self):
        # Arrange
        self.data.set_xpath(BASE_XPATH + ":types/str1", "A")
        result = list(self.data.get_xpath(BASE_XPATH + ":types/str1"))
        self.assertEqual(len(result), 1)

        # Act
        self.data.delete_xpath(BASE_XPATH + ":types/str1")

        # Assert
        result = list(self.data.get_xpath(BASE_XPATH + ":types/str1"))
        self.assertEqual(len(result), 0)

    def test_numbers(self):
        # Arrange
        for node, value in (
            ("int_8", -128),
            ("int_16", 234),
            ("int_32", 32444),
            ("u_int_8", 255),
            ("u_int_16", 234),
            ("u_int_32", 32444),
        ):
            xpath = BASE_XPATH + ":types/" + node

            # Act
            self.data.set_xpath(xpath, value)
            result = next(self.data.get_xpath(xpath)).value

            # Assert
            self.assertEqual(result, value)

    def test_invalid_value(self):
        # Arrange
        xpath1 = BASE_XPATH + ":types/str1"
        xpath2 = BASE_XPATH + ":types/u_int_8"
        value1 = "HELLO"
        value2 = 9999

        # Act
        self.data.set_xpath(xpath1, value1)
        with self.assertRaises(libyang.util.InvalidSchemaOrValueError) as err:
            self.data.set_xpath(xpath2, value2)

        # Assert
        self.assertEqual(
            (
                "The value could not be set, either the value or path is invalid\n"
                'Value: "9999"\n'
                "XPATH: /minimal-integrationtest:types/u_int_8\n"
            ),
            str(err.exception),
        )

    def test_invalid_path(self):
        # Arrange
        xpath1 = BASE_XPATH + ":types/str1"
        xpath2 = BASE_XPATH + ":types/uint8"
        value1 = "HELLO"
        value2 = 99

        # Act
        self.data.set_xpath(xpath1, value1)
        with self.assertRaises(libyang.util.InvalidSchemaOrValueError) as err:
            self.data.set_xpath(xpath2, value2)

        # Assert
        self.assertEqual(
            (
                "The value could not be set, either the value or path is invalid\n"
                'Value: "99"\n'
                "XPATH: /minimal-integrationtest:types/uint8\n"
            ),
            str(err.exception),
        )

    def test_decimal64(self):
        # Arrange
        xpath = BASE_XPATH + ":types/dec_64"
        value = 4.442

        # Act
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, value)

    def test_empty(self):
        # Arrange
        xpath = BASE_XPATH + ":types/void"
        value = None

        # Act
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, "")

    def test_boolean_true(self):
        # Act
        xpath = BASE_XPATH + ":types/bool"
        value = True

        # Act
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, value)

    def test_boolean_false(self):
        # Arrange
        xpath = BASE_XPATH + ":types/bool"
        value = False

        # Act
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, value)

    def test_container(self):
        # Arrange
        xpath2 = BASE_XPATH + ":types/pcont"
        value2 = ""

        # Act
        self.data.set_xpath(xpath2, value2)
        result2 = next(self.data.get_xpath(xpath2)).value

        # Assert
        self.assertEqual(result2, value2)

    def test_list(self):
        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='mykey']/x"
        value = "mykey"

        xpath2 = BASE_XPATH + ":types/collection[x='mykey']/y"
        value2 = "mynonkey"

        xpath3 = BASE_XPATH + ":types/collection[x='mykey']"

        xpath4 = BASE_XPATH + ":types/collection[x='my-non-exist']"

        # Act
        self.data.set_xpath(xpath, value)
        self.data.set_xpath(xpath2, value2)
        result = next(self.data.get_xpath(xpath)).value
        result2 = next(self.data.get_xpath(xpath2)).value
        result3 = next(self.data.get_xpath(xpath3)).value
        result4 = list(self.data.get_xpath(xpath4))
        length = self.data.count_xpath(BASE_XPATH + ":types/collection")

        # Assert
        self.assertEqual(result, value)
        self.assertEqual(result2, value2)
        self.assertEqual(result3, "")
        self.assertEqual(result4, [])
        self.assertEqual(length, 1)

    def test_leaflist(self):
        # Arrange
        xpath = BASE_XPATH + ":types/simplecollection"
        value = "ABC"
        value2 = "DEF"
        value3 = "GHI"

        # Act
        self.data.set_xpath(xpath, value)
        self.data.set_xpath(xpath, value)
        self.data.set_xpath(xpath, value2)
        self.data.set_xpath(xpath, value3)
        results = self.data.get_xpath(xpath)

        # Assert
        expected_results = ["ABC", "DEF", "GHI"]
        for result in results:
            self.assertEqual(result.value, expected_results.pop(0))

    def test_dumps(self):
        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='mykey']/x"
        value = "mykey"
        self.data.set_xpath(xpath, value)

        # Act
        result = self.data.dumps(libyang.lib.LYD_JSON)

        # Assert
        expected_result = (
            '{"minimal-integrationtest:types":{"collection":[{"x":"mykey"}]}}'
        )
        self.assertEqual(result, expected_result)

    def test_loads(self):
        # Arrange
        payload = '{"minimal-integrationtest:types":{"str1":"this-is-a-string"}}'

        # Act
        self.data.loads(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertEqual(
            next(self.data.get_xpath("/minimal-integrationtest:types/str1")).value,
            "this-is-a-string",
        )

    def test_loads_merges(self):
        # Arrange
        payload = '{"minimal-integrationtest:types":{"str1":"this-is-a-string"}}'

        # Act
        self.data.loads(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertEqual(
            next(self.data.get_xpath("/minimal-integrationtest:types/str1")).value,
            "this-is-a-string",
        )
        with self.assertRaises(StopIteration):
            next(self.data.get_xpath("/minimal-integrationtest:types/str2"))

        # Arrange
        payload = '{"minimal-integrationtest:types":{"str2":"this-is-a-string"}}'

        # Act
        self.data.merges(payload, libyang.lib.LYD_JSON)

        # Arrange
        payload = (
            '{"minimal-integrationtest:types":{"invalid-node-name":"this-is-a-string"}}'
        )

        # Act
        with self.assertRaises(libyang.util.LibyangError) as err:
            self.data.merges(payload, libyang.lib.LYD_JSON, strict=True)

        # Assert
        self.assertTrue('Unknown element "invalid-node-name"' in str(err.exception))
        self.assertEqual(
            next(self.data.get_xpath("/minimal-integrationtest:types/str1")).value,
            "this-is-a-string",
        )
        self.assertEqual(
            next(self.data.get_xpath("/minimal-integrationtest:types/str2")).value,
            "this-is-a-string",
        )

    def test_loads_merges_with_invalid_data_in_second_payload(self):
        # Arrange
        payload = '{"minimal-integrationtest:types":{"str1":"this-is-a-string"}}'

        # Act
        self.data.loads(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertEqual(
            next(self.data.get_xpath("/minimal-integrationtest:types/str1")).value,
            "this-is-a-string",
        )
        with self.assertRaises(StopIteration):
            next(self.data.get_xpath("/minimal-integrationtest:types/str2"))

        # Arrange
        payload = '{"minimal-integrationtest:types":{"u_int_8":"this-is-a-string"}}'

        # Act
        with self.assertRaises(libyang.util.LibyangMarshallingError) as err_context:
            self.data.merges(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertEqual(
            next(self.data.get_xpath("/minimal-integrationtest:types/str1")).value,
            "this-is-a-string",
        )
        self.assertTrue("Marshalling Merge Error" in str(err_context.exception))

    def test_loads_invalid_data(self):
        # Arrange
        payload = '{"minimal-integrationtest:types":{"int_8":"this-is-a-string"}}'

        # Act
        with self.assertRaises(libyang.util.LibyangMarshallingError) as err_context:
            self.data.loads(payload, libyang.lib.LYD_JSON)

        # Assert
        self.assertTrue("Marshalling Error" in str(err_context.exception))

    def test_merge_with_file(self):
        # Arrange
        payload_one = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><iron><ore>AAA</ore></iron></metal></metals>"""

        # Act
        self.data.loads(payload_one)
        self.data.merge("newtests/yang/mergetest.xml")
        result = self.data.dumps()

        # # Assert
        xpath = '/minimal-integrationtest:metals[a="AA"][b="BB"]'
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/iron/ore")).value, "AAA"
        )
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/nickel/coin")).value, "b"
        )

        expected_result = '<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><a>AA</a><b>BB</b>'
        expected_result += "<metal><iron><ore>AAA</ore></iron></metal></metals>"
        self.assertEqual(result, expected_result)

    def test_merge_with_file_marshalling_error_missing_file(self):
        # Arrange
        payload_one = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><iron><ore>AAA</ore></iron></metal></metals>"""

        # Act
        self.data.loads(payload_one)

        with self.assertRaises(libyang.util.LibyangMarshallingError):
            self.data.merge("newtests/yang/mergetestmissing.xml")

    def test_merge_with_file_marshalling_error(self):
        # Arrange
        payload_one = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><iron><ore>AAA</ore></iron></metal></metals>"""

        # Act
        self.data.loads(payload_one)

        with self.assertRaises(libyang.util.LibyangMarshallingError):
            self.data.merge("newtests/yang/mergetestbad.xml")

    def test_merges_into_the_same_container(self):
        # Arrange
        payload_one = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><iron><ore>AAA</ore></iron></metal></metals>"""
        payload_two = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><nickel><coin>b</coin></nickel></metal></metals>"""
        payload_three = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><steel><girder>c</girder></steel></metal></metals>"""

        # Act
        self.data.loads(payload_one)
        self.data.merges(payload_two)
        self.data.merges(payload_three)
        result = self.data.dumps()

        # # Assert
        xpath = '/minimal-integrationtest:metals[a="AA"][b="BB"]'
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/iron/ore")).value, "AAA"
        )
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/nickel/coin")).value, "b"
        )
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/steel/girder")).value, "c"
        )

        expected_result = '<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><a>AA</a><b>BB</b>'
        expected_result += "<metal><iron><ore>AAA</ore></iron><steel><girder>c</girder></steel></metal></metals>"
        self.assertEqual(result, expected_result)

    def test_merges_into_the_same_container_with_matching_default(self):
        # Arrange
        payload_one = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><iron><ore>a</ore></iron></metal></metals>"""
        payload_two = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><nickel><coin>b</coin></nickel></metal></metals>"""
        payload_three = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><steel><girder>c</girder></steel></metal></metals>"""

        # Act
        self.data.loads(payload_one)
        self.data.merges(payload_two)
        self.data.merges(payload_three)
        result = self.data.dumps()

        # # Assert
        xpath = '/minimal-integrationtest:metals[a="AA"][b="BB"]'
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/iron/ore")).value, "a"
        )
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/nickel/coin")).value, "b"
        )
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/steel/girder")).value, "c"
        )

        expected_result = '<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><a>AA</a><b>BB</b>'
        expected_result += "<metal><iron><ore>a</ore></iron><steel><girder>c</girder></steel></metal></metals>"
        self.assertEqual(result, expected_result)

    def test_get_presence_container(self):
        # Arrange
        xpath = "/minimal-integrationtest:ip"

        # Act
        self.data.set_xpath(xpath, "")
        node = next(self.data.get_xpath(xpath))

        # Assert
        self.assertEqual(node.xpath, xpath)
        self.assertEqual(node.value, "")
        self.assertEqual(repr(node.get_schema()), "<libyang.schema.Container: ip>")
        self.assertEqual(node.get_schema_path(), "/minimal-integrationtest:ip")
        self.assertEqual(node.get_schema().presence(), "true")

    def test_get_non_presence_container(self):
        # Arrange
        xpath = "/minimal-integrationtest:nesting/bronze/silver/gold"

        # Act
        self.data.set_xpath(xpath, "")
        node = next(self.data.get_xpath(xpath))
        root = node.get_root()

        # Assert
        self.assertEqual(node.xpath, xpath)
        self.assertEqual(node.value, "")
        self.assertEqual(repr(node.get_schema()), "<libyang.schema.Container: gold>")
        self.assertEqual(node.get_schema().presence(), None)
        self.assertEqual(
            repr(node),
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold>",
        )
        self.assertEqual(
            repr(root), "<libyang.data.DataNode: /minimal-integrationtest:nesting>"
        )

    def test_deep_nodes_and_get_schema(self):
        # Arrange
        xpath = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep"

        # Act
        self.data.set_xpath(xpath, "down here")
        node = next(self.data.get_xpath(xpath))
        root = node.get_root()

        # Assert
        self.assertEqual(node.xpath, xpath)
        self.assertEqual(node.value, "down here")
        self.assertEqual(repr(node.get_schema()), "<libyang.schema.Leaf: deep string>")
        self.assertEqual(
            repr(root), "<libyang.data.DataNode: /minimal-integrationtest:nesting>"
        )

    def test_dump_datanodes(self):
        """
        libyang definetely keeps track of insertion order.

        If we change the order of the set_xpath()'s operations we will get a different
        order in the results.
        """
        # Arrange
        xpath = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep"
        xpath2 = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2"
        xpath3 = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3"
        xpath4 = "/minimal-integrationtest:types/str1"

        # Act
        self.data.set_xpath(xpath, "down here")
        self.data.set_xpath(xpath2, "down here too")
        self.data.set_xpath(xpath3, "im down here too")
        self.data.set_xpath(xpath4, "top level string")

        results = list(self.data.dump_datanodes())

        # Assert
        expected_results = [
            "<libyang.data.DataNode: /minimal-integrationtest:nesting>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3>",
            "<libyang.data.DataNode: /minimal-integrationtest:types>",
            "<libyang.data.DataNode: /minimal-integrationtest:types/str1>",
        ]

        for result in results:
            self.assertEqual(expected_results.pop(0), repr(result))

    def test_dump_datanodes_starting_at_top_branch(self):
        # Arrange
        xpath0 = "/minimal-integrationtest:nesting"
        xpath1 = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep"
        xpath2 = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2"
        xpath3 = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3"
        xpath4 = "/minimal-integrationtest:types/str1"

        # Act
        self.data.set_xpath(xpath1, "down here")
        self.data.set_xpath(xpath2, "down here too")
        self.data.set_xpath(xpath3, "im down here too")
        self.data.set_xpath(xpath4, "top level string")

        node = next(self.data.get_xpath(xpath0))
        results = list(self.data.dump_datanodes(start_node=node))

        # Assert
        expected_results = [
            "<libyang.data.DataNode: /minimal-integrationtest:nesting>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3>",
            "shit",
        ]

        for result in results:
            self.assertEqual(expected_results.pop(0), repr(result))

    def test_dump_datanodes_starting_deeper_down_the_data_tree(self):
        """ """
        # Arrange
        xpath = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep"
        xpath2 = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2"
        xpath3 = "/minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3"
        xpath4 = "/minimal-integrationtest:types/str1"

        # Act
        self.data.set_xpath(xpath, "down here")
        self.data.set_xpath(xpath2, "down here too")
        self.data.set_xpath(xpath3, "im down here too")
        self.data.set_xpath(xpath4, "top level string")

        node = next(self.data.get_xpath(xpath2))
        results = list(self.data.dump_datanodes(start_node=node))

        # Assert
        expected_results = [
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep2>",
            "<libyang.data.DataNode: /minimal-integrationtest:nesting/bronze/silver/gold/platinum/deep3>",
            "<libyang.data.DataNode: /minimal-integrationtest:types>",
            "<libyang.data.DataNode: /minimal-integrationtest:types/str1>",
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

    def test_libyang_1_0_130_defect_with_setting_invalid_data(self):
        # Arrange
        xpath = "/minimal-integrationtest:types/enumeratio"

        # Act
        self.data.set_xpath(xpath, "A")

        self.assertEqual(next(self.data.get_xpath(xpath)).value, "A")

        # Act
        self.data.set_xpath(xpath, "C")

        self.assertEqual(next(self.data.get_xpath(xpath)).value, "A")

    def test_deleting_a_list_element_from_a_list(self):
        # Arrange
        payload = (
            '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><collection>'
            "<x>a</x></collection><collection><x>b</x><y>b</y></collection><collection><x>c</x>"
            "</collection></types>"
        )

        # Act
        self.data.loads(payload, libyang.lib.LYD_XML)
        self.data.delete_xpath("/minimal-integrationtest:types/collection[x='b']")

        # Assert
        expected_result = (
            '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest">'
            "<collection><x>a</x></collection><collection><x>c</x></collection></types>"
        )

        self.assertEqual(self.data.dumps(), expected_result)

    def test_deleting_a_presence_container_that_is_empty(self):
        # Arrange
        self.maxDiff = None
        payload = (
            '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><collection>'
            "<x>a</x></collection><collection><x>b</x><y>b</y><z><zzz/></z></collection><collection><x>c</x>"
            "</collection></types>"
        )

        # Act
        self.data.loads(payload, libyang.lib.LYD_XML)
        self.data.delete_xpath("/minimal-integrationtest:types/collection[x='b']/z/zzz")

        # Assert

        expected_result = (
            '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest">'
            "<collection><x>a</x></collection><collection><x>b</x><y>b</y><z/>"
            "</collection><collection><x>c</x></collection></types>"
        )

        self.assertEqual(self.data.dumps(), expected_result)

    def test_deleting_a_presence_container_that_is_populated_and_then_trying_to_delete_its_contents(
        self,
    ):
        # Arrange
        self.maxDiff = None
        payload = (
            '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><collection>'
            "<x>a</x></collection><collection><x>b</x><y>b</y><z><zzz/></z></collection><collection><x>c</x>"
            "</collection></types>"
        )

        # Act
        self.data.loads(payload, libyang.lib.LYD_XML)
        self.data.delete_xpath("/minimal-integrationtest:types/collection[x='b']/z")

        # Assert

        expected_result = (
            '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest">'
            "<collection><x>a</x></collection><collection><x>b</x><y>b</y>"
            "</collection><collection><x>c</x></collection></types>"
        )

        self.assertEqual(self.data.dumps(), expected_result)

        self.data.delete_xpath("/minimal-integrationtest:types/collection[x='b']/z/zzz")

    def test_dumps_a_subtree(
        self,
    ):
        # Arrange
        self.maxDiff = None
        payload = (
            '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><collection>'
            "<x>a</x></collection><collection><x>b</x><y>b</y><z><zzz/></z></collection><collection><x>c</x>"
            "</collection></types>"
        )

        # Act
        self.data.loads(payload, libyang.lib.LYD_XML)
        self.data.delete_xpath("/minimal-integrationtest:types/collection[x='b']/z")

        # Assert

        expected_result = (
            '<x xmlns="http://mellon-collie.net/yang/minimal-integrationtest">a</x>'
        )
        self.assertEqual(
            self.data.subdumps("/minimal-integrationtest:types/collection/x"),
            expected_result,
        )

    def test_dumps_a_subtree_with_traversing_to_parent(
        self,
    ):
        # Arrange
        self.maxDiff = None
        payload = (
            '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><collection>'
            "<x>a</x></collection><collection><x>b</x><y>b</y><z><zzz/></z></collection><collection><x>c</x>"
            "</collection></types>"
        )

        # Act
        self.data.loads(payload, libyang.lib.LYD_XML)
        self.data.delete_xpath("/minimal-integrationtest:types/collection[x='b']/z")

        # Assert

        expected_result = (
            '<collection xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><x>a</x></collection>'
            '<collection xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><x>b</x><y>b</y></collection>'
            '<collection xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><x>c</x></collection>'
        )

        self.assertEqual(
            self.data.subdumps(
                "/minimal-integrationtest:types/collection/x", select_parent=True
            ),
            expected_result,
        )

    def test_merge_remove_tags(self):
        payload_one = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest">
        <a>AA</a><b>BB</b><metal><iron><ore>AAA</ore></iron><nickel><coin>money</coin></nickel></metal></metals>"""
        self.data.loads(payload_one)

        payload_two = """<metals xmlns="http://mellon-collie.net/yang/minimal-integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <a>AA</a><b>BB</b><metal><iron><ore nc:operation="remove">AAA</ore></iron><nickel><coin>money</coin></nickel></metal></metals>"""

        self.data.advanced_merges(payload_two)

        # Assert
        xpath = '/minimal-integrationtest:metals[a="AA"][b="BB"]'
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/iron/ore")).value, "a"
        )
        self.assertEqual(
            next(self.data.get_xpath(xpath + "/metal/nickel/coin")).value, "money"
        )

    def test_merge_complex_tags_delete_simple(self):
        self.data.load("newtests/yang/base.xml")
        with open("newtests/yang/template1.xml") as template:
            self.data.advanced_merges(template.read())

        result = self.data.dumps()
        expected = ""
        with open("newtests/yang/answer1.xml") as expected_fh:
            for line in expected_fh:
                expected += line.strip()
            self.assertEqual(result, expected)

    def test_merge_complex_tags_delete_lists(self):
        self.data.load("newtests/yang/base.xml")
        with open("newtests/yang/template3.xml") as template:
            self.data.advanced_merges(template.read())

        result = self.data.dumps()
        expected = ""
        with open("newtests/yang/answer3.xml") as expected_fh:
            for line in expected_fh:
                expected += line.strip()
            self.assertEqual(result, expected)

    def test_merge_complex_tags_replace_location(self):
        self.data.load("newtests/yang/base.xml")
        with open("newtests/yang/template2.xml") as template:
            self.data.advanced_merges(template.read())

        result = self.data.dumps()
        expected = ""
        self.maxDiff = None
        with open("newtests/yang/answer2.xml") as expected_fh:
            for line in expected_fh:
                expected += line.strip()
            self.assertEqual(result, expected)

    def test_merge_complex_tags_replace_container(self):
        self.data.load("newtests/yang/base.xml")
        with open("newtests/yang/template4.xml") as template:
            self.data.advanced_merges(template.read())

        result = self.data.dumps()
        expected = ""
        self.maxDiff = None
        with open("newtests/yang/answer4.xml") as expected_fh:
            for line in expected_fh:
                expected += line.strip()
            self.assertEqual(result, expected)

    def test_merge_multiple_attributes(self):
        self.data.load("newtests/yang/base.xml")
        with open("newtests/yang/template5.xml") as template:
            self.data.advanced_merges(template.read())

        result = self.data.dumps()
        expected = ""
        self.maxDiff = None
        with open("newtests/yang/answer5.xml") as expected_fh:
            for line in expected_fh:
                expected += line.strip()
            self.assertEqual(result, expected)

    def test_advanced_merge_creating_an_invalid_result(self):
        self.data.set_xpath("/minimal-integrationtest:merges/a", "a")
        with self.assertRaises(libyang.util.LibyangError) as err:
            self.data.advanced_merge("newtests/yang/template6.xml")
        self.assertTrue('Must condition "../a" not satisfied.' in str(err.exception))

    def test_advanced_merges_creating_an_invalid_result(self):
        self.data.set_xpath("/minimal-integrationtest:merges/a", "a")
        with self.assertRaises(libyang.util.LibyangError) as err:
            with open("newtests/yang/template6.xml") as template:
                self.data.advanced_merges(template.read())

        self.assertTrue('Must condition "../a" not satisfied.' in str(err.exception))

    def test_advanced_merge_creating_an_invalid_template(self):
        self.data.set_xpath("/minimal-integrationtest:merges/a", "a")

        # Act
        with self.assertRaises(libyang.util.LibyangError) as err:
            self.data.advanced_merge("newtests/yang/mergetestbad.xml")

        # Assert
        self.assertEqual(
            str(err.exception),
            (
                'Marshalling Error: /metals/a: Data after closing element tag "a".\n'
                "\n"
                "Carefully check\n"
                " - the data has valid values according to the minimal-integrationtest yang model\n"
                " - the structure of the xml is well formed and free from syntax issues\n"
                " - there are no additional nodes that are not part of the minimal-integrationtest yang model\n"
                " - all mandatory conditions, leaf-refs, must and when expressions are satisfied\n"
            ),
        )

    def test_advanced_merges_creating_an_invalid_invalidtemplate(self):
        self.data.set_xpath("/minimal-integrationtest:merges/a", "a")
        with self.assertRaises(libyang.util.LibyangError) as err:
            with open("newtests/yang/mergetestbad.json") as template:
                self.data.advanced_merges(template.read(), 2)

        # Assert
        self.assertEqual(
            str(err.exception),
            (
                'Marshalling Error: Unknown element "metals".\n'
                "\n"
                "Carefully check\n"
                " - the data has valid values according to the minimal-integrationtest yang model\n"
                " - the structure of the json is well formed and free from syntax issues\n"
                " - there are no excess commas, or comments in the JSON payload\n"
                " - there are no additional nodes that are not part of the minimal-integrationtest yang model\n"
                " - all mandatory conditions, leaf-refs, must and when expressions are satisfied\n"
            ),
        )

    def test_advanced_merge_json(self):
        self.data.set_xpath("/minimal-integrationtest:merges/a", "a")
        with open("newtests/yang/mergetest.json") as template:
            self.data.advanced_merges(template.read(), 2)

        # Assert
        self.assertEqual(
            self.data.dumps(2),
            '{"minimal-integrationtest:merges":{"a":"a"},"minimal-integrationtest:metals":[{"a":"a","b":"b"}]}',
        )

    def test_ipv4addresses(self):
        xpath = "/minimal-integrationtest:ip/minimal-integrationtest:ipv4"
        self.data.set_xpath(xpath, "10.4.4.4/8")

        node = next(self.data.get_xpath(xpath))
        self.assertEqual(node.value, "10.0.0.0/8")

        xpath = "/minimal-integrationtest:ip/minimal-integrationtest:v4[prefix='10.4.4.4/8']"
        self.data.set_xpath(xpath, "")

        node = next(self.data.get_xpath(xpath + "/prefix"))
        self.assertEqual(node.value, "10.0.0.0/8")

        xpath = (
            "/minimal-integrationtest:ip/minimal-integrationtest:four[.='10.4.4.4/16']"
        )
        self.data.set_xpath(xpath, "")

        node = next(self.data.get_xpath(xpath))
        self.assertEqual(node.value, "10.4.0.0/16")

    def test_ipv6addresses_test2(self):
        xpath = "/minimal-integrationtest:ip/minimal-integrationtest:ipv6"
        self.data.set_xpath(xpath, "1:2:3::1/126")

        node = next(self.data.get_xpath(xpath))
        self.assertEqual(node.value, "1:2:3::/126")

        xpath = "/minimal-integrationtest:ip/minimal-integrationtest:v6[prefix='1:2:3::1/126']"
        self.data.set_xpath(xpath, "")

        node = next(self.data.get_xpath(xpath + "/prefix"))
        self.assertEqual(node.value, "1:2:3::/126")

        xpath = (
            "/minimal-integrationtest:ip/minimal-integrationtest:six[.='1:2:3::1/126']"
        )
        self.data.set_xpath(xpath, "")

        node = next(self.data.get_xpath(xpath))
        self.assertEqual(node.value, "1:2:3::/126")

    def test_ipv6addresses(self):
        xpath = "/minimal-integrationtest:ip/minimal-integrationtest:ipv6"
        self.data.set_xpath(xpath, "2001:8d8:100f:f000::2e1/32")

        node = next(self.data.get_xpath(xpath))
        self.assertEqual(node.value, "2001:8d8::/32")

        xpath = "/minimal-integrationtest:ip/minimal-integrationtest:v6[prefix='2001:8d8:100f:f000::2e1/32']"
        self.data.set_xpath(xpath, "")

        node = next(self.data.get_xpath(xpath + "/prefix"))
        self.assertEqual(node.value, "2001:8d8::/32")

        xpath = "/minimal-integrationtest:ip/minimal-integrationtest:six[.='2001:8d8:100f:f000::2e1/48']"
        self.data.set_xpath(xpath, "")

        node = next(self.data.get_xpath(xpath))
        self.assertEqual(node.value, "2001:8d8:100f::/48")

    def test_when_must_extraction(self):

        node = next(self.ctx.find_path("/minimal-integrationtest:nesting"))
        self.assertEqual(node.when_condition(), None)

        prefix = "/minimal-integrationtest:types/minimal-integrationtest:when-condition"

        # a container with a when and a must
        node = next(self.ctx.find_path(prefix))
        self.assertEqual(node.when_condition(), "../str1='z'")
        self.assertListEqual(
            list(node.must_conditions()), ["../str1!='a'", "../str2!='z'"]
        )

        # a leaf with a when
        node = next(self.ctx.find_path(prefix + "/minimal-integrationtest:a"))
        self.assertEqual(node.when_condition(), "../b='a'")

        #  a leaf with a must
        node = next(self.ctx.find_path(prefix + "/minimal-integrationtest:c"))
        self.assertListEqual(list(node.must_conditions()), ["../b='b'"])

        # leaf lists supports whens and musts
        node = next(self.ctx.find_path(prefix + "/minimal-integrationtest:d"))
        self.assertListEqual(list(node.must_conditions()), ["../b!='a'"])
        self.assertEqual(node.when_condition(), "../a='z'")

        # lists support whens and musts
        node = next(self.ctx.find_path(prefix + "/minimal-integrationtest:e"))
        self.assertListEqual(list(node.must_conditions()), ["../b='brewyork'"])
        self.assertEqual(node.when_condition(), "../a='z'")

        # Choices support when's but not musts - but libyang-python (robin jarry's code)
        # doesn't support Choices as an object type
        prefix += "/minimal-integrationtest:beer"
        node = next(self.ctx.find_path(prefix))
        # self.assertEqual(node.when_condition(), "../a='z'")
        # self.assertListEqual(list(node.must_conditions()), ["../b='just-a-couple'"])

        # Cases - upstream doesn't support the cases a specifically in the schema.
        # really need to rebase my fork from robin jarry's original project to
        # libyang-python and then contribute the choice/case schema objects bakc
        # upstream.
        prefix2 = prefix + "/minimal-integrationtest:jackhammer"
        node = next(self.ctx.find_path(prefix2 + "/minimal-integrationtest:bitter"))
        self.assertListEqual(list(node.must_conditions()), ["../b='just-a-couple'"])

        prefix2 = prefix + "/minimal-integrationtest:johnbiscotti"
        node = next(
            self.ctx.find_path(prefix2 + "/minimal-integrationtest:pastrystout")
        )
        self.assertListEqual(list(node.must_conditions()), ["../b='have-just-one'"])

    def test_parent(self):
        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='l[/]\"ist']/z/zzz"
        value = ""

        # Act
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath))

        self.assertEqual(
            result.parent().xpath,
            "/minimal-integrationtest:types/collection[x='l[/]\"ist']/z",
        )
        self.assertEqual(
            result.parent().parent().xpath,
            "/minimal-integrationtest:types/collection[x='l[/]\"ist']",
        )
        self.assertEqual(
            result.parent().parent().parent().xpath, "/minimal-integrationtest:types"
        )

    def test_get_list_key_values(self):
        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='xxx']/inner[a='A'][b='B']/e[.='ll1']"
        value = ""

        # Act / Assert
        self.data.set_xpath(xpath, value)
        datanode = next(self.data.get_xpath(xpath))

        self.assertEqual(datanode.xpath, xpath)

        with self.assertRaises(libyang.util.LibyangError) as err:
            next(datanode.get_list_key_values())
        self.assertTrue(
            "cannot extract list keys from non-list node" in str(err.exception)
        )

        result = list(datanode.parent().get_list_key_values())
        self.assertEqual(result, [("a", "A"), ("b", "B")])

        root = next(self.data.get_xpath(BASE_XPATH + ":types/collection"))
        result = list(root.get_list_key_values(datanode.parent()))
        self.assertEqual(result, [("a", "A"), ("b", "B")])

    def test_get_all_list_key_values(self):
        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='xxx']/inner[a='A'][b='B']/e[.='ll1']"
        value = ""

        # Act / Assert
        self.data.set_xpath(xpath, value)
        datanode = next(self.data.get_xpath(xpath))

        self.assertEqual(datanode.xpath, xpath)

        result = list(datanode.get_all_list_key_values())
        self.assertEqual(result, [("x", "xxx"), ("a", "A"), ("b", "B")])

        xpath = BASE_XPATH + ":types/collection[x='xxx']/inner[a='A'][b='B']/g"
        value = "true"

        # Act / Assert
        self.data.set_xpath(xpath, value)
        datanode = next(self.data.get_xpath(xpath))

        self.assertEqual(datanode.xpath, xpath)

        result = list(datanode.get_all_list_key_values())
        self.assertEqual(result, [("x", "xxx"), ("a", "A"), ("b", "B")])

    def test_get_all_node_names(self):
        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='xxx']/inner[a='A'][b='B']/e[.='ll1']"
        value = ""

        # Act / Assert
        self.data.set_xpath(xpath, value)
        datanode = next(self.data.get_xpath(xpath))

        self.assertEqual(datanode.xpath, xpath)
        self.assertEqual(datanode.name, "e")
        self.assertEqual(datanode.parent().name, "inner")

        result = list(datanode.get_all_node_names())
        self.assertEqual(result, ["types", "collection", "inner", "e"])

        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='xxx']/inner[a='A'][b='B']/g"
        value = "a"

        # Act / Assert
        self.data.set_xpath(xpath, value)
        datanode = next(self.data.get_xpath(xpath))

        self.assertEqual(datanode.xpath, xpath)
        self.assertEqual(datanode.name, "g")
        self.assertEqual(datanode.parent().name, "inner")

        result = list(datanode.get_all_node_names())
        self.assertEqual(result, ["types", "collection", "inner", "g"])

        # Arrange
        xpath = BASE_XPATH + ":types/collection[x='xxx']/inner[a='A'][b='B']/g"
        value = "true"

        # Act / Assert
        self.data.set_xpath(xpath, value)
        datanode = next(self.data.get_xpath(xpath))

        self.assertEqual(datanode.xpath, xpath)
        self.assertEqual(datanode.name, "g")
        self.assertEqual(datanode.parent().name, "inner")

        result = list(datanode.get_all_node_names())
        self.assertEqual(result, ["types", "collection", "inner", "g"])

    def test_insert_attribute_onto_an_existing_data_node(self):
        # Arrange
        xpath1 = BASE_XPATH + ":types/str1"
        value1 = "HELLO"
        self.data.set_xpath(xpath1, value1)
        self.data.insert_attribute(xpath1, "ietf-netconf", "operation", "remove")
        self.assertEqual(
            self.data.dumps(),
            (
                '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"'
                ' xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">'
                '<str1 nc:operation="remove">HELLO</str1></types>'
            ),
        )

    def test_insert_attribute_onto_an_existing_data_node_from_our_yang_model(self):
        # Arrange
        xpath1 = BASE_XPATH + ":types/str1"
        value1 = "HELLO"
        xpath2 = BASE_XPATH + ":types/u_int_8"

        self.data.set_xpath(xpath1, value1)
        self.data.insert_attribute(xpath1, "ietf-netconf", "operation", "remove")
        self.data.insert_attribute(
            xpath1, "minimal-integrationtest", "my-second-annotation", "boo"
        )
        self.data.insert_attribute(
            xpath1, "minimal-intnegrationtest", "my-annotation", "hoo"
        )
        self.data.insert_attribute(xpath1, None, "my-annotation", "hoo")
        self.data.insert_attribute(xpath1, "other", "my-foreign-annotation", "bonjour")

        self.assertEqual(self.data.get_attribute(xpath1, "my-annotation"), "hoo")

        self.assertEqual(
            self.data.get_attribute(xpath1, "my-annotation-not-existing"), None
        )

        with self.assertRaises(libyang.util.DataXpathDoesNotExistError):
            self.data.get_attribute(xpath2, "my-annotation-not-existing")

        self.assertEqual(self.data.get_attribute(xpath1, "my-second-annotation"), "boo")
        self.assertEqual(
            self.data.get_attribute(xpath1, "my-foreign-annotation"), "bonjour"
        )
        self.assertEqual(self.data.get_attribute(xpath1, "operation"), "remove")
        self.assertEqual(
            list(self.data.get_attributes(xpath1)),
            [
                ("operation", "remove"),
                ("my-second-annotation", "boo"),
                ("my-annotation", "hoo"),
                ("my-foreign-annotation", "bonjour"),
            ],
        )

        self.assertEqual(
            self.data.dumps(),
            (
                '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"'
                ' xmlns:other="http://mellon-collie.net/yang/other"'
                ' xmlns:mit="http://mellon-collie.net/yang/minimal-integrationtest"'
                ' xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">'
                '<str1 nc:operation="remove" mit:my-second-annotation="boo"'
                ' mit:my-annotation="hoo"'
                ' other:my-foreign-annotation="bonjour">HELLO</str1></types>'
            ),
        )

        self.data.remove_attribute(xpath1, "my-second-annotation")
        self.assertEqual(
            self.data.dumps(),
            (
                '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"'
                ' xmlns:other="http://mellon-collie.net/yang/other"'
                ' xmlns:mit="http://mellon-collie.net/yang/minimal-integrationtest"'
                ' xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">'
                '<str1 nc:operation="remove"'
                ' mit:my-annotation="hoo"'
                ' other:my-foreign-annotation="bonjour">HELLO</str1></types>'
            ),
        )

    def test_remove_attribute_from_a_data_node(self):
        # Arrange
        xpath1 = BASE_XPATH + ":types/str1"
        xpath2 = BASE_XPATH + ":types/u_int_8_x"
        value1 = "HELLO"
        self.data.set_xpath(xpath1, value1)
        self.data.insert_attribute(xpath1, "ietf-netconf", "operation", "remove")
        self.assertEqual(
            self.data.dumps(),
            (
                '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"'
                ' xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">'
                '<str1 nc:operation="remove">HELLO</str1></types>'
            ),
        )

        self.data.remove_attribute(xpath1, "operation", "replace")
        self.assertEqual(
            self.data.dumps(),
            (
                '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"'
                ' xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">'
                '<str1 nc:operation="remove">HELLO</str1></types>'
            ),
        )

        self.data.remove_attribute(xpath1, "operation", "remove")
        self.assertEqual(
            self.data.dumps(),
            (
                '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest">'
                "<str1>HELLO</str1></types>"
            ),
        )

        self.data.insert_attribute(xpath1, "ietf-netconf", "operation", "remove")
        self.assertEqual(
            self.data.dumps(),
            (
                '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest"'
                ' xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">'
                '<str1 nc:operation="remove">HELLO</str1></types>'
            ),
        )
        self.data.remove_attribute(xpath1, "operation")
        self.assertEqual(
            self.data.dumps(),
            (
                '<types xmlns="http://mellon-collie.net/yang/minimal-integrationtest">'
                "<str1>HELLO</str1></types>"
            ),
        )

        self.data.remove_attribute(xpath1, "non_existing_attribute")

        with self.assertRaises(libyang.util.DataXpathDoesNotExistError):
            self.data.remove_attribute(xpath2, "operation")

    def test_insert_attribute_onto_an_existing_data_node_not_set(self):
        # Arrange
        xpath1 = BASE_XPATH + ":types/str1"
        value1 = "HELLO"
        self.data.set_xpath(xpath1, value1)
        with self.assertRaises(libyang.util.AttributeCannotBeSetError) as err:
            self.data.insert_attribute(
                xpath1, "non_existing_module", "operation", "remove"
            )

        # Assert
        self.assertEqual(
            (
                'The attribute non_existing_module:operation could not be set to "remove"\n'
                "XPATH: /minimal-integrationtest:types/str1\n"
            ),
            str(err.exception),
        )

    def test_insert_attribute_onto_an_existing_data_node_not_exists(self):
        # Arrange
        xpath1 = BASE_XPATH + ":types/str1"
        with self.assertRaises(libyang.util.DataXpathDoesNotExistError) as err:
            self.data.insert_attribute(
                xpath1, "non_existing_module", "operation", "remove"
            )

        # Assert
        self.assertEqual(
            (
                "The provided XPATH did not provide any results - check the XPATH\n"
                "XPATH: /minimal-integrationtest:types/str1\n"
            ),
            str(err.exception),
        )

    def test_inserting_into_augmented_containers(self):
        # Act
        xpath = BASE_XPATH + ":augments/go-in-here/other:room"
        value = "kitchen"
        self.data.set_xpath(xpath, value)
        result = next(self.data.get_xpath(xpath)).value

        # Assert
        self.assertEqual(result, value)

        xpath = (
            BASE_XPATH
            + ":augments/go-in-here/other:cupboards[cupboard='big']/shelves[shelf='topshelf']/front/items[.='cup']"
        )
        self.data.set_xpath(xpath, "")

        self.assertEqual(
            self.data.dumps(2),
            (
                '{"minimal-integrationtest:augments":{"go-in-here":{"other:room":"kitchen",'
                '"other:cupboards":[{"cupboard":"big","shelves":[{"shelf":"topshelf","front":{"items":["cup"]}}]}]}}}'
            ),
        )
        self.assertEqual(
            self.data.dumps(),
            (
                '<augments xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><go-in-here>'
                '<room xmlns="http://mellon-collie.net/yang/other">kitchen</room><cupboards '
                'xmlns="http://mellon-collie.net/yang/other"><cupboard>big</cupboard><shelves><shelf>'
                "topshelf</shelf><front><items>cup</items></front></shelves></cupboards></go-in-here></augments>"
            ),
        )

    def test_loading_with_augmented_data_tress(self):
        # Act
        xpath = BASE_XPATH + ":augments/go-in-here/other:room"
        value = "kitchen"
        self.data.set_xpath(xpath, value)

        # Act
        self.data.merges(
            (
                '{"minimal-integrationtest:augments":{"go-in-here":{"other:room":"bathroom",'
                '"other:cupboards":[{"cupboard":"big","shelves":'
                '[{"shelf":"topshelf","front":{"items":["toothbrush"]}}]}]}}}'
            ),
            2,
        )

        # Assert
        self.assertEqual(
            self.data.dumps(),
            (
                '<augments xmlns="http://mellon-collie.net/yang/minimal-integrationtest"><go-in-here>'
                '<room xmlns="http://mellon-collie.net/yang/other">bathroom</room><cupboards '
                'xmlns="http://mellon-collie.net/yang/other"><cupboard>big</cupboard><shelves><shelf>'
                "topshelf</shelf><front><items>toothbrush</items></front></shelves></cupboards></go-in-here></augments>"
            ),
        )
