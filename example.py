#
#  Simple "Hello world!" program.
#

import template
from template import util

TEMPLATE_TEXT = "Hello [% thing %]!"

t = template.Template()
if not t.process(util.Reference(TEMPLATE_TEXT), {"thing": "world"}):
    print "ERROR: %s" % (t.error(),)
    
