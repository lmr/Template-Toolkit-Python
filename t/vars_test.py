from template import Template, TemplateException
from template.stash import Stash
from template.test import TestCase, main


class VarsTest(TestCase):
    def testVarsV1(self):
        params = self.make_params()
        tt = (("default", Template({"INTERPOLATE": 1,
                                    "ANYCASE": 1,
                                    "V1DOLLAR": 1})),
              ("notcase", Template({"INTERPOLATE": 1,
                                    "V1DOLLAR": 0})))
        self.Expect(DATA_V1, tt, params)

    def testVarsV2(self):
        params = self.make_params()
        tt = (("default", Template({"INTERPOLATE": 1, "ANYCASE": 1})),
              ("notcase", Template({"INTERPOLATE": 1, "ANYCASE": 0})))
        self.Expect(DATA_V2, tt, params)

    def make_params(self):
        c = self._callsign()
        count = [0]

        def up():
            count[0] += 1
            return count[0]

        def down():
            count[0] -= 1
            return count[0]

        def reset(arg=None):
            count[0] = arg or 0
            return count[0]

        def halt():
            raise TemplateException("stop", "stopped")

        def expose():
            Stash.PRIVATE = None
        return {
            "a": c["a"],
            "b": c["b"],
            "c": c["c"],
            "d": c["d"],
            "e": c["e"],
            "f": {"g": c["g"],
                  "h": c["h"],
                  "i": {"j": c["j"],
                        "k": c["k"]}},
            "g": "solo %s" % c["g"],
            "l": c["l"],
            "r": c["r"],
            "s": c["s"],
            "t": c["t"],
            "w": c["w"],
            "n": lambda *_: count[0],
            "up": up,
            "down": down,
            "reset": reset,
            "undef": lambda *_: None,
            "zero": lambda *_: 0,
            "one": lambda *_: "one",
            "halt": halt,
            "join": lambda join="", *args: join.join(args),
            "split": lambda s="", arg="": arg.split(s),
            "magic": {"chant": "Hocus Pocus",
                      "spell": lambda *args: " and a bit of ".join(args)},
            "day": {"prev": yesterday,
                    "this": today,
                    "next": tomorrow},
            "belief": belief,
            "people": lambda *_: ("Tom", "Dick", "Harry"),
            "gee": "g",
            "letter%s" % c["a"]: "'%s'" % c["a"],
            "yankee": yankee,
            "_private": 123,
            "_hidden": 456,
            "expose": expose,
            "add": lambda x, y: x + y}


def yesterday():
    return "All my troubles seemed so far away..."


def today(when="Now"):
    return "%s it looks as though they're here to stay." % when


days = ["Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"]
day = -1


def tomorrow(dayno=None):
    global day
    if dayno is None:
        day = (day + 1) % 7
        dayno = day
    return days[dayno]


def belief(*beliefs):
    return "Oh I believe in %s." % (" and ".join(beliefs) or "<nothing>")


def yankee():
    return [None, {"a": 1}, None, {"a": 2}]


