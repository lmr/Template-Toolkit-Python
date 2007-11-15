from template import util, Template
from template.test import TestCase, main
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


class ChompTest(TestCase):
  def AssertExpectedOutput(self, tmpl, block, vars, expected):
    self.assertEquals(expected, tmpl.process(block, vars))

  def testNoChomp(self):
    tmpl = Template({ "BLOCKS": blocks })
    self.AssertExpectedOutput(tmpl, "foo", vars, "\n3.14\n")
    self.AssertExpectedOutput(tmpl, "bar", vars, "2.718")
    self.AssertExpectedOutput(tmpl, "baz", vars, "\n1.618\n")
    self.AssertExpectedOutput(tmpl, "ding", vars, "!Hello!")
    self.AssertExpectedOutput(tmpl, "dong", vars, "! World !")
    self.AssertExpectedOutput(tmpl, "dang", vars, "Hello!")

  def testPreChomp(self):
    tmpl = Template({ "PRE_CHOMP": 1, "BLOCKS": blocks })
    self.AssertExpectedOutput(tmpl, "foo", vars, "3.14\n")
    self.AssertExpectedOutput(tmpl, "bar", vars, "2.718")
    self.AssertExpectedOutput(tmpl, "baz", vars, "\n1.618\n")
    self.AssertExpectedOutput(tmpl, "ding", vars, "!Hello!")
    self.AssertExpectedOutput(tmpl, "dong", vars, "! World !")

  def testPostChomp(self):
    tmpl = Template({ 'POST_CHOMP': 1, 'BLOCKS': blocks })
    self.AssertExpectedOutput(tmpl, "foo", vars, "\n3.14")
    self.AssertExpectedOutput(tmpl, "bar", vars, "2.718")
    self.AssertExpectedOutput(tmpl, "baz", vars, "\n1.618\n")
    self.AssertExpectedOutput(tmpl, "ding", vars, "!Hello!")
    self.AssertExpectedOutput(tmpl, "dong", vars, "! World !")

  def testChomp(self):
    tt = (('tt_pre_none', Template({ 'PRE_CHOMP': CHOMP_NONE })),
          ('tt_pre_one', Template({ 'PRE_CHOMP': CHOMP_ONE })),
          ('tt_pre_all', Template({ 'PRE_CHOMP': CHOMP_ALL })),
          ('tt_pre_coll', Template({ 'PRE_CHOMP': CHOMP_COLLAPSE })),
          ('tt_post_none', Template({ 'POST_CHOMP': CHOMP_NONE })),
          ('tt_post_one', Template({ 'POST_CHOMP': CHOMP_ONE })),
          ('tt_post_all', Template({ 'POST_CHOMP': CHOMP_ALL })),
          ('tt_post_coll', Template({ 'POST_CHOMP': CHOMP_COLLAPSE })))
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

main()
