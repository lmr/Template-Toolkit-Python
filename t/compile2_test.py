import os

from template import Template
from template.test import TestCase, main


class CompileTest(TestCase):
  def testCompile(self):
    ttcfg = { "POST_CHOMP": 1,
              "INCLUDE_PATH": "test/src",
              "COMPILE_EXT": ".ttc" }
    # Check that compiled template files exist.
    compiled = "test/src/foo.ttc"
    self.assert_(os.path.exists(compiled))
    self.assert_(os.path.exists("test/src/complex.ttc"))

    # Ensure template metadata is saved in compiled file.
    output = Template(ttcfg).process("baz", { "showname": 1 })
    self.assertNotEqual(-1, output.find("name: baz"))

    # We're going to hack on the foo.ttc file to change some key text.
    # This way we can tell that the template was loaded from the compiled
    # version and not the source.
    fh = open(compiled, "r+")
    stat = os.fstat(fh.fileno())
    foo = fh.read()
    fh.seek(0)
    fh.write(foo.replace("the foo file", "the hacked foo file"))
    fh.close()
    os.utime(compiled, (stat.st_atime, stat.st_mtime))

    self.Expect(DATA, ttcfg)


DATA = r"""
-- test --
[% INCLUDE foo a = 'any value' %]
-- expect --
This is the hacked foo file, a is any value

-- test --
[% META author => 'billg' version => 6.66  %]
[% INCLUDE complex %]
-- expect --
This is the header, title: Yet Another Template Test
This is a more complex file which includes some BLOCK definitions
This is the footer, author: billg, version: 6.66
- 3 - 2 - 1 

-- test --
[% META author => 'billg' version => 6.66  %]
[% INCLUDE complex %]
-- expect --
This is the header, title: Yet Another Template Test
This is a more complex file which includes some BLOCK definitions
This is the footer, author: billg, version: 6.66
- 3 - 2 - 1 

"""

main()

