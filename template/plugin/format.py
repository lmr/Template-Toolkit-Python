from template import plugin


def make_formatter(format="%s"):
  def formatter(*args):
    # This is a pretty hacky way to simulate Perl's permissive string
    # formatting, which doesn't insist on having exactly the number of
    # specified arguments available.  It should work all right as long
    # as only strings are to be formatted.
    while True:
      try:
        return format % args
      except TypeError, e:
        if e.args[0].startswith("not enough arguments"):
          args += ("",)
        elif e.args[0].startswith("not all arguments converted"):
          args = args[:-1]
        else:
          raise
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

