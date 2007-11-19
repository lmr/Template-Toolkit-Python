from template.plugin import Plugin


class Filter(Plugin):
  _DYNAMIC = False

  def __init__(self, context, *args):
    Plugin.__init__(self)
    if args and isinstance(args[-1], dict):
      config = args.pop()
    else:
      config = {}
    self._CONTEXT = context
    self._ARGS    = args
    self._CONFIG  = config

  def factory(self):
    if self._DYNAMIC:
      if not self._DYNAMIC_FILTER:
        def factory(context, *args):
          if args and isinstance(args[-1], dict):
            config = args.pop()
          else:
            config = {}
          def filter(text):
            return self.filter(text, args, config)
          return filter
        self._DYNAMIC_FILTER = [factory, True]
      return self._DYNAMIC_FILTER
    else:
      if not self._STATIC_FILTER:
        def filter(text):
          return self.filter(text)
        self._STATIC_FILTER = filter
      return self._STATIC_FILTER

  def filter(self, text, args=None, config=None):
    return text

  def merge_config(self, newcfg):
    owncfg = self._CONFIG
    if not newcfg:
      return owncfg
    copy = owncfg.copy()
    copy.update(newcfg)
    return copy

  def merge_args(self, newargs):
    ownargs = self._ARGS
    if not newargs:
      return ownargs
    return ownargs + newargs

  def install_filter(self, name):
    self._CONTEXT.define_filter(name, self.factory())
    return self


