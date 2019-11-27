import libyang
ctx=libyang.Context('/Users/adam/python-yang-voodoo/yang')
ctx.load_module('integrationtest')
data=libyang.DataTree(ctx)
data.set_xpath('/integrationtest:simpleleaf', 'A')
data.set_xpath('/integrationtest:validator/mandatories', '')
#data.set_xpath('/integrationtest:validator/mandatories/this-is-mandatory', 'th')
data.validate()
