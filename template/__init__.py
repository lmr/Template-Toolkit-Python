import os

from template import util
from template.base import Base
from template.service import Service
from template.config import Config


DEBUG = False

BINMODE = False

# Convenience alias.
Literal = util.Literal

TemplateException = base.TemplateException

class Error(Exception):
  pass


class Template(Base):
  def __init__(self, config=None):
    Base.__init__(self)
    config = config or {}
    # Prepare a namespace handler for any CONSTANTS definition.
    constants = config.get("CONSTANTS")
    if constants:
      config.setdefault("NAMESPACE", {})[config.get("CONSTANTS_NAMESPACE", "constants")] = Config.constants(constants)
    self.__service = Service(config)
    self.__output = config.get("OUTPUT")
    self.__output_path = config.get("OUTPUT_PATH")

  def processString(self, template, *args, **kwargs):
    """A simple wrapper around process() that wraps its template argument
    in a Literal."""
    return self.process(Literal(template), *args, **kwargs)

  def process(self, template, vars=None, options=None):
    options = options or {}
    if options.setdefault("binmode", BINMODE):
      self.DEBUG("set binmode\n")

    output = self.__service.process(template, vars)

    if output is not None:
      if self.__output:
        if not isinstance(self.__output, str):
          self.__output.write(output)
        else:
          path = self.__output
          if self.__output_path:
            path = os.path.join(self.__output_path, path)
          mode = "w%s" % (options["binmode"] and "b" or "")
          fh = open(path, mode)
          fh.write(output)
          fh.close()
      return output
    else:
      raise self.__service.error()

  def context(self):
    return self.__service.CONTEXT

  def service(self):
    return self.__service
