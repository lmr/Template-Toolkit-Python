from template.test import TestCase, main


class ReplaceTest(TestCase):
  def testReplace(self):
    self.Expect(DATA)


DATA = r"""

-- test --
-- name: two backrefs --
[% text = 'The cat sat on the mat';
   text.replace( '(\w+) sat on the (\w+)',
                 'dirty $1 shat on the filthy $2' )
%]
-- expect --
The dirty cat shat on the filthy mat


# test more than 9 captures to make sure $10, $11, etc., work ok
-- test --
-- name: ten+ backrefs --
[% text = 'one two three four five six seven eight nine ten eleven twelve thirteen';
   text.replace(
      '(\w+) (\w+) (\w+) (\w+) (\w+) (\w+) (\w+) (\w+) (\w+) (\w+) (\w+) (\w+)',
      '[$12-$11-$10-$9-$8-$7-$6-$5-$4-$3-$2-$1]'
   )
%]
-- expect --
[twelve-eleven-ten-nine-eight-seven-six-five-four-three-two-one] thirteen


-- test --
-- name: repeat backrefs --
[% text = 'one two three four five six seven eight nine ten eleven twelve thirteen';
   text.replace(
      '(\w+) ',
      '[$1]-'
   )
%]
-- expect --
[one]-[two]-[three]-[four]-[five]-[six]-[seven]-[eight]-[nine]-[ten]-[eleven]-[twelve]-thirteen

-- test --
-- name: one backref --
[% var = 'foo'; var.replace('f(o+)$', 'b$1') %]
-- expect --
boo

-- test --
-- name: three backrefs --
[% var = 'foo|bar/baz'; var.replace('(fo+)\|(bar)(.*)$', '[ $1, $2, $3 ]') %]
-- expect --
[ foo, bar, /baz ]


#------------------------------------------------------------------------
# tests based on Sergey's test script: http://martynoff.info/tt2/
#------------------------------------------------------------------------

-- test --
[% text = 'foo bar';
   text.replace('foo', 'bar')
%]
-- expect --
bar bar


-- test --
[% text = 'foo bar';
   text.replace('(f)(o+)', '$2$1')
%]
-- expect --
oof bar

-- test --
[% text = 'foo bar foo';
   text.replace('(?i)FOO', 'zoo')
%]
-- expect --
zoo bar zoo


#------------------------------------------------------------------------
# references to $n vars that don't exists are ignored
#------------------------------------------------------------------------

-- test --
[% text = 'foo bar';
   text.replace('(f)(o+)', '$20$1')
%]
-- expect --
f bar

-- test --
[% text = 'foo bar';
   text.replace('(f)(o+)', '$2$10')
%]
-- expect --
oo bar

-- test --
[% text = 'foo fgoo foooo bar';
   text.replace('((?:f([^o]*)(o+)\s)+)', '1=$1;2=$2;3=$3;')
%]
-- expect --
1=foo fgoo foooo ;2=;3=oooo;bar


#------------------------------------------------------------------------
# $n in source string should not be interpolated
#------------------------------------------------------------------------

-- test --
[% text = 'foo $1 bar';
   text.replace('(foo)(.*)(bar)', '$1$2$3')
%]
-- expect --
foo $1 bar

-- test --
[% text = 'foo $1 bar';
   text.replace('(foo)(.*)(bar)', '$3$2$1')
%]
-- expect --
bar $1 foo

-- test --
[% text = 'foo $200bar foobar';
   text.replace('(f)(o+)', 'zoo')
%]
-- expect --
zoo $200bar zoobar


#------------------------------------------------------------------------
# escaped \$ in replacement string
#------------------------------------------------------------------------

-- test --
-- name: escape dollar --
[% text = 'foo bar';
   text.replace('(f)(o+)', '\\$2$1')
%]
-- expect --
$2f bar


-- test --
-- name: escape backslash --
[% text = 'foo bar';
   text.replace('(f)(o+)', 'x$1\\\\y$2'); # this is 'x$1\\y$2'
%]
-- expect --
xf\yoo bar

-- test --
-- name: backslash again --
[% text = 'foo bar';
   text.replace('(f)(o+)', '$2\\\\$1');   # this is '$2\\$1'
%]
-- expect --
oo\f bar

-- test --
-- name: escape all over --
[% text = 'foo bar';
   text.replace('(f)(o+)', '$2\\\\\\$1'); # this is '$2\\\$')
%]
-- expect --
oo\$1 bar


-- test --
[% text = 'foo bar foobar';
   text.replace('(o)|([ar])', '$2!')
%]
-- expect --
f!! ba!r! f!!ba!r!


"""

main()
