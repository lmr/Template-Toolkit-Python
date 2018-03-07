from template import Template
from template.stash import Stash
from template.test import TestCase, main


class MyObject:
    def __init__(self, name):
        self.__name = name

    def name(self):
        return self.__name


def jumble(seq, chop=1):
    if len(seq) > 3:
        for i in range(chop):
            seq.append(seq.pop(0))
    return seq


class ListVmethodsTest(TestCase):
    def testListVmethods(self):
        def odd(seq): return [x for x in seq if x % 2 != 0]
        Stash.LIST_OPS["sum"] = lambda seq: sum(seq, 0)
        Stash.LIST_OPS["odd"] = odd
        Stash.LIST_OPS["jumble"] = jumble
        params = {"metavars": ("foo", "bar", "baz", "qux", "wiz", "waz", "woz"),
                  "people": [{"id": "tom", "name": "Tom"},
                             {"id": "dick", "name": "Richard"},
                             {"id": "larry", "name": "Larry"}],
                  "primes": (13, 11, 17, 19, 2, 3, 5, 7),
                  "phones": {"3141": "Leon", "5131": "Andy", "4131": "Simon"},
                  "groceries": {"Flour": 3, "Milk": 1, "Peanut Butter": 21},
                  "names": [MyObject(x) for x in ("Tom", "Dick", "Larry")],
                  "numbers": [MyObject(x) for x in ("1", "02", "10", "12", "021")],
                  "duplicates": (1, 1, 2, 2, 3, 3, 4, 4, 5, 5)}
        context = Template().context()
        context.define_vmethod("list", "oddnos", odd)
        context.define_vmethod("array", "jumblate", jumble)

        self.Expect(DATA, None, params)


