import re
import sys

import template
from template import base, constants, util
from template.plugin import filter as plugin_filter

eval_namespace = {}

# Static filters:

def html_filter(text):
  return (text.replace("&", "&amp;")
              .replace("<", "&lt;")
              .replace(">", "&gt;")
              .replace('"', "&quot;"))

def html_paragraph(text):
  return ("<p>\n"
          + "\n</p>\n\n<p>\n".join(re.split(r"(?:\r?\n){2,}", text))
          + "</p>\n")

def html_para_break(text):
  return re.sub(r"(\r?\n){2,}", r"\1<br />\1<br />\1", text)

def html_line_break(text):
  return re.sub(r"(\r?\n)", r"<br />\1", text)

URI_ESCAPES = dict((chr(x), "%%%02X" % x) for x in range(256))

def uri_filter(text):
  return re.sub(r"[^;\/?:@&=+\$,A-Za-z0-9\-_.!~*'()]",
                lambda m: URI_ESCAPES[m.group(0)], text)

def ucfirst(text):
  if text:
    text = text[0].upper() + text[1:]
  return text

def lcfirst(text):
  if text:
    text = text[0].lower() + text[1:]
  return text

def stderr(*args):
  for arg in args:
    sys.stderr.write(str(arg))
  return ""

def collapse(text):
  return re.sub(r"\s+", " ", text.strip())


# Dynamic filter factories:

def html_entity_filter_factory(context):
  try:
    import htmlentitydefs
  except:
    return None, base.Exception("html_entity", "cannot import htmlentitydefs")
  def encode(char):
    return (htmlentitydefs.codepoint2name.get(char)
            or "%%%02X" % char)
  def filter(text=""):
    return re.sub(r"[^\n\r\t !\#\$%\'-;=?-~]",
                  lambda m: encode(ord(m.group(0))), text)
  return filter

def indent_filter_factory(context, pad=4):
  try:
    pad = " " * int(pad)
  except:
    pass
  def indent(text=""):
    return re.sub(r"(?m)^(?=(?s).)", lambda m: pad, text)
  return indent

def format_filter_factory(context, formatstr="%s"):
  def format(text=""):
    # The "rstrip" is to emulate Perl's strip, which elides trailing nulls.
    return "\n".join(formatstr % string
                     for string in text.rstrip("\n").split("\n"))
  return format


def truncate_filter_factory(context, length=32, char="..."):
  def truncate(text=""):
    if len(text) <= length:
      return text
    else:
      return text[:length-len(char)] + char
  return truncate

def repeat_filter_factory(context, iter=1):
  def repeat(text=""):
    return text * iter
  return repeat

def replace_filter_factory(context, search="", replace=""):
  def replace_(text=""):
    return re.sub(search, replace, text)
  return replace_

def remove_filter_factory(context, search="", *args):
  def remove(text=""):
    return re.sub(search, "", text)
  return remove

def eval_filter_factory(context):
  def eval(text=""):
    return context.process(util.Literal(text))
  return eval

def python_filter_factory(context):
  if not context.eval_python():
    return None, base.Exception("python", "EVAL_PYTHON is not set")
  def python_filter(text):
    saved = (eval_namespace.get("context"), eval_namespace.get("stash"))
    eval_namespace["context"] = context
    eval_namespace["stash"] = context.stash()
    try:
      try:
        return str(eval(text, eval_namespace))
      except Exception, e:
        context.throw(e)
    finally:
      eval_namespace["context"], eval_namespace["stash"] = saved
  return python_filter

def redirect_filter_factory(context, file, options=None):
  outpath = context.config().get("OUTPUT_PATH")
  if not outpath:
    return None, base.Exception("redirect", "OUTPUT_PATH is not set")
  if not isinstance(options, dict):
    options = { "binmode": options }
  def redirect(text=""):
    outpath = context.config().get("OUTPUT_PATH")
    if not outpath:
      return ""
    outpath += "/" + str(file)
    error = template._output(outpath, util.Reference(text), options)
    if error:
      raise base.Exception("redirect", error)
    return ""
  return redirect

def stdout_filter_factory(context, options=None):
  if not isinstance(options, dict):
    options = {"binmode": options}
  def stdout(text):
    sys.stdout.write(text)
    return ""
  return stdout



FILTERS = {
  "html": html_filter,
  "html_para": html_paragraph,
  "html_break": html_para_break,
  "html_para_break": html_para_break,
  "html_line_break": html_line_break,
  "uri": uri_filter,
  "upper": str.upper,
  "lower": str.lower,
  "ucfirst": ucfirst,
  "lcfirst": lcfirst,
  "stderr": stderr,
  "trim": str.strip,
  "null": lambda x: "",
  "collapse": collapse,

  # dynamic filters
  "html_entity": [html_entity_filter_factory, True],
  "indent":      [indent_filter_factory, True],
  "format":      [format_filter_factory, True],
  "truncate":    [truncate_filter_factory, True],
  "repeat":      [repeat_filter_factory, True],
  "replace":     [replace_filter_factory, True],
  "remove":      [remove_filter_factory, True],
  "eval":        [eval_filter_factory, True],
  "evaltt":      [eval_filter_factory, True], # alias
  "python":      [python_filter_factory, True],
  "redirect":    [redirect_filter_factory, True],
  "file":        [redirect_filter_factory, True], # alias
  "stdout":      [stdout_filter_factory, True],
##   "latex":       [latex_filter_factory, True],
 }

class Filters(base.Base):
  def __init__(self, params):
    self.FILTERS  = params.get("FILTERS")  or {}
    self.TOLERANT = params.get("TOLERANT") or False
    self.DEBUG    = (params.get("DEBUG") or 0) & constants.DEBUG_FILTERS

  def fetch(self, name, args, context):
    factory = None
    error   = None

    if not isinstance(name, str):
      if isinstance(name, plugin_filter.Filter):
        factory = name.factory()
        if not factory:
          return self.error(name.error())
      else:
        return name, None
    else:
      factory = self.FILTERS.get(name) or FILTERS.get(name)
      if not factory:
        return None, constants.STATUS_DECLINED
    if isinstance(factory, (tuple, list)):
      factory, is_dynamic = util.unpack(factory, 2)
    else:
      is_dynamic = False

    if callable(factory):
      if is_dynamic:
        try:
          retval = factory(context, *(args or []))
          if isinstance(retval, (tuple, list)):
            filter, error = util.unpack(retval, 2)
          else:
            filter, error = retval, None
        except base.Exception, e:
          error = error or e
        except Exception, e:
          error = error or base.Exception(constants.ERROR_FILTER, str(e))
        if not (error or callable(filter)):
          error = "invalid FILTER for '%s' (not callable)" % name
      else:
        filter = factory
    else:
      error = "invalid FILTER entry for '%s' (not callable)" % name

    if not error:
      return filter, None
    elif self.TOLERANT:
      return None, constants.STATUS_DECLINED
    else:
      return error, constants.STATUS_ERROR

  def store(self, name, filter):
    self.FILTERS[name] = filter
    return True, None
