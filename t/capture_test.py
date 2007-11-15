from template.test import TestCase, main

class CaptureTest(TestCase):
  def testCapture(self):
    config = { 'POST_CHOMP': 1 }
    replace = { 'a': 'alpha', 'b': 'bravo' }
    self.Expect(DATA, config, replace)


DATA = r"""

-- test --
[% BLOCK foo %]
This is block foo, a is [% a %]
[% END %]
[% b = INCLUDE foo %]
[% c = INCLUDE foo a = 'ammended' %]
b: <[% b %]>
c: <[% c %]>
-- expect --
b: <This is block foo, a is alpha>
c: <This is block foo, a is ammended>

-- test --
[% d = BLOCK %]
This is the block, a is [% a %]
[% END %]
[% a = 'charlie' %]
a: [% a %]   d: [% d %]
-- expect --
a: charlie   d: This is the block, a is alpha

-- test --
[% e = IF a == 'alpha' %]
a is [% a %]
[% ELSE %]
that was unexpected
[% END %]
e: [% e %]
-- expect --
e: a is alpha

-- test --
[% a = FOREACH b = [1 2 3] %]
[% b %],
[%- END %]
a is [% a %]

-- expect --
a is 1,2,3,

-- test --
[% BLOCK userinfo %]
name: [% user +%]
[% END %]
[% out = PROCESS userinfo FOREACH user = [ 'tom', 'dick', 'larry' ] %]
Output:
[% out %]
-- expect --
Output:
name: tom
name: dick
name: larry



"""

main()