DATA = r"""

#------------------------------------------------------------------------
# list virtual methods
#------------------------------------------------------------------------

-- test --
[% metavars.first %]
-- expect --
foo

-- test --
[% metavars.last %]
-- expect --
woz

-- test --
[% metavars.size %]
-- expect --
7

-- test --
[% empty = [ ];
   empty.size 
%]
-- expect --
0

-- test --
[% metavars.max %]
-- expect --
6

-- test --
[% metavars.join %]
-- expect --
foo bar baz qux wiz waz woz

-- test --
[% metavars.join(', ') %]
-- expect --
foo, bar, baz, qux, wiz, waz, woz

-- test --
[% metavars.sort.join(', ') %]
-- expect --
bar, baz, foo, qux, waz, wiz, woz

-- test --
[% metavars.defined ? 'list def ok' : 'list def not ok' %]
[% metavars.defined(2) ? 'list two ok' : 'list two not ok' %]
[% metavars.defined(7) ? 'list seven not ok' : 'list seven ok' %]
-- expect --
list def ok
list two ok
list seven ok

-- test --
[% FOREACH person = people.sort('id') -%]
[% person.name +%]
[% END %]
-- expect --
Richard
Larry
Tom

-- test --
[% FOREACH obj = names.sort('name') -%]
[% obj.name +%]
[% END %]
-- expect --
Dick
Larry
Tom

-- test --
[% FOREACH obj = numbers.sort('name') -%]
[% obj.name +%]
[% END %]
-- expect --
02
021
1
10
12

-- test --
[% FOREACH obj = numbers.nsort('name') -%]
[% obj.name +%]
[% END %]
-- expect --
1
02
10
12
021

-- test --
[% FOREACH person = people.sort('name') -%]
[% person.name +%]
[% END %]
-- expect --
Larry
Richard
Tom

-- test --
[% folk = [] -%]
[% folk.push("<a href=\"${person.id}.html\">$person.name</a>")
    FOREACH person = people.sort('id') -%]
[% folk.join(",\n") %]
-- expect --
<a href="dick.html">Richard</a>,
<a href="larry.html">Larry</a>,
<a href="tom.html">Tom</a>

-- test --
[% primes.sort.join(', ') %]
-- expect --
11, 13, 17, 19, 2, 3, 5, 7

-- test --
[% primes.nsort.join(', ') %]
-- expect --
2, 3, 5, 7, 11, 13, 17, 19

-- test --
[% duplicates.unique.join(', ') %]
--expect --
1, 2, 3, 4, 5

-- test --
[% duplicates.unique.join(', ') %]
-- expect --
1, 2, 3, 4, 5



-- test --
-- name list import one --
[% list_one = [ 1 2 3 ];
   list_two = [ 4 5 6 ];
   list_one.import(list_two).join(', ') %]
-- expect --
1, 2, 3, 4, 5, 6

-- test --
-- name list import two --
[% list_one = [ 1 2 3 ];
   list_two = [ 4 5 6 ];
   list_three = [ 7 8 9 0 ];
   list_one.import(list_two, list_three).join(', ') %]
-- expect --
1, 2, 3, 4, 5, 6, 7, 8, 9, 0


-- test --
-- name list merge one --
[% list_one = [ 1 2 3 ];
   list_two = [ 4 5 6 ];
   "'$l' " FOREACH l = list_one.merge(list_two) %]
-- expect --
'1' '2' '3' '4' '5' '6' 

-- test --
-- name list merge two --
[% list_one = [ 1 2 3 ];
   list_two = [ 4 5 6 ];
   list_three = [ 7 8 9 0 ];
   "'$l' " FOREACH l = list_one.merge(list_two, list_three) %]
-- expect --
'1' '2' '3' '4' '5' '6' '7' '8' '9' '0' 

-- test --
[% list_one = [ 1 2 3 4 5 ] -%]
a: [% list_one.splice.join(', ') %]
b: [% list_one.size ? list_one.join(', ') : 'empty list' %]
-- expect --
a: 1, 2, 3, 4, 5
b: empty list

-- test --
[% list_one = [ 'a' 'b' 'c' 'd' 'e' ] -%]
a: [% list_one.splice(3).join(', ') %]
b: [% list_one.join(', ') %]
-- expect --
a: d, e
b: a, b, c

-- test --
[% list_one = [ 'a' 'b' 'c' 'd' 'e' ] -%]
c: [% list_one.splice(3, 1).join(', ') %]
d: [% list_one.join(', ') %]
-- expect --
c: d
d: a, b, c, e

-- test --
[% list_one = [ 'a' 'b' 'c' 'd' 'e' ] -%]
c: [% list_one.splice(3, 1, 'foo').join(', ') %]
d: [% list_one.join(', ') %]
e: [% list_one.splice(0, 1, 'ping', 'pong').join(', ') %]
f: [% list_one.join(', ') %]
g: [% list_one.splice(-1, 1, ['wibble', 'wobble']).join(', ') %]
h: [% list_one.join(', ') %]
-- expect --
c: d
d: a, b, c, foo, e
e: a
f: ping, pong, b, c, foo, e
g: e
h: ping, pong, b, c, foo, wibble, wobble

-- test --
-- name scrabble --
[% play_game = [ 'play', 'scrabble' ];
   ping_pong = [ 'ping', 'pong' ] -%]
a: [% play_game.splice(1, 1, ping_pong).join %]
b: [% play_game.join %]
-- expect --
a: scrabble
b: play ping pong


-- test --
-- name first --
[% primes = [ 2, 3, 5, 7, 11, 13 ] -%]
[% primes.first +%]
[% primes.first(3).join(', ') %]
-- expect --
2
2, 3, 5

-- test --
-- name first --
[% primes = [ 2, 3, 5, 7, 11, 13 ] -%]
[% primes.last +%]
[% primes.last(3).join(', ') %]
-- expect --
13
7, 11, 13


-- test --
-- name slice --
[% primes = [ 2, 3, 5, 7, 11, 13 ] -%]
[% primes.slice(0, 2).join(', ') +%]
[% primes.slice(-2, -1).join(', ') +%]
[% primes.slice(3).join(', ') +%]
[% primes.slice.join(', ') +%]
--expect --
2, 3, 5
11, 13
7, 11, 13
2, 3, 5, 7, 11, 13


-- test --
-- name list.hash --
[% items = ['zero', 'one', 'two', 'three'];
   hash = items.hash(0);
   "$key = $value\n" FOREACH hash.pairs;
-%]
-- expect --
0 = zero
1 = one
2 = two
3 = three

-- test --
-- name list.hash(10) --
[% items = ['zero', 'one', 'two', 'three'];
   hash = items.hash(10);
   "$key = $value\n" FOREACH hash.pairs;
-%]
-- expect --
10 = zero
11 = one
12 = two
13 = three


-- test --
-- name list.hash --
[% items = ['zero', 'one', 'two', 'three'];
   hash = items.hash;
   "$key = $value\n" FOREACH hash.pairs;
-%]
-- expect --
two = three
zero = one



#------------------------------------------------------------------------
# USER DEFINED LIST OPS
#------------------------------------------------------------------------

-- test --
[% items = [0..6] -%]
[% items.jumble.join(', ') %]
[% items.jumble(3).join(', ') %]
-- expect --
1, 2, 3, 4, 5, 6, 0
4, 5, 6, 0, 1, 2, 3

-- test --
-- name jumblate method --
[% items = [0..6] -%]
[% items.jumblate.join(', ') %]
[% items.jumblate(3).join(', ') %]
-- expect --
1, 2, 3, 4, 5, 6, 0
4, 5, 6, 0, 1, 2, 3

-- test -- 
[% primes.sum %]
-- expect --
77

-- test --
[% primes.odd.nsort.join(', ') %]
-- expect --
3, 5, 7, 11, 13, 17, 19

-- test --
-- name oddnos --
[% primes.oddnos.nsort.join(', ') %]
-- expect --
3, 5, 7, 11, 13, 17, 19

-- test --
[% FOREACH n = phones.sort -%]
[% phones.$n %] is [% n %],
[% END %]
-- expect --
Andy is 5131,
Leon is 3141,
Simon is 4131,

-- test --
-- name groceries --
[% FOREACH n = groceries.nsort.reverse -%]
I want [% groceries.$n %] kilos of [% n %],
[% END %]
-- expect --
I want 21 kilos of Peanut Butter,
I want 3 kilos of Flour,
I want 1 kilos of Milk,



-- test --
[% hash = { }
   list = [ hash ]
   list.last.message = 'Hello World';
   "message: $list.last.message\n"
-%]

-- expect --
message: Hello World

"""

main()
