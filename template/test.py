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

  def Expect(self, data, tproc=None, vars=None):
    vars = vars or {}
    data = re.sub(r"(?s).*?\n__DATA__\n", "", data)
    data = re.sub(r"(?m)^#.*\n", "", data)
    data = re.sub(r"(?s).*?\s*--\s*start\s*--\s*", "", data)
    data = re.sub(r"(?s)\s*--\s*stop\s*--.*", "", data)
    tests = re.split(r"(?mi)^\s*--\s*test\s*--\s*", data)
    if not tests[0]:
      tests.pop(0)
    ttprocs = None
    if isinstance(tproc, dict):
      tproc = template.Template(tproc)
    elif isinstance(tproc, (tuple, list)):
      ttprocs = dict(tproc)
      tproc = tproc[0][1]
    elif not isinstance(tproc, template.Template):
      tproc = template.Template()
    for count, test in enumerate(tests):
      match = re.search(r"(?mi)^\s*-- name:? (.*?) --\s*\n", test)
      if match:
        name = match.group(1)
        test = test[:match.start()] + test[match.end():]
      else:
        name = "template text %d" % (count + 1)
      match = re.search(r"(?mi)^\s*--\s*expect\s*--\s*\n", test)
      if match:
        input, expect = test[:match.start()], test[match.end():]
      else:
        input, expect = test, ""
      match = re.match(r"(?mi)^\s*--\s*use\s+(\S+)\s*--\s*\n", input)
      if match:
        ttname = match.group(1)
        ttlookup = ttprocs.get(ttname)
        if ttlookup:
          tproc = ttlookup
        else:
          self.fail("no such template object to use: %s\n" % ttname)
        input = input[:match.start()] + input[match.end():]
      out = util.Reference("")
      if not tproc.processString(input, vars, out):
        self.fail("Test #%d: %s process FAILED: %s\n%s" %
                  (count + 1, name, subtext(input), tproc.error()))
      match = re.match(r"(?i)\s*--+\s*process\s*--+\s*\n", expect)
      if match:
        out2 = util.Reference("")
        expect = expect[match.end():]
        if not tproc.processString(expect, vars, out2):
          self.fail("Test #%d: Template process failed (expect): %s" % (
            count + 1, tproc.error()))
        expect = out2.get()
      out = out.get().rstrip("\n")
      stripped = expect.rstrip("\n")
      self.assertEqual(stripped, out, "Test #%d:\n%s\n%r != %r" %
                       (count + 1, test, stripped, out))

def subtext(text):
  text = text.rstrip()
  if len(text) > 32:
    text = text[:32] + "..."
  text = text.replace("\n", "\\n")
  return text
