import os

from template import util
from template.base import Base
from template.service import Service
from template.config import Config


DEBUG = False

BINMODE = False

# Convenience aliases.
Literal = util.Literal

TemplateException = base.TemplateException


class Template(Base):
  """Module implementing a simple, user-oriented front-end to the Template
  Toolkit.
  """
  def __init__(self, config=None):
    Base.__init__(self)
    config = config or {}
    # Prepare a namespace handler for any CONSTANTS definition.
    constants = config.get("CONSTANTS")
    if constants:
      namespace = config.get("CONSTANTS_NAMESPACE", "constants")
      config.setdefault("NAMESPACE", {})[namespace] = (
        Config.constants(constants))
    self.__service = Service(config)
    self.__output = config.get("OUTPUT")
    self.__output_path = config.get("OUTPUT_PATH")

  def processString(self, template, vars=None, options=None):
    """A simple wrapper around process() that wraps its template argument
    in a Literal.
    """
    return self.process(Literal(template), vars, options)

  def process(self, template, vars=None, options=None):
    """Main entry point for the Template Toolkit.  Delegates most of the
    processing effort to the underlying Service object.
    """
    options = options or {}
    if options.setdefault("binmode", BINMODE):
      self.DEBUG("set binmode\n")

    output = self.__service.process(template, vars)
    if output is not None:
      self.__MaybeWriteOutput(output, options["binmode"])
    else:
      raise self.__service.error()

    return output

  def service(self):
    """Returns a reference to this object's Service object."""
    return self.__service

  def context(self):
    """Returns a reference to this object's Service object's Context
    object.
    """
    return self.__service.CONTEXT

  def __MaybeWriteOutput(self, text, binmode=False):
    if not self.__output:
      return
    if not isinstance(self.__output, str):
      self.__output.write(text)
    else:
      path = self.__output
      if self.__output_path:
        path = os.path.join(self.__output_path, path)
      mode = "w%s" % (binmode and "b" or "")
      fh = open(path, mode)
      fh.write(text)
      fh.close()

