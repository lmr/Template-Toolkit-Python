from template.config import Config
from template.test import TestCase, main
from template.util import Literal


class ConfigTest(TestCase):
    def testConfig(self):
        factory = Config

        # Parser:
        parser = factory.parser({'PRE_CHOMP': 1, 'INTERPOLATE': True})
        self.assertTrue(parser)
        self.assertEqual(1, parser.pre_chomp)
        self.assertTrue(parser.interpolate)
        parser = factory.parser({'POST_CHOMP': 1})
        self.assertTrue(parser)
        self.assertEqual(1, parser.post_chomp)

        # Provider:
        provider = factory.provider({'INCLUDE_PATH': 'here:there',
                                     'PARSER': parser})
        self.assertTrue(provider)
        self.assertEqual(['here', 'there'], provider.include_path())
        self.assertEqual(1, provider.parser().post_chomp)
        provider = factory.provider({'INCLUDE_PATH': 'cat:mat',
                                     'ANYCASE': True,
                                     'INTERPOLATE': True})
        self.assertTrue(provider)
        self.assertEqual(['cat', 'mat'], provider.include_path())
        # Force the provider to instantiate a parser and check it uses the
        # correct parameters.
        text = 'The cat sat on the mat'
        self.assertTrue(provider.fetch(Literal(text)))
        self.assertTrue(provider.parser().anycase)
        self.assertTrue(provider.parser().interpolate)

        # Plugins:
        plugins = factory.plugins({'PLUGIN_BASE': ('my.plugins', 'MyPlugins')})
        self.assertTrue(plugins)
        self.assertEqual([('my.plugins', 'MyPlugins'), 'template.plugin'],
                          plugins.plugin_base())
        plugins = factory.plugins({'LOAD_PYTHON': True,
                                   'PLUGIN_BASE': ('my.plugins', 'NewPlugins')})
        self.assertTrue(plugins)
        self.assertTrue(plugins.load_python())
        self.assertEqual([('my.plugins', 'NewPlugins'), 'template.plugin'],
                          plugins.plugin_base())

        # Filters:
        filters = factory.filters({'TOLERANT': True})
        self.assertTrue(filters)
        self.assertTrue(filters.tolerant())
        filters = factory.filters({'TOLERANT': True})
        self.assertTrue(filters)
        self.assertTrue(filters.tolerant())

        # Stash:
        stash = factory.stash({'foo': 10, 'bar': 20})
        self.assertTrue(stash)
        self.assertEqual(10, stash.get('foo').value())
        self.assertEqual(20, stash.get('bar').value())
        stash = factory.stash({'foo': 30, 'bar': lambda *_: 'forty'})
        self.assertTrue(stash)
        self.assertEqual(30, stash.get('foo').value())
        self.assertEqual('forty', stash.get('bar').value())

        # Context:
        context = factory.context({})
        self.assertTrue(context)
        context = factory.context({'INCLUDE_PATH': 'anywhere'})
        self.assertTrue(context)
        self.assertEqual('anywhere',
                          context.load_templates()[0].include_path()[0])
        context = factory.context({'LOAD_TEMPLATES': [provider],
                                   'LOAD_PLUGINS': [plugins],
                                   'LOAD_FILTERS': [filters],
                                   'STASH': stash})
        self.assertTrue(context)
        self.assertEqual(30, context.stash().get('foo').value())
        self.assertTrue(context.load_templates()[0].parser().interpolate)
        self.assertTrue(context.load_plugins()[0].load_python())
        self.assertTrue(context.load_filters()[0].tolerant())

        # Service:
        service = factory.service({'INCLUDE_PATH': 'amsterdam'})
        self.assertTrue(service)
        self.assertEqual(['amsterdam'],
                          service.context().load_templates()[0].include_path())

        # Iterator:
        iterator = factory.iterator(['foo', 'bar', 'baz'])
        self.assertTrue(iterator)
        self.assertEqual('foo', iterator.get_first())
        self.assertEqual('bar', iterator.get_next())
        self.assertEqual('baz', iterator.get_next())

        # Instdir:
        # (later)


main()
