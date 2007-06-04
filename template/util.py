import types
import operator

def make_list(*args):
  list = []
  for arg in args:
    if isinstance(arg, xrange):
      list.extend(arg)
    else:
      list.append(arg)
  return list


class Reference:
  def __init__(self, value, key=None):
    self.value = value
    self.key   = key

  def set(self, newvalue):
    if self.key is None:
      self.value = newvalue
    elif isinstance(self.value, types.InstanceType):
      setattr(self.value, self.key, newvalue)
    elif isinstance(self.value, (dict, list)):
      self.value[self.key] = newvalue

  def get(self):
    if self.key is None:
      return self.value
    elif isinstance(self.value, types.InstanceType):
      return getattr(self.value, self.key)
    elif isinstance(self.value, (dict, list)):
      return self.value[self.key]
    else:
      pass

  def __str__(self):
    return "\\" + repr(self.get())


def can(object, method):
  return callable(getattr(object, method, None))


def chop(seq, n):
  buf = []
  for elt in seq:
    buf.append(elt)
    if len(buf) == n:
      yield tuple(buf)
      buf[:] = []
  if buf:
    yield tuple(buf) + (None,) * (n - len(buf))


def unpack(seq, n):
  return chop(seq, n).next()


def listify(arg):
  if isinstance(arg, list):
    return arg
  else:
    return [arg]

