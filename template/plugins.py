from types import ClassType

from template import base, constants, util


PLUGIN_BASE = "template.plugin"

STD_PLUGINS = {
  "datafile":  ("template.plugin.datafile", "Datafile"),
  "date":      ("template.plugin.date", "Date"),
  "directory": ("template.plugin.directory", "Directory"),
  "file":      ("template.plugin.file", "File"),
  "format":    ("template.plugin.format", "Format"),
  "html":      ("template.plugin.html", "Html"),
  "image":     ("template.plugin.image", "Image"),
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
    self.TOLERANT = bool(params.get("TOLERANT"))
    self.LOAD_PYTHON = bool(params.get("LOAD_PYTHON"))
    self.FACTORY = factory or {}
    self.DEBUG = (params.get("DEBUG") or 0) & constants.DEBUG_PLUGINS

  def fetch(self, name, args=None, context=None):
    args = args or []
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
        module = __import__(module_name, globals(), None, ["."])
      except Exception, e:
        error = e
      else:
        ok = True
    elif name:
      # Try each of the PLUGIN_BASE values to build module name
      for pbase in self.PLUGIN_BASE:
        module_name = "%s.%s" % (pbase, name[0].lower() + name[1:])
        class_name = name[0].upper() + name[1:]
        try:
          module = __import__(module_name, globals(), None, ["."])
        except ImportError, e:
          pass
        except Exception, e:
          error = e
        else:
          ok = True
          break

    if ok:
      try:
        factory = getattr(getattr(module, class_name), "load")(context)
      except Exception, e:
        error = e
    elif self.LOAD_PYTHON:
      dot = name.rfind(".")
      if dot == -1:
        module_name = class_name = name
      else:
        module_name = name[:dot+1] + name[dot+1].lower() + name[dot+2:]
        class_name = name[dot+1:]
      try:
        module = __import__(module_name, globals(), None, ["."])
        classobj = getattr(module, class_name)
        factory = lambda context, *args: classobj(*args)
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