DATA_V1 = r"""

#------------------------------------------------------------------------
# GET 
#------------------------------------------------------------------------

-- test --
[% a %]
[% $a %]
[% GET b %]
[% GET $b %]
[% get c %]
[% get $c %]
-- expect --
alpha
alpha
bravo
bravo
charlie
charlie

-- test --
[% b %] [% $b %] [% GET b %] [% GET $b %]
-- expect --
bravo bravo bravo bravo

-- test --
$a $b ${c} ${d} [% $e %]
-- expect --
alpha bravo charlie delta echo

-- test --
[% letteralpha %]
[% ${"letter$a"} %]
[% GET ${"letter$a"} %]
-- expect --
'alpha'
'alpha'
'alpha'

-- test --
[% f.g %] [% $f.g %] [% $f.$g %]
-- expect --
golf golf golf

-- test --
[% GET f.h %] [% get $f.h %] [% get f.${'h'} %] [% get $f.${'h'} %]
-- expect --
hotel hotel hotel hotel

-- test --
$f.h ${f.g} ${f.h}.gif
-- expect --
hotel golf hotel.gif

-- test --
[% f.i.j %] [% $f.i.j %] [% f.$i.j %] [% f.i.$j %] [% $f.$i.$j %]
-- expect --
juliet juliet juliet juliet juliet

-- test --
[% f.i.j %] [% $f.i.j %] [% GET f.i.j %] [% GET $f.i.j %]
-- expect --
juliet juliet juliet juliet

-- test --
[% get $f.i.k %]
-- expect --
kilo

-- test --
[% f.i.j %] $f.i.k [% f.${'i'}.${"j"} %] ${f.i.k}.gif
-- expect --
juliet kilo juliet kilo.gif

-- test --
[% 'this is literal text' %]
[% GET 'so is this' %]
[% "this is interpolated text containing $r and $f.i.j" %]
[% GET "$t?" %]
[% "<a href=\"${f.i.k}.html\">$f.i.k</a>" %]
-- expect --
this is literal text
so is this
this is interpolated text containing romeo and juliet
tango?
<a href="kilo.html">kilo</a>

-- test --
[% name = "$a $b $w" -%]
Name: $name
-- expect --
Name: alpha bravo whisky

-- test --
[% join('--', a b, c, f.i.j) %]
-- expect --
alpha--bravo--charlie--juliet

-- test --
[% text = 'The cat sat on the mat' -%]
[% FOREACH word = split(' ', text) -%]<$word> [% END %]
-- expect --
<The> <cat> <sat> <on> <the> <mat> 

-- test -- 
[% magic.chant %] [% GET magic.chant %]
[% magic.chant('foo') %] [% GET $magic.chant('foo') %]
-- expect --
Hocus Pocus Hocus Pocus
Hocus Pocus Hocus Pocus

-- test -- 
<<[% magic.spell %]>>
[% magic.spell(a b c) %]
-- expect --
<<>>
alpha and a bit of bravo and a bit of charlie

-- test --
[% one %] [% one('two', 'three') %] [% one(2 3) %]
-- expect --
one one one

-- test --
[% day.prev %]
[% day.this %]
[% belief('yesterday') %]
-- expect --
All my troubles seemed so far away...
Now it looks as though they're here to stay.
Oh I believe in yesterday.

-- test --
Yesterday, $day.prev
$day.this
${belief('yesterday')}
-- expect --
Yesterday, All my troubles seemed so far away...
Now it looks as though they're here to stay.
Oh I believe in yesterday.

-- test --
-- use notcase --
[% day.next %]
$day.next
-- expect --
Monday
Tuesday

-- test --
[% FOREACH [ 1 2 3 4 5 ] %]$day.next [% END %]
-- expect --
Wednesday Thursday Friday Saturday Sunday 

-- test --
-- use default --
before
[% halt %]
after

-- expect --
before

#------------------------------------------------------------------------
# CALL 
#------------------------------------------------------------------------

-- test --
before [% CALL a %]a[% CALL b %]n[% CALL c %]d[% CALL d %] after
-- expect --
before and after

-- test --
..[% CALL undef %]..
-- expect --
....

-- test --
..[% CALL zero %]..
-- expect --
....

-- test --
..[% n %]..[% CALL n %]..
-- expect --
..0....

-- test --
..[% up %]..[% CALL up %]..[% n %]
-- expect --
..1....2

-- test --
[% CALL reset %][% n %]
-- expect --
0

-- test --
[% CALL reset(100) %][% n %]
-- expect --
100

#------------------------------------------------------------------------
# SET 
#------------------------------------------------------------------------

-- test --
[% a = a %] $a
[% a = b %] $a
[% a = $c %] $a
[% $a = d %] $a
[% $a = $e %] $a
-- expect --
 alpha
 bravo
 charlie
 delta
 echo

-- test -- 
[% SET a = a %] $a
[% SET a = b %] $a
[% SET a = $c %] $a
[% SET $a = d %] $a
[% SET $a = $e %] $a
-- expect --
 alpha
 bravo
 charlie
 delta
 echo

-- test --
[% a = b
   b = c
   c = d
   d = e
%][% a %] [% b %] [% c %] [% d %]
-- expect --
bravo charlie delta echo

-- test --
[% SET
   a = c
   b = d
   c = e
%]$a $b $c
-- expect --
charlie delta echo

-- test --
[% a = f.g %] $a
[% a = $f.h %] $a
[% a = f.i.j %] $a
[% a = $f.i.k %] $a
-- expect --
 golf
 hotel
 juliet
 kilo

-- test --
[% f.g = r %] $f.g
[% $f.h = $r %] $f.h
[% f.i.j = $s %] $f.i.j
[% $f.i.k = f.i.j %] ${f.i.k}
-- expect --
 romeo
 romeo
 sierra
 sierra

-- test --
[% user = {
    id = 'abw'
    name = 'Andy Wardley'
    callsign = "[-$a-$b-$w-]"
   }
-%]
${user.id} ${ user.id } $user.id ${user.id}.gif
[% message = "$b: ${ user.name } (${user.id}) ${ user.callsign }" -%]
MSG: $message
-- expect --
abw abw abw abw.gif
MSG: bravo: Andy Wardley (abw) [-alpha-bravo-whisky-]

-- test --
[% product = {
     id   => 'XYZ-2000',
     desc => 'Bogon Generator',
     cost => 678,
   }
-%]
The $product.id $product.desc costs \$${product.cost}.00
-- expect --
The XYZ-2000 Bogon Generator costs $678.00

#------------------------------------------------------------------------
# DEFAULT
#------------------------------------------------------------------------

-- test --
[% a %]
[% DEFAULT a = b -%]
[% a %]
-- expect --
alpha
alpha

-- test --
[% a = '' -%]
[% DEFAULT a = b -%]
[% a %]
-- expect --
bravo

-- test --
[% a = ''   b = '' -%]
[% DEFAULT 
   a = c
   b = d
   z = r
-%]
[% a %] [% b %] [% z %]
-- expect --
charlie delta romeo


#------------------------------------------------------------------------
# 'global' vars
#------------------------------------------------------------------------

-- test --
[% global.version = '3.14' -%]
Version: [% global.version %]
-- expect --
Version: 3.14

-- test --
Version: [% global.version %]
-- expect --
Version: 3.14

"""

