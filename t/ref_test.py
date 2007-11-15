from template.test import TestCase, main


def comma_list(format):
  def func(*args):
    return format % ", ".join(str(x) for x in args)
  return func


class RefTest(TestCase):
  def testRef(self):
    replace = {
      "a": comma_list("a sub [%s]"),
      "j": { "k": 3,
             "l": 5,
             "m": { "n": comma_list("nsub [%s]") } },
      "z": lambda sub: "z called %s" % sub(10, 20, 30)
      }
    self.Expect(DATA, None, replace)


DATA = r"""
-- test --
a: [% a %]
a(5): [% a(5) %]
a(5,10): [% a(5,10) %]
-- expect --
a: a sub []
a(5): a sub [5]
a(5,10): a sub [5, 10]

-- test --
[% b = \a -%]
b: [% b %]
b(5): [% b(5) %]
b(5,10): [% b(5,10) %]
-- expect --
b: a sub []
b(5): a sub [5]
b(5,10): a sub [5, 10]

-- test --
[% c = \a(10,20) -%]
c: [% c %]
c(30): [% c(30) %]
c(30,40): [% c(30,40) %]
-- expect --
c: a sub [10, 20]
c(30): a sub [10, 20, 30]
c(30,40): a sub [10, 20, 30, 40]

-- test --
[% z(\a) %]
-- expect --
z called a sub [10, 20, 30]

-- test --
[% f = \j.k -%]
f: [% f %]
-- expect --
f: 3

-- test --
[% f = \j.m.n -%]
f: [% f %]
f(11): [% f(11) %]
-- expect --
f: nsub []
f(11): nsub [11]


"""

main()

