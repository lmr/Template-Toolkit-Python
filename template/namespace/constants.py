from template.base import Base
from template.config import Config
from template.directive import Directive
from template.util import PerlScalar

class Constants(Base):
  def __init__(self, config):
    Base.__init__(self)
    self.__stash = Config.stash(config)

  def ident(self, ident):
    save = ident[:]
    ident[:2] = []
    nelems = len(ident) / 2
    for e in range(nelems):
      # Node name must be a constant.
      if ident[e * 2].startswith("'") and ident[e * 2].endswith("'"):
        ident[e * 2] = ident[e * 2][1:-1]
      else:
        return Directive.Ident(save)
      # If args is nonzero then it must be eval-ed.
      if ident[e * 2 + 1]:
        args = ident[e * 2 + 1]
        try:
          comp = eval(args, {"scalar": PerlScalar})
        except Exception, ex:
          return Directive.Ident(save)
        ident[e * 2 + 1] = comp

    result = self.__stash.get(ident).value()
    if len(str(result)) == 0 or not isinstance(result, (str, int, long)):
      return Directive.Ident(save)
    else:
      return repr(result)
