import os
import time

import template
from template import config, constants, provider, test

# To test the $MAX_DIRS runaway limit:
provider.MAX_DIRS = 42


def delivered(provider, file):
  result, error = provider.fetch(file)
  return not error


def declined(provider, file):
  result, error = provider.fetch(file)
  return error == constants.STATUS_DECLINED


def denied(provider, file):
  result, error = provider.fetch(file)
  return error == constants.STATUS_ERROR


class DynamicPaths:
  def __init__(self, *paths):
    self.__paths = paths

  def paths(self):
    return list(self.__paths)


class ProviderTest(test.TestCase):
  def testProvider(self):
    dir = "test/src"
    lib = "test/lib"
    file = "foo"
    relfile = os.path.join(".", dir, file)
    absfile = os.path.join(os.path.abspath(dir), file)
    newfile = os.path.join(dir, "foobar")

    def update_file(*args):
      time.sleep(2)  # ensure file time stamps are different
      f = open(newfile, "w")
      for arg in args:
        f.write(str(arg))
      f.close()

    vars = { "file": file,
             "relfile": relfile,
             "absfile": absfile,
             "fixfile": update_file }

    update_file("This is the old content")

    #------------------------------------------------------------------------
    # instantiate a bunch of providers, using various different techniques, 
    # with different load options but sharing the same parser;  then set them
    # to work fetching some files and check they respond as expected
    #------------------------------------------------------------------------

    parser = config.Config.parser({"POST_CHOMP": 1})
    provinc = config.Config.provider(
      { "INCLUDE_PATH": dir, "PARSER": parser, "TOLERANT": 1 })
    provabs = config.Config.provider(
      { "ABSOLUTE": 1, "PARSER": parser })
    provrel = config.Config.provider(
      { "RELATIVE": 1, "PARSER": parser })
    self.assert_(provinc.PARSER is provabs.PARSER)
    self.assert_(provabs.PARSER is provrel.PARSER)

    self.assert_(delivered(provinc, file))
    self.assert_(declined(provinc, absfile))
    self.assert_(declined(provinc, relfile))
    self.assert_(declined(provabs, file))
    self.assert_(delivered(provabs, absfile))
    self.assert_(denied(provabs, relfile))
    self.assert_(declined(provrel, file))
    self.assert_(denied(provrel, absfile))
    self.assert_(delivered(provrel, relfile))

    #------------------------------------------------------------------------
    # now we'll fold those providers up into some Template objects that
    # we can pass to text_expect() to do some template driven testing
    #------------------------------------------------------------------------

    ttinc = template.Template({ "LOAD_TEMPLATES": [provinc] })
    ttabs = template.Template({ "LOAD_TEMPLATES": [provabs] })
    ttrel = template.Template({ "LOAD_TEMPLATES": [provrel] })

    def dpaths():
      return [os.path.join(lib, x) for x in "one", "two"]
    
    def badpaths():
      return [badpaths]

    ttd1 = template.Template(
      { "INCLUDE_PATH": [dpaths, dir], "PARSER": parser })
    ttd2 = template.Template(
      { "INCLUDE_PATH": [DynamicPaths(os.path.join(lib, "two"),
                                      os.path.join(lib, "one")), dir],
        "PARSER": parser })
    ttd3 = template.Template(
      { "INCLUDE_PATH": [ badpaths ], "PARSER": parser })
    uselist = (("ttinc", ttinc),
               ("ttabs", ttabs),
               ("ttrel", ttrel),
               ("ttd1", ttd1),
               ("ttd2", ttd2),
               ("ttdbad", ttd3))
    self.Expect(DATA, uselist, vars)


