import template
from template import document, test
from template.plugin import table


class ContextTest(test.TestCase):
  def testContext(self):
    tt = template.Template({ 'INCLUDE_PATH': 'test/src:test/lib',
                             'TRIM': True,
                             'POST_CHOMP': True })
    ttperl = tt

    context = tt.service().context()
    self.failUnless(context)
    self.assertEquals(context, tt.context())
    self.failUnless(context.trim())
    # self.failUnless(not context.eval_perl())
    # context = ttperl.service().context()
    # self.failUnless(context)
    # self.failUnless(context.trim())
    # self.failUnless(context.eval_perl())

    # template()

    # Test that we can fetch a template via template()
    tmpl = context.template('header')
    self.failUnless(tmpl)
    self.failUnless(isinstance(tmpl, document.Document))

    # Test that non-existence of a template is reported
    error = None
    try:
      tmpl = context.template('no_such_template')
    except Exception, e:
      error = e
    self.failUnless(error)
    self.assertEquals('file error - no_such_template: not found', str(error))

    # Check that template() returns subroutine and template.document.Document
    # refs intact
    code = lambda *_: "this is a hard-coded template"
    tmpl = context.template(code)
    self.assertEquals(code, tmpl)

    class FakeDocument:
      def __init__(self, text):
        self.text = text
    old_document = document.Document
    document.Document = FakeDocument
    doc = FakeDocument("this is a document")
    try:
      tmpl = context.template(doc)
    finally:
      document.Document = old_document
    self.assertEquals(doc, tmpl)
    self.assertEquals("this is a document", doc.text)

    # Check the use of visit() and leave() to add temporary BLOCK lookup
    # tables to the context's search space
    blocks1 = { 'some_block_1': 'hello' }
    blocks2 = { 'some_block_2': 'world' }
    self.assertRaises(Exception, context.template, 'some_block_1')
    context.visit('no doc', blocks1)
    self.assertEquals('hello', context.template('some_block_1'))
    self.assertRaises(Exception, context.template, 'some_block_2')
    context.visit('no doc', blocks2)
    self.assertEquals('hello', context.template('some_block_1'))
    self.assertEquals('world', context.template('some_block_2'))
    context.leave()
    self.assertEquals('hello', context.template('some_block_1'))
    self.assertRaises(Exception, context.template, 'some_block_2')
    context.leave()
    self.assertRaises(Exception, context.template, 'some_block_1')
    self.assertRaises(Exception, context.template, 'some_block_2')

    # Test that reset() clears all blocks
    context.visit('no doc', blocks1)
    self.assertEquals('hello', context.template('some_block_1'))
    self.assertRaises(Exception, context.template, 'some_block_2')
    context.visit('no doc', blocks2)
    self.assertEquals('hello', context.template('some_block_1'))
    self.assertEquals('world', context.template('some_block_2'))
    context.reset()
    self.assertRaises(Exception, context.template, 'some_block_1')
    self.assertRaises(Exception, context.template, 'some_block_2')

    # plugin()

    plugin = context.plugin('Table', [ [ 1, 2, 3, 4 ], { 'rows': 2 } ])
    self.failUnless(plugin)
    self.failUnless(isinstance(plugin, table.Table))

    row = plugin.row(0)
    self.failUnless(row and isinstance(row, list))
    self.assertEquals(1, row[0])
    self.assertEquals(3, row[1])
    error = None
    try:
      plugin = context.plugin('no_such_plugin')
    except Exception, e:
      error = e
    self.failUnless(error)
    self.assertEquals('plugin error - no_such_plugin: plugin not found',
                      str(error))

    # filter()

    filter = context.filter('html')
    self.failUnless(filter)
    self.failUnless(callable(filter))
    self.assertEquals('&lt;input/&gt;', filter('<input/>'))

    filter = context.filter('replace', [ 'foo', 'bar' ], 'repsave')
    self.failUnless(filter)
    self.failUnless(callable(filter))
    self.assertEquals('this is bar, so it is', filter('this is foo, so it is'))

    # Check that filter got cached
    filter = context.filter('repsave')
    self.failUnless(filter)
    self.failUnless(callable(filter))
    self.assertEquals('this is bar, so it is', filter('this is foo, so it is'))

    # include() and process()

    context = tt.context()
    self.failUnless(context)
    stash = context.stash()
    self.failUnless(stash)
    stash.set('a', 'alpha')
    self.assertEquals('alpha', stash.get('a'))
    text = context.include('baz')
    self.assertEquals('This is the baz file, a: alpha', text)
    text = context.include('baz', { 'a': 'bravo' })
    self.assertEquals('This is the baz file, a: bravo', text)
    # Check that the stash hasn't been altered
    self.assertEquals('alpha', stash.get('a'))
    text = context.process('baz')
    self.assertEquals('This is the baz file, a: alpha', text)
    # Check that stash *has* been altered
    self.assertEquals('charlie', stash.get('a'))
    text = context.process('baz', { 'a': 'bravo' })
    self.assertEquals('This is the baz file, a: bravo', text)
    self.assertEquals('charlie', stash.get('a'))


test.main()
