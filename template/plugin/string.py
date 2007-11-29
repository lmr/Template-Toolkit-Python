import re

from template.plugin import Plugin


class String(Plugin):
  def __init__(self, context, *args):
    Plugin.__init__(self)
    args, config = self._split_arguments(args)
    if "text" in config:
      self._text = config["text"]
    elif args:
      self._text = args[0]
    else:
      self._text = ""
    self.filters = []
    self._CONTEXT = context
    filter = config.get("filter") or config.get("filters")
    if filter:
      self.output_filter(filter)

  # Perl-style "new" method:
  def new(self, *args):
    return self.__class__(self._CONTEXT, *args)

  def text(self):
    if not self.filters:
      return self._text
    _text = self._text
    for name, args in self.filters:
      code = self._CONTEXT.filter(name, args)
      _text = code(_text)
    return _text

  __str__ = text

  def __eq__(self, other):
    return self.text() == other.text()

  def __ne__(self, other):
    return self.text() != other.text()

  def copy(self):
    return String(self._CONTEXT, self._text)

  def output_filter(self, filter):
    if isinstance(filter, dict):
      filter = list(sum(filter.items(), ()))
    elif isinstance(filter, str):
      filter = re.split(r"\s*\W+\s*", filter)

    while filter:
      name = filter.pop(0)
      if filter and (isinstance(filter[0], (list, tuple, dict))
                     or len(filter[0]) == 0):
        args = filter.pop(0)
        if args:
          if not isinstance(args, (list, tuple)):
            args = [args]
        else:
          args = []
      else:
        args = []
      self.filters.append([name, args])
    return ""

  def push(self, *args):
    self._text += "".join(args)
    return self

  def unshift(self, *args):
    self._text = "".join(args) + self._text
    return self

  def pop(self, strip=None):
    if strip is not None:
      self._text = re.sub(strip + "$", "", self._text)
    return self

  def shift(self, strip=None):
    if strip is not None:
      self._text = re.sub("^" + strip, "", self._text)
    return self

  def center(self, width=0):
    length = len(self._text)
    if length < width:
      lpad = (width - length) // 2
      rpad = width - length - lpad
      self._text = " " * lpad + self._text + " " * rpad
    return self

  def left(self, width=0):
    if width > len(self._text):
      self._text += " " * (width - len(self._text))
    return self

  def right(self, width=0):
    if width > len(self._text):
      self._text = " " * (width - len(self._text)) + self._text
    return self

  def format(self, fmt="%s"):
    self._text = fmt % self._text
    return self

  def filter(self, name, *args):
    code = self._CONTEXT.filter(name, args)
    return code(self._text)

  def upper(self):
    self._text = self._text.upper()
    return self

  def lower(self):
    self._text = self._text.lower()
    return self

  def capital(self):
    if self._text:
      self._text = self._text[0].upper() + self._text[1:]
    return self

  def chop(self):
    if self._text:
      self._text = self._text[:-1]
    return self

  def chomp(self):
    # Not exactly like Perl's chomp, but what is one to do...
    if self._text and self._text[-1] == "\n":
      self._text = self._text[:-1]
    return self

  def trim(self):
    self._text = self._text.strip()
    return self

  def collapse(self):
    self._text = re.sub(r"\s+", " ", self._text.strip())
    return self

  def length(self):
    return len(self._text)

  def truncate(self, length=None, suffix=""):
    if length is not None:
      if len(self._text) > length:
        self._text = self._text[:length - len(suffix)] + suffix
    return self

  def substr(self, offset=0, length=None, replacement=None):
    if length is not None:
      if replacement is not None:
        removed = self._text[offset:offset+length]
        self._text = (self._text[:offset]
                      + replacement
                      + self._text[offset+length:])
        return removed
      else:
        return self._text[offset:offset+length]
    else:
      return self._text[offset:]

  def repeat(self, n=None):
    if n is not None:
      self._text = self._text * n
    return self

  def replace(self, search=None, replace=""):
    if search is not None:
      self._text = re.sub(search, replace, self._text)
    return self

  def remove(self, search=""):
    self._text = re.sub(search, "", self._text)
    return self

  def split(self, split=r"\s", limit=0):
    if limit == 0:
      return re.split(split, self._text)
    else:
      return re.split(split, self._text, limit - 1)

  def search(self, pattern):
    return re.search(pattern, self._text) is not None

  def equals(self, comparison=""):
    return self._text == str(comparison)

  # Alternate method names:
  centre = center
  append = push
  prepend = unshift

