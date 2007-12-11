from template.test import TestCase, main


class MacroTest(TestCase):
  def testMacro(self):
    config = { "INCLUDE_PATH": "test/src",
               "TRIM": 1,
               "EVAL_PYTHON": True }
    self.Expect(DATA, config, self._callsign())


DATA = r"""
-- test --
[% MACRO foo INCLUDE foo -%]
foo: [% foo %]
foo(b): [% foo(a = b) %]
-- expect --
foo: This is the foo file, a is alpha
foo(b): This is the foo file, a is bravo

-- test --
foo: [% foo %].
-- expect --
foo: .

-- test --
[% MACRO foo(a) INCLUDE foo -%]
foo: [% foo %]
foo(c): [% foo(c) %]
-- expect --
foo: This is the foo file, a is
foo(c): This is the foo file, a is charlie


-- test --
[% BLOCK mypage %]
Header
[% content %]
Footer
[% END %]

[%- MACRO content BLOCK -%]
This is a macro which encapsulates a template block.
a: [% a -%]
[% END -%]

begin
[% INCLUDE mypage %]
mid
[% INCLUDE mypage a = 'New Alpha' %]
end
-- expect --
begin
Header
This is a macro which encapsulates a template block.
a: alpha
Footer
mid
Header
This is a macro which encapsulates a template block.
a: New Alpha
Footer
end

-- test --
[% BLOCK table %]
<table>
[% rows %]
</table>
[% END -%]

[% # define some dummy data
   udata = [
      { id => 'foo', name => 'Fubar' },
      { id => 'bar', name => 'Babar' }
   ] 
-%]

[% # define a macro to print each row of user data
   MACRO user_summary INCLUDE user_row FOREACH user = udata 
%]

[% # here's the block for each row
   BLOCK user_row %]
<tr>
  <td>[% user.id %]</td>
  <td>[% user.name %]</td>
</tr>
[% END -%]

[% # now we can call the main table template, and alias our macro to 'rows' 
   INCLUDE table 
     rows = user_summary
%]
-- expect --
<table>
<tr>
  <td>foo</td>
  <td>Fubar</td>
</tr><tr>
  <td>bar</td>
  <td>Babar</td>
</tr>
</table>

-- test --
[% MACRO one BLOCK -%]
one: [% title %]
[% END -%]
[% saveone = one %]
[% MACRO two BLOCK; title="2[$title]" -%]
two: [% title %] -> [% saveone %]
[% END -%]
[% two(title="The Title") %]
-- expect --
two: 2[The Title] -> one:

-- test --
[% MACRO one BLOCK -%]
one: [% title %]
[% END -%]
[% saveone = \one %]
[% MACRO two BLOCK; title="2[$title]" -%]
two: [% title %] -> [% saveone %]
[% END -%]
[% two(title="The Title") %]
-- expect --
two: 2[The Title] -> one: 2[The Title]

-- test --
-- name number macro --
[% MACRO number(n) GET n.chunk(-3).join(',') -%]
[% number(1234567) %]
-- expect --
1,234,567

-- test --
-- name python macro --
[% MACRO triple(n) PYTHON %]
    n = stash.get('n').value()
    print n * 3
[% END -%]
[% triple(10) %]
-- expect --
30
"""

main()
