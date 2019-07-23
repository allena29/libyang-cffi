import unittest
import libyang


class test_libyangdata( unittest.TestCase):

    def setUp(self):
        # self.ctx=libyang.Context("/Users/adam/python-yang-voodoo/yang")
        # self.ctx.load_module("integrationtest")
        self.ctx=libyang.Context("/Users/adam/libyang-cffi/my-stuff/yang")
        self.module_name = "minimal-integrationtest"
        #self.module_name = "integrationtest"
        sec =self.ctx.load_module(self.module_name)
        print(sec)
        self.subject = libyang.Data(self.ctx)

    def dump_files(self):
        self.subject.save_to_file("/tmp/x")
        self.subject.save_to_file("/tmp/j", format="json")
    #
    # def test_nested(self):
    #     xpath="/integrte-integrationtest:bronze/silver/gold/platinum/deep"
    #     value = "DOWNHERE"
    #     self.subject.set_data_by_xpath(xpath, value)
    #     self.assertEqual(self.subject.get_data_by_xpath(xpath), value)
    #
    # def test_list(self):
    #     self.subject.set_data_by_xpath("/simple-integrationtest:bronze/silver/gold/platinum/deep", "DOWN HERE")

    def test_leaf_uint8(self):
        #self.module_name = "integrationtest"
        xpath="/" +self.module_name +":types/number-u8"
        schema_xpath="/" +self.module_name +":types/"+ self.module_name+ ":number-u8"
        print(schema_xpath)
        print(list(self.ctx.find_path(schema_xpath)))
        value = 50
        self.subject.set_data_by_xpath(xpath, value)

        result = self.subject.get_data_by_xpath(xpath)
        self.assertEqual(result, value)
        self.dump_files()

    def test_leaf(self):
        #self.module_name = "integrationtest"
        xpath="/" +self.module_name +":simpleleaf"

        print(list(self.ctx.find_path(xpath)))
        value = "UP HERE"
        self.subject.set_data_by_xpath(xpath, value)

        result = self.subject.get_data_by_xpath(xpath)
        self.assertEqual(result, value)
