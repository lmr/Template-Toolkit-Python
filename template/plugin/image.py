import os
import PIL.Image

from template.base import TemplateException
from template.plugin import Plugin


def Init(func):
  def decorated(self):
    self.init()
    return func(self)
  return decorated


class Image(Plugin):
  def __init__(self, context, name=None, config=None):
    if isinstance(name, dict):
      name, config = None, name
    Plugin.__init__(self)
    if not isinstance(config, dict):
      config = {}
    if name is None:
      name = config.get("name")
    if not name:
      return self.throw("no image file specfied")
    root = config.get("root")
    if root:
      file = os.path.join(root, name)
    else:
      file = config.get("file") or name
    self.__name = name
    self.__file = file
    self.__root = root
    self.__size = None
    self.__width = None
    self.__height = None
    self.__alt = config.get("alt", "")

  def init(self):
    if self.__size is None:
      try:
        self.__size = PIL.Image.open(self.__file).size
      except Exception, e:
        self.throw(e)
      self.__width, self.__height = self.__size
      self.__modtime = os.stat(self.__file).st_mtime
    return self

  @Init
  def name(self):
    return self.__name

  @Init
  def file(self):
    return self.__file

  @Init
  def size(self):
    return self.__size

  @Init
  def width(self):
    return self.__width

  @Init
  def height(self):
    return self.__height

  @Init
  def root(self):
    return self.__root

  @Init
  def modtime(self):
    """Return last modification time as a time_t."""
    return self.__modtime

  def attr(self):
    """Return the width and height as HTML/XML attributes."""
    return 'width="%d" height="%d"' % self.size()

  def tag(self, options=None):
    """Returns an XHTML img tag."""
    options = options or {}
    options.setdefault("alt", self.__alt)
    return '<img src="%s" %s%s />' % (
      self.name(), self.attr(),
      "".join(' %s="%s"' % (key, escape(value))
              for key, value in options.items()))

  def throw(self, error):
    raise TemplateException("Image", error)


def escape(text):
  return str(text) \
         .replace("&", "&amp;") \
         .replace("<", "&lt;") \
         .replace(">", "&gt;") \
         .replace('"', "&quot;")

