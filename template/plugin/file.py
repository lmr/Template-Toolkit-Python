import os
import re

from template import plugin, util

STAT_KEYS = ("dev", "ino", "mode", "nlink", "uid", "gid", "rdev", "size",
             "atime", "mtime", "ctime", "blksize", "blocks")


class File(plugin.Plugin):
  def __init__(self, context, path, config=None):
    if not isinstance(config, dict):
      config = {}
    if not path:
      self.throw("no file specified")
    if os.path.isabs(path):
      root = ""
    else:
      root = config.get("root")
      if root:
        if root.endswith("/"):
          root = root[:-1]
      else:
        root = ""
    dir, name = os.path.split(path)
    name, ext = util.unpack(re.split(r"(\.\w+)$", name), 2)
    if ext is None:
      ext = ""
    if dir.endswith("/"):
      dir = dir[:-1]
    if dir == ".":
      dir = ""
    name = name + ext
    if ext.startswith("."):
      ext = ext[1:]
    fields = splitpath(dir)
    if fields and not fields[0]:
      fields.pop(0)
    home = "/".join(("..",) * len(fields))
    abs = os.path.join(root, path)
    self.path = path
    self.name = name
    self.root = root
    self.home = home
    self.dir = dir
    self.ext = ext
    self.abs = abs
    self.user = ""
    self.group = ""
    self.isdir = ""
    self.stat = config.get("stat") or not config.get("nostat")
    if self.stat:
      try:
        stat = os.stat(abs)
      except OSError, e:
        self.throw("%s: %s" % (abs, e))
      for key in STAT_KEYS:
        setattr(self, key, getattr(stat, "st_%s" % key, None))
      if not config.get("noid"):
        pass  # ...
      self.isdir = os.path.isdir(abs)
    else:
      for key in STAT_KEYS:
        setattr(self, key, "")

def splitpath(path):
  def helper(path):
    while True:
      path, base = os.path.split(path)
      if base:
        yield base
      else:
        break
  pathcomp = list(helper(path))
  pathcomp.reverse()
  return pathcomp
