import os

import template
from template.test import TestCase, main


class MyTemplate(template.Template):
  def __init__(self, *args, **kwargs):
    template.Template.__init__(self, *args, **kwargs)

  MESSAGE = None

  @classmethod
  def DEBUG(cls, *args):
    cls.MESSAGE = "".join(args)


class OutputTest(TestCase):
  def testOutput(self):
    f1 = "foo.bar"
    f2 = "foo.baz"
    file1 = os.path.join("test", "tmp", f1)
    file2 = os.path.join("test", "tmp", f2)
    tt = template.Template({ "INCLUDE_PATH": "test/src:test/lib",
                             "OUTPUT_PATH": "test/tmp" })
    if os.path.exists(file1):
      os.remove(file1)
    self.assert_(tt.process("foo", self._callsign(), f1))
    self.assert_(os.path.exists(file1))
    out = open(file1).read()
    self.assertEquals("This is the foo file, a is alpha", out)
    os.remove(file1)

    tt = template.Template({ "INCLUDE_PATH": "test/src:test/lib",
                             "OUTPUT_PATH": "test/tmp",
                             "OUTPUT": f2 })
    if os.path.exists(file2):
      os.remove(file2)
    self.assert_(tt.process("foo", self._callsign()))
    self.assert_(os.path.exists(file2))
    out = open(file2).read()
    self.assertEquals("This is the foo file, a is alpha", out)
    os.remove(file2)

    template.DEBUG = True
    tt = MyTemplate({ "INCLUDE_PATH": "test/src:test/lib",
                      "OUTPUT_PATH": "test/tmp",
                      "OUTPUT": f2 })
    self.assert_(tt.process("foo", self._callsign(), None, { "binmode": 1 }))
    self.assert_(os.path.exists(file2))
    self.assertEquals("set binmode\n", MyTemplate.MESSAGE)
    MyTemplate.MESSAGE = "reset"
    self.assert_(tt.process("foo", self._callsign(), f2, { "binmode": 1 }))
    self.assert_(os.path.exists(file2))
    self.assertEquals("set binmode\n", MyTemplate.MESSAGE)


main()
