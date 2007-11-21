from template.base import Base
from template.util import split_arguments


class Plugin(Base):
  @classmethod
  def load(cls, context=None):
    return cls

  _split_arguments = staticmethod(split_arguments)
