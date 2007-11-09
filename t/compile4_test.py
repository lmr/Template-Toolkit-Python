import os
import shutil

from template.test import TestCase, main


class CompileTest(TestCase):
  def testCompile(self):
    dir = os.path.abspath("test")
    cdir = os.path.join(dir, "tmp", "cache")
    ttcfg = { "POST_CHOMP": 1,
              "INCLUDE_PATH": os.path.join(dir, "src"),
              "COMPILE_DIR": cdir,
              "COMPILE_EXT": ".ttc",
              "ABSOLUTE": 1 }
    if os.path.exists(cdir):
      shutil.rmtree(cdir)
    os.makedirs(cdir)
    self.Expect(DATA, ttcfg, { "root": dir })


DATA = r"""
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
[% TRY %]
[% INCLUDE bar/baz word = 'wibble' %]
[% CATCH file %]
Error: [% error.type %] - [% error.info %]
[% END %]
-- expect --
This is file baz
The word is 'wibble'

-- test --
[% INCLUDE "$root/src/blam" %]
-- expect --
This is the blam file
"""

main()

