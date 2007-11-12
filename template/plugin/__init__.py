from template.base import Base

class Plugin(Base):
  @classmethod
  def load(cls, context=None):
    return cls

