import template
from template import test, util
from template.constants import *

foo = "\n[% foo %]\n"
bar = "\n[%- bar -%]\n"
baz = "\n[%+ baz +%]\n"
ding = "!\n\n[%~ ding ~%]\n\n!"
dong = "!\n\n[%= dong =%]\n\n!"
dang = "Hello[%# blah blah blah -%]\n!"
blocks = {"foo": foo, "bar": bar, "baz": baz,
          "ding": ding, "dong": dong, "dang": dang}
vars = {'foo': 3.14, 'bar': 2.718, 'baz': 1.618,
        'ding': 'Hello', 'dong': 'World'}

class ChompTest(test.TestCase):
  def foo(self, tmpl, block, vars, expected):
    out = util.Reference("")
    self.failUnless(tmpl.process(block, vars, out))
    self.assertEquals(expected, out.value)
    
  def testNoChomp(self):
    tmpl = template.Template({ "BLOCKS": blocks })
    self.foo(tmpl, "foo", vars, "\n3.14\n")
    self.foo(tmpl, "bar", vars, "2.718")
    self.foo(tmpl, "baz", vars, "\n1.618\n")
    self.foo(tmpl, "ding", vars, "!Hello!")
    self.foo(tmpl, "dong", vars, "! World !")
    self.foo(tmpl, "dang", vars, "Hello!")

  def testPreChomp(self):
    tmpl = template.Template({ "PRE_CHOMP": 1, "BLOCKS": blocks })
    self.foo(tmpl, "foo", vars, "3.14\n")
    self.foo(tmpl, "bar", vars, "2.718")
    self.foo(tmpl, "baz", vars, "\n1.618\n")
    self.foo(tmpl, "ding", vars, "!Hello!")
    self.foo(tmpl, "dong", vars, "! World !")

  def testPostChomp(self):
    tmpl = template.Template({ 'POST_CHOMP': 1, 'BLOCKS': blocks })
    self.foo(tmpl, "foo", vars, "\n3.14")
    self.foo(tmpl, "bar", vars, "2.718")
    self.foo(tmpl, "baz", vars, "\n1.618\n")
    self.foo(tmpl, "ding", vars, "!Hello!")
    self.foo(tmpl, "dong", vars, "! World !")

  def testChomp(self):
    tt = (('tt_pre_none', template.Template({ 'PRE_CHOMP': CHOMP_NONE })),
          ('tt_pre_one', template.Template({ 'PRE_CHOMP': CHOMP_ONE })),
          ('tt_pre_all', template.Template({ 'PRE_CHOMP': CHOMP_ALL })),
          ('tt_pre_coll', template.Template({ 'PRE_CHOMP': CHOMP_COLLAPSE })),
          ('tt_post_none', template.Template({ 'POST_CHOMP': CHOMP_NONE })),
          ('tt_post_one', template.Template({ 'POST_CHOMP': CHOMP_ONE })),
          ('tt_post_all', template.Template({ 'POST_CHOMP': CHOMP_ALL })),
          ('tt_post_coll', template.Template({ 'POST_CHOMP': CHOMP_COLLAPSE })))
    self.Expect(DATA, tt)


DATA = r"""
#------------------------------------------------------------------------
# tt_pre_none
#------------------------------------------------------------------------
-- test --
begin[% a = 10; b = 20 %]
     [% a %]
     [% b %]
end
-- expect --
begin
     10
     20
end

#------------------------------------------------------------------------
# tt_pre_one
#------------------------------------------------------------------------
-- test --
-- use tt_pre_one --
-- test --
begin[% a = 10; b = 20 %]
     [% a %]
     [% b %]
end
-- expect --
begin1020
end


#------------------------------------------------------------------------
# tt_pre_all
#------------------------------------------------------------------------
-- test --
-- use tt_pre_all --
-- test --
begin[% a = 10; b = 20 %]
     [% a %]
     [% b %]
end
-- expect --
begin1020
end

#------------------------------------------------------------------------
# tt_pre_coll
#------------------------------------------------------------------------
-- test --
-- use tt_pre_coll --
-- test --
begin[% a = 10; b = 20 %]
     [% a %]
     [% b %]
end
-- expect --
begin 10 20
end


#------------------------------------------------------------------------
# tt_post_none
#------------------------------------------------------------------------
-- test --
-- use tt_post_none --
begin[% a = 10; b = 20 %]
     [% a %]
     [% b %]
end
-- expect --
begin
     10
     20
end

#------------------------------------------------------------------------
# tt_post_all
#------------------------------------------------------------------------
-- test --
-- use tt_post_all --
-- test --
begin[% a = 10; b = 20 %]
     [% a %]
     [% b %]
end
-- expect --
begin     10     20end

#------------------------------------------------------------------------
# tt_post_one
#------------------------------------------------------------------------
-- test --
-- use tt_post_one --
-- test --
begin[% a = 10; b = 20 %]
     [% a %]
     [% b %]
end
-- expect --
begin     10     20end

#------------------------------------------------------------------------
# tt_post_coll
#------------------------------------------------------------------------
-- test --
-- use tt_post_coll --
-- test --
begin[% a = 10; b = 20 %]     
[% a %]     
[% b %]     
end
-- expect --
begin 10 20 end

"""

test.main()
