import os

from template import Template
from template.test import TestCase, main


class BlocksTest(TestCase):
  def testBlocks(self):
    dir = os.getcwd() + "/test/lib"
    tt1 = Template({ 'INCLUDE_PATH': ['test/lib'],
                     'ABSOLUTE': True })
    tt2 = Template({ 'INCLUDE_PATH': ['test/lib'],
                     'EXPOSE_BLOCKS': True,
                     'ABSOLUTE': True })
    vars = { 'a': 'alpha', 'b': 'bravo', 'dir': dir }
    self.Expect(DATA, (('off', tt1), ('on', tt2)), vars)


DATA = r"""
-- test --
[% TRY; INCLUDE blockdef/block1; CATCH; error; END %]

-- expect --
file error - blockdef/block1: not found

-- test --
-- use on --
[% INCLUDE blockdef/block1 %]

-- expect --
This is block 1, defined in blockdef, a is alpha

-- test --
[% INCLUDE blockdef/block1 a='amazing' %]

-- expect --
This is block 1, defined in blockdef, a is amazing

-- test -- 
[% TRY; INCLUDE blockdef/none; CATCH; error; END %]
-- expect --
file error - blockdef/none: not found

-- test --
[% INCLUDE "$dir/blockdef/block1" a='abstract' %]

-- expect --
This is block 1, defined in blockdef, a is abstract

-- test --
[% BLOCK one -%]
block one
[% BLOCK two -%]
this is block two, b is [% b %]
[% END -%]
two has been defined, let's now include it
[% INCLUDE one/two b='brilliant' -%]
end of block one
[% END -%]
[% INCLUDE one -%]
=
[% INCLUDE one/two b='brazen'-%]
--expect --
block one
two has been defined, let's now include it
this is block two, b is brilliant
end of block one
=
this is block two, b is brazen
"""

main()

