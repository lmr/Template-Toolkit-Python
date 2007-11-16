import os
import shutil
import time

from template import Template, TemplateException
from template.test import TestCase, main


def append_file(path, text):
  time.sleep(2)  # Ensure file time stamps are different.
  fh = open(path, "a")
  fh.write(text)
  fh.close()


class CompileTest(TestCase):
  def testCompile(self):
    ttcfg = { "POST_CHOMP": 1,
              "INCLUDE_PATH": "test/src",
              "COMPILE_EXT": ".ttc" }

    # Test process fails when EVAL_PYTHON not set.
    try:
      Template(ttcfg).process("evalpython", {})
      self.fail("did not raise exception")
    except TemplateException, e:
      self.assertEquals("python", e.type())
      self.assertEquals("EVAL_PYTHON not set", e.info())

    # Ensure we can run compiled templates without loading parser.
    ttcfg["EVAL_PYTHON"] = 1
    Template(ttcfg).process("evalpython", {})

    # Check that compiled template file exists and grab modification time.
    path = "test/src/complex"
    self.assert_(os.path.exists(path + ".ttc"))
    mod = os.stat(path + ".ttc")[9]
    # Save copy of the source file because we're going to try to break it.
    shutil.copy(path, path + ".org")
    # Sleep for a couple of seconds to ensure clock has ticked.
    time.sleep(2)
    # Append a harmless newline to the end of the source file to change
    # its modification time.
    append_file(path, "\n")
    # Define "bust_it" to append a lone "[% TRY %]" onto the end of the
    # source file to cause re-compilation to fail.
    replace = { "bust_it": lambda: append_file(path, "[% TRY %]") }

    self.Expect(DATA, ttcfg, replace)
    self.assert_(os.stat(path)[9] > mod)
    # Restore original source file.
    shutil.copy(path + ".org", path)


DATA = r"""
-- test --
[% META author => 'albert' version => 'emc2'  %]
[% INCLUDE complex %]
-- expect --
This is the header, title: Yet Another Template Test
This is a more complex file which includes some BLOCK definitions
This is the footer, author: albert, version: emc2
- 3 - 2 - 1 

-- test --
[%# we want to break 'compile' to check that errors get reported -%]
[% CALL bust_it -%]
[% TRY; INCLUDE complex; CATCH; "$error"; END %]
-- expect --
file error - parse error - complex line 18: unexpected end of input

"""

main()

