from template import context, Template
from template.document import Document
from template.test import TestCase, main
from template.plugin.table import Table


class ContextTest(TestCase):
  def testContext(self):
    tt = Template({ 'INCLUDE_PATH': 'test/src:test/lib',
                    'TRIM': True,
                    'POST_CHOMP': 1 })
    ttpython = Template({ 'INCLUDE_PATH': 'test/src:test/lib',
                          'TRIM': True,
                          'POST_CHOMP': 1,
                          'EVAL_PYTHON': True })

    ctx = tt.service().context()
    self.failUnless(ctx)
    self.assertEquals(ctx, tt.context())
    self.failUnless(ctx.trim())
    self.failUnless(not ctx.eval_python())
    ctx = ttpython.service().context()
    self.failUnless(ctx)
    self.failUnless(ctx.trim())
    self.failUnless(ctx.eval_python())

    # template()

    # Test that we can fetch a template via template()
    tmpl = ctx.template('header')
    self.failUnless(tmpl)
    self.failUnless(isinstance(tmpl, Document))

    # Test that non-existence of a template is reported
    error = None
    try:
      tmpl = ctx.template('no_such_template')
    except Exception, e:
      error = e
    self.failUnless(error)
    self.assertEquals('file error - no_such_template: not found', str(error))

    # Check that template() returns subroutine and template.document.Document
    # refs intact
    code = lambda *_: "this is a hard-coded template"
    tmpl = ctx.template(code)
    self.assertEquals(code, tmpl)

    class FakeDocument:
      def __init__(self, text):
        self.text = text
    old_document = context.Document
    context.Document = FakeDocument
    doc = FakeDocument("this is a document")
    try:
      tmpl = ctx.template(doc)
    finally:
      context.Document = old_document
    self.assertEquals(doc, tmpl)
    self.assertEquals("this is a document", doc.text)

    # Check the use of visit() and leave() to add temporary BLOCK lookup
    # tables to the context's search space
    blocks1 = { 'some_block_1': 'hello' }
    blocks2 = { 'some_block_2': 'world' }
    self.assertRaises(Exception, ctx.template, 'some_block_1')
    ctx.visit('no doc', blocks1)
    self.assertEquals('hello', ctx.template('some_block_1'))
    self.assertRaises(Exception, ctx.template, 'some_block_2')
    ctx.visit('no doc', blocks2)
    self.assertEquals('hello', ctx.template('some_block_1'))
    self.assertEquals('world', ctx.template('some_block_2'))
    ctx.leave()
    self.assertEquals('hello', ctx.template('some_block_1'))
    self.assertRaises(Exception, ctx.template, 'some_block_2')
    ctx.leave()
    self.assertRaises(Exception, ctx.template, 'some_block_1')
    self.assertRaises(Exception, ctx.template, 'some_block_2')

    # Test that reset() clears all blocks
    ctx.visit('no doc', blocks1)
    self.assertEquals('hello', ctx.template('some_block_1'))
    self.assertRaises(Exception, ctx.template, 'some_block_2')
    ctx.visit('no doc', blocks2)
    self.assertEquals('hello', ctx.template('some_block_1'))
    self.assertEquals('world', ctx.template('some_block_2'))
    ctx.reset()
    self.assertRaises(Exception, ctx.template, 'some_block_1')
    self.assertRaises(Exception, ctx.template, 'some_block_2')

    # plugin()

    plugin = ctx.plugin('Table', [ [ 1, 2, 3, 4 ], { 'rows': 2 } ])
    self.failUnless(plugin)
    self.failUnless(isinstance(plugin, Table))

    row = plugin.row(0)
    self.failUnless(row and isinstance(row, list))
    self.assertEquals(1, row[0])
    self.assertEquals(3, row[1])
    error = None
    try:
      plugin = ctx.plugin('no_such_plugin')
      self.fail('Exception not raised')
    except Exception, e:
      self.assertEquals('plugin error - no_such_plugin: plugin not found',
                        str(e))

    # filter()

    filter = ctx.filter('html')
    self.failUnless(filter)
    self.failUnless(callable(filter))
    self.assertEquals('&lt;input/&gt;', filter('<input/>'))

    filter = ctx.filter('replace', [ 'foo', 'bar' ], 'repsave')
    self.failUnless(filter)
    self.failUnless(callable(filter))
    self.assertEquals('this is bar, so it is', filter('this is foo, so it is'))

    # Check that filter got cached
    filter = ctx.filter('repsave')
    self.failUnless(filter)
    self.failUnless(callable(filter))
    self.assertEquals('this is bar, so it is', filter('this is foo, so it is'))

    # include() and process()

    ctx = tt.context()
    self.failUnless(ctx)
    stash = ctx.stash()
    self.failUnless(stash)
    stash.set('a', 'alpha')
    self.assertEquals('alpha', stash.get('a').value())
    text = ctx.include('baz')
    self.assertEquals('This is the baz file, a: alpha', text)
    text = ctx.include('baz', { 'a': 'bravo' })
    self.assertEquals('This is the baz file, a: bravo', text)
    # Check that the stash hasn't been altered
    self.assertEquals('alpha', stash.get('a').value())
    text = ctx.process('baz')
    self.assertEquals('This is the baz file, a: alpha', text)
    # Check that stash *has* been altered
    self.assertEquals('charlie', stash.get('a').value())
    text = ctx.process('baz', { 'a': 'bravo' })
    self.assertEquals('This is the baz file, a: bravo', text)
    self.assertEquals('charlie', stash.get('a').value())


main()
