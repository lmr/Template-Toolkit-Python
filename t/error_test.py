import template
from template import base, test


class ErrorTest(test.TestCase):
  def testError(self):
    tmpl = template.Template(
      { 'BLOCKS': { 'badinc': '[% INCLUDE nosuchfile %]' } })
    self.assert_(not tmpl.process('badinc'))
    error = tmpl.error()
    self.assert_(error)
    self.assert_(isinstance(error, base.Exception))
    self.assertEquals('file', error.type())
    self.assertEquals('nosuchfile: not found', error.info())


test.main()
