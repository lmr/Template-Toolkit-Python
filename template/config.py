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
