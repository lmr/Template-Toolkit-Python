from template import Template, TemplateException
from template.test import TestCase, main


class ErrorTest(TestCase):
  def testError(self):
    tmpl = Template({ 'BLOCKS': { 'badinc': '[% INCLUDE nosuchfile %]' } })
    try:
      tmpl.process("badinc")
      self.fail("Failed to raise exception")
    except TemplateException, e:
      self.assertEquals('file', e.type())
      self.assertEquals('nosuchfile: not found', e.info())


main()
