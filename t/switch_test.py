from template.test import TestCase, main


class SwitchTest(TestCase):
  def testSwitch(self):
    ttcfg = { 'POST_CHOMP': 1 }
    self.Expect(DATA, ttcfg, self._callsign())


DATA = r"""
#------------------------------------------------------------------------
# test simple case
#------------------------------------------------------------------------
-- test --
before
[% SWITCH a %]
this is ignored
[% END %]
after

-- expect --
before
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE x %]
not matched
[% END %]
after

-- expect --
before
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE not_defined %]
not matched
[% END %]
after

-- expect --
before
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE 'alpha' %]
matched
[% END %]
after

-- expect --
before
matched
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE a %]
matched
[% END %]
after

-- expect --
before
matched
after

-- test --
before
[% SWITCH 'alpha' %]
this is ignored
[% CASE a %]
matched
[% END %]
after

-- expect --
before
matched
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE b %]
matched
[% END %]
after

-- expect --
before
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE a %]
matched
[% CASE b %]
not matched
[% END %]
after

-- expect --
before
matched
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE b %]
not matched
[% CASE a %]
matched
[% END %]
after

-- expect --
before
matched
after

#------------------------------------------------------------------------
# test default case
#------------------------------------------------------------------------
-- test --
before
[% SWITCH a %]
this is ignored
[% CASE a %]
matched
[% CASE b %]
not matched
[% CASE %]
default not matched
[% END %]
after

-- expect --
before
matched
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE a %]
matched
[% CASE b %]
not matched
[% CASE DEFAULT %]
default not matched
[% END %]
after

-- expect --
before
matched
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE z %]
not matched
[% CASE x %]
not matched
[% CASE %]
default matched
[% END %]
after

-- expect --
before
default matched
after


-- test --
before
[% SWITCH a %]
this is ignored
[% CASE z %]
not matched
[% CASE x %]
not matched
[% CASE DEFAULT %]
default matched
[% END %]
after

-- expect --
before
default matched
after

#------------------------------------------------------------------------
# test multiple matches
#------------------------------------------------------------------------

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE [ a b c ] %]
matched
[% CASE d %]
not matched
[% CASE %]
default not matched
[% END %]
after

-- expect --
before
matched
after

-- test --
before
[% SWITCH a %]
this is ignored
[% CASE [ a b c ] %]
matched
[% CASE a %]
not matched, no drop-through
[% CASE DEFAULT %]
default not matched
[% END %]
after

-- expect --
before
matched
after

"""

main()
