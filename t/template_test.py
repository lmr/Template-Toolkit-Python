from template import Template, TemplateException
from template.util import StringBuffer
from template.test import TestCase, main


class TemplateTest(TestCase):
  def testTemplate(self):
    out = StringBuffer()
    tt = Template({ "INCLUDE_PATH": "test/src:test/lib",
                    "OUTPUT": out })
    tt.process("header")
    self.assert_(out.get())
    out.clear()
    try:
      tt.process("this_file_does_not_exist")
      self.fail("exception not raised")
    except TemplateException, e:
      self.assertEquals("file", e.type())
      self.assertEquals("this_file_does_not_exist: not found", e.info())


main()
