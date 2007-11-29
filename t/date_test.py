import locale as Locale
import re
import time as Time

from template.plugin import date as date_plugin
from template.test import TestCase, main
from template.util import TemplateException


def time_locale(time, format, locale):
  old_locale = Locale.setlocale(Locale.LC_ALL)
  try:
    # Some systems expect locales to have a particular suffix.
    for suffix in ("",) + date_plugin.LOCALE_SUFFIX:
      try_locale = "%s%s" % (locale, suffix)
      try:
        setlocale = Locale.setlocale(Locale.LC_ALL, try_locale)
      except Locale.Error:
        continue
      else:
        if try_locale == setlocale:
          locale = try_locale
          break
    datestr = Time.strftime(format, Time.localtime(time))
  finally:
    Locale.setlocale(Locale.LC_ALL, old_locale)
  return datestr

def date_locale(time, format, locale):
  date = re.split(r"[-/ :]", time)
  if len(date) < 6:
    return None, TemplateException(
      "date", "bad time/date string:  expects 'h:m:s d:m:y'  got: '%s'"
      % time)
  date = [str(int(x)) for x in date[:6]]
  date = Time.mktime(Time.strptime(" ".join(date), "%H %M %S %d %m %Y"))
  return time_locale(date, format, locale)


class DateTest(TestCase):
  def testDate(self):
    format = { "default": date_plugin.FORMAT,
               "time": "%H:%M:%S",
               "date": "%d-%b-%Y",
               "timeday": "the time is %H:%M:%S on %A" }
    now = int(Time.time())
    ltime = Time.localtime(now)
    params = { "time": now,
               "format": format,
               "timestr": Time.strftime(format["time"], ltime),
               "datestr": Time.strftime(format["date"], ltime),
               "daystr": Time.strftime(format["timeday"], ltime),
               "defstr": Time.strftime(format["default"], ltime),
               "now": lambda arg=None: Time.strftime(arg or format["default"],
                                                     Time.localtime()),
               "time_locale": time_locale,
               "date_locale": date_locale,
               "date_calc": False }
    Time.sleep(1)
    self.Expect(DATA, { "POST_CHOMP": 1 }, params)


DATA = r"""
-- test --
[% USE date %]
Let's hope the year doesn't roll over in between calls to date.format()
and now()...
Year: [% date.format(format => '%Y') %]

-- expect --
-- process --
Let's hope the year doesn't roll over in between calls to date.format()
and now()...
Year: [% now('%Y') %]

-- test --
[% USE date(time => time) %]
default: [% date.format %]

-- expect --
-- process --
default: [% defstr %]

-- test --
[% USE date(time => time) %]
[% date.format(format => format.timeday) %]

-- expect --
-- process --
[% daystr %]

-- test --
[% USE date(time => time, format = format.date) %]
Date: [% date.format %]

-- expect --
-- process --
Date: [% datestr %]

-- test --
[% USE date(format = format.date) %]
Time: [% date.format(time, format.time) %]

-- expect --
-- process --
Time: [% timestr %]

-- test --
[% USE date(format = format.date) %]
Time: [% date.format(time, format = format.time) %]

-- expect --
-- process --
Time: [% timestr %]


-- test --
[% USE date(format = format.date) %]
Time: [% date.format(time = time, format = format.time) %]

-- expect --
-- process --
Time: [% timestr %]

-- test --
[% USE english = date(format => '%A', locale => 'en_GB') %]
[% USE french  = date(format => '%A', locale => 'fr_FR') %]
In English, today's day is: [% english.format +%]
In French, today's day is: [% french.format +%]

-- expect --
-- process --
In English, today's day is: [% time_locale(time, '%A', 'en_GB') +%]
In French, today's day is: [% time_locale(time, '%A', 'fr_FR') +%]

-- test --
[% USE english = date(format => '%A') %]
[% USE french  = date() %]
In English, today's day is: 
[%- english.format(locale => 'en_GB') +%]
In French, today's day is: 
[%- french.format(format => '%A', locale => 'fr_FR') +%]

-- expect --
-- process --
In English, today's day is: [% time_locale(time, '%A', 'en_GB') +%]
In French, today's day is: [% time_locale(time, '%A', 'fr_FR') +%]

-- test --
[% USE date %]
# [% date.format('4:20:00 6-13-2000', '%H') %]
[% date.format('4:20:00 13-6-2000', '%H') %]

-- expect --
04

-- test --
-- name September 13th 2000 --
[% USE day = date(format => '%A', locale => 'en_GB') %]
[% day.format('4:20:00 13-9-2000') %]

-- expect --
-- process --
[% date_locale('4:20:00 13-9-2000', '%A', 'en_GB') %]


-- test --
[% TRY %]
[% USE date %]
[% date.format('some stupid date') %]
[% CATCH date %]
Bad date: [% e.info %]
[% END %]
-- expect --
Bad date: bad time/date string:  expects 'h:m:s d:m:y'  got: 'some stupid date'

-- test --
[% USE date %]
[% template.name %] [% date.format(template.modtime, format='%Y') %]
-- expect --
-- process --
input text [% now('%Y') %]

-- test --
[% IF date_calc -%]
[% USE date; calc = date.calc; calc.Monday_of_Week(22, 2001).join('/') %]
[% ELSE -%]
not testing
[% END -%]
-- expect --
-- process --
[% IF date_calc -%]
2001/5/28
[% ELSE -%]
not testing
[% END -%]

-- test --
[% USE date;
   date.format('12:59:00 30/09/2001', '%H:%M')
-%]
-- expect --
12:59


"""

main()
