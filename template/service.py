import cStringIO
import re
import sys

from template import base
from template.base import Base
from template.config import Config
from template.constants import DEBUG_SERVICE

class Service(Base):
  _NewContext = Config.context

  def __init__(self, config=None):
    Base.__init__(self)
    if config is None:
      config = {}
    delim = config.get("DELIMITER", ":")

    # coerce PRE_PROCESS, PROCESS, and POST_PROCESS to lists if necessary,
    # by splitting on non-word characters
    for item in "PRE_PROCESS", "PROCESS", "POST_PROCESS", "WRAPPER":
      data = config.get(item)
      if not data:
        setattr(self, item, [])
      else:
        if not isinstance(data, list):
          data = re.split(delim, data or "")
        setattr(self, item, data)

    # unset PROCESS option unless explicitly specified in config
    if config.get("PROCESS") is None:
      self.PROCESS = None

    self.ERROR = config.get("ERROR") or config.get("ERRORS")
    if config.get("AUTO_RESET") is not None:
      self.AUTO_RESET = config["AUTO_RESET"]
    else:
      self.AUTO_RESET = True
    self.DEBUG = config.get("DEBUG", 0) & DEBUG_SERVICE
    self.CONTEXT = config.get("CONTEXT") or self._NewContext(config)
    if not self.CONTEXT:
      raise base.Exception()

  def context(self):
    return self.CONTEXT

  def process(self, template, params=None):
    context = self.CONTEXT
    output  = cStringIO.StringIO()
    procout = cStringIO.StringIO()
    error   = None
    procout_ok = False

    if self.AUTO_RESET:
      context.reset()
    try:
      template = context.template(template)
    except base.Exception, e:
      return self.error(e)

    # localise the variable stash with any parameters passed
    # and set the 'template' variable
    if params is None:
      params = {}
    if not callable(template):
      params["template"] = template
    context.localise(params)

    # SERVICE: {
    while True:
      try:
        for name in self.PRE_PROCESS:
          output.write(context.process(name))
      except base.Exception, e:
        error = e
        break
      else:
        error = None

      try:
        if self.PROCESS is not None:
          proc = self.PROCESS
        else:
          proc = [template]
        for name in proc:
          procout.write(context.process(name))
          procout_ok = True
      except base.Exception, e:
        recovery, error = self._recover(e)
        if recovery is None:
          procout_ok = False
          break
        else:
          procout.seek(0)
          procout.truncate()
          procout.write(recovery)
          procout_ok = True
      else:
        error = None

      if procout_ok:
        procout = procout.getvalue()
        try:
          for name in reversed(self.WRAPPER):
            procout = context.process(name, {"content": procout})
        except base.Exception, e:
          error = e
          break
        else:
          error = None
        output.write(procout)
        procout = cStringIO.StringIO()

      try:
        for name in self.POST_PROCESS:
          output.write(context.process(name))
      except base.Exception, e:
        error = e
        break
      else:
        error = None

      break  # end of SERVICE block

    context.delocalise()
    if "template" in params:
      del params["template"]

    if error:
      return self.error(error)

    return output.getvalue()

  def _recover(self, error):
    # a 'stop' exception is thrown by [% STOP %] - we return the output
    # buffer stored in the exception object
    if error.type() == "stop":
      return error.text(), error
    handlers = self.ERROR
    if not handlers:
      return None, error
    if isinstance(handlers, dict):
      hkey = error.select_handler(*handlers.keys())
      if hkey:
        handler = handlers.get(hkey)
      else:
        handler = handlers.get("default")
        if not handler:
          return None, error
    else:
      handler = handlers

    try:
      handler = self.CONTEXT.template(handler)
    except base.Exception, e:
      return None, e

    self.CONTEXT.stash().set("error", error)
    try:
      output = self.CONTEXT.process(handler)
    except base.Exception, e:
      return None, e

    return output, None
