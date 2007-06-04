from template import base

class Plugin(base.Base):
  @classmethod
  def load(cls, context=None):
    return cls

