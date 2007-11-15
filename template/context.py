import cStringIO
import os
import re
import time


from template import stash, constants, document, provider, plugins, \
                     filters, base, util

DEBUG = None


class Context(base.Base):
  def __init__(self, config):
    base.Base.__init__(self)
    self.LOAD_TEMPLATES = util.listify(config.get("LOAD_TEMPLATES")
                                       or provider.Provider(config))
    self.LOAD_PLUGINS   = util.listify(config.get("LOAD_PLUGINS")
                                       or plugins.Plugins(config))
    self.LOAD_FILTERS   = util.listify(config.get("LOAD_FILTERS")
                                       or filters.Filters(config))
    providers  = self.LOAD_TEMPLATES
    prefix_map = config.get("PREFIX_MAP") or {}
    self.FILTER_CACHE = {}
    self.PREFIX_MAP = {}
    for key, value in prefix_map.items():
      if util.is_seq(value):
        self.PREFIX_MAP[key] = value
      elif isinstance(value, str):
        self.PREFIX_MAP[key] = [providers[int(x)]
                                for x in re.split(r"\D+", value)]
      else:
        self.PREFIX_MAP[key] = value

    # STASH
    if "STASH" in config:
      self.STASH = config["STASH"]
    else:
      predefs = config.get("VARIABLES") or config.get("PRE_DEFINE") or {}
      if predefs.get("_DEBUG") is None:
        debug = config.get("DEBUG", 0) & constants.DEBUG_UNDEF
        predefs["_DEBUG"] = debug and 1 or 0
      self.STASH = stash.Stash(predefs)

    # compile any template BLOCKS specified as text
    self.BLOCKS = {}
    self.BLKSTACK = []
    blocks = config.get("BLOCKS") or {}
    b = {}
    for key, block in blocks.items():
      if isinstance(block, str):
        block = self.template(util.Literal(block))
      b[key] = block
    self.INIT_BLOCKS = self.BLOCKS = b

    self.RECURSION = config.get("RECURSION", False)
    self.EVAL_PYTHON = config.get("EVAL_PYTHON", False)
    self.TRIM = config.get("TRIM", False)
    self.BLKSTACK = []
    self.CONFIG   = config
    if config.get("EXPOSE_BLOCKS") is not None:
      self.EXPOSE_BLOCKS = config.get("EXPOSE_BLOCKS")
    else:
      self.EXPOSE_BLOCKS = False
    self.DEBUG_FORMAT = config.get("DEBUG_FORMAT")
    self.DEBUG_DIRS   = config.get("DEBUG", 0) & constants.DEBUG_DIRS
    if config.get("DEBUG") is not None:
      self.DEBUG = config["DEBUG"] & (constants.DEBUG_CONTEXT |
                                      constants.DEBUG_FLAGS)
    else:
      self.DEBUG = DEBUG

  def config(self):
    return self.CONFIG

  def catch(self, error, output=None):
    if isinstance(error, base.Exception):
      if output:
        error.text(output)
      return error
    else:
      return base.Exception("None", error, output)

  def insert(self, files):
    # TODO: Clean this up; unify the way "files" is passed to this routine.
    files = util.unscalar(files)
    if util.is_seq(files):
      files = util.unscalar_list(files)
    else:
      files = [util.unscalar(files)]
    prefix = None
    providers = None
    text = None
    output = cStringIO.StringIO()
    if not isinstance(files, list):
      files = [files]
    for f in files:  # FILE: {
      name = f
      regex = r"(\w{%d,}):" % (int(os.name == "nt") + 1)
      match = re.match(regex, name)
      if match:
        prefix = match.group(1)
        name = name[len(prefix)+1:]
      if prefix:
        providers = self.PREFIX_MAP.get(prefix)
        if not providers:
          return self.throw(constants.ERROR_FILE,
                            "no providers for file prefix '%s'" % prefix)
      else:
        providers = self.PREFIX_MAP.get("default") or self.LOAD_TEMPLATES

      for provider in providers:
        text, error = provider.load(name, prefix)
        if not error:
          output.write(text)
          break
        if error == constants.STATUS_ERROR:
          if isinstance(text, list):
            self.throw(text)
          else:
            self.throw(constants.ERROR_FILE, text)
      else:
        self.throw(constants.ERROR_FILE, "%s: not found" % f)

    return output.getvalue()

  def throw(self, error, info=None, output=None):
    error = util.unscalar(error)
    info = util.unscalar(info)
    if isinstance(error, base.Exception):
      raise error
    elif info is not None:
      raise base.Exception(error, info, output)
    else:
      raise base.Exception("None", error or "", output)

  def include(self, template, params=None):
    return self.process(template, params, True)

  def view(self, *args, **kwargs):
    """Create a new View object bound to this context."""
    from template.view import View
    return View(self, *args, **kwargs)

  def process(self, template, params=None, localize=False):
    template = util.listify(util.unscalar(template))
    params = util.unscalar(params)
    compileds = []
    for name in template:
      compileds.append(self.template(name))
    if localize:
      self.STASH = self.STASH.clone(params)
    else:
      self.STASH.update(params)

    output = cStringIO.StringIO()
    error = None
    try:
      # save current component
      try:
        component = self.STASH.get("component")
      except:
        component = None
      for name, compiled in zip(template, compileds):
        if callable(compiled):
          element = {"modtime": time.time()}
          if isinstance(name, str):
            element["name"] = name
          else:
            element["name"] = ""
        else:
          element = compiled
        if isinstance(component, document.Document):
          if isinstance(element, dict):
            element["caller"] = component.name
            element["callers"] = getattr(component, "callers") or []
            element["callers"].append(element["caller"])
          else:
            element.caller = component.name
            element.callers = getattr(component, "callers") or []
            element.callers.append(element.caller)
        self.STASH.set("component", element)
        if not localize:
          # merge any local blocks defined in the Template::Document
          # info our local BLOCKS cache
          if isinstance(compiled, document.Document):
            tblocks = compiled.blocks()
            if tblocks:
              self.BLOCKS.update(tblocks)
        if callable(compiled):
          tmpout = compiled(self)
        elif util.can(compiled, "process"):
          tmpout = compiled.process(self)
        else:
          self.throw("file", "invalid template reference: %s" % compiled)
        if self.TRIM:
          tmpout = tmpout.strip()
        output.write(tmpout)
        # pop last item from callers
        if isinstance(component, document.Document):
          if isinstance(element, dict):
            element["callers"].pop()
          else:
            element.callers.pop()
      self.STASH.set("component", component)
    except base.Exception, e:
      error = e

    if localize:
      # ensure stash is delocalised before dying
      self.STASH = self.STASH.declone()

    if error:
      self.throw(error)

    return output.getvalue()

  def localise(self, *args):
    self.STASH = self.STASH.clone(*args)
    return self.STASH

  def delocalise(self):
    self.STASH = self.STASH.declone()

  def plugin(self, name, args=None):
    args = util.unscalar_list(args)
    for provider in self.LOAD_PLUGINS:
      plugin, error = provider.fetch(name, args, self)
      if not error:
        return plugin
      if error == constants.STATUS_ERROR:
        self.throw(plugin)
    self.throw(constants.ERROR_PLUGIN, "%s: plugin not found" % name)

  def filter(self, name, args=None, alias=None):
    name = util.unscalar(name)
    args = util.unscalar_list(args or [])
    filter = None
    if not args and isinstance(name, str):
      filter = self.FILTER_CACHE.get(name)
      if filter:
        return filter
    for provider in self.LOAD_FILTERS:
      filter, error = provider.fetch(name, args, self)
      if not error:
        break
      if error == constants.STATUS_ERROR:
        if not isinstance(filter, (str, int)):
          self.throw(filter)
        else:
          self.throw(constants.ERROR_FILTER, filter)
    if not filter:
      return self.error("%s: filter not found" % name)
    if alias:
      self.FILTER_CACHE[alias] = filter
    return filter

  def reset(self, blocks=None):
    self.BLKSTACK = []
    self.BLOCKS = self.INIT_BLOCKS.copy()

  def template(self, name):
    if isinstance(name, document.Document) or callable(name):
      return name
    shortname = name
    prefix = None
    providers = None
    if isinstance(name, str):
      template = self.BLOCKS.get(name)
      if template:
        return template
      for blocks in self.BLKSTACK:
        if blocks:
          template = blocks.get(name)
          if template:
            return template
      regex = "(\w{%d,}):" % (int(os.name == "nt") + 1)
      match = re.match(regex, shortname)
      if match:
        prefix = match.group(1)
        shortname = shortname[len(prefix)+1:]
      if prefix is not None:
        providers = self.PREFIX_MAP.get(prefix)
        if not providers:
          self.throw(constants.ERROR_FILE,
                     "no providers for template prefix '%s'" % prefix)
    if not providers:
      providers = self.PREFIX_MAP.get("default") or self.LOAD_TEMPLATES

    blockname = ""
    while shortname:
      for provider in providers:
        template, error = provider.fetch(shortname, prefix)
        if error:
          if error == constants.STATUS_ERROR:
            if (isinstance(template, base.Exception)
                and template.type == constants.ERROR_FILE):
              self.throw(template)
            else:
              self.throw(constants.ERROR_FILE, template)
        elif blockname:
          template = template.blocks().get(blockname)
          if template:
            return template
        else:
          return template
      if not isinstance(shortname, str) or not self.EXPOSE_BLOCKS:
        break
      match = re.search(r"/([^/]+)$", shortname)
      if not match:
        break
      shortname = shortname[:match.start()] + shortname[match.end():]
      if blockname:
        blockname = "%s/%s" % (match.group(1), blockname)
      else:
        blockname = match.group(1)

    # TODO: This is the error thrown when a template has syntax
    # errors.  Confusing!  Is this what the Perl version does?
    self.throw(constants.ERROR_FILE, "%s: not found" % name)

  def stash(self):
    return self.STASH

  def define_vmethod(self, *args):
    self.STASH.define_vmethod(*args)

  def visit(self, document, blocks):
    self.BLKSTACK.insert(0, blocks)

  def leave(self):
    self.BLKSTACK.pop(0)

  def define_filter(self, name, filter, dynamic=False):
    if dynamic:
      filter = [filter, True]
    for provider in self.LOAD_FILTERS:
      result, error = provider.store(name, filter)
      if not error:
        return 1
      if error == constants.STATUS_ERROR:
        self.throw(constants.ERROR_FILTER, result)
    self.throw(constants.ERROR_FILTER,
               "FILTER providers declined to store filter %s" % name)

  def eval_python(self):
    return self.EVAL_PYTHON

  def trim(self):
    return self.TRIM
