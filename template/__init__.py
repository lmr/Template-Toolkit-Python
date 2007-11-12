import errno
import os
import sys
from template import util
from template.base import Base
from template.service import Service


DEBUG = False

BINMODE = False

# Convenience alias.
Literal = util.Literal


class Template(Base):
  def __init__(self, config=None):
    Base.__init__(self)
    if config is None:
      config = {}
    # prepare a namespace handler for any CONSTANTS definition
    # (later)
    self.SERVICE = Service(config)
    self.OUTPUT = config.get("OUTPUT") or sys.stdout
    self.OUTPUT_PATH = config.get("OUTPUT_PATH")

  def processString(self, template, *args, **kwargs):
    """A simple wrapper around process() that wraps its template argument
    in a Literal."""
    return self.process(Literal(template), *args, **kwargs)

  def process(self, template, vars=None, outstream=None, options=None):
    options = options or {}
    if "binmode" not in options:
      options["binmode"] = BINMODE
    if DEBUG and options["binmode"]:
      self.DEBUG("set binmode\n")
    output = self.SERVICE.process(template, vars)
    if output is not None:
      if outstream is None:
        outstream = self.OUTPUT
      if isinstance(outstream, str):
        if self.OUTPUT_PATH:
          outstream = os.path.join(self.OUTPUT_PATH, outstream)
      ref = util.Reference(output)
      error = _output(outstream, ref, options)
      if error:
        return self.error(error)
      return True
    else:
      return self.error(self.SERVICE.error())

  def context(self):
    return self.SERVICE.CONTEXT

  def service(self):
    return self.SERVICE


def _output(where, textref, options):
  error = None
  text  = textref.get()
  if callable(where):
    where(text)
  elif util.can(where, "write"):
    where.write(text)
  elif isinstance(where, util.Reference):
    where.set(str(where.get()) + text)
  elif isinstance(where, list):
    where.append(text)
  elif isinstance(where, str):
    dirname = os.path.dirname(where)
    try:
      os.makedirs(dirname)
    except OSError, e:
      if e.errno != errno.EEXIST:
        error = e
    if not error:
      mode = "w%s" % (options and options.get("binmode") and "b" or "")
      try:
        fp = open(where, mode)
        fp.write(text)
        fp.close()
      except OSError, e:
        error = e
  else:
    error = "output_handler() cannot determine target type (%s)" % where
  return error
