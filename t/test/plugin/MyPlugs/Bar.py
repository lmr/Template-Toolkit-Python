from template.plugin import Plugin


class Bar(Plugin):
  def __init__(self, context, value):
    Plugin.__init__(self)
    self.__value = value

  def output(self):
    return "This is the Bar plugin, value is %s" % (self.__value,)

