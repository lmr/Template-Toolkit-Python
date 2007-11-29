from template import Template
from template.config import Config
from template.parser import Parser
from template.test import TestCase, main


class ParserTest(TestCase):
  def testParser(self):
    p2 = Parser({"START_TAG": r"\[\*",
                 "END_TAG": r"\*\]",
                 "ANYCASE": 1,
                 "PRE_CHOMP": 1,
                 "V1DOLLAR": 1})
    # Test new/old styles.
    s1 = p2.new_style({"TAG_STYLE": "metatext",
                       "PRE_CHOMP": 0,
                       "POST_CHOMP": 1})
    self.assert_(s1)
    self.assertEquals(r"%%", s1["START_TAG"])
    self.assertEquals(0, s1["PRE_CHOMP"])
    self.assertEquals(1, s1["POST_CHOMP"])
    s2 = p2.old_style()
    self.assert_(s2)
    self.assertEquals(r"\[\*", s2["START_TAG"])
    self.assertEquals(1, s2["PRE_CHOMP"])
    self.assertEquals(0, s2["POST_CHOMP"])
    p3 = Config.parser(
      {"TAG_STYLE": "html", "POST_CHOMP": 1, "ANYCASE": 1, "INTERPOLATE": 1})
    p4 = Config.parser({"ANYCASE": 0})
    tt = (("tt1", Template({"ANYCASE": 1})),
          ("tt2", Template({"PARSER": p2})),
          ("tt3", Template({"PARSER": p3})),
          ("tt4", Template({"PARSER": p4})))
    replace = self._callsign()
    replace["alist"] = ["foo", 0, "bar", 0]
    replace["wintxt"] = "foo\r\n\r\nbar\r\n\r\nbaz"
    self.Expect(DATA, tt, replace)


DATA = r"""
#------------------------------------------------------------------------
# tt1
#------------------------------------------------------------------------
-- test --
start $a
[% BLOCK a %]
this is a
[% END %]
=[% INCLUDE a %]=
=[% include a %]=
end
-- expect --
start $a

=
this is a
=
=
this is a
=
end

#------------------------------------------------------------------------
# tt2
#------------------------------------------------------------------------
-- test --
-- use tt2 --
begin
[% this will be ignored %]
[* a *]
end
-- expect --
begin
[% this will be ignored %]alpha
end

-- test --
$b does nothing: 
[* c = 'b'; 'hello' *]
stuff: 
[* $c *]
-- expect --
$b does nothing: hello
stuff: b

#------------------------------------------------------------------------
# tt3
#------------------------------------------------------------------------
-- test --
-- use tt3 --
begin
[% this will be ignored %]
<!-- a -->
end

-- expect --
begin
[% this will be ignored %]
alphaend

-- test --
$b does something: 
<!-- c = 'b'; 'hello' -->
stuff: 
<!-- $c -->
end
-- expect --
bravo does something: 
hellostuff: 
bravoend


#------------------------------------------------------------------------
# tt4
#------------------------------------------------------------------------
-- test --
-- use tt4 --
start $a[% 'include' = 'hello world' %]
[% BLOCK a -%]
this is a
[%- END %]
=[% INCLUDE a %]=
=[% include %]=
end
-- expect --
start $a

=this is a=
=hello world=
end


#------------------------------------------------------------------------
-- test --
[% sql = "
     SELECT *
     FROM table"
-%]
SQL: [% sql %]
-- expect --
SQL: 
     SELECT *
     FROM table

-- test --
[% a = "\a\b\c\ndef" -%]
a: [% a %]
-- expect --
a: abc
def

-- test --
[% a = "\f\o\o"
   b = "a is '$a'"
   c = "b is \$100"
-%]
a: [% a %]  b: [% b %]  c: [% c %]

-- expect --
a: foo  b: a is 'foo'  c: b is $100

-- test --
[% tag = {
      a => "[\%"
      z => "%\]"
   }
   quoted = "[\% INSERT foo %\]"
-%]
A directive looks like: [% tag.a %] INCLUDE foo [% tag.z %]
The quoted value is [% quoted %]

-- expect --
A directive looks like: [% INCLUDE foo %]
The quoted value is [% INSERT foo %]

-- test --
=[% wintxt | replace("(\r\n){2,}", "\n<break>\n") %]

-- expect --
=foo
<break>
bar
<break>
baz

-- test --
[% nl  = "\n"
   tab = "\t"
-%]
blah blah[% nl %][% tab %]x[% nl; tab %]y[% nl %]end
-- expect --
blah blah
	x
	y
end

#------------------------------------------------------------------------
# STOP RIGHT HERE!
#------------------------------------------------------------------------

-- stop --

-- test --
alist: [% $alist %]
-- expect --
alist: ??

-- test --
[% foo.bar.baz %]
"""

main()
