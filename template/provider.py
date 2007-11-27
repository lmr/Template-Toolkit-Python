import os
import re
import sys
import time
import types

from template import util
from template.base import Base, TemplateException
from template.config import Config
from template.constants import *
from template.document import Document


PREV = 0
NAME = 1
DATA = 2
LOAD = 3
NEXT = 4
STAT = 5

MAX_DIRS = 64
STAT_TTL = 1
DEBUG = 0

RELATIVE_PATH = re.compile(r"(?:^|/)\.+/")


class Error(Exception):
  pass


class Provider(Base):
  def __init__(self, params):
    Base.__init__(self)
    size = params.get("CACHE_SIZE")
    paths = params.get("INCLUDE_PATH", ".")
    cdir = params.get("COMPILE_DIR", "")
    dlim = params.get("DELIMITER", os.name == "nt" and r":(?!\/)" or ":")
    debug = params.get("DEBUG")

    if isinstance(paths, str):
      paths = re.split(dlim, paths)
    if size == 1 or size < 0:
      size = 2
    if debug is not None:
      self.__debug = debug & (DEBUG_PROVIDER & DEBUG_FLAGS)
    else:
      self.__debug = DEBUG
    if cdir:
      for path in paths:
        if not isinstance(path, str):
          continue
        if os.name == "nt":
          path = path.replace(":", "")
        if not os.path.isdir(path):
          os.makedirs(path)

    self.__lookup = {}
    self.__slots = 0
    self.__size = size
    self.__include_path = paths
    self.__delimiter = dlim
    self.__compile_dir = cdir
    self.__compile_ext = params.get("COMPILE_EXT", "")
    self.__absolute = bool(params.get("ABSOLUTE"))
    self.__relative = bool(params.get("RELATIVE"))
    self.__tolerant = bool(params.get("TOLERANT"))
    self.__document = params.get("DOCUMENT", Document)
    self.__parser= params.get("PARSER")
    self.__default = params.get("DEFAULT")
    self.__encoding = params.get("ENCODING")
    self.__params = params
    self.__head = None
    self.__tail = None

  def fetch(self, name, prefix=None):
    if not isinstance(name, str):
      data = self._load(name)
      data = self._compile(data)
      return data and data.data
    elif os.path.isabs(name):
      if self.__absolute:
        return self._fetch(name)
      elif self.__tolerant:
        return None
      else:
        raise Error("%s: absolute paths are not allowed (set ABSOLUTE option)"
                    % name)
    elif RELATIVE_PATH.search(name):
      if self.__relative:
        return self._fetch(name)
      elif self.__tolerant:
        return None
      else:
        raise Error("%s: relative paths are not allowed (set RELATIVE option)"
                    % name)
    elif self.__include_path:
      return self._fetch_path(name)
    else:
      return None

  def _load(self, name, alias=None):
    now = time.time()
    if alias is None and isinstance(name, str):
      alias = name
    if isinstance(name, util.Literal):
      # name can be a Literal wrapper around the input text...
      data = Data(name.text(), alias, alt="input text", load=0)
    elif not isinstance(name, str):
      # ...or a file handle...
      data = Data(name.read(), alias, alt="input file", load=0)
    elif os.path.isfile(name):
      try:
        fh = open(name)
      except IOError, e:
        if self.__tolerant:
          return None
        else:
          raise Error("%s: %s" % (alias, e))
      data = Data(fh.read(), alias, when=os.stat(name).st_mtime, path=name)
      fh.close()
    else:
      return None

    return data

  def _fetch(self, name):
    compiled = self._compiled_filename(name)
    if self.__size is not None and not self.__size:
      if (compiled
          and os.path.isfile(compiled)
          and not self._modified(name, os.stat(compiled).st_mtime)):
        data = self.__load_compiled(compiled)
      else:
        data = self._load(name)
        data = self._compile(data, compiled)
        data = data and data.data
    else:
      slot = self.__lookup.get(name)
      if slot:
        # cached entry exists, so refresh slot and extract data
        data = self._refresh(slot)
        data = slot[DATA]
      else:
        # nothing in cache so try to load, compile, and cache
        if (compiled
            and os.path.isfile(compiled)
            and os.stat(name).st_mtime <= os.stat(compiled).st_mtime):
          data = self.__load_compiled(compiled)
          self.store(name, data)
        else:
          data = self._load(name)
          data = self._compile(data, compiled)
          data = data and self._store(name, data)

    return data

  def _compile(self, data, compfile=None):
    if data is None:
      return None

    text = data.text
    error = None

    if not self.__parser:
      self.__parser = Config.parser(self.__params)

    # discard the template text - we don't need it any more
    del data.text

    parsedoc = self.__parser.parse(text, data)
    if parsedoc:
      parsedoc["METADATA"].setdefault("name", data.name)
      parsedoc["METADATA"].setdefault("modtime", data.time)
      # write the Python code to the file compfile, if defined
      if compfile:
        basedir = os.path.dirname(compfile)
        if not os.path.isdir(basedir):
          try:
            os.makedirs(basedir)
          except IOError, e:
            error = ("failed to create compiled templates "
                     "directory: %s (%s)" % (basedir, e))
        if not error:
          docclass = self.__document
          if not docclass.write_python_file(compfile, parsedoc):
            error = "cache failed to write %s: %s" % (
              os.path.basename(compfile), docclass.Error())
        if error is None and data.time is not None:
          if not compfile:
            raise Error("invalid null filename")
          ctime = int(data.time)
          os.utime(compfile, (ctime, ctime))

      if not error:
        data.data = Document(parsedoc)
        return data

    else:
      error = TemplateException("parse", "%s %s" % (data.name,
                                                    self.__parser.error()))

    if self.__tolerant:
      return None
    else:
      raise Error(error)

  def _fetch_path(self, name):
    compiled = None
    caching = self.__size is None or self.__size
    # INCLUDE: {
    while True:
      # the template may have been stored using a non-filename name
      slot = self.__lookup.get(name)
      if caching and slot:
        # cached entry exists, so refresh slot and extract data
        data = self._refresh(slot)
        data = slot[DATA]
        break  # last INCLUDE;
      paths = self.paths()
      # search the INCLUDE_PATH for the file, in cache or on disk
      for dir in paths:
        path = os.path.join(dir, name)
        slot = self.__lookup.get(path)
        if caching and slot:
          # cached entry exists, so refresh slot and extract data
          data = self._refresh(slot)
          data = slot[DATA]
          return data  # last INCLUDE;
        elif os.path.isfile(path):
          if self.__compile_ext or self.__compile_dir:
            compiled = self._compiled_filename(path)
          if (compiled
              and os.path.isfile(compiled)
              and os.stat(path).st_mtime <= os.stat(compiled).st_mtime):
            data = self.__load_compiled(compiled)
            if data:
              # store in cache
              data = self.store(path, data)
              return data  # last INCLUDE;
          # compiled is set if an attempt to write the compiled
          # template to disk should be made
          data = self._load(path, name)
          data = self._compile(data, compiled)
          if caching:
            data = data and self._store(path, data)
          if not caching:
            data = data and data.data
          # all done if error is OK or ERROR
          return data  # last INCLUDE;

      # template not found, so look for a DEFAULT template
      if self.__default is not None and name != self.__default:
        name = self.__default
        # redo INCLUDE;
      else:
        return None

    return data

  def _compiled_filename(self, file):
    if not (self.__compile_ext or self.__compile_dir):
      return None
    path = file
    if os.name == "nt":
      path = path.replace(":", "")
    compiled = "%s%s" % (path, self.__compile_ext)
    if self.__compile_dir:
      # Can't use os.path.join here; compiled may be absolute.
      compiled = "%s%s%s" % (self.__compile_dir, os.path.sep, compiled)
    return compiled

  def _modified(self, name, time=None):
    load = os.stat(name).st_mtime
    if not load:
      return time and 1 or 0
    if time:
      return load > time
    else:
      return load

  def _refresh(self, slot):
    data = None
    if time.time() - slot[STAT] > STAT_TTL:
      statbuf = statfile(slot[NAME])
      if statbuf:
        slot[STAT] = time.time()
        if statbuf.st_mtime != slot[LOAD]:
          data = self._load(slot[NAME], slot[DATA].name)
          data = self._compile(data)
          slot[DATA] = data.data
          slot[LOAD] = data.time
    if self.__head is not slot:
      # remove existing slot from usage chain...
      if slot[PREV]:
        slot[PREV][NEXT] = slot[NEXT]
      else:
        self.__head = slot[NEXT]
      if slot[NEXT]:
        slot[NEXT][PREV] = slot[PREV]
      else:
        self.__tail = slot[PREV]
      # ...and add to start of list
      head = self.__head
      if head:
        head[PREV] = slot
      slot[PREV] = None
      slot[NEXT] = head
      self.__head  = slot

    return data

  def __load_compiled(self, path):
    try:
      return Document.evaluate_file(path, "document")
    except TemplateException, e:
      raise Error("compiled template %s: %s" % (path, e))

  def _store(self, name, data, compfile=None):
    load = self._modified(name)
    data = data.data
    if self.__size is not None and self.__slots >= self.__size:
      # cache has reached size limit, so reuse oldest entry
      # remove entry from tail or list
      slot = self.__tail
      slot[PREV][NEXT] = None
      self.__tail = slot[PREV]

      # remove name lookup for old node
      del self.__lookup[slot[NAME]]

      # add modified node to head of list
      head = self.__head
      if head:
        head[PREV] = slot
      slot[:] = [None, name, data, load, head, time.time()]
      self.__head = slot

      # add name lookup for new node
      self.__lookup[name] = slot
    else:
      # cache is under size limit, or none is defined
      head = self.__head
      slot = [None, name, data, load, head, time.time()]
      if head:
        head[PREV] = slot
      self.__head = slot
      if not self.__tail:
        self.__tail = slot
      # add lookup from name to slot and increment nslots
      self.__lookup[name] = slot
      self.__slots += 1

    return data

  def paths(self):
    ipaths = self.__include_path[:]
    opaths = []
    count = MAX_DIRS
    while ipaths and count > 0:
      count -= 1
      dir = ipaths.pop(0)
      if not dir:
        continue
      # dir can be a sub or object ref which returns a reference
      # to a dynamically generated list of search paths
      if callable(dir):
        dpaths = dir()
        ipaths[:0] = dpaths
      elif isinstance(dir, types.InstanceType) and util.can(dir, "paths"):
        dpaths = dir.paths()
        if not dpaths:
          raise Error(dir.error())
        ipaths[:0] = dpaths
      else:
        opaths.append(dir)

    if ipaths:
      raise Error("INCLUDE_PATH exceeds %d directories" % (MAX_DIRS,))

    return opaths

  def store(self, name, data):
    return self._store(name, Data(data=data, load=0))

  def load(self, name, prefix=None):
    path = name
    error = None
    if os.path.isabs(name):
      if not self.__absolute:
        error = ("%s: absolute paths are not allowed (set ABSOLUTE option)"
                 % name)
    elif RELATIVE_PATH.search(name):
      if not self.__relative:
        error = ("%s: relative paths are not allowed (set RELATIVE option)"
                 % name)
    else:
      paths = self.paths()
      if not paths:
        return self.error(), STATUS_ERROR
      for dir in paths:
        path = os.path.join(dir, name)
        if os.path.isfile(path):
          break
      else:
        path = None

    if path is not None and not error:
      try:
        data = open(path).read()
      except IOError, e:
        error = "%s: %s" % (name, e)

    if error:
      if self.__tolerant:
        return None
      else:
        raise Error(error)
    elif path is None:
      return None
    else:
      return data

  def include_path(self, path=None):
    if path:
      self.__include_path = None
    return self.__include_path

  def parser(self):
    return self.__parser

  def tolerant(self):
    return self.__tolerant


class Data:
  def __init__(self, text=None, name=None, alt=None, when=None, path=None,
               load=None, data=None):
    self.text = text
    if name is not None:
      self.name = name
    else:
      self.name = alt
    if when is not None:
      self.time = when
    else:
      self.time = time.time()
    if path is not None:
      self.path = path
    else:
      self.path = self.name
    self.load = load
    self.data = data


def statfile(path):
  try:
    return os.stat(path)
  except OSError:
    return None