DATA = r"""
-- test --
-- use ttinc --
[% TRY %]
[% INCLUDE foo %]
[% INCLUDE $relfile %]
[% CATCH file %]
Error: [% error.type %] - [% error.info.split(': ').1 %]
[% END %]
-- expect --
This is the foo file, a is Error: file - not found


-- test --
[% TRY %]
[% INCLUDE foo %]
[% INCLUDE $absfile %]
[% CATCH file %]
Error: [% error.type %] - [% error.info.split(': ').1 %]
[% END %]
-- expect --
This is the foo file, a is Error: file - not found


-- test --
[% TRY %]
[% INSERT foo +%]
[% INSERT $absfile %]
[% CATCH file %]
Error: [% error %]
[% END %]
-- expect --
-- process --
[% TAGS [* *] %]
This is the foo file, a is [% a -%]
Error: file error - [* absfile *]: not found

#------------------------------------------------------------------------

-- test --
-- use ttrel --
[% TRY %]
[% INCLUDE $relfile %]
[% INCLUDE foo %]
[% CATCH file -%]
Error: [% error.type %] - [% error.info %]
[% END %]
-- expect --
This is the foo file, a is Error: file - foo: not found

-- test --
[% TRY %]
[% INCLUDE $relfile -%]
[% INCLUDE $absfile %]
[% CATCH file %]
Error: [% error.type %] - [% error.info.split(': ').1 %]
[% END %]
-- expect --
This is the foo file, a is Error: file - absolute paths are not allowed (set ABSOLUTE option)


-- test --
foo: [% TRY; INSERT foo;      CATCH; "$error\n"; END %]
rel: [% TRY; INSERT $relfile; CATCH; "$error\n"; END +%]
abs: [% TRY; INSERT $absfile; CATCH; "$error\n"; END %]
-- expect --
-- process --
[% TAGS [* *] %]
foo: file error - foo: not found
rel: This is the foo file, a is [% a -%]
abs: file error - [* absfile *]: absolute paths are not allowed (set ABSOLUTE option)

#------------------------------------------------------------------------

-- test --
-- use ttabs --
[% TRY %]
[% INCLUDE $absfile %]
[% INCLUDE foo %]
[% CATCH file %]
Error: [% error.type %] - [% error.info %]
[% END %]
-- expect --
This is the foo file, a is Error: file - foo: not found

-- test --
[% TRY %]
[% INCLUDE $absfile %]
[% INCLUDE $relfile %]
[% CATCH file %]
Error: [% error.type %] - [% error.info.split(': ').1 %]
[% END %]
-- expect --
This is the foo file, a is Error: file - relative paths are not allowed (set RELATIVE option)


-- test --
foo: [% TRY; INSERT foo;      CATCH; "$error\n"; END %]
rel: [% TRY; INSERT $relfile; CATCH; "$error\n"; END %]
abs: [% TRY; INSERT $absfile; CATCH; "$error\n"; END %]
-- expect --
-- process --
[% TAGS [* *] %]
foo: file error - foo: not found
rel: file error - [* relfile *]: relative paths are not allowed (set RELATIVE option)
abs: This is the foo file, a is [% a -%]



#------------------------------------------------------------------------
# test that files updated on disk are automatically reloaded.
#------------------------------------------------------------------------

-- test --
-- use ttinc --
[% INCLUDE foobar %]
-- expect --
This is the old content

-- test --
[% CALL fixfile('This is the new content') %]
[% INCLUDE foobar %]
-- expect --
This is the new content

#------------------------------------------------------------------------
# dynamic path tests 
#------------------------------------------------------------------------

-- test --
-- use ttd1 --
foo: [% PROCESS foo | trim +%]
bar: [% PROCESS bar | trim +%]
baz: [% PROCESS baz a='alpha' | trim %]
-- expect --
foo: This is one/foo
bar: This is two/bar
baz: This is the baz file, a: alpha

-- test --
foo: [% INSERT foo | trim +%]
bar: [% INSERT bar | trim +%]
-- expect --
foo: This is one/foo
bar: This is two/bar

-- test --
-- use ttd2 --
foo: [% PROCESS foo | trim +%]
bar: [% PROCESS bar | trim +%]
baz: [% PROCESS baz a='alpha' | trim %]
-- expect --
foo: This is two/foo
bar: This is two/bar
baz: This is the baz file, a: alpha

-- test --
foo: [% INSERT foo | trim +%]
bar: [% INSERT bar | trim +%]
-- expect --
foo: This is two/foo
bar: This is two/bar

-- test --
-- use ttdbad --
[% TRY; INCLUDE foo; CATCH; e; END %]
-- expect --
file error - INCLUDE_PATH exceeds 42 directories
"""

test.main()
