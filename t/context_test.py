from template import context, Template
from template.document import Document
from template.test import TestCase, main
from template.plugin.table import Table


class ContextTest(TestCase):
    def testContext(self):
        tt = Template({'INCLUDE_PATH': 'test/src:test/lib',
                       'TRIM': True,
                       'POST_CHOMP': 1})
        ttpython = Template({'INCLUDE_PATH': 'test/src:test/lib',
                             'TRIM': True,
                             'POST_CHOMP': 1,
                             'EVAL_PYTHON': True})

        ctx = tt.service().context()
        self.assertTrue(ctx)
        self.assertEqual(ctx, tt.context())
        self.assertTrue(ctx.trim())
        self.assertTrue(not ctx.eval_python())
        ctx = ttpython.service().context()
        self.assertTrue(ctx)
        self.assertTrue(ctx.trim())
        self.assertTrue(ctx.eval_python())

        # template()

        # Test that we can fetch a template via template()
        tmpl = ctx.template('header')
        self.assertTrue(tmpl)
        self.assertTrue(isinstance(tmpl, Document))

        # Test that non-existence of a template is reported
        error = None
        try:
            tmpl = ctx.template('no_such_template')
        except Exception as e:
            error = e
        self.assertTrue(error)
        self.assertEqual('file error - no_such_template: not found', str(error))

        # Check that template() returns subroutine and template.document.Document
        # refs intact
        code = lambda *_: "this is a hard-coded template"
        tmpl = ctx.template(code)
        self.assertEqual(code, tmpl)

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
        self.assertEqual(doc, tmpl)
        self.assertEqual("this is a document", doc.text)

        # Check the use of visit() and leave() to add temporary BLOCK lookup
        # tables to the context's search space
        blocks1 = {'some_block_1': 'hello'}
        blocks2 = {'some_block_2': 'world'}
        self.assertRaises(Exception, ctx.template, 'some_block_1')
        ctx.visit('no doc', blocks1)
        self.assertEqual('hello', ctx.template('some_block_1'))
        self.assertRaises(Exception, ctx.template, 'some_block_2')
        ctx.visit('no doc', blocks2)
        self.assertEqual('hello', ctx.template('some_block_1'))
        self.assertEqual('world', ctx.template('some_block_2'))
        ctx.leave()
        self.assertEqual('hello', ctx.template('some_block_1'))
        self.assertRaises(Exception, ctx.template, 'some_block_2')
        ctx.leave()
        self.assertRaises(Exception, ctx.template, 'some_block_1')
        self.assertRaises(Exception, ctx.template, 'some_block_2')

        # Test that reset() clears all blocks
        ctx.visit('no doc', blocks1)
        self.assertEqual('hello', ctx.template('some_block_1'))
        self.assertRaises(Exception, ctx.template, 'some_block_2')
        ctx.visit('no doc', blocks2)
        self.assertEqual('hello', ctx.template('some_block_1'))
        self.assertEqual('world', ctx.template('some_block_2'))
        ctx.reset()
        self.assertRaises(Exception, ctx.template, 'some_block_1')
        self.assertRaises(Exception, ctx.template, 'some_block_2')

        # plugin()

        plugin = ctx.plugin('Table', [[1, 2, 3, 4], {'rows': 2}])
        self.assertTrue(plugin)
        self.assertTrue(isinstance(plugin, Table))

        row = plugin.row(0)
        self.assertTrue(row and isinstance(row, list))
        self.assertEqual(1, row[0])
        self.assertEqual(3, row[1])
        error = None
        try:
            plugin = ctx.plugin('no_such_plugin')
            self.fail('Exception not raised')
        except Exception as e:
            self.assertEqual('plugin error - no_such_plugin: plugin not found',
                              str(e))

        # filter()

        filter = ctx.filter('html')
        self.assertTrue(filter)
        self.assertTrue(callable(filter))
        self.assertEqual('&lt;input/&gt;', filter('<input/>'))

        filter = ctx.filter('replace', ['foo', 'bar'], 'repsave')
        self.assertTrue(filter)
        self.assertTrue(callable(filter))
        self.assertEqual('this is bar, so it is', filter('this is foo, so it is'))

        # Check that filter got cached
        filter = ctx.filter('repsave')
        self.assertTrue(filter)
        self.assertTrue(callable(filter))
        self.assertEqual('this is bar, so it is', filter('this is foo, so it is'))

        # include() and process()

        ctx = tt.context()
        self.assertTrue(ctx)
        stash = ctx.stash()
        self.assertTrue(stash)
        stash.set('a', 'alpha')
        self.assertEqual('alpha', stash.get('a').value())
        text = ctx.include('baz')
        self.assertEqual('This is the baz file, a: alpha', text)
        text = ctx.include('baz', {'a': 'bravo'})
        self.assertEqual('This is the baz file, a: bravo', text)
        # Check that the stash hasn't been altered
        self.assertEqual('alpha', stash.get('a').value())
        text = ctx.process('baz')
        self.assertEqual('This is the baz file, a: alpha', text)
        # Check that stash *has* been altered
        self.assertEqual('charlie', stash.get('a').value())
        text = ctx.process('baz', {'a': 'bravo'})
        self.assertEqual('This is the baz file, a: bravo', text)
        self.assertEqual('charlie', stash.get('a').value())


if __name__ == '__main__':
    main()
