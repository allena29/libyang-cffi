import libyang

context = libyang.Context("/Users/adam/python-yang-voodoo/yang")
context.load_module("integrationtest")


data = libyang.Data(context)
data.set_data_by_xpath("/integrationtest:simpleleaf", "A")
data.set_data_by_xpath("/integrationtest:dirty-secret", "AX")

data.load_from_file("/tmp/x.xml", doc_id=1, format="json")
data.dump("/tmp/x2.xml", format="json")
data.dump("/tmp/x3.xml", doc_id=1, format="json")
