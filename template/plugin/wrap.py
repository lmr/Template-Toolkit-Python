import textwrap

from template import plugin


def tt_wrap(text, width=72, itab="", ntab=""):
  return textwrap.fill(text, width,
                       initial_indent=itab,
                       subsequent_indent=ntab)


def wrap_filter_factory(context, *args):
  def wrap_filter(text):
    return tt_wrap(text, *args)
  return wrap_filter


class Wrap(plugin.Plugin):
  @classmethod
  def load(cls, context=None):
    return cls.factory

  @classmethod
  def factory(cls, context):
    context.define_filter('wrap', [ wrap_filter_factory, True ])
    return tt_wrap
