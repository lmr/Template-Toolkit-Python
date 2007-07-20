import re
import unittest

import template
from template import util

main = unittest.main

words = (
  "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf",
  "hotel", "india", "juliet", "kilo", "lima", "mike", "november",
  "oscar", "papa", "quebec", "romeo", "sierra", "tango", "umbrella",
  "victor", "whisky", "x-ray", "yankee", "zulu"
)

words = dict((word[0], word) for word in words)

class TestCase(unittest.TestCase):
  @classmethod
  def _callsign(cls):
    return words.copy()

  def Expect(self, data, tproc, vars):
    data = re.sub(r"(?s).*?\n__DATA__\n", "", data)
    data = re.sub(r"(?m)^#.*\n", "", data)
    data = re.sub(r"(?s).*?\s*--\s*start\s*--\s*", "", data)
    data = re.sub(r"(?s)\s*--\s*stop\s*--.*", "", data)
    tests = re.split(r"(?mi)^\s*--\s*test\s*--\s*", data)
    if not tests[0]:
      tests.pop(0)
    tmpl = tproc or template.Template()
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
      out = util.Reference("")
      tmpl.process(util.Reference(input), vars or {}, out)
      out = out.get().rstrip("\n")
      stripped = expect.rstrip("\n")
      self.assertEqual(stripped, out, "Test #%d:\n%s\n%r != %r" %
                       (count + 1, test, stripped, out))
