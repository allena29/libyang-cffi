import libyang

context = libyang.Context("/Users/adam/python-yang-voodoo/yang")
context.load_module("integrationtest")


data = libyang.Data(context)
data.set_data_by_xpath("/integrationtest:simpleleaf", "A")
