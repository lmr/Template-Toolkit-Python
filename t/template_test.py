from template import Template
from template.util import StringBuffer
from template.test import TestCase, main


class TemplateTest(TestCase):
  def testTemplate(self):
    out = StringBuffer()
    tt = Template({ "INCLUDE_PATH": "test/src:test/lib",
                    "OUTPUT": out })
    self.assert_(tt.process("header"))
    self.assert_(out.get())
    out.clear()
    self.assert_(not tt.process("this_file_does_not_exist"))
    error = tt.error()
    self.assertEquals("file", error.type())
    self.assertEquals("this_file_does_not_exist: not found", error.info())
    output = []
    tt.process("header", None, output)
    self.assert_(output[-1])
    called = [False]
    def myout(*_):
      called[0] = True
    tt.process("header", None, myout)
    self.assert_(called[0])
    class Myout:
      def __init__(self):
        self.called = False
      def write(self, *_):
        self.called = True
    obj = Myout()
    tt.process("header", None, obj)
    self.assert_(obj.called)


main()
