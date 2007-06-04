from template import plugin

def make_formatter(format="%s"):
  def formatter(*args):
    # NB: Python's formatting operation is much more brittle than Perl's...
    # A robust implementation here would pad out args with the appropriate
    # number and type of unspecified arguments.
    return format % args
  return formatter

class Format(plugin.Plugin):
  @classmethod
  def load(cls, context=None):
    return cls.factory

  @classmethod
  def factory(cls, context, format=None):
    if format is not None:
      return make_formatter(format)
    else:
      return make_formatter

