from template.test import TestCase, main


class MathTest(TestCase):
  def testMath(self):
    self.Expect(DATA)


DATA = r"""
-- test --
[% USE Math; Math.sqrt(9) %]
-- expect --
3

-- test --
[% USE Math; Math.abs(-1) %]
-- expect --
1

-- test --
[% USE Math; Math.atan2(42, 42) %]
-- expect --
0.785398163397

-- test --
[% USE Math; Math.cos(2) %]
-- expect --
-0.416146836547

-- test --
[% USE Math; Math.exp(6) %]
-- expect --
403.428793493

-- test --
[% USE Math; Math.hex(42) %]
-- expect --
66

-- test --
[% USE Math; Math.int(9.9) %]
-- expect --
9

-- test --
[% USE Math; Math.log(42) %]
-- expect --
3.73766961828

-- test --
[% USE Math; Math.oct(72) %]
-- expect --
58

-- test --
[% USE Math; Math.sin(0.304) %]
-- expect --
0.299339178269
"""

main()
