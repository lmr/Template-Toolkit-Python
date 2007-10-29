from template import Template
from template.test import TestCase, main


class ServiceTest(TestCase):
  def testService(self):
    config = { "INCLUDE_PATH": "test/src:test/lib",
               "PRE_PROCESS": ["config", "header"],
               "POST_PROCESS": "footer",
               "BLOCKS": {"demo": lambda *_: "This is a demo",
                          "astext": "Another template block, a is '[% a %]'" },
               "ERROR": { "barf": "barfed", "default": "error" },
               }
    tt1 = Template(config)
    config["AUTO_RESET"] = 0
    tt2 = Template(config)
    config["ERROR"] = "barfed"
    tt3 = Template(config)
    config["PRE_PROCESS"] = "before"
    config["POST_PROCESS"] = "after"
    config["PROCESS"] = "process"
    config["WRAPPER"] = "outer"
    tt4 = Template(config)
    config["WRAPPER"] = ["outer", "inner"]
    tt5 = Template(config)
    replace = { "title": "Joe Random Title" }
    self.Expect(DATA, (("tt1", tt1),
                       ("tt2", tt2),
                       ("tt3", tt3),
                       ("wrapper", tt4),
                       ("nested", tt5)), replace)


DATA = r"""# test that headers and footers get added
-- test --
This is some text
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
This is some text
footer

# test that the 'demo' block (template sub) is defined
-- test --
[% INCLUDE demo %]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
This is a demo
footer

# and also the 'astext' block (template text)
-- test --
[% INCLUDE astext a = 'artifact' %]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
Another template block, a is 'artifact'
footer

# test that 'barf' exception gets redirected to the correct error template
-- test --
[% THROW barf 'Not feeling too good' %]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
barfed: [barf] [Not feeling too good]
footer

# test all other errors get redirected correctly
-- test --
[% INCLUDE no_such_file %]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
error: [file] [no_such_file: not found]
footer

# import some block definitions from 'blockdef'...
-- test --
[% PROCESS blockdef -%]
[% INCLUDE block1
   a = 'alpha'
%]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
start of blockdef

end of blockdef
This is block 1, defined in blockdef, a is alpha

footer

# ...and make sure they go away for the next service
-- test --
[% INCLUDE block1 %]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
error: [file] [block1: not found]
footer

# now try it again with AUTO_RESET turned off...
-- test --
-- use tt2 --
[% PROCESS blockdef -%]
[% INCLUDE block1
   a = 'alpha'
%]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
start of blockdef

end of blockdef
This is block 1, defined in blockdef, a is alpha

footer

# ...and the block definitions should persist
-- test --
[% INCLUDE block1 a = 'alpha' %]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
This is block 1, defined in blockdef, a is alpha

footer

# test that the 'demo' block is still defined
-- test --
[% INCLUDE demo %]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
This is a demo
footer

# and also the 'astext' block
-- test --
[% INCLUDE astext a = 'artifact' %]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
Another template block, a is 'artifact'
footer

# test that a single ERROR template can be specified
-- test --
-- use tt3 --
[% THROW food 'cabbages' %]
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
barfed: [food] [cabbages]
footer

-- test --
-- use wrapper --
[% title = 'The Foo Page' -%]
begin page content
title is "[% title %]"
end page content
-- expect --
This comes before
<outer title="The Foo Page">
begin process
begin page content
title is "The Foo Page"
end page content
end process
</outer>
This comes after

-- test --
-- use nested --
[% title = 'The Bar Page' -%]
begin page content
title is "[% title %]"
end page content
-- expect --
This comes before
<outer title="inner The Bar Page">
<inner title="The Bar Page">
begin process
begin page content
title is "The Bar Page"
end page content
end process
</inner>

</outer>
This comes after
"""

main()
