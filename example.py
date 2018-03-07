#
#  Simple "Hello world!" program.
#

from template import Template
from template.util import TemplateException

TEMPLATE_TEXT = "Hello [% thing %]!"

t = Template()

try:
    print(t.processString(TEMPLATE_TEXT, { "thing": "world" }))
except TemplateException as e:
    print("ERROR: %s" % e)
