from template import constants
from template.iterator import Iterator
from template.test import TestCase, main


class IteratorTest(TestCase):
  def testIterator(self):
    data = ("foo", "bar", "baz", "qux", "wiz", "woz", "waz")
    vars = { "data": data }
    i1 = Iterator(data)
    self.assertEquals("foo", i1.get_first())
    self.assertEquals("bar", i1.get_next())
    self.assertEquals("baz", i1.get_next())
    rest = i1.get_all()
    self.assertEquals(4, len(rest))
    self.assertEquals("qux", rest[0])
    self.assertEquals("waz", rest[3])
    val, err = i1.get_next()
    self.assert_(not val)
    self.assertEquals(constants.STATUS_DONE, err)
    val, err = i1.get_all()
    self.assert_(not val)
    self.assertEquals(constants.STATUS_DONE, err)
    i1.get_first()
    self.assertEquals("foo", i1.get_first())
    self.assertEquals("bar", i1.get_next())
    rest = i1.get_all()
    self.assertEquals(5, len(rest))
    self.Expect(DATA, { "POST_CHOMP": 1 }, vars)


DATA = r"""

-- test --
[% items = [ 'foo' 'bar' 'baz' 'qux' ] %]
[% FOREACH i = items %]
   * [% i +%]
[% END %]
-- expect --
   * foo
   * bar
   * baz
   * qux

-- test --
[% items = [ 'foo' 'bar' 'baz' 'qux' ] %]
[% FOREACH i = items %]
   #[% loop.index %]/[% loop.max %] [% i +%]
[% END %]
-- expect --
   #0/3 foo
   #1/3 bar
   #2/3 baz
   #3/3 qux

-- test --
[% items = [ 'foo' 'bar' 'baz' 'qux' ] %]
[% FOREACH i = items %]
   #[% loop.count %]/[% loop.size %] [% i +%]
[% END %]
-- expect --
   #1/4 foo
   #2/4 bar
   #3/4 baz
   #4/4 qux

-- test --
# test that 'number' is supported as an alias to 'count', for backwards
# compatability
[% items = [ 'foo' 'bar' 'baz' 'qux' ] %]
[% FOREACH i = items %]
   #[% loop.number %]/[% loop.size %] [% i +%]
[% END %]
-- expect --
   #1/4 foo
   #2/4 bar
   #3/4 baz
   #4/4 qux

-- test --
[% USE iterator(data) %]
[% FOREACH i = iterator %]
[% IF iterator.first %]
List of items:
[% END %]
   * [% i +%]
[% IF iterator.last %]
End of list
[% END %]
[% END %]
-- expect --
List of items:
   * foo
   * bar
   * baz
   * qux
   * wiz
   * woz
   * waz
End of list


-- test --
[% FOREACH i = [ 'foo' 'bar' 'baz' 'qux' ] %]
[% "$loop.prev<-" IF loop.prev -%][[% i -%]][% "->$loop.next" IF loop.next +%]
[% END %]
-- expect --
[foo]->bar
foo<-[bar]->baz
bar<-[baz]->qux
baz<-[qux]
"""

main()
