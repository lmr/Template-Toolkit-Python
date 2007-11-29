from template.util import split_arguments


class Plugin:
  def __init__(self):
    pass

  @classmethod
  def load(cls, context=None):
    return cls

  _split_arguments = staticmethod(split_arguments)
