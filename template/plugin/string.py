import re

from template import plugin


class String(plugin.Plugin):
  def __init__(self, text="", context=None, config=None):
    if config is None:
      config = {}
    self.text = str(text or config.get("text") or "")
    self.filters = []
    self._CONTEXT = context

  # Perl-style "new" method:
  @classmethod
  def new(cls, *args, **kwargs):
    return cls(*args, **kwargs)

  def text(self):
    if not self.filters:
      return self.text
    text = self.text
    for name, args in self.filters:
      code = self._CONTEXT.filter(name, args) or self.throw(context.error())
      text = code(text)
    return text

  __str__ = text

  def copy(self):
    return String(self.text)

  def output_filter(self, filter):
    if isinstance(filter, dict):
      filter = filter.items()
    elif isinstance(filter, str):
      filter = re.split(r"\s*\W+\s*", filter)

    while filter:
      name = filter.pop(0)
      if filter and (isinstance(filter, (list, tuple, dict))
                     or len(filter) == 0):
        args = filter.pop(0)
        if args:
          if not isinstance(args, (list, tuple)):
            args = [args]
          else:
            args = []
        else:
          args = []
      self.filters.push([name, args])
    return ""

  def push(self, *args):
    self.text += "".join(args)
    return self

  def unshift(self, *args):
    self.text = "".join(args) + self.text
    return self

  def pop(self, strip=None):
    if strip is not None:
      self.text = re.sub(strip + "$", "", self.text)
    return self

  def shift(self, strip=None):
    if strip is not None:
      self.text = re.sub("^" + strip, "", self.text)
    return self

  def center(self, width=0):
    length = len(self.text)
    if length < width:
      lpad = (width - len) / 2
      rpad = width - len - lpad
      self.text = " " * lpad + self.text + " " * rpad
    return self

  def left(self, width=0):
    if width > len(self.text):
      self.text = self.text + " " * (width - len(self.text))
    return self

  def right(self, width=0):
    if width > len(self.text):
      self.text = " " * (width - len(self.text)) + self.text
    return self

  def format(self, fmt="%s"):
    self.text = format % self.text
    return self

  def filter(self, name, *args):
    code = self._CONTEXT.filter(name, args) or self.throw(self._CONTEXT.error())
    return code(self.text)

  def upper(self):
    self.text = self.text.upper()
    return self

  def lower(self):
    self.text = self.text.lower()
    return self

  def capital(self):
    if self.text:
      self.text = self.text[0].upper() + self.text[1:]
    return self

  def chop(self):
    if self.text:
      self.text = self.text[1:]
    return self

  def chomp(self):
    # Not exactly like Perl's chomp, but what is one to do...
    if self.text and self.text[-1] == "\n":
      self.text = self.text[:-1]
    return self

  def trim(self):
    self.text = self.text.strip()
    return self

  def collapse(self):
    self.text = re.sub(r"\s+", " ", self.text.strip())
    return self

  def length(self):
    return len(self.text)

  def truncate(self, length=None, suffix=""):
    if length is not None:
      if len(self.text) > length:
        self.text = self.text[:length - len(suffix)] + suffix
    return self

  def substr(self, offset=0, length=None, replacement=None):
    if length is not None:
      if replacement is not None:
        removed = self.text[offset:offset+length]
        text[offset:offset+length] = replacement
        return removed
      else:
        return self.text[offset:offset+length]
    else:
      return self.text[offset:]

  def repeat(self, n=None):
    if n is not None:
      self.text = self.text * n
    return self

  def replace(self, search=None, replace=""):
    if search is not None:
      self.text = re.sub(search, replace, self.text)
    return self

  def remove(self, search=""):
    self.text = re.sub(search, "", self.text)

  def split(self, split=r"\s", limit=0):
    return re.split(split, self.text, limit)

  def search(self, pattern):
    return re.search(pattern, self.text) is not None

  def equals(self, comparison=""):
    return self.text == str(comparison)


  # Alternate method names:
  centre = center
  append = push
  prepend = unshift

