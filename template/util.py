import cStringIO
import operator
import re
import sys
import types


class ControlFlowException(Exception):
  pass


class Continue(ControlFlowException):
  pass


class Break(ControlFlowException):
  pass


class StringBuffer:
  """A wrapper around a StringIO object that stringifies all of its
  arguments before writing them.  Provides a handful of other useful
  methods as well.
  """
  def __init__(self, contents=None):
    self.__buffer = cStringIO.StringIO()
    if contents is not None:
      self.write(contents)

  def write(self, *args):
    for arg in args:
      self.__buffer.write(str(arg))

  def clear(self):
    self.__buffer.seek(0)
    self.__buffer.truncate(0)

  def reset(self, *args):
    self.clear()
    self.write(*args)

  def get(self):
    return self.__buffer.getvalue()


class Literal:
  """A trivial wrapper for a template supplied as a string."""
  def __init__(self, text):
    self.__text = text

  def text(self):
    return self.__text


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


NUMBER_RE = re.compile(r"\s*[-+]?(?:\d+(\.\d*)?|(\.\d+))([Ee][-+]?\d+)?")

class PerlScalar:
  __False = (False, 0, "", "0")

  def __init__(self, value, truth=None):
    self.__value = value
    self.__truth = truth

  def value(self):
    return self.__value

  def __rpow__(self, _):
    return PerlScalar(self.__value, True)

  def __add__(self, other):
    return PerlScalar(self.__numify() + other.__numify(), self.__truth)

  def __sub__(self, other):
    return PerlScalar(self.__numify() - other.__numify(), self.__truth)

  def __mul__(self, other):
    return PerlScalar(self.__numify() * other.__numify(), self.__truth)

  def __div__(self, other):
    return PerlScalar(self.__numify() / other.__numify(), self.__truth)

  def __mod__(self, other):
    return PerlScalar(self.__numify() % other.__numify(), self.__truth)

  def __floordiv__(self, other):
    return PerlScalar(self.__numify() // other.__numify(), self.__truth)

  def __eq__(self, other):
    # TODO: These comparison operations might need a little more
    # work to handle Perl-like comparison of strings and numbers, etc.
    return PerlScalar(self.__value == other.__value)

  def __gt__(self, other):
    return PerlScalar(self.__value > other.__value)

  def __ge__(self, other):
    return PerlScalar(self.__value >= other.__value)

  def __lt__(self, other):
    return PerlScalar(self.__value < other.__value)

  def __le__(self, other):
    return PerlScalar(self.__value <= other.__value)

  def __cmp__(self, other):
    return PerlScalar(cmp(self.__value, other.__value))

  def __and__(self, other):
    """String concatenation."""
    return PerlScalar("%s%s" % (self.__value, other.__value))

  def __nonzero__(self):
    if self.__truth is not None:
      return self.__truth
    else:
      return self.__value not in self.__False

  def __invert__(self):
    return PerlScalar(not self)

  def __int__(self):
    try:
      return int(self.__value)
    except (TypeError, ValueError):
      return 0

  def __long__(self):
    try:
      return long(self.__value)
    except (TypeError, ValueError):
      return 0L

  def __iter__(self):
    return iter(self.__value)

  def __str__(self):
    if self.__value is True:
      return "1"
    elif self.__value is False:
      return ""
    else:
      return str(self.__value)

  def __numify(self):
    return numify(self.__value)


def numify(value):
  if isinstance(value, (int, long, float)):
    return value
  match = NUMBER_RE.match(str(value))
  if not match:
    return 0
  elif match.group(1) or match.group(2) or match.group(3):
    return float(match.group(0))
  else:
    return long(match.group(0))


def unindent(code):
  try:
    indent = min(len(match.group())
                 for match in re.finditer(r"(?m)^\s+", code))
    if indent:
      code = re.sub(r"(?m)^.{%d}" % indent, "", code)
  except ValueError:
    pass
  return code


def EvaluateCode(code, context, stash):
  code = unindent(code)
  old_stdout = sys.stdout
  sys.stdout = tmpbuf = cStringIO.StringIO()
  try:
    exec code in {"context": context, "stash": stash}
  finally:
    sys.stdout = old_stdout
  return tmpbuf.getvalue()


def unscalar(x):
  if isinstance(x, PerlScalar):
    return x.value()
  else:
    return x


def unscalar_lex(x):
  if x.startswith("scalar(") and x.endswith(")"):
    return eval(x[7:-1])
  else:
    return x


def unscalar_list(seq):
  try:
    return [unscalar(item) for item in seq]
  except TypeError:
    return []


def ScalarList(*args):
  list = []
  for arg in args:
    if isinstance(arg, xrange):
      list.extend(arg)
    else:
      list.append(unscalar(arg))
  return PerlScalar(list)


def SwitchList(arg):
  value = arg.value()
  if is_seq(value):
    return arg
  else:
    return ScalarList(value)


def ScalarDictionary(*pairs):
  return PerlScalar(dict((unscalar(key), unscalar(val)) for key, val in pairs))


def Concatenate(*args):
  return PerlScalar("".join(str(x) for x in args))


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


def is_seq(x):
  try:
    iter(x)
  except TypeError:
    return False
  else:
    return not isinstance(x, str)


