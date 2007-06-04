import sys
import types

from template import util, base, constants

class Iterator(base.Base):
  def __init__(self, data=None, params=None):
    if data is None:
      data = []
    if params is None:
      params = {}
    if isinstance(data, dict):
      data = [{"key": key, "value": data[key]} for key in sorted(data.keys())]
    elif util.can(data, "as_list"):
      data = data.as_list()
    elif not isinstance(data, (list, tuple)):
      # coerce any non-list data in a list
      data = [data]

    self._DATA = data
    self._ERROR = ""
    self._DATASET = self.SIZE = self.MAX = self.INDEX = self.COUNT = None
    self.FIRST = self.LAST = False
    self.PREV = self.NEXT = None

  def size(self): return self.SIZE
  def max(self): return self.MAX
  def index(self): return self.INDEX
  def count(self): return self.COUNT
  def number(self): return self.COUNT
  def first(self): return self.FIRST
  def last(self): return self.LAST
  def prev(self): return self.PREV
  def next(self): return self.NEXT

  def get_first(self):
    self._DATASET = self._DATA
    self.SIZE  = len(self._DATA)
    if not self.SIZE:
      return None, constants.STATUS_DONE
    self.MAX   = len(self._DATA) - 1
    self.INDEX = 0
    self.COUNT = 1
    self.FIRST = len(self._DATA) > 0
    self.LAST  = len(self._DATA) == 1
    self.PREV  = None
    if len(self._DATASET) >= 2:
      self.NEXT = self._DATASET[1]
    else:
      self.NEXT = None
    return self._DATASET[0], None

  def get_next(self):
    if self.INDEX is None:
      sys.stderr.write("iterator get_next() called before get_first()")
      return None, constants.STATUS_DONE
    if self.INDEX < self.MAX:
      self.INDEX += 1
      self.COUNT = self.INDEX + 1
      self.FIRST = False
      self.LAST  = self.INDEX == self.MAX
      self.PREV  = self._DATA[self.INDEX - 1]
      if self.INDEX < len(self._DATA) - 1:
        self.NEXT = self._DATA[self.INDEX + 1]
      else:
        self.NEXT = None
      return self._DATA[self.INDEX], None
    else:
      return None, constants.STATUS_DONE

  def get_all(self):
    if self.INDEX < self.MAX:
      self.INDEX += 1
      data = self._DATASET[self.INDEX:]
      self.INDEX = self.MAX
      self.COUNT = self.MAX + 1
      self.FIRST = False
      self.LAST  = True
      return data
    else:
      return None, constants.STATUS_DONE

