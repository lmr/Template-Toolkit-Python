import types

from template import base, constants, util


PLUGIN_BASE = ("template.plugin", "Plugin")

STD_PLUGINS = {
  "datafile":  ("template.plugin.datafile", "Datafile"),
  "date":      ("template.plugin.date", "Date"),
  "directory": ("template.plugin.directory", "Directory"),
  "file":      ("template.plugin.file", "File"),
  "format":    ("template.plugin.format", "Format"),
  "iterator":  ("template.plugin.iterator", "Iterator"),
  "math":      ("template.plugin.math", "Math"),
  "string":    ("template.plugin.string", "String"),
  "table":     ("template.plugin.table", "Table"),
  "Table":     ("template.plugin.table", "Table"),
  "wrap":      ("template.plugin.wrap", "Wrap"),
  "url":       ("template.plugin.url", "URL"),
}

class Plugins(base.Base):
  def __init__(self, params):
    pbase   = util.listify(params.get("PLUGIN_BASE") or [])
    plugins = params.get("PLUGINS") or {}
    factory = params.get("PLUGIN_FACTORY")
    if PLUGIN_BASE:
      pbase.append(PLUGIN_BASE)
    self.PLUGIN_BASE = pbase
    self.PLUGINS = STD_PLUGINS.copy()
    self.PLUGINS.update(plugins)
    self.TOLERANT = params.get("TOLERANT") or False
    self.LOAD_PYTHON = params.get("LOAD_PYTHON") or False
    self.FACTORY = factory or {}
    self.DEBUG = (params.get("DEBUG") or 0) & constants.DEBUG_PLUGINS

  def fetch(self, name, args=None, context=None):
    if not args:
      args = []
    args.insert(0, context)
    factory, error = self._load(name, context)
    if error:
      return factory, error
    self.FACTORY[name] = factory
    try:
      if callable(factory):
        plugin = factory(*args)
        if not plugin:
          raise base.Exception(None, "%s plugin failed" % name)
      else:
        raise base.Exception(None, "%s plugin is not callable" % name)
    except base.Exception, e:
      if self.TOLERANT:
        return None, constants.STATUS_DECLINED
      else:
        return e, constants.STATUS_ERROR
    return plugin, None

  def _load(self, name, context):
    error = factory = ok = None
    impl = self.PLUGINS.get(name) or self.PLUGINS.get(name.lower())
    if impl:
      # plugin name is explicitly stated in PLUGIN_NAME
      module_name, class_name = impl
      try:
        module = __import__(module_name, globals(), None, True)
        ok = True
      except Exception, e:
        error = e
    else:
      # Try each of the PLUGIN_BASE values to build module name
      # ...Only it's not clear how this should work in Python,
      # so we skip it for now.
      pass

    if ok:
      try:
        factory = getattr(getattr(module, class_name), "load")(context)
      except Exception, e:
        error = e

    if factory:
      return factory, None
    elif error:
      if self.TOLERANT:
        return None, constants.STATUS_DECLINED
      else:
        return error, constants.STATUS_ERROR
    else:
      return None, constants.STATUS_DECLINED
