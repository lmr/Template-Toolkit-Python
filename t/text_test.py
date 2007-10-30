from template import Template
from template.test import TestCase, main


class Stringy:
  def __init__(self, text):
    self.text = text

  def asString(self):
    return self.text

  __str__ = asString


class TextTest(TestCase):
  def testText(self):
    tt = (("basic", Template()),
          ("interp", Template({ "INTERPOLATE": 1 })))
    vars = self._callsign()
    v2 = { "ref": lambda obj: "%s[%s]" % (obj, obj.__class__.__name__),
           "sfoo": Stringy("foo"),
           "sbar": Stringy("bar") }
    vars.update(v2)
    self.Expect(DATA, tt, vars)


DATA = r"""
-- test --
This is a text block "hello" 'hello' 1/3 1\4 <html> </html>
$ @ { } @{ } ${ } # ~ ' ! % *foo
$a ${b} $c
-- expect --
This is a text block "hello" 'hello' 1/3 1\4 <html> </html>
$ @ { } @{ } ${ } # ~ ' ! % *foo
$a ${b} $c

-- test --
<table width=50%>&copy;
-- expect --
<table width=50%>&copy;

-- test --
[% foo = 'Hello World' -%]
start
[%
#
# [% foo %]
#
#
-%]
end
-- expect --
start
end

-- test --
pre
[%
# [% PROCESS foo %]
-%]
mid
[% BLOCK foo; "This is foo"; END %]
-- expect --
pre
mid

-- test --
-- use interp --
This is a text block "hello" 'hello' 1/3 1\4 <html> </html>
\$ @ { } @{ } \${ } # ~ ' ! % *foo
$a ${b} $c
-- expect --
This is a text block "hello" 'hello' 1/3 1\4 <html> </html>
$ @ { } @{ } ${ } # ~ ' ! % *foo
alpha bravo charlie

-- test --
<table width=50%>&copy;
-- expect --
<table width=50%>&copy;

-- test --
[% foo = 'Hello World' -%]
start
[%
#
# [% foo %]
#
#
-%]
end
-- expect --
start
end

-- test --
pre
[%
#
# [% PROCESS foo %]
#
-%]
mid
[% BLOCK foo; "This is foo"; END %]
-- expect --
pre
mid

-- test --
[% a = "C'est un test"; a %]
-- expect --
C'est un test

-- test --
[% META title = "C'est un test" -%]
[% component.title -%]
-- expect --
C'est un test

-- test --
[% META title = 'C\'est un autre test' -%]
[% component.title -%]
-- expect --
C'est un autre test

-- test --
[% META title = "C'est un \"test\"" -%]
[% component.title -%]
-- expect --
C'est un "test"

-- test --
[% sfoo %]/[% sbar %]
-- expect --
foo/bar

-- test --
[%  s1 = "$sfoo"
    s2 = "$sbar ";
    s3  = sfoo;
    ref(s1);
    '/';
    ref(s2);
    '/';
    ref(s3);
-%]
-- expect --
foo[str]/bar [str]/foo[Stringy]

"""

main()

