import re

from template.plugin import Plugin
from template import util


JOINT = "&amp;"


class Url(Plugin):
  @classmethod
  def load(cls, context=None):
    return cls.factory

  @classmethod
  def factory(cls, context, base=None, args=None):
    def url(newbase=None, newargs=None):
      if isinstance(newbase, dict):
        newbase, newargs = None, newbase
      combo = (args or {}).copy()
      combo.update(newargs or {})
      urlargs = JOINT.join([var for key, value in combo.items()
                                for var in Args(key, value)
                                if value is not None and len(str(value)) > 0])
      query = newbase or base or ""
      if query and urlargs:
        query += "?"
      if urlargs:
        query += urlargs
      return query
    return url


def Args(key, val):
  key = escape(key)
  if not util.is_seq(val):
    val = [val]
  return ["%s=%s" % (key, escape(v)) for v in val]


def escape(toencode):
  if toencode is None:
    return None
  return re.sub(r"[^a-zA-Z0-9_.-]", lambda m: "%%%02x" % ord(m.group()),
                str(toencode))


