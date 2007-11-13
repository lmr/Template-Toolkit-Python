import re

from template.plugin import Plugin


class Html(Plugin):
  def __init__(self, context, args=None):
    Plugin.__init__(self)
    self.__sorted = bool(args and args.get("sorted"))

  def element(self, name, attr=None):
    if isinstance(name, dict):
      name, attr = name.items()[0]
    if name is None or len(str(name)) == 0:
      return ""
    attr = self.attributes(attr)
    return "<%s%s%s>" % (name, attr and " " or "", attr)

  def attributes(self, hash):
    if not isinstance(hash, dict):
      return ""
    items = hash.items()
    if self.__sorted:
      items.sort()
    return " ".join('%s="%s"' % (k, self.escape(v)) for k, v in items)

  def escape(self, text=""):
    return str(text) \
           .replace("&", "&amp;") \
           .replace("<", "&lt;") \
           .replace(">", "&gt;") \
           .replace('"', "&quot;")

  def url(self, text=None):
    if text is None:
      return None
    else:
      return re.sub(r"[^a-zA-Z0-9_.-]",
                    lambda match: "%%%02x" % ord(match.group()),
                    text)
