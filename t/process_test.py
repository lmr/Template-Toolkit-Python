from template import Template
from template.test import TestCase, main


class ProcessTest(TestCase):
  def testProcess(self):
    config = { "INCLUDE_PATH": "test/src:test/lib",
               "PROCESS": "content",
               "TRIM": 1 }
    tt1 = Template(config)
    config["PRE_PROCESS"] = "config"
    config["PROCESS"] = "header:content"
    config["POST_PROCESS"] = "footer"
    config["TRIM"] = 0
    tt2 = Template(config)
    config["PRE_PROCESS"] = "config:header.tt2"
    config["PROCESS"] = ""
    tt3 = Template(config)
    replace = { "title": "Joe Random Title" }
    self.Expect(DATA, (("tt1", tt1), ("tt2", tt2), ("tt3", tt3)), replace)


DATA = r"""
-- test --
This is the first test
-- expect --
This is the main content wrapper for "untitled"
This is the first test
This is the end.

-- test --
[% META title = 'Test 2' -%]
This is the second test
-- expect --
This is the main content wrapper for "Test 2"
This is the second test
This is the end.

-- test --
-- use tt2 --
[% META title = 'Test 3' -%]
This is the third test
-- expect --
header:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
This is the main content wrapper for "Test 3"
This is the third test

This is the end.
footer

-- test --
-- use tt3 --
[% META title = 'Test 3' -%]
This is the third test
-- expect --
header.tt2:
  title: Joe Random Title
  menu: This is the menu, defined in 'config'
footer

"""

main()

