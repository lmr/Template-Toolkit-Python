import os

from template import base
from template.plugin import file

class Directory(file.File):
  def __init__(self, context, path, config=None):
    if not isinstance(config, dict):
      config = {}
    if not path:
      raise base.Exception("no directory specified")
    file.File.__init__(self, context, path, config)
    self.files = []
    self.dirs  = []
    self.list  = []
    self._dir  = {}
    # don't read directory if 'nostat' or 'noscan' set
    if config.get("nostat") or config.get("noscan"):
      return
    if not self.isdir:
      self.throw("%s: not a directory" % path)
    self.scan(config)

  def scan(self, config=None):
    if not config:
      config = {}
    # set 'noscan' in config if recurse isn't set, to ensure Directories
    # created don't try to scan deeper
    if not config.get("recurse"):
      config["noscan"] = True
    try:
      files = os.listdir(self.abs)
    except OSError, e:
      self.throw("%s: %s" % (self.abs, e))
    self.files = []
    self.dirs  = []
    self.list  = []
    for name in sorted(files):
      if name.startswith("."):
        continue
      abs = os.path.join(self.abs, name)
      rel = os.path.join(self.path, name)
      if os.path.isdir(abs):
        item = Directory(None, rel, config)
        self.dirs.append(item)
      else:
        item = file.File(None, rel, config)
        self.files.append(item)
      self.list.append(item)
      self._dir[name] = item
    return ""

  def file(self, name):
    return self._dir.get(name)

  def throw(self, error):
    raise base.Exception("Directory", error)

