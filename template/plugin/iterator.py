from template import iterator, plugin

class Iterator(plugin.Plugin):
  @classmethod
  def load(cls, context=None):
    return cls.factory

  @classmethod
  def factory(cls, context, *args):
    return iterator.Iterator(*args)

