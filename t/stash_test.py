from template import Template, constants
from template.stash import Stash
from template.test import TestCase, main


class AnObject:
  def __init__(self, **kwargs):
    for name, value in kwargs.items():
      setattr(self, name, value)


class HashObject(AnObject):
  def __init__(self, **kwargs):
    AnObject.__init__(self, **kwargs)

  def hello(self):
    return "Hello %s" % getattr(self, "planet", "")

  def goodbye(self):
    return self.no_such_method()


class StashTest(TestCase):
  def testStash(self):
    count = [20]
    def boz():
      count[0] += 10
      return count[0]
    def biz(*args):
      return args and args[0] or "<undef>"
    data = { "foo": 10,
             "bar": { "baz": 20 },
             "baz": lambda: { "boz": boz, "biz": biz },
             "obj": AnObject(name="an object"),
             "hashobj": HashObject(planet="World") }
    stash = Stash(data)
    self.assertEquals(10, stash.get("foo").value())
    self.assertEquals(20, stash.get(["bar", 0, "baz", 0]).value())
    self.assertEquals(20, stash.get("bar.baz").value())
    self.assertEquals(20, stash.get("bar(10).baz").value())
    self.assertEquals(30, stash.get("baz.boz").value())
    self.assertEquals(40, stash.get("baz.boz").value())
    self.assertEquals("<undef>", stash.get("baz.biz").value())
    self.assertEquals("<undef>", stash.get("baz(50).biz").value())  # args are ignored

    stash.set("bar.buz", 100)
    self.assertEquals(100, stash.get("bar.buz").value())

    ttlist = (("default", Template()),
              ("warn", Template({"DEBUG": constants.DEBUG_UNDEF,
                                 "DEBUG_FORMAT": ""})))
    self.Expect(DATA, ttlist, data)


DATA = r"""
-- test --
a: [% a %]
-- expect --
a: 

-- test --
-- use warn --
[% TRY; a; CATCH; "ERROR: $error"; END %]
-- expect --
ERROR: None error - a is undefined

-- test --
-- use default --
[% myitem = 'foo' -%]
1: [% myitem %]
2: [% myitem.item %]
3: [% myitem.item.item %]
-- expect --
1: foo
2: foo
3: foo

-- test --
[% myitem = 'foo' -%]
[% "* $item\n" FOREACH item = myitem -%]
[% "+ $item\n" FOREACH item = myitem.list %]
-- expect --
* foo
+ foo

-- test --
[% myitem = 'foo' -%]
[% myitem.hash.value %]
-- expect --
foo

-- test --
[% myitem = 'foo'
   mylist = [ 'one', myitem, 'three' ]
   global.mylist = mylist
-%]
[% mylist.item %]
0: [% mylist.item(0) %]
1: [% mylist.item(1) %]
2: [% mylist.item(2) %]
-- expect --
one
0: one
1: foo
2: three

-- test --
[% "* $item\n" FOREACH item = global.mylist -%]
[% "+ $item\n" FOREACH item = global.mylist.list -%]
-- expect --
* one
* foo
* three
+ one
+ foo
+ three

-- test --
[% global.mylist.push('bar');
   "* $item.key => $item.value\n" FOREACH item = global.mylist.hash -%]
-- expect --
* one => foo
* three => bar

-- test --
[% myhash = { msg => 'Hello World', things => global.mylist, a => 'alpha' };
   global.myhash = myhash 
-%]
* [% myhash.item('msg') %]
-- expect --
* Hello World

-- test --
[% global.myhash.delete('things') -%]
keys: [% global.myhash.keys.sort.join(', ') %]
-- expect --
keys: a, msg

-- test --
[% "* $item\n" 
    FOREACH item IN global.myhash.items.sort -%]
-- expect --
* a
* alpha
* Hello World
* msg

-- test --
[% items = [ 'foo', 'bar', 'baz' ];
   take  = [ 0, 2 ];
   slice = items.$take;
   slice.join(', ');
%]
-- expect --
foo, baz

-- test --
[% items = {
    foo = 'one',
    bar = 'two',
    baz = 'three'
   }
   take  = [ 'foo', 'baz' ];
   slice = items.$take;
   slice.join(', ');
%]
-- expect --
one, three

-- test --
[% items = {
    foo = 'one',
    bar = 'two',
    baz = 'three'
   }
   keys = items.keys.sort;
   items.${keys}.join(', ');
%]
-- expect --
two, three, one


-- test --
[% obj.name %]
-- expect --
an object

-- test --
[% obj.name.list.first %]
-- expect --
an object

-- test --
[% obj.items.first %]
-- expect --
name

-- test --
[% obj.items.1 %]
-- expect --
an object

#-- test --
#[% listobj.0 %] / [% listobj.first %]
#-- expect --
#10 / 10
#
#-- test --
#[% listobj.2 %] / [% listobj.last %]
#-- expect --
#30 / 30
#
#-- test --
#[% listobj.join(', ') %]
#-- expect --
#10, 20, 30
#
-- test --
=[% size %]=
-- expect --
==

# test Dave Howorth's patch (v2.15) which makes the stash more strict
# about what it considers to be a missing method error

-- test --
[% hashobj.hello %]
-- expect --
Hello World

-- test --
[% TRY; hashobj.goodbye; CATCH; "ERROR: "; error; END %]
-- expect --
ERROR: None error - HashObject instance has no attribute 'no_such_method'
"""

main()
