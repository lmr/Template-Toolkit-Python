import sys

from template.test import TestCase, main

PY3 = sys.version_info[0] >= 3


class MathTest(TestCase):
    def testMath(self):
        self.Expect(DATA)


DATA_PY2 = r"""
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

DATA_PY3 = r"""
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
0.7853981633974483

-- test --
[% USE Math; Math.cos(2) %]
-- expect --
-0.4161468365471424

-- test --
[% USE Math; Math.exp(6) %]
-- expect --
403.4287934927351

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
3.7376696182833684

-- test --
[% USE Math; Math.oct(72) %]
-- expect --
58

-- test --
[% USE Math; Math.sin(0.304) %]
-- expect --
0.2993391782690932
"""

if PY3:
    DATA = DATA_PY3
else:
    DATA = DATA_PY2


if __name__ == '__main__':
    main()
