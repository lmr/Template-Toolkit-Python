from template import Template
from template.test import TestCase, main


class TagsTest(TestCase):
  def testTags(self):
    params = { "a": "alpha", "b": "bravo", "c": "charlie", "d": "delta",
               "e": "echo" }
    tt = (("basic", Template({ "INTERPOLATE": 1 })),
          ("htags", Template({ "TAG_STYLE": "html" })),
          ("stags", Template({ "START_TAG": r"\[\*", "END_TAG": r"\*\]" })))
    self.Expect(DATA, tt, params)


DATA = r"""
-- test --
[%a%] [% a %] [% a %]
-- expect --
alpha alpha alpha

-- test --
Redefining tags
[% TAGS (+ +) %]
[% a %]
[% b %]
(+ c +)
-- expect --
Redefining tags

[% a %]
[% b %]
charlie

-- test --
[% a %]
[% TAGS (+ +) %]
[% a %]
%% b %%
(+ c +)
(+ TAGS <* *> +)
(+ d +)
<* e *>
-- expect --
alpha

[% a %]
%% b %%
charlie

(+ d +)
echo

-- test --
[% TAGS default -%]
[% a %]
%% b %%
(+ c +)
-- expect --
alpha
%% b %%
(+ c +)

-- test --
# same as 'default'
[% TAGS template -%]
[% a %]
%% b %%
(+ c +)
-- expect --
alpha
%% b %%
(+ c +)

-- test --
[% TAGS metatext -%]
[% a %]
%% b %%
<* c *>
-- expect --
[% a %]
bravo
<* c *>

-- test --
[% TAGS template1 -%]
[% a %]
%% b %%
(+ c +)
-- expect --
alpha
bravo
(+ c +)

-- test --
[% TAGS html -%]
[% a %]
%% b %%
<!-- c -->
-- expect --
[% a %]
%% b %%
charlie

-- test --
[% TAGS asp -%]
[% a %]
%% b %%
<!-- c -->
<% d %>
<? e ?>
-- expect --
[% a %]
%% b %%
<!-- c -->
delta
<? e ?>

-- test --
[% TAGS php -%]
[% a %]
%% b %%
<!-- c -->
<% d %>
<? e ?>
-- expect --
[% a %]
%% b %%
<!-- c -->
<% d %>
echo

#------------------------------------------------------------------------
# test processor with pre-defined TAG_STYLE
#------------------------------------------------------------------------
-- test --
-- use htags --
[% TAGS ignored -%]
[% a %]
<!-- c -->
more stuff
-- expect --
[% TAGS ignored -%]
[% a %]
charlie
more stuff

#------------------------------------------------------------------------
# test processor with pre-defined START_TAG and END_TAG
#------------------------------------------------------------------------
-- test --
-- use stags --
[% TAGS ignored -%]
<!-- also totally ignored and treated as text -->
[* a *]
blah [* b *] blah
-- expect --
[% TAGS ignored -%]
<!-- also totally ignored and treated as text -->
alpha
blah bravo blah


#------------------------------------------------------------------------
# XML style tags
#------------------------------------------------------------------------

-- test --
-- use basic --
[% TAGS <tt: > -%]
<tt:a=10->
a: <tt:a>
<tt:FOR a = [ 1, 3, 5, 7 ]->
<tt:a>
<tt:END->
-- expect --
a: 10
1
3
5
7

-- test --
[% TAGS star -%]
[* a = 10 -*]
a is [* a *]
-- expect --
a is 10
"""

main()

