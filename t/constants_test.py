from template import Template
from template.directive import Directive
from template.namespace.constants import Constants
from template.parser import Parser
from template.test import TestCase, main


class ConstantsTest(TestCase):
  def testConstants(self):
    n = [0]
    def counter():
      n[0] += 1
      return n[0] - 1
    constants = { "author": "Andy 'Da Man' Wardley",
                  "single": "foo'bar",
                  "double": 'foo"bar',
                  "joint": ", ",
                  "col": { "back": "#ffffff", "text": "#000000" },
                  "counter": counter }
    namespace = Constants(constants)
    self.assertEquals('"Andy \'Da Man\' Wardley"',
                      namespace.ident(["constants", 0, "'author'", 0]))
    self.assertEquals('"foo\'bar"',
                      namespace.ident(["constants", 0, "'single'", 0]))
    self.assertEquals("'foo\"bar'",
                      namespace.ident(["constants", 0, "'double'", 0]))
    self.assertEquals("'#ffffff'", namespace.ident(["constants", 0,
                                                    "'col'", 0,
                                                    "'back'", 0]))
    self.assertEquals("'#000000'", namespace.ident(["constants", 0,
                                                    "'col'", 0,
                                                    "'text'", 0]))
    factory = Directive({ "NAMESPACE": { "const": namespace } })
    parser1 = Parser({ "FACTORY": factory })
    parser2 = Parser({ "NAMESPACE": { "const": namespace } })
    for parser in parser1, parser2:
      parsed = parser.parse('hello [% const.author %]\n'
                            '[% "back is $const.col.back" %]'
                            ' and text is {% const.col.text %]\n'
                            'but a col is still a [% col.user %]\n')
      text = parsed["BLOCK"]
      self.assertNotEqual(-1, text.find('"Andy \'Da Man\' Wardley"'))
      self.assertNotEqual(-1, text.find("'back is ', '#ffffff'"))
      self.assertNotEqual(-1, text.find("stash.get(['col', 0, 'user', 0])"))

    tt1 = Template({ "NAMESPACE": { "const": namespace } })
    const2 = { "author": "abw",
               "joint": " is the new ",
               "col": { "back": "orange", "text": "black" },
               "fave": "back" }
    tt2 = Template({ "CONSTANTS": const2 })
    tt3 = Template({ "CONSTANTS": const2,
                     "CONSTANTS_NAMESPACE": "const" })
    engines = (("tt1", tt1), ("tt2", tt2), ("tt3", tt3))
    vars = { "col": { "user": "red", "luza": "blue" },
             "constants": constants }
    self.Expect(DATA, engines, vars)


DATA = r"""
-- test --
hello [% const.author %]
[% "back is $const.col.back" %] and text is [% const.col.text %]
col.user is [% col.user %]
-- expect --
hello Andy 'Da Man' Wardley
back is #ffffff and text is #000000
col.user is red

-- test --
# look ma!  I can even call virtual methods on constants!
[% const.col.keys.sort.join(', ') %]
-- expect --
back, text

-- test --
# and even pass constant arguments to constant virtual methods!
[% const.col.keys.sort.join(const.joint) %]
-- expect --
back, text

-- test --
# my constants can be subs, etc.
zero [% const.counter %]
one [% const.counter %]
-- expect --
zero 0
one 1

-- test --
-- use tt2 --
[% "$constants.author thinks " %]
[%- constants.col.values.sort.reverse.join(constants.joint) %]
-- expect --
abw thinks orange is the new black

-- test --
-- use tt3 --
[% "$const.author thinks " -%]
[% const.col.values.sort.reverse.join(const.joint) %]
-- expect --
abw thinks orange is the new black

-- test --
no [% const.foo %]?
-- expect --
no ?

-- test --
fave [% const.fave %]
col  [% const.col.${const.fave} %]
-- expect --
fave back
col  orange

-- test --
-- use tt2 --
-- name defer references --
[% "$key\n" FOREACH key = constants.col.keys.sort %]
-- expect --
back
text

-- test --
-- use tt3 --
a: [% const.author %]
b: [% const.author = 'Fred Smith' %]
c: [% const.author %]
-- expect --
a: abw
b: 
c: abw
"""

main()

