from template.directive import Directive
from template.test import TestCase, main


class MyDirective(Directive):
  constants = { 'pi': 3.14, 'e': 2.718 }
  def ident(self, ident):
    if isinstance(ident, (tuple, list)) and ident[0] == "'constant'":
      key = ident[2].replace("'", "")
      return self.constants.get(key, "")
    return Directive.ident(self, ident)


class FactoryTest(TestCase):
  def testFactory(self):
    cfg = { 'FACTORY': MyDirective }
    vars = { 'foo': { 'bar': 'Place to purchase drinks',
                      'baz': 'Short form of "Basil"' } }
    self.Expect(DATA, cfg, vars)


DATA = r"""
-- test --
[% foo.bar %]
-- expect --
Place to purchase drinks

-- test --
[% constant.pi %]
-- expect --
3.14
"""

main()
