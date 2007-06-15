import types

from template import base, constants, util


PLUGIN_BASE = ("template.plugin", "Plugin")

STD_PLUGINS = {
  "directory": "template.plugin.directory.Directory",
  "file":      "template.plugin.file.File",
  "format":    "template.plugin.format.Format",
  "iterator":  "template.plugin.iterator.Iterator",
  "math":      "template.plugin.math.Math",
  "string":    "template.plugin.string.String",
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
    self.TOLERANT = params.get("TOLERANT") or 0
    # self.LOAD_PERL = ...
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
          raise base.Exception("%s plugin failed" % name)
      else:
        raise base.Exception("%s plugin is not callable" % name)
    except base.Exception, e:
      if self.TOLERANT:
        return None, constants.STATUS_DECLINED
      else:
        return error, constants.STATUS_ERROR
    return plugin, None
    
  def _load(self, name, context):
    error = factory = None
    impl = self.PLUGINS.get(name) or self.PLUGINS.get(name.lower())
    if impl:
      # plugin name is explicitly stated in PLUGIN_NAME
      module_name, class_name = impl.rsplit(".", 1)
      try:
        module = __import__(module_name, globals(), None, True)
      except Exception, e:
        error = e
    else:
      raise NotImplementedError("plugin search by PLUGIN_BASE")

    if not error:
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

