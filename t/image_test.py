import os
import sys

from template.test import TestCase, main

try:
  import PIL
except ImportError:
  print >>sys.stderr, "Failed to import PIL module; skipping test"
  sys.exit(0)

class ImageTest(TestCase):
  def testImage(self):
    dir = os.path.join(os.pardir, "images")
    vars = { "dir": dir,
             "file": { "logo": os.path.join(dir, "ttdotorg.gif"),
                       "power": os.path.join(dir, "tt2power.gif"),
                       "lname": "ttdotorg.gif" } }
    self.Expect(DATA, None, vars)


DATA = r"""
-- test --
[% USE Image(file.logo) -%]
file: [% Image.file %]
size: [% Image.size.join(', ') %]
width: [% Image.width %]
height: [% Image.height %]
-- expect --
-- process --
file: [% file.logo %]
size: 110, 60
width: 110
height: 60

-- test --
[% USE image( name = file.power) -%]
name: [% image.name %]
file: [% image.file %]
width: [% image.width %]
height: [% image.height %]
size: [% image.size.join(', ') %]
-- expect --
-- process --
name: [% file.power %]
file: [% file.power %]
width: 78
height: 47
size: 78, 47

-- test --
[% USE image file.logo -%]
attr: [% image.attr %]
-- expect --
attr: width="110" height="60"

-- test --
[% USE image file.logo -%]
tag: [% image.tag %]
tag: [% image.tag(class="myimage", alt="image") %]
-- expect --
-- process --
tag: <img src="[% file.logo %]" width="110" height="60" alt="" />
tag: <img src="[% file.logo %]" width="110" height="60" alt="image" class="myimage" />


# test "root"
-- test --
[% USE image( root=dir name=file.lname ) -%]
[% image.tag %]
-- expect --
-- process --
<img src="[% file.lname %]" width="110" height="60" alt="" />

# test separate file and name
-- test --
[% USE image( file= file.logo  name = "other.jpg" alt="myfile") -%]
[% image.tag %]
-- expect --
<img src="other.jpg" width="110" height="60" alt="myfile" />
"""

main()
