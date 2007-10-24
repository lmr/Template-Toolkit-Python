from template import config, test, util


class ConfigTest(test.TestCase):
  def testConfig(self):
    factory = config.Config

    # Parser:
    parser = factory.parser({ 'PRE_CHOMP': True, 'INTERPOLATE': True })
    self.failUnless(parser)
    self.failUnless(parser.PRE_CHOMP)
    self.failUnless(parser.INTERPOLATE)
    parser = factory.parser({ 'POST_CHOMP': True })
    self.failUnless(parser)
    self.failUnless(parser.POST_CHOMP)

    # Provider:
    provider = factory.provider({ 'INCLUDE_PATH': 'here:there',
                                  'PARSER': parser })
    self.failUnless(provider)
    self.assertEquals(['here', 'there'], provider.INCLUDE_PATH)
    self.failUnless(provider.PARSER.POST_CHOMP)
    provider = factory.provider({ 'INCLUDE_PATH': 'cat:mat',
                                  'ANYCASE': True,
                                  'INTERPOLATE': True })
    self.failUnless(provider)
    self.assertEquals(['cat', 'mat'], provider.INCLUDE_PATH)
    # Force the provider to instantiate a parser and check it uses the
    # correct parameters.
    text = 'The cat sat on the mat'
    self.failUnless(provider.fetch(util.Literal(text)))
    self.failUnless(provider.PARSER.ANYCASE)
    self.failUnless(provider.PARSER.INTERPOLATE)

    # Plugins:
    plugins = factory.plugins({ 'PLUGIN_BASE': ('my.plugins', 'MyPlugins') })
    self.failUnless(plugins)
    self.assertEquals([('my.plugins', 'MyPlugins'),
                       ('template.plugin', 'Plugin')], plugins.PLUGIN_BASE)
    plugins = factory.plugins({ 'LOAD_PYTHON': True,
                                'PLUGIN_BASE': ('my.plugins', 'NewPlugins') })
    self.failUnless(plugins)
    self.failUnless(plugins.LOAD_PYTHON)
    self.assertEquals([('my.plugins', 'NewPlugins'),
                       ('template.plugin', 'Plugin')], plugins.PLUGIN_BASE)

    # Filters:
    filters = factory.filters({ 'TOLERANT': True })
    self.failUnless(filters)
    self.failUnless(filters.TOLERANT)
    filters = factory.filters({ 'TOLERANT': True })
    self.failUnless(filters)
    self.failUnless(filters.TOLERANT)

    # Stash:
    stash = factory.stash({ 'foo': 10, 'bar': 20 })
    self.failUnless(stash)
    self.assertEquals(10, stash.get('foo'))
    self.assertEquals(20, stash.get('bar'))
    stash = factory.stash({ 'foo': 30, 'bar': lambda *_: 'forty' })
    self.failUnless(stash)
    self.assertEquals(30, stash.get('foo'))
    self.assertEquals('forty', stash.get('bar'))

    # Context:
    context = factory.context({})
    self.failUnless(context)
    context = factory.context({ 'INCLUDE_PATH': 'anywhere' })
    self.failUnless(context)
    self.assertEquals('anywhere', context.LOAD_TEMPLATES[0].INCLUDE_PATH[0])
    context = factory.context({ 'LOAD_TEMPLATES': [ provider ],
                                'LOAD_PLUGINS': [ plugins ],
                                'LOAD_FILTERS': [ filters ],
                                'STASH': stash })
    self.failUnless(context)
    self.assertEquals(30, context.stash().get('foo'))
    self.failUnless(context.LOAD_TEMPLATES[0].PARSER.INTERPOLATE)
    self.failUnless(context.LOAD_PLUGINS[0].LOAD_PYTHON)
    self.failUnless(context.LOAD_FILTERS[0].TOLERANT)

    # Service:
    service = factory.service({ 'INCLUDE_PATH': 'amsterdam' })
    self.failUnless(service)
    self.assertEquals(['amsterdam'],
                      service.CONTEXT.LOAD_TEMPLATES[0].INCLUDE_PATH)

    # Iterator:
    iterator = factory.iterator(['foo', 'bar', 'baz'])
    self.failUnless(iterator)
    value, error = iterator.get_first()
    self.assertEquals('foo', value)
    value, error = iterator.get_next()
    self.assertEquals('bar', value)
    value, error = iterator.get_next()
    self.assertEquals('baz', value)

    # Instdir:
    # (later)


test.main()
