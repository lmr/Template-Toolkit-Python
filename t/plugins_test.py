import os
import sys

from template import Template
from template.plugins import Plugins
from template.test import TestCase, main


class PluginsTest(TestCase):
  def testPlugins(self):
    sys.path.insert(0, os.path.abspath("test/plugin"))
    tt1 = Template({ "PLUGIN_BASE": "MyPlugs" })
    tt2 = Template({ "PLUGINS": { "bar": "MyPlugs.Bar",
                                  "baz": ("MyPlugs.Foo", "Foo"),
                                  "cgi": ("MyPlugs.Bar", "Bar") } })
    tt3 = Template({ "LOAD_PYTHON": 1 })
    del Plugins.STD_PLUGINS["date"]
    Plugins.PLUGIN_BASE = ""
    tt4 = Template({ "PLUGIN_BASE": "MyPlugs" })
    tt5 = Template()
    tt = (("def", Template()),
          ("tt1", tt1),
          ("tt2", tt2),
          ("tt3", tt3),
          ("tt4", tt4),
          ("tt5", tt5))
    self.Expect(DATA, tt, self._callsign())


DATA = r"""
#------------------------------------------------------------------------
# basic plugin loads
#------------------------------------------------------------------------
-- test --
[% USE Table([2, 3, 5, 7, 11, 13], rows=2) -%]
[% Table.row(0).join(', ') %]
-- expect --
2, 5, 11

-- test --
[% USE table([17, 19, 23, 29, 31, 37], rows=2) -%]
[% table.row(0).join(', ') %]
-- expect --
17, 23, 31

-- test --
[% USE t = Table([41, 43, 47, 49, 53, 59], rows=2) -%]
[% t.row(0).join(', ') %]
-- expect --
41, 47, 53

-- test --
[% USE t = table([61, 67, 71, 73, 79, 83], rows=2) -%]
[% t.row(0).join(', ') %]
-- expect --
61, 71, 79

#------------------------------------------------------------------------
# load Foo plugin through custom PLUGIN_BASE
#------------------------------------------------------------------------
-- test --
-- use tt1 --
-- test --
[% USE t = table([89, 97, 101, 103, 107, 109], rows=2) -%]
[% t.row(0).join(', ') %]
-- expect --
89, 101, 107

-- test --
[% USE Foo(2) -%]
[% Foo.output %]
-- expect --
This is the Foo plugin, value is 2

-- test --
[% USE Bar(4) -%]
[% Bar.output %]
-- expect --
This is the Bar plugin, value is 4

#------------------------------------------------------------------------
# load Foo plugin through custom PLUGINS
#------------------------------------------------------------------------

-- test --
-- use tt2 --
[% USE t = table([113, 127, 131, 137, 139, 149], rows=2) -%]
[% t.row(0).join(', ') %]
-- expect --
113, 131, 139

-- test --
[% TRY -%]
[% USE Foo(8) -%]
[% Foo.output %]
[% CATCH -%]
ERROR: [% error.info %]
[% END %]
-- expect --
ERROR: Foo: plugin not found

-- test --
[% USE bar(16) -%]
[% bar.output %]
-- expect --
This is the Bar plugin, value is 16

-- test --
[% USE qux = baz(32) -%]
[% qux.output %]
-- expect --
This is the Foo plugin, value is 32

-- test --
[% USE wiz = cgi(64) -%]
[% wiz.output %]
-- expect --
This is the Bar plugin, value is 64

#------------------------------------------------------------------------
# LOAD_PERL
#------------------------------------------------------------------------

-- test --
-- use tt3 --
[% USE baz = MyPlugs.Baz(128) -%]
[% baz.output %]
-- expect --
This is the Baz module, value is 128

-- test --
[% USE boz = MyPlugs.Baz(256) -%]
[% boz.output %]
-- expect --
This is the Baz module, value is 256


#------------------------------------------------------------------------
# Test case insensitivity of plugin names.  We first look for the plugin 
# using the name specified in its original case. From v2.15 we also look 
# for standard plugins using the lower case conversion of the plugin name
# specified.
#------------------------------------------------------------------------

-- test --
[% USE mycgi = url('/cgi-bin/bar.pl', debug=1); %][% mycgi %]
-- expect --
/cgi-bin/bar.pl?debug=1

-- test --
[% USE mycgi = URL('/cgi-bin/bar.pl', debug=1); %][% mycgi %]
-- expect --
/cgi-bin/bar.pl?debug=1

-- test --
[% USE mycgi = UrL('/cgi-bin/bar.pl', debug=1); %][% mycgi %]
-- expect --
/cgi-bin/bar.pl?debug=1




#------------------------------------------------------------------------
# ADD_DEFAULT_PLUGIN_BASE = 0.
# Template::Plugins::URL no longer works since Template::Plugins is not
# added to the default plugin base. Same with others. However, url will
# work since it is specified as a plugin in
# Template::Plugins::STD_PLUGINS.
#------------------------------------------------------------------------

# should find Foo as we've specified 'MyPlugs' in the PLUGIN_BASE
-- test --
-- use tt4 --
[% USE Foo(20) -%]
[% Foo.output %]
-- expect --
This is the Foo plugin, value is 20


-- test --
-- use tt4 --
[% TRY -%]
[% USE Date() -%]
[% CATCH -%]
ERROR: [% error.info %]
[% END %]
-- expect --
ERROR: Date: plugin not found

-- test --
[% USE mycgi = url('/cgi-bin/bar.pl', debug=1); %][% mycgi %]
-- expect --
/cgi-bin/bar.pl?debug=1

"""

main()

