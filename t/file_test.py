import os

from template.test import TestCase, main
from template.plugin import file as file_plugin


class FileTest(TestCase):
  def testFile(self):
    vars = { 'dir': 'test', 'file': 'test/src/foo' }
    stat = os.stat(vars['file'])
    for key in file_plugin.STAT_KEYS:
      vars[key] = getattr(stat, "st_" + key)
    self.Expect(DATA, None, vars)


DATA = r"""
-- test --
[% USE f = File('/foo/bar/baz.html', nostat=1) -%]
p: [% f.path %]
r: [% f.root %]
n: [% f.name %]
d: [% f.dir %]
e: [% f.ext %]
h: [% f.home %]
a: [% f.abs %]
-- expect --
p: /foo/bar/baz.html
r: 
n: baz.html
d: /foo/bar
e: html
h: ../..
a: /foo/bar/baz.html

-- test --
[% USE f = File('foo/bar/baz.html', nostat=1) -%]
p: [% f.path %]
r: [% f.root %]
n: [% f.name %]
d: [% f.dir %]
e: [% f.ext %]
h: [% f.home %]
a: [% f.abs %]
-- expect --
p: foo/bar/baz.html
r: 
n: baz.html
d: foo/bar
e: html
h: ../..
a: foo/bar/baz.html

-- test --
[% USE f = File('baz.html', nostat=1) -%]
p: [% f.path %]
r: [% f.root %]
n: [% f.name %]
d: [% f.dir %]
e: [% f.ext %]
h: [% f.home %]
a: [% f.abs %]
-- expect --
p: baz.html
r: 
n: baz.html
d: 
e: html
h: 
a: baz.html


-- test --
[% USE f = File('bar/baz.html', root='/foo', nostat=1) -%]
p: [% f.path %]
r: [% f.root %]
n: [% f.name %]
d: [% f.dir %]
e: [% f.ext %]
h: [% f.home %]
a: [% f.abs %]
-- expect --
p: bar/baz.html
r: /foo
n: baz.html
d: bar
e: html
h: ..
a: /foo/bar/baz.html


-- test -- 
[% USE f = File('bar/baz.html', root='/foo', nostat=1) -%]
p: [% f.path %]
h: [% f.home %]
rel: [% f.rel('wiz/waz.html') %]
-- expect --
p: bar/baz.html
h: ..
rel: ../wiz/waz.html


-- test -- 
[% USE baz = File('foo/bar/baz.html', root='/tmp/tt2', nostat=1) -%]
[% USE waz = File('wiz/woz/waz.html', root='/tmp/tt2', nostat=1) -%]
[% baz.rel(waz) %]
-- expect --
../../wiz/woz/waz.html


-- test --
[% USE f = File('foo/bar/baz.html', nostat=1) -%]
[[% f.atime %]]
-- expect --
[]

-- test --
[% USE f = File(file) -%]
[% f.path %]
[% f.name %]
-- expect --
-- process --
[% dir %]/src/foo
foo

-- test --
[% USE f = File(file) -%]
[% f.path %]
[% f.mtime %]
-- expect --
-- process --
[% dir %]/src/foo
[% mtime %]

-- test --
[% USE file(file) -%]
[% file.path %]
[% file.mtime %]
-- expect --
-- process --
[% dir %]/src/foo
[% mtime %]

-- test --
[% TRY -%]
[% USE f = File('') -%]
n: [% f.name %]
[% CATCH -%]
Drat, there was a [% error.type %] error.
[% END %]
-- expect --
Drat, there was a File error.


"""

main()

