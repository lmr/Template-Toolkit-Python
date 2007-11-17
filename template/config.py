"""

template.config.Config - Factory module for instantiating other TT2 modules


SYNOPSIS

    import template.config


DESCRIPTION

This class implements various methods for loading and instantiating
other modules that comprise the Template Toolkit.  It provides a
consistent way to create toolkit components and allows custom modules
to be used in place of the regular ones.

Global variables such as STASH, SERVICE, CONTEXT, etc., contain the
default module/package name for each component (template.stash.Stash,
template.service.Service and template.context.Context, respectively)
and are used by the various factory methods (stash(), service() and
context()) to load the appropriate module.  Changing these global
variables will cause subsequent calls to the relevant factory method
to load and instantiate an object from the new class.


PUBLIC METHODS

parser(config)

Instantiate a new parser object of the class whose module and name is
denoted by the global 2-tuple PARSER (default: ('template.parser',
'Parser')).


provider(config)

Instantiate a new template provider object (default:
template.provider.Provider).


plugins(config)

Instantiate a new plugins provider object (default:
template.plugins.Plugins).


filters(config)

Instantiate a new filter provider object (default:
template.filters.Filters).


stash(vars)

Instantiate a new stash object (default: template.stash.Stash) using
the contents of the optional dictionary passed by parameter as initial
variable definitions.


context(config)

Instantiate a new template context object (default:
template.context.Context).


service(config)

Instantiate a new template service object (default:
template.service.Service).

"""

CONSTANTS = ('template.namespace.constants', 'Constants')
CONTEXT = ('template.context', 'Context')
FILTERS = ('template.filters', 'Filters')
ITERATOR = ('template.iterator', 'Iterator')
PARSER = ('template.parser', 'Parser')
PLUGINS = ('template.plugins', 'Plugins')
PROVIDER = ('template.provider', 'Provider')
SERVICE = ('template.service', 'Service')
STASH = ('template.stash', 'Stash')


class Config:
  @classmethod
  def __create(cls, (modname, classname), params):
    module = __import__(modname, globals(), [], ["."])
    klass = getattr(module, classname)
    return klass(params)

  @classmethod
  def parser(cls, params):
    return cls.__create(PARSER, params)

  @classmethod
  def provider(cls, params):
    return cls.__create(PROVIDER, params)

  @classmethod
  def plugins(cls, params):
    return cls.__create(PLUGINS, params)

  @classmethod
  def filters(cls, params):
    return cls.__create(FILTERS, params)

  @classmethod
  def iterator(cls, params):
    return cls.__create(ITERATOR, params)

  @classmethod
  def stash(cls, params):
    return cls.__create(STASH, params)

  @classmethod
  def context(cls, params):
    return cls.__create(CONTEXT, params)

  @classmethod
  def service(cls, params):
    return cls.__create(SERVICE, params)

  @classmethod
  def constants(cls, params):
    return cls.__create(CONSTANTS, params)
