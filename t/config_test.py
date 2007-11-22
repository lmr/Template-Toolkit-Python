from template.config import Config
from template.test import TestCase, main
from template.util import Literal


class ConfigTest(TestCase):
  def testConfig(self):
    factory = Config

    # Parser:
    parser = factory.parser({ 'PRE_CHOMP': 1, 'INTERPOLATE': True })
    self.failUnless(parser)
    self.assertEquals(1, parser.pre_chomp)
    self.failUnless(parser.interpolate)
    parser = factory.parser({ 'POST_CHOMP': 1 })
    self.failUnless(parser)
    self.assertEquals(1, parser.post_chomp)

    # Provider:
    provider = factory.provider({ 'INCLUDE_PATH': 'here:there',
                                  'PARSER': parser })
    self.failUnless(provider)
    self.assertEquals(['here', 'there'], provider.include_path())
    self.assertEquals(1, provider.parser().post_chomp)
    provider = factory.provider({ 'INCLUDE_PATH': 'cat:mat',
                                  'ANYCASE': True,
                                  'INTERPOLATE': True })
    self.failUnless(provider)
    self.assertEquals(['cat', 'mat'], provider.include_path())
    # Force the provider to instantiate a parser and check it uses the
    # correct parameters.
    text = 'The cat sat on the mat'
    self.failUnless(provider.fetch(Literal(text)))
    self.failUnless(provider.parser().anycase)
    self.failUnless(provider.parser().interpolate)

    # Plugins:
    plugins = factory.plugins({ 'PLUGIN_BASE': ('my.plugins', 'MyPlugins') })
    self.failUnless(plugins)
    self.assertEquals([('my.plugins', 'MyPlugins'), 'template.plugin'],
                      plugins.plugin_base())
    plugins = factory.plugins({ 'LOAD_PYTHON': True,
                                'PLUGIN_BASE': ('my.plugins', 'NewPlugins') })
    self.failUnless(plugins)
    self.failUnless(plugins.load_python())
    self.assertEquals([('my.plugins', 'NewPlugins'), 'template.plugin'],
                      plugins.plugin_base())

    # Filters:
    filters = factory.filters({ 'TOLERANT': True })
    self.failUnless(filters)
    self.failUnless(filters.tolerant())
    filters = factory.filters({ 'TOLERANT': True })
    self.failUnless(filters)
    self.failUnless(filters.tolerant())

    # Stash:
    stash = factory.stash({ 'foo': 10, 'bar': 20 })
    self.failUnless(stash)
    self.assertEquals(10, stash.get('foo').value())
    self.assertEquals(20, stash.get('bar').value())
    stash = factory.stash({ 'foo': 30, 'bar': lambda *_: 'forty' })
    self.failUnless(stash)
    self.assertEquals(30, stash.get('foo').value())
    self.assertEquals('forty', stash.get('bar').value())

    # Context:
    context = factory.context({})
    self.failUnless(context)
    context = factory.context({ 'INCLUDE_PATH': 'anywhere' })
    self.failUnless(context)
    self.assertEquals('anywhere',
                      context.load_templates()[0].include_path()[0])
    context = factory.context({ 'LOAD_TEMPLATES': [ provider ],
                                'LOAD_PLUGINS': [ plugins ],
                                'LOAD_FILTERS': [ filters ],
                                'STASH': stash })
    self.failUnless(context)
    self.assertEquals(30, context.stash().get('foo').value())
    self.failUnless(context.load_templates()[0].parser().interpolate)
    self.failUnless(context.load_plugins()[0].load_python())
    self.failUnless(context.load_filters()[0].tolerant())

    # Service:
    service = factory.service({ 'INCLUDE_PATH': 'amsterdam' })
    self.failUnless(service)
    self.assertEquals(['amsterdam'],
                      service.context().load_templates()[0].include_path())

    # Iterator:
    iterator = factory.iterator(['foo', 'bar', 'baz'])
    self.failUnless(iterator)
    self.assertEquals('foo', iterator.get_first())
    self.assertEquals('bar', iterator.get_next())
    self.assertEquals('baz', iterator.get_next())

    # Instdir:
    # (later)


main()
