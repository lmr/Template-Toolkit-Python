import re

from template import Template
from template.stash import Stash
from template.test import TestCase, main


def commify(text, c=",", n=3):
  if n >= 1:
    regex = re.compile(r"[-+]?\d+(\d{%d})" % n)
    while True:
      match = regex.match(text)
      if match:
        text = "%s%s%s" % (text[:match.start(1)], c, text[match.start(1):])
      else:
        break
  return text


class TextVmethodsTest(TestCase):
  def testTextVmethods(self):
    Stash.SCALAR_OPS["commify"] = commify
    Template().context().define_vmethod("item", "commas", commify)
    params = { "undef": None,
               "zero": 0,
               "one": 1,
               "animal": "cat",
               "string": "The cat sat on the mat",
               "spaced": "  The dog sat on the log" }
    self.Expect(DATA, None, params)


DATA = r"""

#------------------------------------------------------------------------
# defined
#------------------------------------------------------------------------

-- test --
[% notdef.defined ? 'def' : 'undef' %]
-- expect --
undef

-- test --
[% undef.defined ? 'def' : 'undef' %]
-- expect --
undef

-- test --
[% zero.defined ? 'def' : 'undef' %]
-- expect --
def

-- test --
[% one.defined ? 'def' : 'undef' %]
-- expect --
def

-- test --
[% string.length %]
-- expect --
22

-- test --
[% string.sort.join %]
-- expect --
The cat sat on the mat

-- test --
[% string.split.join('_') %]
-- expect --
The_cat_sat_on_the_mat
-- test --

-- test --
[% string.split(' ', 3).join('_') %]
-- expect --
The_cat_sat on the mat

-- test --
[% spaced.split.join('_') %]
-- expect --
The_dog_sat_on_the_log

-- test --
[% spaced.split(' ').join('_') %]
-- expect --
__The_dog_sat_on_the_log

-- test --
-- name: text.list --
[% string.list.join %]
-- expect --
The cat sat on the mat

-- test --
-- name: text.hash --
[% string.hash.value %]
-- expect --
The cat sat on the mat

-- test --
-- name: text.size --
[% string.size %]
-- expect --
1

-- test --
-- name: text.repeat --
[% animal.repeat(3) %]
-- expect --
catcatcat

-- test --
-- name: text.search --
[% animal.search('at$') ? "found 'at\$'" : "didn't find 'at\$'" %]
-- expect --
found 'at$'

-- test --
-- name: text.search --
[% animal.search('^at') ? "found '^at'" : "didn't find '^at'" %]
-- expect --
didn't find '^at'

-- test --
-- name: text.match an --
[% text = 'bandanna';
   text.match('an') ? 'match' : 'no match'
%]
-- expect --
match

-- test --
-- name: text.match on --
[% text = 'bandanna';
   text.match('on') ? 'match' : 'no match'
%]
-- expect --
no match

-- test --
-- name: text.match global an --
[% text = 'bandanna';
   text.match('an', 1).size %] matches
-- expect --
2 matches

-- test --
-- name: text.match global an --
[% text = 'bandanna' -%]
matches are [% text.match('an+', 1).join(', ') %]
-- expect --
matches are an, ann

-- test --
-- name: text.match global on --
[% text = 'bandanna';
   text.match('on+', 1) ? 'match' : 'no match'
%]
-- expect --
no match

-- test --
-- name: text substr method --
[% text = 'Hello World' -%]
a: [% text.substr(6) %]!
b: [% text.substr(0, 5) %]!
c: [% text.substr(0, 5, 'Goodbye') %]!
d: [% text %]!
-- expect --
a: World!
b: Hello!
c: Goodbye World!
d: Hello World!

-- test --
-- name: another text substr method --
[% text = 'foo bar baz wiz waz woz' -%]
a: [% text.substr(4, 3) %]
b: [% text.substr(12) %]
c: [% text.substr(0, 11, 'FOO') %]
d: [% text %]
-- expect --
a: bar
b: wiz waz woz
c: FOO wiz waz woz
d: foo bar baz wiz waz woz


-- test --
-- name: text.remove --
[% text = 'hello world!';
   text.remove('\s+world')
%]
-- expect --
hello!



-- test --
-- name chunk left --
[% string = 'TheCatSatTheMat' -%]
[% string.chunk(3).join(', ') %]
-- expect --
The, Cat, Sat, The, Mat

-- test --
-- name chunk leftover --
[% string = 'TheCatSatonTheMat' -%]
[% string.chunk(3).join(', ') %]
-- expect --
The, Cat, Sat, onT, heM, at

-- test --
-- name chunk right --
[% string = 'TheCatSatTheMat' -%]
[% string.chunk(-3).join(', ') %]
-- expect --
The, Cat, Sat, The, Mat

-- test --
-- name chunk rightover --
[% string = 'TheCatSatonTheMat' -%]
[% string.chunk(-3).join(', ') %]
-- expect --
Th, eCa, tSa, ton, The, Mat

-- test --
-- name chunk ccard  --
[% ccard_no = "1234567824683579";
   ccard_no.chunk(4).join
%]
-- expect --
1234 5678 2468 3579


-- test --
[% string = 'foo' -%]
[% string.repeat(3) %]
-- expect --
foofoofoo

-- test --
[% string1 = 'foobarfoobarfoo'
   string2 = 'foobazfoobazfoo'
-%]
[% string1.search('bar') ? 'ok' : 'not ok' %]
[% string2.search('bar') ? 'not ok' : 'ok' %]
[% string1.replace('bar', 'baz') %]
[% string2.replace('baz', 'qux') %]
-- expect --
ok
ok
foobazfoobazfoo
fooquxfooquxfoo

-- test --
[% string1 = 'foobarfoobarfoo'
   string2 = 'foobazfoobazfoo'
-%]
[% string1.match('bar') ? 'ok' : 'not ok' %]
[% string2.match('bar') ? 'not ok' : 'ok' %]
-- expect --
ok
ok

-- test --
[% string = 'foo     bar   ^%$ baz' -%]
[% string.replace('\W+', '_') %]
-- expect --
foo_bar_baz

-- test --
[% var = 'value99' ;
   var.replace('value', '')
%]
-- expect --
99

-- test --
[% bob = "0" -%]
bob: [% bob.replace('0','') %].
-- expect --
bob: .

-- test --
[% string = 'The cat sat on the mat';
   match  = string.match('The (\w+) (\w+) on the (\w+)');
-%]
[% match.0 %].[% match.1 %]([% match.2 %])
-- expect --
cat.sat(mat)

-- test --
[% string = 'The cat sat on the mat' -%]
[% IF (match  = string.match('The (\w+) sat on the (\w+)')) -%]
matched animal: [% match.0 %]  place: [% match.1 %]
[% ELSE -%]
no match
[% END -%]
[% IF (match  = string.match('The (\w+) shat on the (\w+)')) -%]
matched animal: [% match.0 %]  place: [% match.1 %]
[% ELSE -%]
no match
[% END -%]
-- expect --
matched animal: cat  place: mat
no match


-- test --
[% big_num = "1234567890"; big_num.commify %]
-- expect --
1,234,567,890

-- test --
[% big_num = "1234567890"; big_num.commify(":", 2) %]
-- expect --
12:34:56:78:90

-- test --
[% big_num = "1234567812345678"; big_num.commify(" ", 4) %]
-- expect --
1234 5678 1234 5678

-- test --
[% big_num = "hello world"; big_num.commify %]
-- expect --
hello world

-- test --
[% big_num = "1234567890"; big_num.commas %]
-- expect --
1,234,567,890

"""

main()
