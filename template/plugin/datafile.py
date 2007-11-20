import re

from template.plugin import Plugin


class Datafile(Plugin):
  def __init__(self, context, filename, params=None):
    Plugin.__init__(self)
    params = params or {}
    delim = params.get("delim") or ":"
    items = []
    line = None
    names = None
    splitter = re.compile(r'\s*%s\s*' % re.escape(delim))

    try:
      f = open(filename)
    except IOError, e:
      return self.fail("%s: %s" % (filename, e))

    for line in f:
      line = line.rstrip("\n\r")
      if not line or line.startswith("#") or line.isspace():
        continue
      fields = splitter.split(line)
      if names is None:
        names = fields
      else:
        fields.extend([None] * (len(names) - len(fields)))
        items.append(dict(zip(names, fields)))

    f.close()
    self.items = items
    # Hack to allow stash to recognize this object as a list:
    self.TT_LIST_ATTRIBUTE = self.items

  def __iter__(self):
    return iter(self.items)
