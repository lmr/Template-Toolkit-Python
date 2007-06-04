#
#  First stab at a unit test program for the Python Template Toolkit.
#
#  These tests should all go in separate files at some point.
#

import re
import unittest
import cStringIO as StringIO

import template
from template import util

words = (
  "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf",
  "hotel", "india", "juliet", "kilo", "lima", "mike", "november",
  "oscar", "papa", "quebec", "romeo", "sierra", "tango", "unbrella",
  "victor", "whisky", "x-ray", "yankee", "zulu"
)

words = dict((chr(letter), word)
             for letter, word in zip(range(ord("a"), ord("a") + 26), words))

def callsign():
  return words.copy()


class TemplateToolkitTest(unittest.TestCase):
  def _testExpect(self, path, tproc, vars):
    input = open(path).read()
    input = re.sub(r"(?s).*?\n__DATA__\n", "", input)
    input = re.sub(r"(?m)^#.*\n", "", input)
    input = re.sub(r"(?s).*?\s*--\s*start\s*--\s*", "", input)
    input = re.sub(r"(?s)\s*--\s*stop\s*--.*", "", input)
    tests = re.split(r"(?mi)^\s*--\s*test\s*--\s*", input)
    if not tests[0]:
      tests.pop(0)
    for count, test in enumerate(tests):
      match = re.search(r"(?mi)^\s*-- name:? (.*?) --\s*\n", test)
      if match:
        name = match.group(1)
      else:
        name = "template text %d" % (count + 1)
      match = re.search(r"(?mi)^\s*--\s*expect\s*--\s*\n", test)
      if match:
        input, expect = test[:match.start()], test[match.end():]
      else:
        input, expect = test, ""
      match = re.match(r"(?mi)^\s*--\s*use\s+(\S+)\s*--\s*\n", input)
      if match:
        # ...
        input = input[:match.start()] + input[match.end():]
      tmpl = template.Template(tproc or {})
      out = util.Reference("")
      tmpl.process(util.Reference(input), vars or {}, out)
      out = out.get().rstrip("\n")
      self.assertEqual(expect.rstrip("\n"), out)


class IteratorTest(TemplateToolkitTest):
  def testIterator(self):
    from template import iterator, constants
    data = ["foo", "bar", "baz", "qux", "wiz", "woz", "waz"]
    vars = {"data": data}
    i1 = iterator.Iterator(data)
    self.assertEquals("foo", i1.get_first()[0])
    self.assertEquals("bar", i1.get_next()[0])
    self.assertEquals("baz", i1.get_next()[0])

    rest = i1.get_all()
    self.assertEquals(4, len(rest))
    self.assertEquals("qux", rest[0])
    self.assertEquals("waz", rest[3])

    self.assertEquals((None, constants.STATUS_DONE), i1.get_next())
    self.assertEquals((None, constants.STATUS_DONE), i1.get_all())

    val, err = i1.get_first()
    self.assertEquals("foo", i1.get_first()[0])
    self.assertEquals("bar", i1.get_next()[0])
    self.assertEquals(5, len(i1.get_all()))

    self._testExpect("/Users/smcafee/Template-Toolkit-2.15/t/iterator.t",
                     {"POST_CHOMP": 1}, vars)


class ListTest(TemplateToolkitTest):
  def testList(self):
    x = callsign()
    vars = {
      "data": [x[c] for c in "rjstyefz"],
      "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      "wxyz": [{"id": x["z"], "name": "Zebedee", "rank": "aa"},
               {"id": x["y"], "name": "Yinyang", "rank": "ba"},
               {"id": x["x"], "name": "Xeexeez", "rank": "ab"},
               {"id": x["w"], "name": "Warlock", "rank": "bb"}],
      "inst": [{"name": "piano", "url": "/roses.html"},
               {"name": "flute", "url": "/blow.html"},
               {"name": "organ", "url": "/tulips.html"}],
      "nest": [[3, 1, 4], [2, [7, 1, 8]]]
    }
    for char in "abcde":
      vars[char] = x[char]
    self._testExpect("/Users/smcafee/Template-Toolkit-2.15/t/list.t",
                     {}, vars)


unittest.main()
