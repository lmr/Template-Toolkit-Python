import re
import sys


class TemplateException(Exception):
  def __init__(self, type, info, buffer=None):
    Exception.__init__(self)
    self.__type = type
    self.__info = info
    self.__buffer = buffer

  def text(self, buffer=None):
    if buffer:
      if self.__buffer and self.__buffer is not buffer:
        buffer.reset(buffer.get() + self.__buffer.get())
      self.__buffer = buffer
      return ""
    elif self.__buffer:
      return self.__buffer.get()
    else:
      return ""

  def select_handler(self, options):
    type = str(self.__type)
    hlut = dict((str(option), True) for option in options)
    while type:
      if hlut.get(type):
        return type
      type = re.sub(r'\.?[^.]*$', '', type)
    return None

  def type(self):
    return self.__type

  def info(self):
    return self.__info

  def type_info(self):
    return self.__type, self.__info

  def __str__(self):
    return "%s error - %s" % (self.__type or "", self.__info)


class Base:
  def __init__(self):
    self._ERROR = None

  def error(self, *args):
    if args:
      self._ERROR = self.__ErrorMessage(args)
    else:
      return self._ERROR

  def DEBUG(self, *args):
    sys.stderr.write("DEBUG: ")
    for arg in args:
      sys.stderr.write(str(arg))

  @classmethod
  def Error(cls, *args):
    if args:
      cls.ERROR = self.__ErrorMessage(args)
    else:
      return getattr(cls, "ERROR", None)

  @staticmethod
  def __ErrorMessage(args):
    if len(args) == 1:
      return args[0]
    else:
      return "".join(args)
