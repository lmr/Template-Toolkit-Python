import math
import random
import re

from template import util
from template.plugin import Plugin


OCT_REGEX = re.compile(r'^\s*(0[xb]?)?')

OCT_DIGITS = {
  '0b': (2, re.compile(r'[01]*')),
  '0': (8, re.compile(r'[0-7]*')),
  None: (8, re.compile(r'[0-7]*')),
  '0x': (16, re.compile(r'[0-9A-Fa-f]*')),
}

# Our global random number object:
Random = random.Random()

# A casual search finds no obvious Python counterpart to Perl's
# Math::TrulyRandom module.  If you have one, set the following global
# variable to the function you want.
TrulyRandomFunction = None


# A trivial local error class.
class Error(Exception):
  pass


def numify(func):
  """A function decorator that converts all arguments to numbers via the
  Perl-style parsing routine util.numify.
  """
  def decorated(self, *args):
    return func(*(util.numify(arg) for arg in args))
  return decorated


def numify_method(func):
  """A function decorator that converts all arguments to numbers via the
  Perl-style parsing routine util.numify.
  """
  def decorated(self, *args):
    return func(self, *(util.numify(arg) for arg in args))
  return decorated


class Math(Plugin):
  def __init__(self, context, config=None):
    Plugin.__init__(self)
    self.__config = config  # unused

  def abs(self, x):
    # The built-in abs always returns a float, which is here cast back to
    # the type of the input argument, so that (for example) the absolute
    # value of an int is returned as an int.
    return type(x)(abs(util.numify(x)))

  atan2 = numify(math.atan2)

  cos = numify(math.cos)

  exp = numify(math.exp)

  @numify_method
  def hex(self, x):
    return int(str(x), 16)

  int = numify(int)

  log = numify(math.log)

  def oct(self, x):
    x = str(x)
    match = OCT_REGEX.match(x)
    base, regex = OCT_DIGITS[match.group(1)]
    digits = regex.match(x[len(match.group()):]).group()
    if len(digits) == 0:
      return 0
    else:
      return int(digits, base)

  @numify_method
  def rand(self, x):
    return Random.uniform(0, x)

  sin = numify(math.sin)

  @numify_method
  def sqrt(self, x):
    root = math.sqrt(x)
    trunc = long(root)
    # Try to return an integer, if possible:
    if root == trunc:
      return trunc
    else:
      return root

  srand = numify(Random.seed)

  @numify_method
  def truly_random(self, x):
    if TrulyRandomFunction is None:
      raise Error("No truly_random dispatch function has been defined")
    return TrulyRandomFunction(x)

  pi = math.pi

  tan = numify(math.tan)

  @numify_method
  def csc(self, x):
    return 1.0 / math.sin(x)

  cosec = csc

  @numify_method
  def sec(self, x):
    return 1.0 / math.cos(x)

  @numify_method
  def cot(self, x):
    return 1.0 / math.tan(x)

  cotan = cot

  asin = numify(math.asin)

  acos = numify(math.acos)

  atan = numify(math.atan)

  def acsc(x):
    return math.pi / 2.0 - self.asec(x)

  acosec = acsc

  @numify_method
  def asec(self, x):
    return math.acos(1.0 / x)

  @numify_method
  def acot(self, x):
    return math.pi / 2.0 - math.atan(x)

  acotan = acot

  sinh = numify(math.sinh)

  cosh = numify(math.cosh)

  tanh = numify(math.tanh)

  @numify_method
  def csch(self, x):
    return 1.0 / math.sinh(x)

  cosech = csch

  @numify_method
  def sech(self, x):
    return 1.0 / math.cosh(x)

  @numify_method
  def coth(self, x):
    return 1.0 / math.tanh(x)

  cotanh = coth

  @numify_method
  def asinh(self, x):
    return math.log(x + math.sqrt(x*x + 1))

  @numify_method
  def acosh(self, x):
    pass  # Not sure what to do here...

  @numify_method
  def atanh(self, x):
    return math.log((1 + x) / (1 - x)) / 2.0

  @numify_method
  def acsch(self, x):
    if x < 0:
      return math.log((1.0 - math.sqrt(1 + x * x)) / x)
    else:
      return math.log((1.0 + math.sqrt(1 + x * x)) / x)

  acosech = acsch

  @numify_method
  def asech(self, x):
    pass  # Not sure what to do here either...

  @numify_method
  def acoth(self, x):
    return math.log((1.0 + x) / (1.0 - x)) / 2.0

  acotanh = acoth

  rad2deg = numify(math.degrees)

  @numify_method
  def rad2grad(self, x):
    return math.degrees(x) * 10.0 / 9.0

  deg2rad = numify(math.radians)

  @numify_method
  def deg2grad(self, x):
    return x * 10.0 / 9.0

  @numify_method
  def grad2rad(self, x):
    return math.radians(x * 0.9)

  @numify_method
  def grad2deg(self, x):
    return x * 0.9


