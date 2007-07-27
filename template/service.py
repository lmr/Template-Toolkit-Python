import sys
import re
import cStringIO as StringIO

from template import base, context, config, constants, util

class Service(base.Base):
  _NewContext = config.Config.context

  def __init__(self, config=None):
    base.Base.__init__(self)
    if config is None:
      config = {}
    delim = config.get("DELIMITER", ":")

    # coerce PRE_PROCESS, PROCESS, and POST_PROCESS to lists if necessary,
    # by splitting on non-word characters
    for item in "PRE_PROCESS", "PROCESS", "POST_PROCESS", "WRAPPER":
      data = config.get(item)
      if data is None:
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
    self.DEBUG = config.get("DEBUG", 0) & constants.DEBUG_SERVICE
    self.CONTEXT = config.get("CONTEXT") or self._NewContext(config)
    if not self.CONTEXT:
      raise base.Exception()

  def process(self, template, params=None):
    context = self.CONTEXT
    output  = StringIO.StringIO()
    procout = StringIO.StringIO()
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
        error = util.Reference(e)
        break

      try:
        for name in self.PROCESS or [template]:
          procout.write(context.process(name))
          procout_ok = True
      except base.Exception, e:
        error = util.Reference(e)
        recovery = self._recover(error)
        if recovery is None:
          procout_ok = False
          break
        else:
          procout.seek(0)
          procout.truncate()
          procout.write(recovery)
          procout_ok = True

      if procout_ok:
        procout = procout.getvalue()
        try:
          for name in reversed(self.WRAPPER):
            procout = context.process(name, {"content": procout})
        except base.Exception, e:
          break
        output.write(procout)
        procout = StringIO.StringIO()
      
      try:
        for name in self.POST_PROCESS:
          output.write(context.process(name))
      except base.Exception, e:
        break

      break  # end of SERVICE block

    context.delocalise()
    if "template" in params:
      del params["template"]

    if error:
      return self.error(error.get())

    return output.getvalue()

  def _recover(self, error):
    # a 'stop' exception is thrown by [% STOP %] - we return the output
    # buffer stored in the exception object
#    if error.get().type == "stop":
#      return error.get().text()
    handlers = self.ERROR
    if not handlers:
      return None
    if isinstance(handlers, dict):
      hkey = error.get().select_handler(handlers.keys())
      if hkey:
        handler = handlers.get(hkey)
      else:
        handler = handlers.get("default")
        if not handler:
          return None
    else:
      handler = handlers

    try:
      handler = context.template(handler)
    except base.Exception, e:
      error.set(e)
      return None

    context.stash().set("error", error.get())
    try:
      output = context.process(handler)
    except base.Exception, e:
      error.set(e)
      return None

    return output
