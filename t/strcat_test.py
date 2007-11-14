from template.test import TestCase, main


class TestStrcat(TestCase):
  def testStrcat(self):
    self.Expect(DATA)


DATA = r"""
-- test --
[% foo = 'the foo string'
   bar = 'the bar string'
   baz = foo _ ' and ' _ bar
-%]
baz: [% baz %]
-- expect --
baz: the foo string and the bar string

"""

main()
