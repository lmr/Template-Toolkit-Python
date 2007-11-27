import os

from template import Template
from template.test import TestCase, main


class IncludeTest(TestCase):
  def testInclude(self):
    callsign = self._callsign()
    replace = { "a": callsign["a"],
                "b": callsign["b"],
                "c": { "d": callsign["d"],
                       "e": callsign["e"],
                       "f": { "g": callsign["g"],
                              "h": callsign["h"] } },
                "r": callsign["r"],
                "s": callsign["s"],
                "t": callsign["t"] }
    tproc = Template({ "INTERPOLATE": True,
                       "INCLUDE_PATH": "test/src:test/lib",
                       "TRIM": True,
                       "AUTO_RESET": False,
                       "DEFAULT": "default" })
    incpath = [ "test/src", "/nowhere" ]
    tt_reset = Template({ "INTERPOLATE": True,
                          "INCLUDE_PATH": incpath,
                          "TRIM": True,
                          "RECURSION": True,
                          "DEFAULT": "bad_default" })
    incpath[1] = "test/lib"

    replace["metaout"] = tproc.process("metadata", replace)
    replace["metamod"] = os.stat("test/src/metadata").st_mtime

    self.Expect(DATA, (('default', tproc), ('reset', tt_reset)), replace)


DATA = r"""
-- test --
[% a %]
[% PROCESS incblock -%]
[% b %]
[% INCLUDE first_block %]
-- expect --
alpha
bravo
this is my first block, a is set to 'alpha'

-- test --
[% INCLUDE first_block %]
-- expect --
this is my first block, a is set to 'alpha'

-- test --
[% INCLUDE first_block a = 'abstract' %]
[% a %]
-- expect --
this is my first block, a is set to 'abstract'
alpha

-- test --
[% INCLUDE 'first_block' a = t %]
[% a %]
-- expect --
this is my first block, a is set to 'tango'
alpha

-- test --
[% INCLUDE 'second_block' %]
-- expect --
this is my second block, a is initially set to 'alpha' and 
then set to 'sierra'  b is bravo  m is 98

-- test --
[% INCLUDE second_block a = r, b = c.f.g, m = 97 %]
[% a %]
-- expect --
this is my second block, a is initially set to 'romeo' and 
then set to 'sierra'  b is golf  m is 97
alpha

-- test --
FOO: [% INCLUDE foo +%]
FOO: [% INCLUDE foo a = b -%]
-- expect --
FOO: This is the foo file, a is alpha
FOO: This is the foo file, a is bravo

-- test --
GOLF: [% INCLUDE $c.f.g %]
GOLF: [% INCLUDE $c.f.g  g = c.f.h %]
[% DEFAULT g = "a new $c.f.g" -%]
[% g %]
-- expect --
GOLF: This is the golf file, g is golf
GOLF: This is the golf file, g is hotel
a new golf

-- test --
BAZ: [% INCLUDE bar/baz %]
BAZ: [% INCLUDE bar/baz word='wizzle' %]
BAZ: [% INCLUDE "bar/baz" %]
-- expect --
BAZ: This is file baz
The word is 'qux'
BAZ: This is file baz
The word is 'wizzle'
BAZ: This is file baz
The word is 'qux'

-- test --
BAZ: [% INCLUDE bar/baz.txt %]
BAZ: [% INCLUDE bar/baz.txt time = 'nigh' %]
-- expect --
BAZ: This is file baz
The word is 'qux'
The time is now
BAZ: This is file baz
The word is 'qux'
The time is nigh

-- test --
[% BLOCK bamboozle -%]
This is bamboozle
[%- END -%]
Block defined...
[% blockname = 'bamboozle' -%]
[% INCLUDE $blockname %]
End
-- expect --
Block defined...
This is bamboozle
End


# test that BLOCK definitions get AUTO_RESET (i.e. cleared) by default
-- test --
-- use reset --
[% a %]
[% PROCESS incblock -%]
[% INCLUDE first_block %]
[% INCLUDE second_block %]
[% b %]
-- expect --
alpha
this is my first block, a is set to 'alpha'
this is my second block, a is initially set to 'alpha' and 
then set to 'sierra'  b is bravo  m is 98
bravo

-- test --
[% TRY %]
[% INCLUDE first_block %]
[% CATCH file %]
ERROR: [% error.info %]
[% END %]
-- expect --
ERROR: first_block: not found

-- test --
-- use default --
[% metaout %]
-- expect --
-- process --
TITLE: The cat sat on the mat
metadata last modified [% metamod %]

-- test -- 
[% TRY %]
[% PROCESS recurse counter = 1 %]
[% CATCH file -%]
[% error.info %]
[% END %]
-- expect --
recursion count: 1
recursion into 'my file'

-- test --
[% INCLUDE nosuchfile %]
-- expect --
This is the default file

-- test -- 
-- use reset --
[% TRY %]
[% PROCESS recurse counter = 1 %]
[% CATCH file %]
[% error.info %]
[% END %]
-- expect --
recursion count: 1
recursion count: 2
recursion count: 3

-- test --
[% TRY;
   INCLUDE nosuchfile;
   CATCH;
   "ERROR: $error";
   END
%]
-- expect --
ERROR: file error - nosuchfile: not found

-- test --
[% INCLUDE src:foo %]
[% BLOCK src:foo; "This is foo!"; END %]
-- expect --
This is foo!

-- test --
[% a = ''; b = ''; d = ''; e = 0 %]
[% INCLUDE foo name = a or b or 'c'
               item = d or e or 'f' -%]
[% BLOCK foo; "name: $name  item: $item\n"; END %]
-- expect --
name: c  item: f

-- test --
[% style = 'light'; your_title="Hello World" -%]
[% INCLUDE foo 
         title = my_title or your_title or default_title
         bgcol = (style == 'dark' ? '#000000' : '#ffffff') %]
[% BLOCK foo; "title: $title\nbgcol: $bgcol\n"; END %]
-- expect --
title: Hello World
bgcol: #ffffff

-- test --
[% myhash = {
    name  = 'Tom'
    item  = 'teacup'
   }
-%]
[% INCLUDE myblock
    name = 'Fred'
    item = 'fish'
%]
[% INCLUDE myblock
     import=myhash
%]
import([% import %])
[% PROCESS myblock
     import={ name = 'Tim', item = 'teapot' }
%]
import([% import %])
[% BLOCK myblock %][% name %] has a [% item %][% END %]
-- expect --
Fred has a fish
Tom has a teacup
import()
Tim has a teapot
import()

-- test --
"""

main()