DATA_V2 = r"""

#------------------------------------------------------------------------
# GET 
#------------------------------------------------------------------------

-- test --
[[% nosuchvariable %]]
[$nosuchvariable]
-- expect --
[]
[]

-- test --
[% a %]
[% GET b %]
[% get c %]
-- expect --
alpha
bravo
charlie

-- test --
[% b %] [% GET b %]
-- expect --
bravo bravo

-- test --
$a $b ${c} ${d} [% e %]
-- expect --
alpha bravo charlie delta echo

-- test --
[% letteralpha %]
[% ${"letter$a"} %]
[% GET ${"letter$a"} %]
-- expect --
'alpha'
'alpha'
'alpha'

-- test --
[% f.g %] [% f.$gee %] [% f.${gee} %]
-- expect --
golf golf golf

-- test --
[% GET f.h %] [% get f.h %] [% f.${'h'} %] [% get f.${'h'} %]
-- expect --
hotel hotel hotel hotel

-- test --
$f.h ${f.g} ${f.h}.gif
-- expect --
hotel golf hotel.gif

-- test --
[% f.i.j %] [% GET f.i.j %] [% get f.i.k %]
-- expect --
juliet juliet kilo

-- test --
[% f.i.j %] $f.i.k [% f.${'i'}.${"j"} %] ${f.i.k}.gif
-- expect --
juliet kilo juliet kilo.gif

-- test --
[% 'this is literal text' %]
[% GET 'so is this' %]
[% "this is interpolated text containing $r and $f.i.j" %]
[% GET "$t?" %]
[% "<a href=\"${f.i.k}.html\">$f.i.k</a>" %]
-- expect --
this is literal text
so is this
this is interpolated text containing romeo and juliet
tango?
<a href="kilo.html">kilo</a>

-- test --
[% name = "$a $b $w" -%]
Name: $name
-- expect --
Name: alpha bravo whisky

-- test --
[% join('--', a b, c, f.i.j) %]
-- expect --
alpha--bravo--charlie--juliet

-- test --
[% text = 'The cat sat on the mat' -%]
[% FOREACH word = split(' ', text) -%]<$word> [% END %]
-- expect --
<The> <cat> <sat> <on> <the> <mat> 

-- test -- 
[% magic.chant %] [% GET magic.chant %]
[% magic.chant('foo') %] [% GET magic.chant('foo') %]
-- expect --
Hocus Pocus Hocus Pocus
Hocus Pocus Hocus Pocus

-- test -- 
<<[% magic.spell %]>>
[% magic.spell(a b c) %]
-- expect --
<<>>
alpha and a bit of bravo and a bit of charlie

-- test --
[% one %] [% one('two', 'three') %] [% one(2 3) %]
-- expect --
one one one

-- test --
[% day.prev %]
[% day.this %]
[% belief('yesterday') %]
-- expect --
All my troubles seemed so far away...
Now it looks as though they're here to stay.
Oh I believe in yesterday.

-- test --
Yesterday, $day.prev
$day.this
${belief('yesterday')}
-- expect --
Yesterday, All my troubles seemed so far away...
Now it looks as though they're here to stay.
Oh I believe in yesterday.

-- test --
-- use notcase --
[% day.next %]
$day.next
-- expect --
Monday
Tuesday

-- test --
[% FOREACH [ 1 2 3 4 5 ] %]$day.next [% END %]
-- expect --
Wednesday Thursday Friday Saturday Sunday 

-- test --
-- use default --
before
[% halt %]
after

-- expect --
before

-- test --
[% FOREACH k = yankee -%]
[% loop.count %]. [% IF k; k.a; ELSE %]undef[% END %]
[% END %]
-- expect --
1. undef
2. 1
3. undef
4. 2


#------------------------------------------------------------------------
# CALL 
#------------------------------------------------------------------------

-- test --
before [% CALL a %]a[% CALL b %]n[% CALL c %]d[% CALL d %] after
-- expect --
before and after

-- test --
..[% CALL undef %]..
-- expect --
....

-- test --
..[% CALL zero %]..
-- expect --
....

-- test --
..[% n %]..[% CALL n %]..
-- expect --
..0....

-- test --
..[% up %]..[% CALL up %]..[% n %]
-- expect --
..1....2

-- test --
[% CALL reset %][% n %]
-- expect --
0

-- test --
[% CALL reset(100) %][% n %]
-- expect --
100

#------------------------------------------------------------------------
# SET 
#------------------------------------------------------------------------

-- test --
[% a = a %] $a
[% a = b %] $a
-- expect --
 alpha
 bravo

-- test -- 
[% SET a = a %] $a
[% SET a = b %] $a
[% SET a = $c %] [$a]
[% SET a = $gee %] $a
[% SET a = ${gee} %] $a
-- expect --
 alpha
 bravo
 []
 solo golf
 solo golf

-- test --
[% a = b
   b = c
   c = d
   d = e
%][% a %] [% b %] [% c %] [% d %]
-- expect --
bravo charlie delta echo

-- test --
[% SET
   a = c
   b = d
   c = e
%]$a $b $c
-- expect --
charlie delta echo

-- test --
[% 'a' = d
   'include' = e
   'INCLUDE' = f.g
%][% a %]-[% ${'include'} %]-[% ${'INCLUDE'} %]
-- expect --
delta-echo-golf

-- test --
[% a = f.g %] $a
[% a = f.i.j %] $a
-- expect --
 golf
 juliet

-- test --
[% f.g = r %] $f.g
[% f.i.j = s %] $f.i.j
[% f.i.k = f.i.j %] ${f.i.k}
-- expect --
 romeo
 sierra
 sierra

-- test --
[% user = {
    id = 'abw'
    name = 'Andy Wardley'
    callsign = "[-$a-$b-$w-]"
   }
-%]
${user.id} ${ user.id } $user.id ${user.id}.gif
[% message = "$b: ${ user.name } (${user.id}) ${ user.callsign }" -%]
MSG: $message
-- expect --
abw abw abw abw.gif
MSG: bravo: Andy Wardley (abw) [-alpha-bravo-whisky-]

-- test --
[% product = {
     id   => 'XYZ-2000',
     desc => 'Bogon Generator',
     cost => 678,
   }
-%]
The $product.id $product.desc costs \$${product.cost}.00
-- expect --
The XYZ-2000 Bogon Generator costs $678.00

-- test --
[% data => {
       g => 'my data'
   }
   complex = {
       gee => 'g'
   }
-%]
[% data.${complex.gee} %]
-- expect --
my data


#------------------------------------------------------------------------
# DEFAULT
#------------------------------------------------------------------------

-- test --
[% a %]
[% DEFAULT a = b -%]
[% a %]
-- expect --
alpha
alpha

-- test --
[% a = '' -%]
[% DEFAULT a = b -%]
[% a %]
-- expect --
bravo

-- test --
[% a = ''   b = '' -%]
[% DEFAULT 
   a = c
   b = d
   z = r
-%]
[% a %] [% b %] [% z %]
-- expect --
charlie delta romeo


#------------------------------------------------------------------------
# 'global' vars
#------------------------------------------------------------------------

-- test --
[% global.version = '3.14' -%]
Version: [% global.version %]
-- expect --
Version: 3.14

-- test --
Version: [% global.version %]
-- expect --
Version: 3.14

-- test --
[% hash1 = {
      foo => 'Foo',
      bar => 'Bar',
   }
   hash2 = {
      wiz => 'Wiz',
      woz => 'Woz',
   }
-%]
[% hash1.import(hash2) -%]
keys: [% hash1.keys.sort.join(', ') %]
-- expect --
keys: bar, foo, wiz, woz

-- test --
[% mage = { name    =>    'Gandalf', 
        aliases =>  [ 'Mithrandir', 'Olorin', 'Incanus' ] }
-%]
[% import(mage) -%]
[% name %]
[% aliases.join(', ') %]
-- expect --
Gandalf
Mithrandir, Olorin, Incanus


# test private variables
-- test --
[[% _private %]][[% _hidden %]]
-- expect --
[][]

# make them visible
-- test --
[% CALL expose -%]
[[% _private %]][[% _hidden %]]
-- expect --
[123][456]



# Stas reported a problem with spacing in expressions but I can't
# seem to reproduce it...
-- test --
[% a = 4 -%]
[% b=6 -%]
[% c = a + b -%]
[% d=a+b -%]
[% c %]/[% d %]
-- expect --
10/10

-- test --
[% a = 1
   b = 2
   c = 3
-%]
[% d = 1+1 %]d: [% d %]
[% e = a+b %]e: [% e %]
-- expect --
d: 2
e: 3


# these tests check that the incorrect precedence in the parser has now
# been fixed, thanks to Craig Barrat.
-- test --
[%  1 || 0 && 0  # should be 1 || (0&&0), not (1||0)&&0 %]
-- expect --
1

-- test --
[%  1 + !0 + 1  # should be 1 + (!0) + 0, not 1 + !(0 + 1) %]
-- expect --
3

-- test --
[% "x" _ "y" == "y"; ','  # should be ("x"_"y")=="y", not "x"_("y"=="y") %]
-- expect --
,

-- test --
[% "x" _ "y" == "xy"      # should be ("x"_"y")=="xy", not "x"_("y"=="xy") %]
-- expect --
1

-- test --
[% add(3, 5) %]
-- expect --
8

-- test --
[% add(3 + 4, 5 + 7) %]
-- expect --
19

-- test --
[% a = 10;
   b = 20;
   c = 30;
   add(add(a,b+1),c*3);
%]
-- expect --
121

-- test --
[% a = 10;
   b = 20;
   c = 30;
   d = 5;
   e = 7;
   add(a+5, b < 10 ? c : d + e*5);
-%]
-- expect --
55
"""

if __name__ == '__main__':
    main()
