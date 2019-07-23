import libyang

context = libyang.Context("/Users/adam/python-yang-voodoo/yang")
context.load_module("integrationtest")


data = libyang.Data(context)
data.set_data_by_xpath("/integrationtest:simpleleaf", "B")
# data.set_data_by_xpath("/integrationtest:simpleleaf", "C")
# data.set_data_by_xpath("/integrationtest:dirty-secret", "AX")
# data.set_data_by_xpath("/integrationtest:default", "no-longer-default")
# data.load_from_file("/tmp/x.xml", doc_id=0, format="json")
# data.save_to_file("/tmp/x2.xml", format="json")
# data.save_to_file("/tmp/x0.xml", format="json")
#
#
# data.set_data_by_xpath("/integrationtest:simpleleaf", "Z", doc_id=1)
# data.set_data_by_xpath("/integrationtest:simpleleaf", "Z", doc_id=1)
# data.set_data_by_xpath("/integrationtest:morecomplex/inner/siblings/a","AAAAAaaaa", doc_id=1)
# data.save_to_file("/tmp/x3.xml", doc_id=1, format="json")
print('-' *80)
print(data.get_data_by_xpath("/integrationtest:simpleleaf"))
print('-' *80)
# data.diff()
