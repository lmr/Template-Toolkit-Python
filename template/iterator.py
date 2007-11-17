import operator
import sys
import types

from template import base, config, constants, util


def Create(expr):
  expr = util.unscalar(expr)
  if isinstance(expr, Iterator):
    return expr
  else:
    return config.Config.iterator(expr)


def prepare_data(data):
  data = data or []
  if isinstance(data, dict):
    data = [{"key": key, "value": value} for key, value in data.iteritems()]
    data.sort(key=operator.itemgetter("key"))
  elif util.can(data, "as_list"):
    data = data.as_list()
  elif isinstance(data, str):
    data = [data]
  elif not isinstance(data, list):
    try:
      data = list(data)
    except TypeError:
      data = [data]
  return data



class Iterator(base.Base):
  def __init__(self, data=None, params=None):
    self.__impl = self.__IteratorImpl(prepare_data(data))

  def __iter__(self):
    return iter(self.__impl)

  def size(self):
    return self.__impl.size

  def max(self):
    return self.__impl.max

  def index(self):
    return self.__impl.index

  def count(self):
    return self.__impl.count

  def number(self):
    return self.__impl.count

  def first(self):
    return self.__impl.first

  def last(self):
    return self.__impl.last

  def prev(self):
    return self.__impl.prev

  def next(self):
    return self.__impl.next_

  def get_first(self):
    if self.__impl.start():
      return self.__impl.dataset[0]
    else:
      return None, constants.STATUS_DONE

  def get_next(self):
    if self.__impl.advance():
      return self.__impl.data[self.__impl.index]
    else:
      return None, constants.STATUS_DONE

  def get_all(self):
    remaining = self.__impl.remaining()
    if remaining:
      return remaining
    else:
      return None, constants.STATUS_DONE

  # This implementation class provides a Pythonic iterator interface that's
  # useful in generated code.  The containing class provides the "classic"
  # get_first/get_next interface required by the builtin "loop" variable
  # and by the iterator plugin.  The two interfaces share the same state,
  # and so may be freely invoked in an interleaved fashion.

  class __IteratorImpl:
    def __init__(self, data):
      self.data = data
      self.error = ""
      self.dataset = None
      self.size = None
      self.max = None
      self.index = None
      self.count = None
      self.first = False
      self.last = False
      self.prev = None
      self.next_ = None

    def start(self):
      self.dataset = self.data
      self.size = len(self.data)
      if self.size == 0:
        return False
      self.max = self.size - 1
      self.index = 0
      self.count = 1
      self.first = True
      self.last = self.size == 1
      self.prev = None
      if len(self.dataset) >= 2:
        self.next_ = self.dataset[1]
      else:
        self.next_ = None
      return True

    def advance(self):
      if self.index is None:
        sys.stderr.write("iterator get_next() called before get_first()")
        return False
      elif self.index >= self.max:
        return False
      else:
        self.index += 1
        self.count = self.index + 1
        self.first = False
        self.last = self.index == self.max
        self.prev = self.data[self.index - 1]
        if self.index < len(self.data) - 1:
          self.next_ = self.data[self.index + 1]
        else:
          self.next_ = None
        return True

    def remaining(self):
      if self.index >= self.max:
        return None
      else:
        start = self.index + 1
        self.index = self.max
        self.count = self.max + 1
        self.first = False
        self.last = True
        return util.unscalar_list(self.dataset[start:])

    def __iter__(self):
      self.start()
      # Tell the next call to next() that the current state already
      # points to the first object, and not to advance to the second:
      self.ready = False
      return self

    def next(self):
      if not self.ready:
        self.ready = True
        if self.data:
          return util.unscalar(self.data[0])
      elif self.advance():
        return util.unscalar(self.data[self.index])
      raise StopIteration
