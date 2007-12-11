import os

from template import Template, util
from template.test import TestCase, main


class InterceptDebug:
  def __init__(self):
    self.message = None

  def __call__(self, *args):
    self.message = "".join(args)


class MyTemplate(Template):
  def __init__(self, *args, **kwargs):
    Template.__init__(self, *args, **kwargs)

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
    if os.path.exists(file1):
      os.remove(file1)
    if os.path.exists(file2):
      os.remove(file2)
    tt = Template({ "INCLUDE_PATH": "test/src:test/lib",
                    "OUTPUT_PATH": "test/tmp",
                    "OUTPUT": f2 })
    tt.process("foo", self._callsign())
    self.assert_(os.path.exists(file2))
    out = open(file2).read()
    self.assertEquals("This is the foo file, a is alpha", out)
    os.remove(file2)

    intercept = InterceptDebug()
    Template.DEBUG = True
    util.Debug = intercept
    tt.process("foo", self._callsign(), { "binmode": 1 })
    self.assert_(os.path.exists(file2))
    self.assertEquals("set binmode\n", intercept.message)
    MyTemplate.MESSAGE = "reset"
    intercept.message = "reset"
    tt.process("foo", self._callsign(), { "binmode": 1 })
    self.assert_(os.path.exists(file2))
    self.assertEquals("set binmode\n", intercept.message)


main()
