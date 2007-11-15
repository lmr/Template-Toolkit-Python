from template.test import TestCase, main


class ListTest(TestCase):
  def testList(self):
    callsign = self._callsign()
    vars = {
      "data": [callsign[char] for char in "rjstyefz"],
      "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      "wxyz": [{"id": callsign["z"], "name": "Zebedee", "rank": "aa"},
               {"id": callsign["y"], "name": "Yinyang", "rank": "ba"},
               {"id": callsign["x"], "name": "Xeexeez", "rank": "ab"},
               {"id": callsign["w"], "name": "Warlock", "rank": "bb"}],
      "inst": [{"name": "piano", "url": "/roses.html"},
               {"name": "flute", "url": "/blow.html"},
               {"name": "organ", "url": "/tulips.html"}],
      "nest": [[3, 1, 4], [2, [7, 1, 8]]]
    }
    for char in "abcde":
      vars[char] = callsign[char]
    self.Expect(DATA, {}, vars)


DATA = r"""

#------------------------------------------------------------------------
# GET 
#------------------------------------------------------------------------
-- test --
[% data.0 %] and [% data.1 %]
-- expect --
romeo and juliet

-- test --
[% data.first %] - [% data.last %]
-- expect --
romeo - zulu

-- test --
[% data.size %] [% data.max %]
-- expect --
8 7

-- test --
[% data.join(', ') %]
-- expect --
romeo, juliet, sierra, tango, yankee, echo, foxtrot, zulu

-- test --
[% data.reverse.join(', ') %]
-- expect --
zulu, foxtrot, echo, yankee, tango, sierra, juliet, romeo

-- test --
[% data.sort.reverse.join(' - ') %]
-- expect --
zulu - yankee - tango - sierra - romeo - juliet - foxtrot - echo

-- test --
[% FOREACH item = wxyz.sort('id') -%]
* [% item.name %]
[% END %]
-- expect --
* Warlock
* Xeexeez
* Yinyang
* Zebedee

-- test --
[% FOREACH item = wxyz.sort('rank') -%]
* [% item.name %]
[% END %]
-- expect --
* Zebedee
* Xeexeez
* Yinyang
* Warlock

-- test --
[% FOREACH n = [0..6] -%]
[% days.$n +%]
[% END -%]
-- expect --
Mon
Tue
Wed
Thu
Fri
Sat
Sun

-- test --
[% data = [ 'one', 'two', data.first ] -%]
[% data.join(', ') %]
-- expect --
one, two, romeo

-- test --
[% data = [ 90, 8, 70, 6, 1, 11, 10, 2, 5, 50, 52 ] -%]
 sort: [% data.sort.join(', ') %]
nsort: [% data.nsort.join(', ') %]
-- expect --
 sort: 1, 10, 11, 2, 5, 50, 52, 6, 70, 8, 90
nsort: 1, 2, 5, 6, 8, 10, 11, 50, 52, 70, 90

-- test --
[% ilist = [] -%]
[% ilist.push("<a href=\"$i.url\">$i.name</a>") FOREACH i = inst -%]
[% ilist.join(",\n") -%]
[% global.ilist = ilist -%]
-- expect --
<a href="/roses.html">piano</a>,
<a href="/blow.html">flute</a>,
<a href="/tulips.html">organ</a>

-- test -- 
[% global.ilist.pop %]
-- expect --
<a href="/tulips.html">organ</a>

-- test -- 
[% global.ilist.shift %]
-- expect --
<a href="/roses.html">piano</a>

-- test -- 
[% global.ilist.unshift('another') -%]
[% global.ilist.join(', ') %]
-- expect --
another, <a href="/blow.html">flute</a>

-- test --
[% nest.0.0 %].[% nest.0.1 %][% nest.0.2 +%]
[% nest.1.shift %].[% nest.1.0.join('') %]
-- expect --
3.14
2.718

-- test --
[% # define some initial data
   people   => [ 
     { id => 'tom',   name => 'Tom'     },
     { id => 'dick',  name => 'Richard' },
     { id => 'larry', name => 'Larry'   },
   ]
-%]
[% folk = [] -%]
[% folk.push("<a href=\"${person.id}.html\">$person.name</a>")
       FOREACH person = people.sort('name') -%]
[% folk.join(",\n") -%]
-- expect --
<a href="larry.html">Larry</a>,
<a href="dick.html">Richard</a>,
<a href="tom.html">Tom</a>

-- test --
[% data.grep('r').join(', ') %]
-- expect --
romeo, sierra, foxtrot

-- test --
[% data.grep('^r').join(', ') %]
-- expect --
romeo
"""

main()
