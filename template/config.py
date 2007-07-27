CONTEXT  = ('template.context', 'Context')
FILTERS  = ('template.filters', 'Filters')
ITERATOR = ('template.iterator', 'Iterator')
PARSER   = ('template.parser', 'Parser')
PLUGINS  = ('template.plugins', 'Plugins')
PROVIDER = ('template.provider', 'Provider')
SERVICE  = ('template.service', 'Service')
STASH    = ('template.stash', 'Stash')


class Config:
  @classmethod
  def _create(cls, modname, classname, params):
    klass = getattr(__import__(modname, globals(), [], ['.']), classname)
    return klass(params)

  @classmethod
  def parser(cls, params):
    return cls._create(PARSER[0], PARSER[1], params)

  @classmethod
  def provider(cls, params):
    return cls._create(PROVIDER[0], PROVIDER[1], params)

  @classmethod
  def plugins(cls, params):
    return cls._create(PLUGINS[0], PLUGINS[1], params)

  @classmethod
  def filters(cls, params):
    return cls._create(FILTERS[0], FILTERS[1], params)

  @classmethod
  def iterator(cls, params):
    return cls._create(ITERATOR[0], ITERATOR[1], params)

  @classmethod
  def stash(cls, params):
    return cls._create(STASH[0], STASH[1], params)

  @classmethod
  def context(cls, params):
    return cls._create(CONTEXT[0], CONTEXT[1], params)

  @classmethod
  def service(cls, params):
    return cls._create(SERVICE[0], SERVICE[1], params)
