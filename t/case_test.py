from template import Template
from template.test import TestCase, main


class CaseTest(TestCase):
  def testCase(self):
    ttdef = Template({ 'POST_CHOMP': 1 })
    ttanycase = Template({ 'ANYCASE': 1, 'POST_CHOMP': 1 })
    tts = (('default', ttdef), ('anycase', ttanycase))
    self.Expect(DATA, tts, self._callsign())


DATA = r"""
-- test --
[% include = a %]
[% for = b %]
i([% include %])
f([% for %])
-- expect --
i(alpha)
f(bravo)

-- test --
[% IF a AND b %]
good
[% ELSE %]
bad
[% END %]
-- expect --
good

-- test --
# 'and', 'or' and 'not' can ALWAYS be expressed in lower case, regardless
# of CASE sensitivity option.
[% IF a and b %]
good
[% ELSE %]
bad
[% END %]
-- expect --
good

-- test --
[% include = a %]
[% include %]
-- expect --
alpha

-- test --
-- use anycase --
[% include foo bar='baz' %]
[% BLOCK foo %]this is foo, bar = [% bar %][% END %]
-- expect --
this is foo, bar = baz

-- test --
[% 10 div 3 %] [% 10 DIV 3 +%]
[% 10 mod 3 %] [% 10 MOD 3 %]
-- expect --
3 3
1 1
"""

main()
