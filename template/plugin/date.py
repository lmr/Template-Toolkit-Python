import locale as Locale
import re
import time as Time

from template import base, plugin


# Default strftime() format:
FORMAT = "%H:%M:%S %d-%b-%Y"

LOCALE_SUFFIX = (".ISO8859-1", ".ISO_8859-15", ".US-ASCII", ".UTF-8");

GMTIME = { True: Time.gmtime,
           False: Time.localtime }


class Date(plugin.Plugin):
  def __init__(self, context, params=None):
    self.params = params or {}

  def now(self):
    return int(Time.time())

  def format(self, *args):
    args = list(args)
    if args and isinstance(args[-1], dict):
      params = args.pop()
    else:
      params = {}
    def get(name):
      if args:
        return args.pop(0)
      else:
        return params.get(name) or self.params.get(name)
    time = get("time") or self.now()
    format = get("format") or FORMAT
    locale = get("locale")
    gmt = get("gmt")

    try:
      # If time is numeric, we assume it's seconds since the epoch:
      time = int(time)
    except StandardError:
      # Otherwise, we try to parse it as a 'H:M:S D:M:Y' string:
      date = re.split(r"[-/ :]", str(time))
      if len(date) < 6:
        # return None,
        raise base.Exception(
          "date", "bad time/date string:  expects 'h:m:s d:m:y'  got: '%s'"
          % time)
      date = [str(int(x)) for x in date[:6]]
      date = Time.strptime(" ".join(date), "%H %M %S %d %m %Y")
    else:
      date = GMTIME[bool(gmt)](time)

    if locale is not None:
      old_locale = Locale.setlocale(Locale.LC_ALL)
      try:
        for suffix in ("",) + LOCALE_SUFFIX:
          try_locale = "%s%s" % (locale, suffix)
          try:
            setlocale = Locale.setlocale(Locale.LC_ALL, try_locale)
          except Locale.Error:
            continue
          else:
            if try_locale == setlocale:
              locale = try_locale
              break
        datestr = Time.strftime(format, date)
      finally:
        Locale.setlocale(Locale.LC_ALL, old_locale)
    else:
      datestr = Time.strftime(format, date)

    return datestr

  def calc(self):
    self.throw("Failed to load date calculation module")

  def manip(self):
    self.throw("Failed to load date manipulation module")

  def throw(self, *args):
    raise base.Exception("date", ", ".join(str(x) for x in args))

