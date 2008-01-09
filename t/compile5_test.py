import os
import re
import shutil

from template.test import TestCase, main


class CompileTest(TestCase):
  def testCompile(self):
    dir = os.path.abspath("test")
    cdir = os.path.join(dir, "tmp", "cache")
    ttcfg = { "POST_CHOMP": 1,
              "INCLUDE_PATH": os.path.join(dir, "src"),
              "COMPILE_DIR": cdir + "/",  # note trailing slash; should be OK
              "COMPILE_EXT": ".ttc",
              "ABSOLUTE": 1 }
    # Check that compiled template files exist.
    def twiddle(*args):
      return tuple(os.path.sep.join((cdir, dir, "src", "%s.ttc" % x))
                   for x in args)
    foo, bar, blam = twiddle("foo", "complex", "blam")
    blam = re.sub(r"/+", "/", blam)
    self.assert_(os.path.exists(foo))
    self.assert_(os.path.exists(bar))
    self.assert_(os.path.exists(blam))

    # We're going to hack on the compiled 'foo' file to change some key text.
    # This way we can tell that the template was loaded from the compiled
    # version and not the source.
    fh = open(foo, "r+")
    stat = os.fstat(fh.fileno())
    text = fh.read()
    fh.seek(0)
    fh.write(text.replace("the foo file", "the newly hacked foo file"))
    fh.close()
    os.utime(foo, (stat.st_atime, stat.st_mtime))
    # Same again for "blam".
    fh = open(blam, "r+")
    stat = os.fstat(fh.fileno())
    text = fh.read()
    fh.seek(0)
    fh.write(text.replace("blam", "wam-bam"))
    fh.close()
    os.utime(blam, (stat.st_atime, stat.st_mtime))

    self.Expect(DATA, ttcfg, { "root": dir })

    if os.path.isdir(cdir):
      shutil.rmtree(cdir)


DATA = r"""
-- test --
[% INCLUDE foo a = 'any value' %]
-- expect --
This is the newly hacked foo file, a is any value

-- test --
[% META author => 'billg' version => 6.66  %]
[% INCLUDE complex %]
-- expect --
This is the header, title: Yet Another Template Test
This is a more complex file which includes some BLOCK definitions
This is the footer, author: billg, version: 6.66
- 3 - 2 - 1 

-- test --
[% INCLUDE "$root/src/blam" %]
-- expect --
This is the wam-bam file
"""

main()
