from template.directive import Directive
from template.test import TestCase, main


class WhileTest(TestCase):
  def testWhile(self):
    config = { "INTERPOLATE": 1, "POST_CHOMP": 1 }
    list = ("x-ray", "yankee", "zulu")
    pending = []
    def dec(x):
      x[0] -= 1
    def inc(x):
      x[0] += 1
    def reset():
      pending[:] = list
      return "Reset list\n"
    def next():
      if pending:
        return pending.pop(0)
      else:
        return None
    replace = { "a": "alpha",
                "b": "bravo",
                "c": "charlie",
                "d": "delta",
                "dec": lambda x: x - 1, #dec,
                "inc": inc,
                "reset": reset,
                "next": next,
                "true": 1 }
    Directive.WHILE_MAX = 100
    self.Expect(DATA, config, replace)


DATA = r"""
-- test --
before
[% WHILE bollocks %]
do nothing
[% END %]
after
-- expect --
before
after

-- test --
Commence countdown...
[% a = 10 %]
[% WHILE a %]
[% a %]..[% a = dec(a) %]
[% END +%]
The end
-- expect --
Commence countdown...
10..9..8..7..6..5..4..3..2..1..
The end

-- test --
[% reset %]
[% WHILE (item = next) %]
item: [% item +%]
[% END %]
-- expect --
Reset list
item: x-ray
item: yankee
item: zulu

-- test --
[% reset %]
[% WHILE (item = next) %]
item: [% item +%]
[% BREAK IF item == 'yankee' %]
[% END %]
Finis
-- expect --
Reset list
item: x-ray
item: yankee
Finis

-- test --
[% reset %]
[% "* $item\n" WHILE (item = next) %]
-- expect --
Reset list
* x-ray
* yankee
* zulu

-- test --
[% TRY %]
[% WHILE true %].[% END %]
[% CATCH +%]
error: [% error.info %]
[% END %]
-- expect --
...................................................................................................
error: WHILE loop terminated (> 100 iterations)


-- test --
[% reset %]
[% WHILE (item = next) %]
[% NEXT IF item == 'yankee' -%]
* [% item +%]
[% END %]
-- expect --
Reset list
* x-ray
* zulu
-- test --
[%  
    i = 1;
    WHILE i <= 10;
        SWITCH i;
        CASE 5;
            i = i + 1;
            NEXT;
        CASE 8;
            LAST;
        END;
        "$i\n";
        i = i + 1;
    END;
-%]
-- expect --
1
2
3
4
6
7
-- test --
[%
    i = 1;
    WHILE i <= 10;
        IF 1;
            IF i == 5; i = i + 1; NEXT; END;
            IF i == 8; LAST; END;
        END;
        "$i\n";
        i = i + 1;
    END;
-%]
-- expect --
1
2
3
4
6
7
-- test --
[%
    i = 1;
    WHILE i <= 4;
        j = 1;
        WHILE j <= 4;
            k = 1;
            SWITCH j;
            CASE 2;
                LAST WHILE k == 1;
            CASE 3;
                IF j == 3; j = j + 1; NEXT; END;
            END;
            "$i,$j,$k\n";
            j = j + 1;
        END;
        i = i + 1;
    END;
-%]
-- expect --
1,1,1
1,2,1
1,4,1
2,1,1
2,2,1
2,4,1
3,1,1
3,2,1
3,4,1
4,1,1
4,2,1
4,4,1
-- test --
[%
    k = 1;
    LAST WHILE k == 1;
    "$k\n";
-%]
-- expect --
1
"""

main()

