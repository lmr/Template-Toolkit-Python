import os

from template.test import TestCase, main


class CompileTest(TestCase):
  def testCompile(self):
    ttcfg = { "POST_CHOMP": 1,
              "INCLUDE_PATH": "test/src",
              "COMPILE_EXT": ".ttc",
              "EVAL_PYTHON": 1 }
    for f in "test/src/foo.ttc", "test/src/complex.ttc":
      if os.path.exists(f):
        os.remove(f)
    self.Expect(DATA, ttcfg)
    self.assert_(os.path.exists("test/src/foo.ttc"))
    self.assert_(os.path.exists("test/src/complex.ttc"))


DATA = r"""
-- test --
[% INCLUDE evalpython %]
-- expect --
This file includes a python block.

-- test --
[% TRY %]
[% INCLUDE foo %]
[% CATCH file %]
Error: [% error.type %] - [% error.info %]
[% END %]
-- expect --
This is the foo file, a is 

-- test --
[% META author => 'abw' version => 3.14 %]
[% INCLUDE complex %]
-- expect --
This is the header, title: Yet Another Template Test
This is a more complex file which includes some BLOCK definitions
This is the footer, author: abw, version: 3.14
- 3 - 2 - 1 

-- test --
[% INCLUDE baz %]
-- expect --
This is the baz file, a: 

"""

main()
