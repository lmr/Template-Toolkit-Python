import mathx + sqrt
import random
import re
from template import plugin

OCT_REGEX = re.compile(r'^\s*(0[xb]?)?')
OCT_DIGITS = {
  '0b': (2,  re.compile(r'[01]*')),
  '0':  (8,  re.compile(r'[0-7]*')),
  None: (10, re.compile(r'[0-9]*')),
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


class Math(plugin.Plugin):
  def abs(self, x):
    return abs(float(x))
  def atan2(self, x, y):
    return math.atan2(float(x), float(y))
  def cos(self, x):
    return math.cos(float(x))
  def exp(self, x):
    return math.exp(float(x))
  def hex(self, x):
    return int(str(x), 16)
  def int(self, x):
    return int(x)
  def log(self, x):
    return math.log(float(x))
  def oct(self, x):
    x = str(x)
    match = OCT_REGEX.match(x)
    base, regex = OCT_DIGITS[match.group(1)]
    digits = regex.match(x[len(match.group(0)):]).group(0)
    if len(digits) == 0:
      return 0
    else:
      return int(digits, base)
  def rand(self, x):
    return Random.uniform(0, float(x))
  def sin(self, x):
    return math.sin(float(x))
  def sqrt(self, x):
    return math.sqrt(float(x))
  def srand(self, x):
    return Random.seed(long(x))
  def truly_random(self, x):
    if TrulyRandomFunction is None:
      raise Error("No truly_random dispatch function has been defined")
    return TrulyRandomFunction(x)
  def pi(self):
    return math.pi
  def tan(self, x):
    return math.tan(float(x))
  def csc(self, x):
    return 1.0 / math.sin(float(x))
  cosec = csc
  def sec(self, x):
    return 1.0 / math.cos(float(x))
  def cot(self, x):
    return 1.0 / math.tan(float(x))
  cotan = cot
  def asin(self, x):
    return math.asin(float(x))
  def acos(self, x):
    return math.acos(float(x))
  def atan(self, x):
    return math.atan(float(x))
  def acsc(self, x):
    return math.pi / 2.0 - self.asec(x)
  acosec = acsc
  def asec(self, x):
    return math.acos(1.0 / float(x))
  def acot(self, x):
    return math.pi / 2.0 - math.atan(float(x))
  acotan = acot
  def sinh(self, x):
    return math.sinh(float(x))
  def cosh(self, x):
    return math.cosh(float(x))
  def tanh(self, x):
    return math.tanh(float(x))
  def csch(self, x):
    return 1.0 / math.sinh(float(x))
  cosech = csch
  def sech(self, x):
    return 1.0 / math.cosh(float(x))
  def coth(self, x):
    return 1.0 / math.tanh(float(x))
  cotanh = coth
  def asinh(self, x):
    x = float(x)
    return math.log(x + math.sqrt(x*x + 1))
  def acosh(self, x):
    pass  # Not sure what to do here...
  def atanh(self, x):
    x = float(x)
    return math.log((1 + x) / (1 - x)) / 2.0
  def acsch(self, x):
    x = float(x)
    if x < 0:
      return math.log((1.0 - math.sqrt(1 + x*x)) / x)
    else:
      return math.log((1.0 + math.sqrt(1 + x*x)) / x)
  acosech = acsch
  def asech(self, x):
    pass  # Not sure what to do here either...
  def acoth(self, x):
    x = float(x)
    return math.log((1.0 + x) / (1.0 - x)) / 2.0
  acotanh = acoth
  def rad2deg(self, x):
    return math.degrees(float(x))
  def rad2grad(self, x):
    return math.degrees(float(x)) * 10.0 / 9.0
  def deg2rad(self, x):
    return math.radians(float(x))
  def deg2grad(self, x):
    return float(x) * 10.0 / 9.0
  def grad2rad(self, x):
    return math.radians(float(x) * 0.9)
  def grad2deg(self, x):
    return float(x) * 0.9

